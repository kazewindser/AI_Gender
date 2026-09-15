from otree.api import Bot, Submission, SubmissionMustFail
from . import C, Instructions, Question, Investment, settle_investment, Complete
from ._lexicon import TEXT


class PlayerBot(Bot):
    cases = ['correct', 'wrong', 'timeout']

    def play_round(self):
        if self.round_number == 1:
            assert TEXT['instructions_title'] in self.html
            yield Instructions
        assert C.QUESTIONS[self.round_number - 1] in self.html
        assert TEXT['next'] in self.html
        if self.round_number == 4:
            for _, label in TEXT['choices']:
                assert label in self.html
        field = 'answer_number' if self.round_number != 4 else 'answer_choice'
        correct = [4, 35, 25, 'C', 250, 5, 47][self.round_number - 1]
        deadline = self.player.deadline
        assert deadline > 0
        Question.get_timeout_seconds(self.player)
        assert self.player.deadline == deadline
        if self.case == 'timeout':
            # Even a correct answer submitted with a timeout must earn zero.
            yield Submission(Question, {field: correct}, timeout_happened=True)
        else:
            yield SubmissionMustFail(Question, {}, error_fields=[field])
            value = correct if self.case == 'correct' else (0 if self.round_number != 4 else 'A')
            yield Question, {field: value}
        expected = self.case == 'correct'
        assert self.player.is_correct == expected
        assert self.player.reward_yen == (20 if expected else 0)
        assert self.participant.vars['crt_payoff_yen'] == (20 * self.round_number if expected else 0)
        if self.round_number == C.NUM_ROUNDS:
            assert self.participant.vars['crt_correct_count'] == (7 if expected else 0)
            assert TEXT['risk_title'] in self.html
            yield SubmissionMustFail(Investment, {}, error_fields=['investment_yen'])
            for invalid in [-1, 101, 0.5]:
                yield SubmissionMustFail(Investment, dict(investment_yen=invalid))
            amount = {'correct': 100, 'wrong': 0, 'timeout': 41}[self.case]
            yield Investment, dict(investment_yen=amount)
            expected_risk = 100 - amount + (amount * 2.5 if self.player.investment_success else 0)
            assert self.participant.vars['risk_payoff_yen'] == expected_risk
            assert self.participant.vars['risk_investment_yen'] == amount
            before = self.player.payoff
            settle_investment(self.player)
            assert self.player.payoff == before
            assert float(self.participant.payoff.to_real_world_currency(self.player.session)) == (140 if expected else 0) + expected_risk
            yield Complete
