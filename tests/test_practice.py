import json
import unittest
import time
from types import SimpleNamespace
import _ai_chat
from unittest.mock import patch

import _practice as practice
import settings


class PracticeTests(unittest.TestCase):
    def player(self, app):
        cls = type('Player', (), {'__module__': app})
        player = cls()
        player.id_in_group = 1
        player.participant = SimpleNamespace(code=app)
        player.round_number = 1
        player.session = SimpleNamespace(config={})
        player.practice_state = ''
        player.field_maybe_none = lambda name: getattr(player, name, None)
        return player

    def test_both_tasks_discard_answers_and_clear_state(self):
        for app in ('CountingZeroPractice', 'StockForecastPractice'):
            with self.subTest(app=app):
                player = self.player(app)
                with patch('settings.ShowFeedback', True):
                    self.assertFalse(practice.context(player)['ShowFeedback'])
                    initial = practice.live_task(player, {'type': 'load'})[1]
                    self.assertLessEqual(initial['remaining_seconds'], 60)
                    self.assertGreater(initial['remaining_seconds'], 59)
                    result = practice.live_task(player, {'type': 'submit', 'answer': '100'})[1]
                self.assertEqual(result['question_number'], 2)
                self.assertNotIn('feedback', result)
                self.assertNotIn('cumulative_score', result)
                state = json.loads(player.practice_state)
                self.assertEqual(set(state) - {'series', 'matrix', 'used'},
                                 {'started', 'question_number', 'ai_messages', 'chat_log'})
                started = state['started']
                with patch('_practice.time.time', return_value=started + 61):
                    self.assertEqual(practice.remaining_seconds(player), 0)
                    self.assertEqual(practice.live_task(player, {'type': 'submit', 'answer': '100'}),
                                     {1: {'time_up': True}})
                practice.clear_state(player)
                self.assertEqual(player.practice_state, '')

    def test_ai_switch_and_chat_protocol(self):
        for app in ('CountingZeroPractice', 'StockForecastPractice'):
            player = self.player(app)
            backend = practice.backend(player)
            for enabled in (False, True):
                with patch('settings.TreatmentAI', enabled):
                    self.assertEqual(practice.context(player)['TreatmentAI'], enabled)
                    if not enabled:
                        result = practice.live_task(player, {'type': 'chat', 'text': 'hello'})
                        self.assertEqual(result[1]['type'], 'chat_error')
                    else:
                        with patch.object(backend, 'get_openai_client') as client:
                            client.return_value.__enter__.return_value.chat.completions.create.return_value.choices[0].message.content = 'Hello'
                            result = practice.live_task(player, {'type': 'chat', 'text': 'hello'})
                            self.assertEqual(result[1]['type'], 'chat_pending')
                            deadline = time.monotonic() + 2
                            while result[1]['type'] == 'chat_pending' and time.monotonic() < deadline:
                                time.sleep(0.01)
                                result = practice.live_task(player, {'type': 'chat_poll'})
                            self.assertEqual(result[1], {'type': 'chat_response', 'text': 'Hello'})
                            self.assertEqual(len(practice.js_context(player)['initial_chat_log']), 2)

    def test_three_pages_and_main_task_follows(self):
        import CountingZeroPractice
        import StockForecastPractice
        for app in (CountingZeroPractice, StockForecastPractice):
            self.assertEqual([page.__name__ for page in app.page_sequence],
                             ['Instructions', 'MyPage', 'Complete'])
            config = next(c for c in settings.SESSION_CONFIGS if app.__name__ in c['app_sequence'])
            sequence = config['app_sequence']
            self.assertEqual(sequence[sequence.index(app.__name__) + 1],
                             app.__name__.replace('Practice', ''))


if __name__ == '__main__':
    unittest.main()
