from otree.api import *
import time
import random
from ._lexicon import TEXT


doc = """Seven timed cognitive reflection questions, paying 20 JPY per correct answer."""


class C(BaseConstants):
    NAME_IN_URL = 'CRT'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 7
    SECONDS_PER_QUESTION = 60
    REWARD_YEN = 20
    QUESTIONS = TEXT['questions']
    ANSWERS = [4, 35, 25, 'C', 250, 5, 47]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    answer_number = models.FloatField(label=TEXT['answer'])
    answer_choice = models.StringField(
        label=TEXT['answer'],
        choices=TEXT['choices'],
        widget=widgets.RadioSelect,
    )
    deadline = models.FloatField(initial=0)
    timed_out = models.BooleanField(initial=False)
    is_correct = models.BooleanField(initial=False)
    reward_yen = models.IntegerField(initial=0)
    investment_yen = models.IntegerField(min=0, max=100, label=TEXT['risk_label'])
    investment_success = models.BooleanField(blank=True)
    investment_payoff_yen = models.FloatField(initial=0)
    investment_settled = models.BooleanField(initial=False)



def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            player.participant.vars['crt_question_count'] = C.NUM_ROUNDS
            player.participant.vars['crt_correct_count'] = 0
            player.participant.vars['crt_payoff_yen'] = 0


def score_answer(player, timeout_happened):
    player.timed_out = timeout_happened or time.time() >= player.deadline
    if player.round_number != 4:
        correct = player.field_maybe_none('answer_number') == C.ANSWERS[player.round_number - 1]
    else:
        correct = player.field_maybe_none('answer_choice') == 'C'
    player.is_correct = correct and not player.timed_out
    player.reward_yen = C.REWARD_YEN if player.is_correct else 0
    # Convert the fixed yen reward to oTree points so it is included exactly once
    # in participant.payoff, even when the session's point conversion changes.
    rate = player.session.config['real_world_currency_per_point']
    player.payoff = player.reward_yen / float(rate)
    rounds = player.in_all_rounds()
    player.participant.vars['crt_correct_count'] = sum(p.is_correct for p in rounds)
    player.participant.vars['crt_payoff_yen'] = sum(p.reward_yen for p in rounds)


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(crt_text=TEXT)

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Question(Page):
    form_model = 'player'
    timer_text = TEXT['timer']

    @staticmethod
    def get_form_fields(player: Player):
        return ['answer_number'] if player.round_number != 4 else ['answer_choice']

    @staticmethod
    def get_timeout_seconds(player: Player):
        if not player.deadline:
            player.deadline = time.time() + C.SECONDS_PER_QUESTION
        return max(0, player.deadline - time.time())

    @staticmethod
    def vars_for_template(player: Player):
        return dict(crt_text=TEXT, question_count=C.NUM_ROUNDS, question_text=C.QUESTIONS[player.round_number - 1])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        score_answer(player, timeout_happened)


def settle_investment(player):
    # Store the draw once; repeated calls must not redraw or double-pay.
    if not player.investment_settled:
        player.investment_success = random.random() < 0.5
        amount = player.investment_yen
        player.investment_payoff_yen = 100 - amount + (amount * 2.5 if player.investment_success else 0)
        player.investment_settled = True
    player.payoff = (player.reward_yen + player.investment_payoff_yen) / float(
        player.session.config['real_world_currency_per_point']
    )
    player.participant.vars.update(
        risk_investment_yen=player.investment_yen,
        risk_success=player.investment_success,
        risk_payoff_yen=player.investment_payoff_yen,
    )


class Investment(Page):
    form_model = 'player'
    form_fields = ['investment_yen']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(crt_text=TEXT)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        settle_investment(player)


class Complete(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(crt_text=TEXT)

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Instructions, Question, Investment, Complete]
