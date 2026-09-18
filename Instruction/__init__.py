from otree.api import *
from settings import LANGUAGE_CODE
from _treatment import ai_enabled


doc = "Treatment-specific experiment instructions embedded from Google Slides."


class C(BaseConstants):
    NAME_IN_URL = 'instruction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    SLIDES = {
        ('CountingZero', False): 'https://docs.google.com/presentation/d/e/2PACX-1vSPPJxFglqp9Zamy1oyRbuLhKx-VRkH1S5sGYMp4cbJ0zHr1irt5s9w74o2082AlYK0A44xA5MhweEc/pubembed',
        ('CountingZero', True): 'https://docs.google.com/presentation/d/e/2PACX-1vToU0SyFNDHSfEXMvikmFkJrKp5NVAH-TS_1dbDl_av5Hon0EnzpKQh7iu-QZL7_dW-MadedkA0Gh-1/pubembed',
        ('StockForecast', False): 'https://docs.google.com/presentation/d/e/2PACX-1vSP1mFrwnIzVuEpwBUSGdZyyjWtqVuJWUYnx7Pm7oTU1JejZnVSDEscXo1J3kHns2sBvsoBSOQBLX9a/pubembed',
        ('StockForecast', True): 'https://docs.google.com/presentation/d/e/2PACX-1vRN4F3qd7fQBcZzhKOAIzp5V9uRR087vFsMjHz8cwgFwwjc2seFG_RyDXlQyxb0_GIDf8_Hd0wIIlcL/pubembed',
    }
    SLIDES_EN = {
        ('CountingZero', False): 'https://docs.google.com/presentation/d/e/2PACX-1vTAPqOKCp6iK-8xTLHHwt1waAtq77-OR81iQdmoWAVK1sQIkj1LsOV-ENAD1yfufu-P9RH10kcfoiqU/pubembed',
        ('CountingZero', True): 'https://docs.google.com/presentation/d/e/2PACX-1vSRtGj-SYXqW6CjmIhpIeTNO4mYtPS4Cm-XbQJDtbpYPQdSmy2orxvy97HTpSKljfwHievEPIz8hNVy/pubembed',
        ('StockForecast', False): 'https://docs.google.com/presentation/d/e/2PACX-1vT3-XZpJR9YuGUqG4S0jBbFmp1SGaerJsbTI57-Dzwao6ZduL6_pNG-GEiDEIRqjPC8LwXQbz-Yx_uq/pubembed',
        ('StockForecast', True): 'https://docs.google.com/presentation/d/e/2PACX-1vTonPHHVyRl5w3uWZfCpgIVCAAo_n9cBRDQeMEeW-Gy5COcWwaGkmO6o1k0VyFrHzQ_G7UMgr4KrEJF/pubembed',
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class Waitplease(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(is_english=LANGUAGE_CODE == 'en')


def get_slides_url(player):
    tasks = [task for task in ('CountingZero', 'StockForecast')
             if task in player.session.config['app_sequence']]
    if len(tasks) != 1:
        raise ValueError('Instruction requires exactly one CountingZero or StockForecast task.')
    slides = C.SLIDES_EN if LANGUAGE_CODE == 'en' else C.SLIDES
    return slides[(tasks[0], ai_enabled(player))]


class Instruction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            slides_url=get_slides_url(player),
            is_english=LANGUAGE_CODE == 'en',
            show_diogo_message=LANGUAGE_CODE == 'en',
        )


page_sequence = [Instruction]
