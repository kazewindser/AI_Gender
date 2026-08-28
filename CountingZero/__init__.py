from otree.api import *

import json
from os import environ
import random
import re
import time
from openai import OpenAI
from settings import ShowFeedback, TreatmentAI


doc = """
Five-minute Counting Zero task. Participants repeatedly count the zeroes in a
random 15 x 15 binary matrix and submit their answer through a live page.
"""


class C(BaseConstants):
    NAME_IN_URL = 'CountingZero'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 3
    MATRIX_SIZE = 15
    MIN_ZERO_COUNT = 0
    MAX_ZERO_COUNT = MATRIX_SIZE * MATRIX_SIZE
    TASK_SECONDS = 5 * 60
    MAX_SCORE_PER_MATRIX = 10
    ZERO_SCORE_ERROR_THRESHOLD = 0.20
    AI_MODEL = 'gpt-5.6-luna'
    AI_REASONING_EFFORT = 'none'
    AI_TEMPERATURE = 1
    AI_SYSTEM_PROMPT = 'Always respond in Japanese.'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    task_started_at = models.FloatField(initial=0)
    current_question_started_at = models.FloatField(initial=0)
    current_matrix = models.LongStringField(blank=True)
    current_correct_count = models.IntegerField(initial=0)
    question_number = models.IntegerField(initial=1)
    cumulative_score = models.FloatField(initial=0)
    round_total_score = models.FloatField(initial=0)
    total_questions = models.IntegerField(initial=0)
    average_response_seconds = models.FloatField(initial=0)
    average_accuracy = models.FloatField(initial=0)
    contemporaneous_rank = models.IntegerField(blank=True)
    rank_in_group = models.IntegerField(blank=True)
    rank_tiebreaker = models.FloatField(blank=True)
    rank_basis = models.StringField(blank=True)
    ranking_comparison = models.LongStringField(blank=True)
    payment_choice = models.StringField(
        choices=[
            ['piece_rate', 'Piece rate'],
            ['tournament', 'Tournament'],
        ],
        widget=widgets.RadioSelect,
    )
    choice_order = models.StringField(blank=True)

    # Reserved for the complete three-stage experiment.
    first_task_score = models.FloatField(initial=0)
    second_task_score = models.FloatField(initial=0)
    third_task_score = models.FloatField(initial=0)
    tournament_rank = models.IntegerField(blank=True)

    # AI chat state. The model context and the analysis log are stored
    # separately so the latter remains easy to export and inspect.
    ai_messages = models.LongStringField(blank=True)
    chat_log = models.LongStringField(blank=True)


class Submission(ExtraModel):
    """One row per submitted matrix, for analysis and custom export."""

    player = models.Link(Player)
    question_number = models.IntegerField()
    matrix = models.LongStringField()
    correct_count = models.IntegerField()
    submitted_count = models.IntegerField()
    absolute_error = models.IntegerField()
    accuracy = models.FloatField()
    score = models.FloatField()
    cumulative_score = models.FloatField()
    question_started_at = models.FloatField()
    response_seconds = models.FloatField()
    submitted_at = models.FloatField()
    elapsed_seconds = models.FloatField()
    remaining_seconds = models.FloatField()


LABEL_PATTERN = re.compile(r'^SUB(\d+)$', re.IGNORECASE)


def initialize_participant_fields(participant):
    """Initialize payment data once; setdefault also supports legacy sessions."""
    defaults = dict(
        cz_round1_score=0,
        cz_round2_score=0,
        cz_round3_score=0,
        cz_round1_rank=0,
        cz_round2_rank=0,
        cz_round3_rank=0,
        cz_round3_choice='',
        cz_selected_round=0,
        cz_final_score=0,
    )
    for field_name, default in defaults.items():
        participant.vars.setdefault(field_name, default)


def creating_session(subsession: Subsession):
    players = subsession.get_players()
    if subsession.round_number == 1:
        for player in players:
            initialize_participant_fields(player.participant)
    labels = [player.participant.label for player in players]

    # Real lab sessions are grouped entirely from labels. Label-free grouping is
    # retained only so the built-in oTree demo launcher remains usable.
    if all(label for label in labels):
        blocks = {}
        seen_numbers = set()
        for player in players:
            match = LABEL_PATTERN.fullmatch(player.participant.label.strip())
            if not match:
                raise ValueError(
                    f'Invalid participant label {player.participant.label!r}; '
                    'expected SUB01, SUB02, ...'
                )
            number = int(match.group(1))
            if number in seen_numbers:
                raise ValueError(f'Duplicate participant label number: SUB{number:02d}')
            seen_numbers.add(number)
            block = (number - 1) // C.PLAYERS_PER_GROUP
            blocks.setdefault(block, []).append((number, player))

        group_matrix = []
        for block, members in sorted(blocks.items()):
            if len(members) != C.PLAYERS_PER_GROUP:
                first = block * C.PLAYERS_PER_GROUP + 1
                last = first + C.PLAYERS_PER_GROUP - 1
                raise ValueError(
                    f'Label group SUB{first:02d}-SUB{last:02d} is incomplete.'
                )
            group_matrix.append([player for _, player in sorted(members)])
        subsession.set_group_matrix(group_matrix)
    elif any(label for label in labels):
        raise ValueError('Either every participant must have a label or none may have one.')


def make_matrix():
    total_cells = C.MATRIX_SIZE * C.MATRIX_SIZE
    correct_count = random.randint(C.MIN_ZERO_COUNT, C.MAX_ZERO_COUNT)
    cells = [0] * correct_count + [1] * (total_cells - correct_count)
    random.shuffle(cells)
    matrix = [
        cells[index:index + C.MATRIX_SIZE]
        for index in range(0, total_cells, C.MATRIX_SIZE)
    ]
    return matrix, correct_count


def sync_stage_scores(player: Player):
    """Keep the three stage totals available on every Player round row."""
    round_players = player.in_all_rounds()
    scores_by_round = {
        round_player.round_number: round_player.cumulative_score
        for round_player in round_players
    }
    for round_player in round_players:
        round_player.first_task_score = scores_by_round.get(1, 0)
        round_player.second_task_score = scores_by_round.get(2, 0)
        round_player.third_task_score = scores_by_round.get(3, 0)


def store_participant_round_result(player: Player):
    participant = player.participant
    if player.round_number == 1:
        participant.cz_round1_score = player.round_total_score
        participant.cz_round1_rank = player.rank_in_group
    elif player.round_number == 2:
        participant.cz_round2_score = player.round_total_score
        participant.cz_round2_rank = player.rank_in_group
    else:
        participant.cz_round3_score = player.round_total_score
        participant.cz_round3_rank = player.rank_in_group
        participant.cz_round3_choice = player.payment_choice


def finalize_participant_payoff(player: Player):
    """Randomly select one stage and calculate its incentive-compatible payoff."""
    participant = player.participant
    # Compatibility for sessions created before participant initialization was
    # introduced. New sessions are initialized in creating_session().
    initialize_participant_fields(participant)
    selected_round = participant.cz_selected_round
    if not selected_round:
        selected_round = random.randint(1, C.NUM_ROUNDS)
        participant.cz_selected_round = selected_round

    scores = {
        1: participant.cz_round1_score,
        2: participant.cz_round2_score,
        3: participant.cz_round3_score,
    }
    ranks = {
        1: participant.cz_round1_rank,
        2: participant.cz_round2_rank,
        3: participant.cz_round3_rank,
    }
    score = scores[selected_round]
    rank = ranks[selected_round]

    if selected_round == 1:
        final_score = score
    elif selected_round == 2:
        final_score = score * C.PLAYERS_PER_GROUP if rank == 1 else 0
    elif participant.cz_round3_choice == 'piece_rate':
        final_score = score
    else:
        # rank_in_group in round 3 already compares the focal participant's
        # round-3 score against the other three players' round-2 scores.
        final_score = score * C.PLAYERS_PER_GROUP if rank == 1 else 0

    final_score = round(final_score, 2)
    participant.cz_final_score = final_score
    player.payoff = final_score


def rank_group(group: Group):
    """Rank performance and apply the NV-style round-3 benchmark."""
    players = group.get_players()

    # Descriptive same-round rank, retained in every round for analysis.
    for player in players:
        player.round_total_score = player.cumulative_score
        player.rank_tiebreaker = random.random()

    contemporaneous_order = sorted(
        players,
        key=lambda player: (-player.round_total_score, player.rank_tiebreaker),
    )
    for rank, player in enumerate(contemporaneous_order, start=1):
        player.contemporaneous_rank = rank

    for player in players:
        if player.round_number == 3 and player.payment_choice == 'tournament':
            # The focal participant's round-3 score competes against the other
            # three group members' round-2 scores, as in NV (2007).
            comparison = [
                dict(
                    id_in_group=player.id_in_group,
                    source_round=3,
                    score=player.round_total_score,
                    is_focal=True,
                    tiebreaker=random.random(),
                )
            ]
            for opponent in players:
                if opponent.id_in_group == player.id_in_group:
                    continue
                opponent_round_2 = opponent.in_round(2)
                comparison.append(
                    dict(
                        id_in_group=opponent.id_in_group,
                        source_round=2,
                        score=opponent_round_2.cumulative_score,
                        is_focal=False,
                        tiebreaker=random.random(),
                    )
                )
            comparison.sort(key=lambda item: (-item['score'], item['tiebreaker']))
            player.rank_in_group = next(
                rank
                for rank, item in enumerate(comparison, start=1)
                if item['is_focal']
            )
            player.rank_tiebreaker = next(
                item['tiebreaker'] for item in comparison if item['is_focal']
            )
            player.rank_basis = 'round3_self_vs_round2_opponents'
            player.ranking_comparison = json.dumps(comparison)
        else:
            # Rounds 1 and 2 use ordinary same-round rankings. Round-3 piece
            # rate participants retain this descriptive rank only.
            player.rank_in_group = player.contemporaneous_rank
            player.rank_basis = 'same_round'
            player.ranking_comparison = json.dumps(
                [
                    dict(
                        id_in_group=member.id_in_group,
                        source_round=player.round_number,
                        score=member.round_total_score,
                        is_focal=member.id_in_group == player.id_in_group,
                        tiebreaker=member.rank_tiebreaker,
                    )
                    for member in contemporaneous_order
                ]
            )

        if player.round_number == 2:
            for round_player in player.in_all_rounds():
                round_player.tournament_rank = player.rank_in_group
        sync_stage_scores(player)
        store_participant_round_result(player)

    if players and players[0].round_number == 3:
        for player in players:
            finalize_participant_payoff(player)


def ensure_task_state(player: Player):
    if not player.field_maybe_none('task_started_at'):
        player.task_started_at = time.time()
    if not player.field_maybe_none('current_matrix'):
        matrix, correct_count = make_matrix()
        player.current_matrix = json.dumps(matrix, separators=(',', ':'))
        player.current_correct_count = correct_count
    if not player.field_maybe_none('current_question_started_at'):
        player.current_question_started_at = time.time()


def state_payload(player: Player, feedback=None):
    ensure_task_state(player)
    elapsed = max(0, time.time() - player.task_started_at)
    payload = dict(
        matrix=json.loads(player.current_matrix),
        question_number=player.question_number,
        remaining_seconds=max(0, C.TASK_SECONDS - elapsed),
    )
    if ShowFeedback:
        payload['cumulative_score'] = round(player.cumulative_score, 2)
    if ShowFeedback and feedback is not None:
        payload['feedback'] = feedback
    return payload


def get_openai_client():
    api_key = environ.get('CHATGPT_KEY') or environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError(
            'OpenAI API key is missing. Set CHATGPT_KEY or OPENAI_API_KEY.'
        )
    return OpenAI(api_key=api_key)


def load_ai_messages(player: Player):
    raw_messages = player.field_maybe_none('ai_messages')
    if raw_messages:
        return json.loads(raw_messages)
    return [{'role': 'system', 'content': C.AI_SYSTEM_PROMPT}]


def load_chat_log(player: Player):
    raw_log = player.field_maybe_none('chat_log')
    return json.loads(raw_log) if raw_log else []


def append_chat_log(player: Player, sender, text):
    log = load_chat_log(player)
    log.append(
        dict(
            sender=sender,
            text=text,
            timestamp=time.time(),
            elapsed_seconds=max(0, time.time() - player.task_started_at),
        )
    )
    player.chat_log = json.dumps(log, ensure_ascii=False)


def live_ai_chat(player: Player, data):
    if not TreatmentAI:
        return {
            player.id_in_group: dict(
                type='chat_error', text='当前实验条件不提供 AI Chat。'
            )
        }

    text = str(data.get('text', '')).strip()
    if not text:
        return {
            player.id_in_group: dict(type='chat_error', text='请输入消息。')
        }

    messages = load_ai_messages(player)
    messages.append({'role': 'user', 'content': text})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    append_chat_log(player, 'Participant', text)

    try:
        completion = get_openai_client().chat.completions.create(
            model=C.AI_MODEL,
            messages=messages,
            reasoning_effort=C.AI_REASONING_EFFORT,
            temperature=C.AI_TEMPERATURE,
        )
        output = completion.choices[0].message.content or ''
    except Exception as error:
        print(f'OpenAI chat request failed: {error}')
        return {
            player.id_in_group: dict(
                type='chat_error',
                text='AI 暂时无法回复，请稍后再试。',
            )
        }

    messages.append({'role': 'assistant', 'content': output})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    append_chat_log(player, 'AI', output)
    return {
        player.id_in_group: dict(type='chat_response', text=output)
    }


def live_task(player: Player, data):
    ensure_task_state(player)
    if data.get('type') == 'chat':
        return live_ai_chat(player, data)
    if data.get('type') == 'load':
        return {player.id_in_group: state_payload(player)}

    if data.get('type') != 'submit':
        return

    elapsed = time.time() - player.task_started_at
    if elapsed >= C.TASK_SECONDS:
        payload = dict(time_up=True)
        if ShowFeedback:
            payload['cumulative_score'] = round(player.cumulative_score, 2)
        return {player.id_in_group: payload}

    try:
        submitted_count = int(data.get('answer'))
    except (TypeError, ValueError):
        return {player.id_in_group: dict(error='请输入一个整数。')}

    max_cells = C.MATRIX_SIZE * C.MATRIX_SIZE
    if not 0 <= submitted_count <= max_cells:
        return {
            player.id_in_group: dict(error=f'答案必须在 0 到 {max_cells} 之间。')
        }

    correct_count = player.current_correct_count
    absolute_error = abs(submitted_count - correct_count)
    if correct_count == 0:
        relative_error = 0.0 if submitted_count == 0 else float('inf')
    else:
        relative_error = absolute_error / correct_count
    accuracy = max(0, 1 - relative_error)
    score = round(
        max(
            0,
            C.MAX_SCORE_PER_MATRIX
            * (1 - relative_error / C.ZERO_SCORE_ERROR_THRESHOLD),
        ),
        2,
    )
    submitted_at = time.time()
    question_started_at = player.current_question_started_at
    response_seconds = max(0, submitted_at - question_started_at)
    previous_questions = player.total_questions
    player.total_questions = previous_questions + 1
    player.average_response_seconds = round(
        (
            player.average_response_seconds * previous_questions
            + response_seconds
        )
        / player.total_questions,
        4,
    )
    player.average_accuracy = round(
        (player.average_accuracy * previous_questions + accuracy)
        / player.total_questions,
        6,
    )
    player.cumulative_score = round(player.cumulative_score + score, 2)
    player.round_total_score = player.cumulative_score

    Submission.create(
        player=player,
        question_number=player.question_number,
        matrix=player.current_matrix,
        correct_count=correct_count,
        submitted_count=submitted_count,
        absolute_error=absolute_error,
        accuracy=accuracy,
        score=score,
        cumulative_score=player.cumulative_score,
        question_started_at=question_started_at,
        response_seconds=response_seconds,
        submitted_at=submitted_at,
        elapsed_seconds=elapsed,
        remaining_seconds=max(0, C.TASK_SECONDS - elapsed),
    )

    player.question_number += 1
    matrix, next_correct_count = make_matrix()
    player.current_matrix = json.dumps(matrix, separators=(',', ':'))
    player.current_correct_count = next_correct_count
    player.current_question_started_at = time.time()

    feedback = dict(score=score, cumulative_score=player.cumulative_score)
    return {player.id_in_group: state_payload(player, feedback)}


class TaskStartWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = '请等待其他参与者'
    body_text = '所有参与者到达后，五分钟计时任务将统一开始。'


class CompensationChoice(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        # Rounds 1 and 2 are information pages. Only round 3 contains a choice.
        return ['payment_choice'] if player.round_number == 3 else []

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number != 3:
            return dict(choice_cards=[])

        choice_order = player.field_maybe_none('choice_order')
        if not choice_order:
            choice_order = random.choice(
                ['tournament_first', 'piece_rate_first']
            )
            player.choice_order = choice_order

        cards = dict(
            tournament=dict(
                value='tournament',
                title='Tournament',
                description=(
                    '你的 Block 3 表现将与同组三名其他参与者的 Block 2 表现比较，'
                    '报酬取决于比较结果。'
                ),
            ),
            piece_rate=dict(
                value='piece_rate',
                title='Piece rate',
                description='你的报酬只根据自己 Block 3 的任务表现计算。',
            ),
        )
        ordered_keys = (
            ['tournament', 'piece_rate']
            if choice_order == 'tournament_first'
            else ['piece_rate', 'tournament']
        )
        return dict(choice_cards=[cards[key] for key in ordered_keys])


class MyPage(Page):
    live_method = live_task
    timer_text = '剩余时间：'

    @staticmethod
    def get_timeout_seconds(player: Player):
        ensure_task_state(player)
        return max(1, C.TASK_SECONDS - (time.time() - player.task_started_at))

    @staticmethod
    def vars_for_template(player: Player):
        ensure_task_state(player)
        return dict(
            matrix_size=C.MATRIX_SIZE,
            TreatmentAI=TreatmentAI,
            ShowFeedback=ShowFeedback,
            CopyButtonText='复制左边整个矩阵',
        )

    @staticmethod
    def js_vars(player: Player):
        ensure_task_state(player)
        return dict(
            initial_matrix=json.loads(player.current_matrix),
            initial_question_number=player.question_number,
            show_feedback=ShowFeedback,
            initial_cumulative_score=(
                round(player.cumulative_score, 2) if ShowFeedback else None
            ),
            initial_chat_log=load_chat_log(player) if TreatmentAI else [],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.round_total_score = player.cumulative_score


class RankingWaitPage(WaitPage):
    title_text = '请等待本组其他参与者'
    body_text = '本组所有参与者完成任务后，将计算当前 Block 排名。'
    after_all_players_arrive = rank_group


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        # When feedback is disabled, do not expose round scores between stages.
        # Scores and ranks are still calculated and stored for payment/analysis.
        return ShowFeedback


page_sequence = [
    CompensationChoice,
    TaskStartWaitPage,
    MyPage,
    RankingWaitPage,
    Results,
]


def custom_export(players):
    yield [
        'participant_code', 'participant_label', 'round_number', 'group_id',
        'contemporaneous_rank', 'round_rank', 'rank_basis',
        'rank_tiebreaker', 'ranking_comparison_json', 'payment_choice',
        'choice_order', 'question_number',
        'matrix_json', 'correct_count', 'submitted_count', 'absolute_error',
        'accuracy', 'score', 'cumulative_score', 'question_started_at_unix',
        'response_seconds', 'round_total_questions',
        'round_average_response_seconds', 'round_average_accuracy',
        'elapsed_seconds', 'remaining_seconds', 'submitted_at_unix',
    ]
    for player in players:
        for submission in Submission.filter(player=player):
            yield [
                player.participant.code,
                player.participant.label,
                player.round_number,
                player.group.id_in_subsession,
                player.contemporaneous_rank,
                player.rank_in_group,
                player.rank_basis,
                player.rank_tiebreaker,
                player.ranking_comparison,
                player.field_maybe_none('payment_choice'),
                player.field_maybe_none('choice_order'),
                submission.question_number,
                submission.matrix,
                submission.correct_count,
                submission.submitted_count,
                submission.absolute_error,
                submission.accuracy,
                submission.score,
                submission.cumulative_score,
                submission.question_started_at,
                submission.response_seconds,
                player.total_questions,
                player.average_response_seconds,
                player.average_accuracy,
                submission.elapsed_seconds,
                submission.remaining_seconds,
                submission.submitted_at,
            ]
