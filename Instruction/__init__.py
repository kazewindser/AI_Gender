from otree.api import *
from settings import LANGUAGE_CODE, TreatmentAI


doc = "Treatment-specific experiment instructions embedded from Google Slides."


class C(BaseConstants):
    NAME_IN_URL = 'instruction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    SLIDES = {
        ('CountingZero', False): 'https://docs.google.com/presentation/d/e/2PACX-1vQU9isqxd0mg8oDANpI1AU_eck1p2OV7n4VpK2A7g1PZmwIS1Hw7wXKgoYmrppSZA/pubembed',
        ('CountingZero', True): 'https://docs.google.com/presentation/d/e/2PACX-1vTOC053eecdfbCol0SLGMwa0y_vDRRIWcxuDimtnR__utFJZKZofP3t3dhGWyeHPA/pubembed',
        ('StockForecast', False): 'https://docs.google.com/presentation/d/e/2PACX-1vTlsEKNn9MQvLFJBmTkMjPGMyJr7241AoqupYIQUtIfGAasgMa6S8VxNgAUc-qq5g/pubembed',
        ('StockForecast', True): 'https://docs.google.com/presentation/d/e/2PACX-1vTT2Xsj3K846ob-nrOVnWKf2SPMo2Ozabzf7gJwrgy6h2WFpw6TjjLJu1AqHalzPg/pubembed',
    }
    SLIDES_EN = {
        ('CountingZero', False): 'https://docs.google.com/presentation/d/e/2PACX-1vTlCFi2BxE_QQD-mttj5GgVSdQ9EwaDZfhQr7Ay6SA7JK9Z3W3g0n700usLo37FzQ/pubembed',
        ('CountingZero', True): 'https://docs.google.com/presentation/d/e/2PACX-1vQnKgoZSwviymtW1ORzvygTNqoiDfPBxnynA7UfdUS3-UI3LkoEIdWhijzIyO6KTg/pubembed',
        ('StockForecast', False): 'https://docs.google.com/presentation/d/e/2PACX-1vSxtcR__avoQn79YzA2CSaLzkUJhc3OCbG2p7nNkmWs2LKyEM6-opsv9TM-zp3_sg/pubembed',
        ('StockForecast', True): 'https://docs.google.com/presentation/d/e/2PACX-1vTkl2OdcINR-laJqkFyIVgVZ3wIOqHF57-wYBwxzAGnDTYvGqgo_lntke1fPYvQzg/pubembed',
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
    return slides[(tasks[0], TreatmentAI)]


class Instruction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(slides_url=get_slides_url(player), is_english=LANGUAGE_CODE == 'en')


page_sequence = [Waitplease, Instruction]
