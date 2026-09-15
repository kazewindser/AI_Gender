from otree.api import *
from Quiz.QuestionBank import QUESTIONS
from Quiz.QuestionBank_en import QUESTIONS as QUESTIONS_EN
from settings import LANGUAGE_CODE

doc = """
実験クイズアプリ - 6問の理解度確認テスト
"""

which_language = {'en': False, 'ja': False}
which_language[LANGUAGE_CODE] = True

QUIZ_TEXT = {
    'start': "Now, let’s begin the quiz." if which_language['en'] else 'それでは、クイズに行きましょう。',
    'question': 'Question' if which_language['en'] else '問題',
    'complete': 'Quiz complete' if which_language['en'] else 'クイズ完了',
    'thanks': 'Thank you!' if which_language['en'] else 'お疲れ様でした！',
    'all_correct': 'You have answered all questions correctly.' if which_language['en'] else '全ての問題に正解しました。',
}

class C(BaseConstants):
    NAME_IN_URL = 'quiz'
    PLAYERS_PER_GROUP = None
    QUESTIONS = QUESTIONS_EN if which_language['en'] else QUESTIONS
    NUM_ROUNDS = len(QUESTIONS)




class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    answer = models.IntegerField()


class Start(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {'quiz_text': QUIZ_TEXT}

    @staticmethod
    def is_displayed(p: Player):
        # 只在第一轮显示
        return p.round_number == 1


class QuestionPage(Page):
    form_model = 'player'
    form_fields = ['answer']

    @staticmethod
    def vars_for_template(player: Player):
        question_data = C.QUESTIONS[player.round_number - 1]
        return {
            'quiz_text': QUIZ_TEXT,
            'question_num': player.round_number,
            'question_count': C.NUM_ROUNDS,
            'question_text': question_data['question'],
            'choices': question_data['choices'],
        }

    @staticmethod
    def error_message(player: Player, values):
        question_data = C.QUESTIONS[player.round_number - 1]
        if values['answer'] != question_data['correct']:
            return question_data['error_msg']


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {'quiz_text': QUIZ_TEXT}

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class WaitForPlayers(WaitPage):
    """等待所有玩家完成所有轮次后再显示最终结果"""

    title_text = 'Please wait' if which_language['en'] else 'お待ちください'
    body_text = 'Please wait for all participants to finish the quiz...' if which_language['en'] else '全ての参加者がクイズを終了するのを待ってください...'
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(p: Player):
        # 只在最后一轮显示
        return p.round_number == C.NUM_ROUNDS

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        pass


page_sequence = [Start,QuestionPage, Results, WaitForPlayers]
