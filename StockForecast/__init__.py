from otree.api import *

import csv
from functools import lru_cache
import json
from os import environ
from pathlib import Path
import random
import re
import time

from openai import OpenAI
from settings import ShowFeedback, TreatmentAI
from _static.StockTS.StockBank import StockBank


doc = """Five-minute stock-price forecasting task with three NV-style stages."""


class C(BaseConstants):
    NAME_IN_URL = 'StockForecast'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 3
    TASK_SECONDS = 5 * 60
    MAX_SCORE_PER_FORECAST = 10
    ZERO_SCORE_ERROR_THRESHOLD = 0.20
    HISTORY_END_DATE = '2025-12-30'
    DATA_DIR = Path(__file__).resolve().parent.parent / '_static' / 'StockTS' / 'TSdata'
    AI_MODEL = 'gpt-4o'
    AI_TEMPERATURE = 1
    AI_SYSTEM_PROMPT = (
        'The user is completing a stock-forecasting task. The user will send you a chronological series of normalized stock prices. '
        'Please help the user predict the normalized price 19 trading days later and provide a clear forecast. '
        'Always respond in Japanese.'
    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    task_started_at = models.FloatField(initial=0)
    current_question_started_at = models.FloatField(initial=0)
    current_stock_code = models.StringField(blank=True)
    current_series = models.LongStringField(blank=True)
    current_correct_price = models.FloatField(initial=0)
    used_stock_codes = models.LongStringField(blank=True)
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
        choices=[['piece_rate', 'Piece rate'], ['tournament', 'Tournament']],
        widget=widgets.RadioSelect,
    )
    choice_order = models.StringField(blank=True)
    first_task_score = models.FloatField(initial=0)
    second_task_score = models.FloatField(initial=0)
    third_task_score = models.FloatField(initial=0)
    tournament_rank = models.IntegerField(blank=True)
    ai_messages = models.LongStringField(blank=True)
    chat_log = models.LongStringField(blank=True)


class Submission(ExtraModel):
    player = models.Link(Player)
    question_number = models.IntegerField()
    stock_code = models.StringField()
    displayed_series = models.LongStringField()
    correct_price = models.FloatField()
    submitted_forecast = models.FloatField()
    absolute_error = models.FloatField()
    relative_error = models.FloatField()
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
    defaults = dict(
        sf_round1_score=0,
        sf_round2_score=0,
        sf_round3_score=0,
        sf_round1_rank=0,
        sf_round2_rank=0,
        sf_round3_rank=0,
        sf_round3_choice='',
        sf_selected_round=0,
        sf_final_score=0,
        sf_used_stock_codes='',
    )
    for field_name, default in defaults.items():
        participant.vars.setdefault(field_name, default)


def creating_session(subsession: Subsession):
    players = subsession.get_players()
    if subsession.round_number == 1:
        for player in players:
            initialize_participant_fields(player.participant)

    labels = [player.participant.label for player in players]
    if all(labels):
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
            blocks.setdefault((number - 1) // C.PLAYERS_PER_GROUP, []).append(
                (number, player)
            )
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
    elif any(labels):
        raise ValueError('Either every participant must have a label or none may have one.')


@lru_cache(maxsize=None)
def load_stock(code):
    path = C.DATA_DIR / f'{code}.csv'
    with path.open(encoding='utf-8', newline='') as stock_file:
        rows = list(csv.DictReader(stock_file))
    history = [
        round(float(row['NormalizedClose']), 2)
        for row in rows
        if row['Date'] <= C.HISTORY_END_DATE
    ]
    if not history or not rows:
        raise ValueError(f'No usable stock data for {code}.')
    target = round(float(rows[-1]['NormalizedClose']), 2)
    return history, target


def draw_stock(player: Player):
    raw_used = player.participant.sf_used_stock_codes
    used = json.loads(raw_used) if raw_used else []
    available = [code for code in StockBank if code not in used]
    if not available:
        used = []
        available = list(StockBank)
    code = random.choice(available)
    history, target = load_stock(code)
    used.append(code)
    player.participant.sf_used_stock_codes = json.dumps(used)
    # Keep a snapshot on the current round row for easier inspection/export.
    player.used_stock_codes = json.dumps(used)
    player.current_stock_code = code
    player.current_series = json.dumps(history, separators=(',', ':'))
    player.current_correct_price = target
    player.current_question_started_at = time.time()


def ensure_task_state(player: Player):
    if not player.field_maybe_none('task_started_at'):
        player.task_started_at = time.time()
    if not player.field_maybe_none('current_stock_code'):
        draw_stock(player)
    if not player.field_maybe_none('current_question_started_at'):
        player.current_question_started_at = time.time()


def sync_stage_scores(player: Player):
    scores = {
        item.round_number: item.cumulative_score for item in player.in_all_rounds()
    }
    for item in player.in_all_rounds():
        item.first_task_score = scores.get(1, 0)
        item.second_task_score = scores.get(2, 0)
        item.third_task_score = scores.get(3, 0)


def store_participant_round_result(player: Player):
    participant = player.participant
    if player.round_number == 1:
        participant.sf_round1_score = player.round_total_score
        participant.sf_round1_rank = player.rank_in_group
    elif player.round_number == 2:
        participant.sf_round2_score = player.round_total_score
        participant.sf_round2_rank = player.rank_in_group
    else:
        participant.sf_round3_score = player.round_total_score
        participant.sf_round3_rank = player.rank_in_group
        participant.sf_round3_choice = player.payment_choice


def finalize_participant_payoff(player: Player):
    participant = player.participant
    initialize_participant_fields(participant)
    selected_round = participant.sf_selected_round
    if not selected_round:
        selected_round = random.randint(1, C.NUM_ROUNDS)
        participant.sf_selected_round = selected_round
    scores = {
        1: participant.sf_round1_score,
        2: participant.sf_round2_score,
        3: participant.sf_round3_score,
    }
    ranks = {
        1: participant.sf_round1_rank,
        2: participant.sf_round2_rank,
        3: participant.sf_round3_rank,
    }
    score = scores[selected_round]
    rank = ranks[selected_round]
    if selected_round == 1:
        final_score = score
    elif selected_round == 2:
        final_score = score * C.PLAYERS_PER_GROUP if rank == 1 else 0
    elif participant.sf_round3_choice == 'piece_rate':
        final_score = score
    else:
        final_score = score * C.PLAYERS_PER_GROUP if rank == 1 else 0
    participant.sf_final_score = round(final_score, 2)
    player.payoff = participant.sf_final_score


def rank_group(group: Group):
    players = group.get_players()
    for player in players:
        player.round_total_score = player.cumulative_score
        player.rank_tiebreaker = random.random()
    same_round = sorted(
        players, key=lambda item: (-item.round_total_score, item.rank_tiebreaker)
    )
    for rank, player in enumerate(same_round, start=1):
        player.contemporaneous_rank = rank

    for player in players:
        if player.round_number == 3 and player.payment_choice == 'tournament':
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
                if opponent.id_in_group != player.id_in_group:
                    comparison.append(
                        dict(
                            id_in_group=opponent.id_in_group,
                            source_round=2,
                            score=opponent.in_round(2).cumulative_score,
                            is_focal=False,
                            tiebreaker=random.random(),
                        )
                    )
            comparison.sort(key=lambda item: (-item['score'], item['tiebreaker']))
            player.rank_in_group = next(
                rank for rank, item in enumerate(comparison, 1) if item['is_focal']
            )
            player.rank_tiebreaker = next(
                item['tiebreaker'] for item in comparison if item['is_focal']
            )
            player.rank_basis = 'round3_self_vs_round2_opponents'
            player.ranking_comparison = json.dumps(comparison)
        else:
            player.rank_in_group = player.contemporaneous_rank
            player.rank_basis = 'same_round'
            player.ranking_comparison = json.dumps(
                [
                    dict(
                        id_in_group=item.id_in_group,
                        source_round=player.round_number,
                        score=item.round_total_score,
                        is_focal=item.id_in_group == player.id_in_group,
                        tiebreaker=item.rank_tiebreaker,
                    )
                    for item in same_round
                ]
            )
        if player.round_number == 2:
            for item in player.in_all_rounds():
                item.tournament_rank = player.rank_in_group
        sync_stage_scores(player)
        store_participant_round_result(player)

    if players and players[0].round_number == 3:
        for player in players:
            finalize_participant_payoff(player)


def state_payload(player: Player, feedback=None):
    ensure_task_state(player)
    elapsed = max(0, time.time() - player.task_started_at)
    payload = dict(
        series=json.loads(player.current_series),
        question_number=player.question_number,
        remaining_seconds=max(0, C.TASK_SECONDS - elapsed),
    )
    if ShowFeedback:
        payload['cumulative_score'] = round(player.cumulative_score, 2)
        if feedback is not None:
            payload['feedback'] = feedback
    return payload


def get_openai_client():
    api_key = environ.get('CHATGPT_KEY') or environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key is missing.')
    return OpenAI(api_key=api_key)


def load_ai_messages(player: Player):
    raw = player.field_maybe_none('ai_messages')
    return json.loads(raw) if raw else [{'role': 'system', 'content': C.AI_SYSTEM_PROMPT}]


def load_chat_log(player: Player):
    raw = player.field_maybe_none('chat_log')
    return json.loads(raw) if raw else []


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
        return {player.id_in_group: dict(type='chat_error', text='当前条件不提供 AI。')}
    text = str(data.get('text', '')).strip()
    if not text:
        return {player.id_in_group: dict(type='chat_error', text='请输入消息。')}
    messages = load_ai_messages(player)
    messages.append({'role': 'user', 'content': text})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    append_chat_log(player, 'Participant', text)
    try:
        completion = get_openai_client().chat.completions.create(
            model=C.AI_MODEL, messages=messages, temperature=C.AI_TEMPERATURE
        )
        output = completion.choices[0].message.content or ''
    except Exception as error:
        print(f'OpenAI chat request failed: {error}')
        return {
            player.id_in_group: dict(
                type='chat_error', text='AI 暂时无法回复，请稍后再试。'
            )
        }
    messages.append({'role': 'assistant', 'content': output})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    append_chat_log(player, 'AI', output)
    return {player.id_in_group: dict(type='chat_response', text=output)}


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
        forecast = float(data.get('answer'))
    except (TypeError, ValueError):
        return {player.id_in_group: dict(error='请输入有效的数字。')}
    if not 0 < forecast < 100000:
        return {player.id_in_group: dict(error='预测价格必须是大于 0 的数字。')}

    correct_price = player.current_correct_price
    absolute_error = abs(forecast - correct_price)
    relative_error = absolute_error / correct_price
    accuracy = max(0, 1 - relative_error)
    score = round(
        max(
            0,
            C.MAX_SCORE_PER_FORECAST
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
        stock_code=player.current_stock_code,
        displayed_series=player.current_series,
        correct_price=correct_price,
        submitted_forecast=forecast,
        absolute_error=absolute_error,
        relative_error=relative_error,
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
    draw_stock(player)
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
        return ['payment_choice'] if player.round_number == 3 else []

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number != 3:
            return dict(choice_cards=[])
        order = player.field_maybe_none('choice_order')
        if not order:
            order = random.choice(['tournament_first', 'piece_rate_first'])
            player.choice_order = order
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
        keys = (
            ['tournament', 'piece_rate']
            if order == 'tournament_first'
            else ['piece_rate', 'tournament']
        )
        return dict(choice_cards=[cards[key] for key in keys])


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
            TreatmentAI=TreatmentAI,
            ShowFeedback=ShowFeedback,
            CopyButtonText='一键复制左边所有股价时间序列',
        )

    @staticmethod
    def js_vars(player: Player):
        ensure_task_state(player)
        return dict(
            initial_series=json.loads(player.current_series),
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
        'contemporaneous_rank', 'round_rank', 'rank_basis', 'rank_tiebreaker',
        'ranking_comparison_json', 'payment_choice', 'choice_order',
        'question_number', 'stock_code', 'displayed_series_json',
        'correct_price', 'submitted_forecast', 'absolute_error',
        'relative_error', 'accuracy', 'score', 'cumulative_score',
        'question_started_at_unix', 'response_seconds',
        'round_total_questions', 'round_average_response_seconds',
        'round_average_accuracy', 'elapsed_seconds', 'remaining_seconds',
        'submitted_at_unix',
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
                submission.stock_code,
                submission.displayed_series,
                submission.correct_price,
                submission.submitted_forecast,
                submission.absolute_error,
                submission.relative_error,
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
