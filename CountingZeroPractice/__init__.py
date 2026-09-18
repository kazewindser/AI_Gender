from otree.api import *
from _i18n import tr
from _practice import context, js_context, live_task, remaining_seconds, clear_state


class C(BaseConstants):
    NAME_IN_URL = 'CountingZeroPractice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TASK_SECONDS = 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Only temporary UI state; no answers, scores, accuracy or submission rows.
    practice_state = models.LongStringField(blank=True)


class Instructions(Page):
    template_name = 'global/PracticeInstructions.html'
    vars_for_template = staticmethod(context)


class MyPage(Page):
    live_method = live_task
    timer_text = tr('remaining_time')
    get_timeout_seconds = staticmethod(remaining_seconds)
    vars_for_template = staticmethod(context)
    js_vars = staticmethod(js_context)

    @staticmethod
    def before_next_page(player, timeout_happened):
        clear_state(player)


class Complete(Page):
    template_name = 'global/PracticeComplete.html'
    vars_for_template = staticmethod(context)


page_sequence = [Instructions, MyPage, Complete]
