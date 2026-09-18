"""Run network requests off the oTree event loop; only live handlers touch models.

Jobs are process-local, matching oTree's single web worker. A restart reports an
interrupted request instead of silently resending it. No ORM objects enter workers.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import time

from _i18n import tr

_POOL = ThreadPoolExecutor(max_workers=32, thread_name_prefix='ai-chat')
_JOBS = {}
JOB_TTL = 120
MAX_JOBS = 64


def key_for(player):
    return (player.__class__.__module__, player.participant.code, player.round_number)


def discard(key):
    job = _JOBS.pop(key, None)
    if job:
        job['future'].cancel()


def request_completion(client_factory, options):
    # This worker receives only a function and plain data, never a Player/session.
    with client_factory() as client:
        completion = client.chat.completions.create(**options)
        return completion.choices[0].message.content or ''


def handle(player, data, source, key):
    reply = lambda **value: {player.id_in_group: value}
    if not source.TreatmentAI:
        return reply(type='chat_error', text=tr('ai_unavailable'))
    now = time.monotonic()
    for old_key, job in list(_JOBS.items()):
        if now - job['created'] > JOB_TTL:
            discard(old_key)
    job = _JOBS.get(key)
    if data.get('type') == 'chat_poll':
        if job is None:
            return reply(type='chat_idle')
        if not job['future'].done():
            return reply(type='chat_pending')
        _JOBS.pop(key)
        try:
            output = job['future'].result()
        except Exception:
            return reply(type='chat_error', text=tr('ai_failed'))
        messages = source.load_ai_messages(player)
        messages.append({'role': 'assistant', 'content': output})
        player.ai_messages = json.dumps(messages, ensure_ascii=False)
        source.append_chat_log(player, 'AI', output)
        return reply(type='chat_response', text=output)
    if job:
        return reply(type='chat_pending')
    text = str(data.get('text', '')).strip()
    if not text:
        return reply(type='chat_error', text=tr('enter_message'))
    if len(_JOBS) >= MAX_JOBS:
        return reply(type='chat_error', text=tr('ai_failed'))
    messages = source.load_ai_messages(player)
    messages.append({'role': 'user', 'content': text})
    player.ai_messages = json.dumps(messages, ensure_ascii=False)
    source.append_chat_log(player, 'Participant', text)
    options = dict(model=source.C.AI_MODEL, messages=messages,
                   reasoning_effort=source.C.AI_REASONING_EFFORT,
                   temperature=source.C.AI_TEMPERATURE)
    _JOBS[key] = dict(created=now, future=_POOL.submit(
        request_completion, source.get_openai_client, options))
    return reply(type='chat_pending')
