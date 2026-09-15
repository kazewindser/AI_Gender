from otree.api import *
from ._lexicon_q import Lexicon, TEXT


doc = """Post-task questionnaire: background and ChatGPT experience."""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(min=17, max=100, label=Lexicon.q_age)
    gender = models.IntegerField(label=Lexicon.q_gender, choices=Lexicon.q_gender_opts)
    lan_jp = models.IntegerField(label=Lexicon.q_lan_jp, choices=Lexicon.q_lan_jp_opts)
    affiliate = models.IntegerField(label=Lexicon.q_affiliate, choices=Lexicon.q_kd_affiliate_opts)
    chatGPT = models.IntegerField(label=Lexicon.q_chatGPT, choices=Lexicon.q_chatGPT_opts)
    chatGPT_times = models.IntegerField(
        min=0, max=7,
        label=Lexicon.q_chatGPT_times,
    )
    chatGPT_plus = models.IntegerField(label=Lexicon.q_chatGPT_plus, choices=Lexicon.q_chatGPT_plus_opts)

    competition_pressure = models.IntegerField(label=TEXT['q_competition_pressure'], choices=TEXT['pressure_choices'])
    ai_performance_impact = models.IntegerField(label=TEXT['q_ai_performance_impact'], choices=TEXT['impact_choices'])
    ai_expected_accuracy = models.FloatField(min=0, max=100, label=TEXT['q_ai_expected_accuracy'])
    investment_experience = models.IntegerField(label=TEXT['q_investment_experience'], choices=Lexicon.q_chatGPT_opts)
    finance_course = models.IntegerField(label=TEXT['q_finance_course'], choices=Lexicon.q_chatGPT_opts)


class Questions1(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(questionnaire_text=TEXT)

    form_model = 'player'
    form_fields = ['age', 'gender', 'lan_jp', 'affiliate', 'chatGPT', 'chatGPT_times', 'chatGPT_plus']


class Questions2(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['competition_pressure', 'ai_performance_impact', 'ai_expected_accuracy']
        if 'StockForecast' in player.session.config['app_sequence']:
            fields += ['investment_experience', 'finance_course']
        return fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(questionnaire_text=TEXT)


page_sequence = [Questions1, Questions2]
