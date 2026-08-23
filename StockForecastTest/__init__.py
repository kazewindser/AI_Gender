from otree.api import *

import csv
from functools import lru_cache
import json
from os import environ
from pathlib import Path
import random
import time

from openai import OpenAI
from settings import ShowFeedback, TreatmentAI
from _static.StockTS.StockBank import StockBank


doc = """Standalone five-minute test of the stock-forecasting task."""


class C(BaseConstants):
    NAME_IN_URL = 'StockForecastTest'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TASK_SECONDS = 5 * 60
    MAX_SCORE_PER_FORECAST = 10
    ZERO_SCORE_ERROR_THRESHOLD = 0.20
    HISTORY_TRADING_DAYS = 252
    FORECAST_TRADING_DAYS = 30
    DATA_DIR = Path(__file__).resolve().parent.parent / '_static' / 'StockTS' / 'TSdata'
    AI_MODEL = 'gpt-5.6-luna'
    AI_REASONING_EFFORT = 'none'
    AI_TEMPERATURE = 1
    AI_SYSTEM_PROMPT = (
        'The user is completing a stock-forecasting task. The user will send you a chronological series of normalized stock prices. '
        'Please help the user predict the normalized price 30 trading days later and provide a clear forecast. '
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
    total_questions = models.IntegerField(initial=0)
    average_response_seconds = models.FloatField(initial=0)
    average_accuracy = models.FloatField(initial=0)
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
    response_seconds = models.FloatField()
    elapsed_seconds = models.FloatField()


@lru_cache(maxsize=None)
def load_stock(code):
    path = C.DATA_DIR / f'{code}.csv'
    with path.open(encoding='utf-8', newline='') as stock_file:
        rows = list(csv.DictReader(stock_file))
    if rows and 'Segment' in rows[0]:
        history_rows = [row for row in rows if row['Segment'] == 'history']
        forecast_rows = [row for row in rows if row['Segment'] == 'forecast']
    else:
        history_rows = rows[:-C.FORECAST_TRADING_DAYS]
        forecast_rows = rows[-C.FORECAST_TRADING_DAYS:]
    history = [round(float(row['NormalizedClose']), 2) for row in history_rows]
    if len(history) != C.HISTORY_TRADING_DAYS or len(forecast_rows) != C.FORECAST_TRADING_DAYS:
        raise ValueError(f'No usable stock data for {code}.')
    return history, round(float(forecast_rows[-1]['NormalizedClose']), 2)


def draw_stock(player):
    used = json.loads(player.used_stock_codes) if player.field_maybe_none('used_stock_codes') else []
    available = [code for code in StockBank if code not in used]
    if not available:
        used = []
        available = list(StockBank)
    code = random.choice(available)
    history, target = load_stock(code)
    used.append(code)
    player.used_stock_codes = json.dumps(used)
    player.current_stock_code = code
    player.current_series = json.dumps(history, separators=(',', ':'))
    player.current_correct_price = target
    player.current_question_started_at = time.time()


def ensure_task_state(player):
    if not player.field_maybe_none('task_started_at'):
        player.task_started_at = time.time()
    if not player.field_maybe_none('current_stock_code'):
        draw_stock(player)


def get_openai_client():
    api_key = environ.get('CHATGPT_KEY') or environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key is missing.')
    return OpenAI(api_key=api_key)


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
        series=json.loads(player.current_series),
        question_number=player.question_number,
        remaining_seconds=max(0, C.TASK_SECONDS - elapsed),
    )
    if ShowFeedback:
        payload['cumulative_score'] = round(player.cumulative_score, 2)
        if feedback is not None:
            payload['feedback'] = feedback
    return payload


def live_ai_chat(player, data):
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
        forecast = float(data.get('answer'))
    except (TypeError, ValueError):
        return {player.id_in_group: dict(error='请输入有效的数字。')}
    if not 0 < forecast < 100000:
        return {player.id_in_group: dict(error='预测价格必须是大于0的数字。')}
    correct_price = player.current_correct_price
    absolute_error = abs(forecast - correct_price)
    relative_error = absolute_error / correct_price
    accuracy = max(0, 1 - relative_error)
    score = round(max(0, C.MAX_SCORE_PER_FORECAST * (1 - relative_error / C.ZERO_SCORE_ERROR_THRESHOLD)), 2)
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
        stock_code=player.current_stock_code,
        displayed_series=player.current_series,
        correct_price=correct_price,
        submitted_forecast=forecast,
        absolute_error=absolute_error,
        relative_error=relative_error,
        accuracy=accuracy,
        score=score,
        cumulative_score=player.cumulative_score,
        response_seconds=response_seconds,
        elapsed_seconds=elapsed,
    )
    player.question_number += 1
    draw_stock(player)
    return {player.id_in_group: state_payload(player, dict(score=score, cumulative_score=player.cumulative_score))}


class Instructions(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(TreatmentAI=TreatmentAI, system_prompt=C.AI_SYSTEM_PROMPT)


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
        return dict(
            TreatmentAI=TreatmentAI,
            ShowFeedback=ShowFeedback,
            CopyButtonText='一键复制左边所有股价时间序列',
        )

    @staticmethod
    def js_vars(player):
        ensure_task_state(player)
        return dict(
            initial_series=json.loads(player.current_series),
            initial_question_number=player.question_number,
            show_feedback=ShowFeedback,
            initial_cumulative_score=round(player.cumulative_score, 2) if ShowFeedback else None,
            initial_chat_log=load_chat_log(player) if TreatmentAI else [],
        )


class Results(Page):
    pass


page_sequence = [Instructions, MyPage, Results]


def custom_export(players):
    yield [
        'participant_code', 'question_number', 'stock_code',
        'displayed_series_json', 'correct_price', 'submitted_forecast',
        'absolute_error', 'relative_error', 'accuracy', 'score',
        'cumulative_score', 'response_seconds', 'elapsed_seconds',
    ]
    for player in players:
        for submission in Submission.filter(player=player):
            yield [
                player.participant.code, submission.question_number,
                submission.stock_code, submission.displayed_series,
                submission.correct_price, submission.submitted_forecast,
                submission.absolute_error, submission.relative_error,
                submission.accuracy, submission.score,
                submission.cumulative_score, submission.response_seconds,
                submission.elapsed_seconds,
            ]
