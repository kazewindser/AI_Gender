import unittest
from types import SimpleNamespace
from unittest.mock import patch
from concurrent.futures import Future

import settings
import Instruction
import CountingZero
import StockForecast
import _practice
import _ai_chat
from _treatment import ai_enabled
from test_ai_chat import player


class TreatmentTests(unittest.TestCase):
    def test_four_configs(self):
        demos = [c for c in settings.SESSION_CONFIGS if 'Instruction' in c['app_sequence']]
        self.assertEqual(len(demos), 4)
        for task in ('CountingZero', 'StockForecast'):
            self.assertEqual({c['treatment_ai'] for c in demos if task in c['app_sequence']}, {False, True})

    def test_session_overrides_global_for_slides_ui_and_chat(self):
        for source in (CountingZero, StockForecast):
            for enabled in (False, True):
                for practice in (False, True):
                    name = source.__name__ + ('Practice' if practice else '')
                    p = player(name, name+str(enabled))
                    p.session.config = {'treatment_ai': enabled, 'app_sequence': ['Instruction', source.__name__]}
                    future = Future()
                    with patch('settings.TreatmentAI', not enabled), patch.object(_ai_chat._POOL, 'submit', return_value=future) as submit:
                        self.assertEqual(ai_enabled(p), enabled)
                        slides = Instruction.C.SLIDES_EN if Instruction.LANGUAGE_CODE == 'en' else Instruction.C.SLIDES
                        self.assertEqual(Instruction.get_slides_url(p), slides[(source.__name__, enabled)])
                        context = _practice.context(p) if practice else source.MyPage.vars_for_template(p)
                        self.assertEqual(context['TreatmentAI'], enabled)
                        live = _practice.live_task if practice else source.live_task
                        response = live(p, {'type': 'chat', 'text': 'hello'})[1]
                        self.assertEqual(response['type'], 'chat_pending' if enabled else 'chat_error')
                        self.assertEqual(submit.call_count, int(enabled))
                        _ai_chat.discard(_ai_chat.key_for(p))

    def test_legacy_fallback(self):
        p = SimpleNamespace(session=SimpleNamespace(config={}))
        for enabled in (False, True):
            with patch('settings.TreatmentAI', enabled):
                self.assertEqual(ai_enabled(p), enabled)
