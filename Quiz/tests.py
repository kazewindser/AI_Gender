from otree.api import Bot, SubmissionMustFail

from . import C, QUIZ_TEXT, QuestionPage, Results, Start


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            assert QUIZ_TEXT['start'] in self.html
            yield Start

        question = C.QUESTIONS[self.round_number - 1]
        assert f"{QUIZ_TEXT['question']} {self.round_number} / {C.NUM_ROUNDS}" in self.html
        assert question['question'] in self.html
        for value, label in question['choices']:
            assert label in self.html

        yield SubmissionMustFail(QuestionPage, {}, error_fields=['answer'])
        for value, _ in question['choices']:
            if value != question['correct']:
                yield SubmissionMustFail(QuestionPage, {'answer': value})
                assert question['error_msg'] in self.html

        yield QuestionPage, {'answer': question['correct']}

        if self.round_number == C.NUM_ROUNDS:
            assert QUIZ_TEXT['all_correct'] in self.html
            yield Results
