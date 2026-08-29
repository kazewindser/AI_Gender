from otree.api import *

import json
from os import environ
import random
import time

from openai import OpenAI
from settings import ShowFeedback


doc = """Standalone five-minute test of the counting-zero task."""


class C(BaseConstants):
    NAME_IN_URL = 'CountingZeroTest'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
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
    total_questions = models.IntegerField(initial=0)
    average_response_seconds = models.FloatField(initial=0)
    average_accuracy = models.FloatField(initial=0)
    ai_messages = models.LongStringField(blank=True)
    chat_log = models.LongStringField(blank=True)


class Submission(ExtraModel):
    player = models.Link(Player)
    question_number = models.IntegerField()
    matrix = models.LongStringField()
    correct_count = models.IntegerField()
    submitted_count = models.IntegerField()
    absolute_error = models.IntegerField()
    relative_error = models.FloatField()
    accuracy = models.FloatField()
    score = models.FloatField()
    cumulative_score = models.FloatField()
    response_seconds = models.FloatField()
    elapsed_seconds = models.FloatField()


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


def draw_matrix(player):
    matrix, correct_count = make_matrix()
    player.current_matrix = json.dumps(matrix, separators=(',', ':'))
    player.current_correct_count = correct_count
    player.current_question_started_at = time.time()


def ensure_task_state(player):
    if not player.field_maybe_none('task_started_at'):
        player.task_started_at = time.time()
    if not player.field_maybe_none('current_matrix'):
        draw_matrix(player)


def get_openai_client():
    api_key = environ.get('CHATGPT_KEY') or environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key is missing.')
    return OpenAI(api_key=api_key)


def treatment_ai(player):
    return player.session.config['treatment_ai']


def load_ai_messages(player):
    raw = player.field_maybe_none('ai_messages')
    return json.loads(raw) if raw else [{'role': 'system', 'content': C.AI_SYSTEM_PROMPT}]


def load_chat_log(player):
    raw = player.field_maybe_none('chat_log')
    return json.loads(raw) if raw else []


def append_chat_log(player, sender, text):
    log = load_chat_log(player)
    log.append(dict(sender=sender, text=text, timestamp=time.time()))
    player.chat_log = json.dumps(log, ensure_ascii=False)


def state_payload(player, feedback=None):
    ensure_task_state(player)
    elapsed = max(0, time.time() - player.task_started_at)
    payload = dict(
        matrix=json.loads(player.current_matrix),
        question_number=player.question_number,
        remaining_seconds=max(0, C.TASK_SECONDS - elapsed),
    )
    if ShowFeedback:
        payload['cumulative_score'] = round(player.cumulative_score, 2)
        if feedback is not None:
            payload['feedback'] = feedback
    return payload


def live_ai_chat(player, data):
    if not treatment_ai(player):
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
            model=C.AI_MODEL,
            messages=messages,
            reasoning_effort=C.AI_REASONING_EFFORT,
            temperature=C.AI_TEMPERATURE,
        )
        output = completion.choices[0].message.content or ''
    except Exception as error:
        print(f'OpenAI chat request failed: {error}')
        return {player.id_in_group: dict(type='chat_error', text='AI 暂时无法回复，请稍后再试。')}
    messages.append({'role': 'assistant', 'content': output})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    append_chat_log(player, 'AI', output)
    return {player.id_in_group: dict(type='chat_response', text=output)}


def live_task(player, data):
    ensure_task_state(player)
    if data.get('type') == 'chat':
        return live_ai_chat(player, data)
    if data.get('type') == 'load':
        return {player.id_in_group: state_payload(player)}
    if data.get('type') != 'submit':
        return
    elapsed = time.time() - player.task_started_at
    if elapsed >= C.TASK_SECONDS:
        return {player.id_in_group: dict(time_up=True)}
    try:
        submitted_count = int(data.get('answer'))
    except (TypeError, ValueError):
        return {player.id_in_group: dict(error='请输入有效的整数。')}
    correct_count = player.current_correct_count
    absolute_error = abs(submitted_count - correct_count)
    if correct_count == 0:
        relative_error = 0.0 if submitted_count == 0 else float('inf')
    else:
        relative_error = absolute_error / correct_count
    accuracy = max(0, 1 - relative_error)
    score = round(max(0, C.MAX_SCORE_PER_MATRIX * (1 - relative_error / C.ZERO_SCORE_ERROR_THRESHOLD)), 2)
    response_seconds = max(0, time.time() - player.current_question_started_at)
    previous_questions = player.total_questions
    player.total_questions += 1
    player.average_response_seconds = round(
        (player.average_response_seconds * previous_questions + response_seconds) / player.total_questions,
        4,
    )
    player.average_accuracy = round(
        (player.average_accuracy * previous_questions + accuracy) / player.total_questions,
        6,
    )
    player.cumulative_score = round(player.cumulative_score + score, 2)
    Submission.create(
        player=player,
        question_number=player.question_number,
        matrix=player.current_matrix,
        correct_count=correct_count,
        submitted_count=submitted_count,
        absolute_error=absolute_error,
        relative_error=relative_error,
        accuracy=accuracy,
        score=score,
        cumulative_score=player.cumulative_score,
        response_seconds=response_seconds,
        elapsed_seconds=elapsed,
    )
    player.question_number += 1
    draw_matrix(player)
    return {player.id_in_group: state_payload(player, dict(score=score, cumulative_score=player.cumulative_score))}


class Instructions(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(TreatmentAI=treatment_ai(player), system_prompt=C.AI_SYSTEM_PROMPT)


class MyPage(Page):
    live_method = live_task
    timer_text = '剩余时间：'

    @staticmethod
    def get_timeout_seconds(player):
        ensure_task_state(player)
        return max(1, C.TASK_SECONDS - (time.time() - player.task_started_at))

    @staticmethod
    def vars_for_template(player):
        ensure_task_state(player)
        has_ai = treatment_ai(player)
        return dict(
            matrix_size=C.MATRIX_SIZE,
            TreatmentAI=has_ai,
            ShowFeedback=ShowFeedback,
            CopyButtonText='复制左边整个矩阵',
        )

    @staticmethod
    def js_vars(player):
        ensure_task_state(player)
        has_ai = treatment_ai(player)
        return dict(
            initial_matrix=json.loads(player.current_matrix),
            initial_question_number=player.question_number,
            show_feedback=ShowFeedback,
            initial_cumulative_score=round(player.cumulative_score, 2) if ShowFeedback else None,
            initial_chat_log=load_chat_log(player) if has_ai else [],
        )


class Results(Page):
    pass


page_sequence = [Instructions, MyPage, Results]


def custom_export(players):
    yield [
        'participant_code', 'question_number', 'matrix_json', 'correct_count',
        'submitted_count', 'absolute_error', 'relative_error', 'accuracy',
        'score', 'cumulative_score', 'response_seconds', 'elapsed_seconds',
    ]
    for player in players:
        for submission in Submission.filter(player=player):
            yield [
                player.participant.code, submission.question_number,
                submission.matrix, submission.correct_count,
                submission.submitted_count, submission.absolute_error,
                submission.relative_error, submission.accuracy, submission.score,
                submission.cumulative_score, submission.response_seconds,
                submission.elapsed_seconds,
            ]
