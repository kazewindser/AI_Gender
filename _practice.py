"""Unscored practice: keep only current UI state and erase it on completion."""
import json
import random
import time
from types import SimpleNamespace

from _treatment import ai_enabled
import _ai_chat
from _i18n import LANGUAGE, TEXT, template_context, tr

DURATION = 60
COPY = {
    'en': ('Practice', 'This is a one-minute practice session. Results will not be shown, your practice performance will not be recorded, and no payment will be earned.', 'Practice complete.', 'Next'),
    'ja': ('練習', 'これは1分間の練習です。結果は表示されません。練習の成績は記録されず、報酬はありません。', '練習終了', '次へ'),
    'zh-hans': ('练习', '这是练习环节，时长为1分钟。不会显示结果，练习表现不会记录，也没有报酬。', '练习结束', '下一步'),
}


COMPLETE_HINT = {
    'en': 'Click “Next” to proceed to Task 1 of the main task.',
    'ja': '「次へ」ボタンをクリックすると、メインタスクのタスク1に進みます。',
    'zh-hans': '点击“下一步”按钮进入正式任务的 task1。',
}


def is_stock(player):
    return player.__class__.__module__.split('.')[0] == 'StockForecastPractice'


def backend(player):
    if is_stock(player):
        import StockForecast
        return StockForecast
    import CountingZero
    return CountingZero


def new_question(player, state):
    source = backend(player)
    if is_stock(player):
        used = state.setdefault('used', [])
        available = [code for code in source.StockBank if code not in used]
        if not available:
            used.clear()
            available = list(source.StockBank)
        code = random.choice(available)
        used.append(code)
        state['series'] = source.load_stock(code)[0]
    else:
        state['matrix'] = source.make_matrix()[0]


def save(player, state):
    player.practice_state = json.dumps(state, ensure_ascii=False)


def get_state(player):
    raw = player.field_maybe_none('practice_state')
    if raw:
        return json.loads(raw)
    state = dict(started=time.time(), question_number=1, ai_messages='', chat_log='')
    new_question(player, state)
    save(player, state)
    return state


def remaining_seconds(player):
    return max(0, DURATION - (time.time() - get_state(player)['started']))


def payload(player, state):
    key = 'series' if is_stock(player) else 'matrix'
    return {key: state[key], 'question_number': state['question_number'],
            'remaining_seconds': max(0, DURATION - (time.time() - state['started']))}


def live_task(player, data):
    state = get_state(player)
    reply = lambda value: {player.id_in_group: value}
    if time.time() - state['started'] >= DURATION:
        _ai_chat.discard(_ai_chat.key_for(player))
        if data.get('type') in ('chat', 'chat_poll'):
            return reply(dict(type='chat_error', text=tr('ai_unavailable')))
        return reply(dict(time_up=True))
    kind = data.get('type')
    if kind == 'load':
        return reply(payload(player, state))
    if kind in ('chat', 'chat_poll'):
        # Reuse the main task's AI settings/protocol with temporary chat state.
        proxy = SimpleNamespace(id_in_group=player.id_in_group, session=player.session,
                                task_started_at=state['started'],
                                ai_messages=state['ai_messages'], chat_log=state['chat_log'])
        proxy.field_maybe_none = lambda name: getattr(proxy, name, None)
        result = backend(player).live_ai_chat(proxy, data, chat_key=_ai_chat.key_for(player))
        state.update(ai_messages=proxy.ai_messages, chat_log=proxy.chat_log)
        save(player, state)
        return result
    if kind != 'submit':
        return
    try:
        answer = float(data.get('answer')) if is_stock(player) else int(data.get('answer'))
    except (ValueError, TypeError, OverflowError):
        return reply(dict(error=tr('enter_number' if is_stock(player) else 'enter_integer')))
    if is_stock(player):
        if not 0 < answer < 100000:
            return reply(dict(error=tr('positive_forecast')))
    elif not 0 <= answer <= 225:
        return reply(dict(error=tr('integer_range', max_cells=225)))
    # Discard the answer without computing or recording performance.
    state['question_number'] += 1
    new_question(player, state)
    save(player, state)
    return reply(payload(player, state))


def context(player):
    title, instructions, complete, next_label = COPY[LANGUAGE]
    return template_context(practice_title=title, practice_instructions=instructions,
                            practice_complete=complete, practice_next=next_label,
                            practice_complete_hint=COMPLETE_HINT[LANGUAGE],
                            TreatmentAI=ai_enabled(player), ShowFeedback=False,
                            matrix_size=15,
                            CopyButtonText=tr('copy_series' if is_stock(player) else 'copy_matrix'))


def js_context(player):
    state = get_state(player)
    key = 'series' if is_stock(player) else 'matrix'
    return {f'initial_{key}': state[key], 'initial_question_number': state['question_number'],
            'show_feedback': False, 'initial_cumulative_score': None,
            'initial_chat_log': json.loads(state['chat_log'] or '[]') if ai_enabled(player) else [],
            'texts': TEXT}


def clear_state(player):
    _ai_chat.discard(_ai_chat.key_for(player))
    player.practice_state = ''
