"""Exercise the same synchronous dispatch called by oTree's async live handler."""
import asyncio
from contextlib import ExitStack
import json
import inspect
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import CountingZero as cz
import StockForecast as sf
import _ai_chat
import _practice
from otree.live import call_live_method_compat


async def dispatch(live, player, data):
    result = call_live_method_compat(live, player, data)
    # oTree 5 returns a dict; oTree 6 wraps replies in an async generator.
    if inspect.isasyncgen(result):
        replies = [reply async for reply in result]
        return replies[-1] if replies else None
    return result


def player(app, code):
    cls = type('Player', (), {'__module__': app})
    p = cls()
    p.__dict__.update(id_in_group=1, round_number=1,
        participant=SimpleNamespace(code=code, sf_used_stock_codes=''),
        session=SimpleNamespace(config={}),
        task_started_at=time.time(), current_question_started_at=time.time(),
        current_matrix=json.dumps([[0] * 15] * 15), current_correct_count=225,
        current_stock_code='test', current_series='[100]', current_correct_price=100,
        question_number=1, total_questions=0, cumulative_score=0, round_total_score=0,
        average_response_seconds=0, average_accuracy=0, ai_messages='', chat_log='',
        practice_state='')
    p.field_maybe_none = lambda name: getattr(p, name, None)
    return p


class BackgroundChatTests(unittest.TestCase):
    def tearDown(self):
        for key in list(_ai_chat._JOBS):
            _ai_chat.discard(key)

    def test_ten_second_ai_does_not_block_answers_or_event_loop(self):
        async def scenario():
            main_thread = threading.get_ident()
            def slow_completion(factory, options):
                self.assertNotEqual(threading.get_ident(), main_thread)
                time.sleep(10)
                return 'Delayed AI reply'
            cases = [(cz, cz.live_task, 'CountingZero'),
                     (sf, sf.live_task, 'StockForecast'),
                     (cz, _practice.live_task, 'CountingZeroPractice'),
                     (sf, _practice.live_task, 'StockForecastPractice')]
            with ExitStack() as stack:
                stack.enter_context(patch('_ai_chat.request_completion', side_effect=slow_completion))
                for backend in (cz, sf):
                    stack.enter_context(patch('settings.TreatmentAI', True))
                    stack.enter_context(patch.object(backend.Submission, 'create'))
                pending = []
                for backend, live, app in cases:
                    a, b = player(app, app+'A'), player(app, app+'B')
                    start = time.monotonic()
                    result = await dispatch(live, a, {'type': 'chat', 'text': 'help'})
                    self.assertEqual(result[1]['type'], 'chat_pending')
                    self.assertLess(time.monotonic()-start, 1)
                    pending.append((live,a))
                    # B submits just before the deadline while A's AI is still running.
                    if 'Practice' not in app:
                        b.task_started_at = time.time()-backend.C.TASK_SECONDS+2
                    start = time.monotonic()
                    answer = '225' if backend is cz else '100'
                    result = await dispatch(live, b, {'type': 'submit', 'answer': answer})
                    latency = time.monotonic()-start
                    self.assertLess(latency, 1)
                    self.assertNotIn('time_up', result[1])
                    self.assertEqual(b.question_number if 'Practice' not in app else json.loads(b.practice_state)['question_number'], 2)
                    if 'Practice' not in app:
                        self.assertEqual(b.cumulative_score, 10)
                    print(f'{app}: B submission {latency:.4f}s while A AI waits 10s')
                # An independent coroutine still runs while all four AI requests wait.
                start = time.monotonic()
                await asyncio.sleep(0.05)
                self.assertLess(time.monotonic()-start, 0.5)
                self.assertTrue(all(not job['future'].done() for job in _ai_chat._JOBS.values()))
                deadline = time.monotonic()+12
                while pending and time.monotonic()<deadline:
                    await asyncio.sleep(0.05)
                    for live,a in list(pending):
                        result = (await dispatch(live,a,{'type':'chat_poll'}))[1]
                        if result['type']=='chat_response':
                            self.assertEqual(result['text'],'Delayed AI reply')
                            pending.remove((live,a))
                self.assertFalse(pending)
        asyncio.run(scenario())

    def test_duplicate_poll_refresh_failure_and_cancel(self):
        a = player('CountingZero', 'lifecycle')
        from concurrent.futures import Future
        future = Future()
        with patch('settings.TreatmentAI',True), patch.object(_ai_chat._POOL,'submit',return_value=future) as submit:
            self.assertEqual(cz.live_task(a,{'type':'chat','text':'hello'})[1]['type'],'chat_pending')
            self.assertEqual(cz.live_task(a,{'type':'chat','text':'again'})[1]['type'],'chat_pending')
            self.assertEqual(cz.live_task(a,{'type':'chat_poll'})[1]['type'],'chat_pending')
            self.assertEqual(submit.call_count,1)
            future.set_result('hello back')
            self.assertEqual(cz.live_task(a,{'type':'chat_poll'})[1]['type'],'chat_response')
            self.assertEqual(cz.live_task(a,{'type':'chat_poll'})[1]['type'],'chat_idle')
            self.assertEqual(len(json.loads(a.chat_log)),2)
        future = Future()
        with patch('settings.TreatmentAI',True), patch.object(_ai_chat._POOL,'submit',return_value=future):
            cz.live_task(a,{'type':'chat','text':'hello'})
            future.set_exception(RuntimeError('simulated failure'))
            self.assertEqual(cz.live_task(a,{'type':'chat_poll'})[1]['type'],'chat_error')
        future = Future()
        with patch('settings.TreatmentAI',True), patch.object(_ai_chat._POOL,'submit',return_value=future):
            cz.live_task(a,{'type':'chat','text':'hello'})
            cz.MyPage.before_next_page(a,True)
            self.assertTrue(future.cancelled())
            self.assertNotIn(_ai_chat.key_for(a),_ai_chat._JOBS)
