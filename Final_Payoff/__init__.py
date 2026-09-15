from otree.api import *
from decimal import Decimal, ROUND_CEILING
from _i18n import template_context, tr
from CRT._lexicon import TEXT as CRT_TEXT


doc = """Display the randomly selected task stage and final payoff."""


class C(BaseConstants):
    NAME_IN_URL = 'Final_Payoff'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def rounded_payment_yen(amount):
    return int((Decimal(amount) / Decimal(10)).to_integral_value(rounding=ROUND_CEILING) * 10)


class FinalResults(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        is_stock_forecast = 'StockForecast' in player.session.config['app_sequence']
        if is_stock_forecast:
            selected_round = participant.vars['sf_selected_round']
            third_choice = participant.vars['sf_round3_choice']
            round_scores = [
                participant.vars['sf_round1_score'],
                participant.vars['sf_round2_score'],
                participant.vars['sf_round3_score'],
            ]
            round_ranks = [
                participant.vars['sf_round1_rank'],
                participant.vars['sf_round2_rank'],
                participant.vars['sf_round3_rank'],
            ]
            final_score = participant.vars['sf_final_score']
        else:
            selected_round = participant.vars['cz_selected_round']
            third_choice = participant.vars['cz_round3_choice']
            round_scores = [
                participant.vars['cz_round1_score'],
                participant.vars['cz_round2_score'],
                participant.vars['cz_round3_score'],
            ]
            round_ranks = [
                participant.vars['cz_round1_rank'],
                participant.vars['cz_round2_rank'],
                participant.vars['cz_round3_rank'],
            ]
            final_score = participant.vars['cz_final_score']

        cards = [
            dict(
                round_number=1,
                title=f"{tr('task_label')} 1",
                scheme=tr('piece_rate'),
                score=round_scores[0],
                rank=round_ranks[0],
                selected=selected_round == 1,
            ),
            dict(
                round_number=2,
                title=f"{tr('task_label')} 2",
                scheme=tr('tournament'),
                score=round_scores[1],
                rank=round_ranks[1],
                selected=selected_round == 2,
            ),
            dict(
                round_number=3,
                title=f"{tr('task_label')} 3",
                scheme=(
                    tr('tournament')
                    if third_choice == 'tournament'
                    else tr('piece_rate')
                ),
                score=round_scores[2],
                rank=round_ranks[2],
                selected=selected_round == 3,
            ),
        ]
        for card in cards:
            card['rank_text'] = tr('rank_format', rank=card['rank'])
        total_payoff = participant.payoff_plus_participation_fee()
        rounded_payoff = rounded_payment_yen(total_payoff)
        # Keep the calculated task payoffs intact and export the final payment
        # separately. Reopening the results page never compounds the rounding.
        participant.vars['payment_before_rounding_yen'] = float(total_payoff)
        participant.vars['payment_rounded_yen'] = rounded_payoff
        return template_context(
            payoff_cards=cards,
            final_score=final_score,
            point_rate=player.session.config['real_world_currency_per_point'],
            main_payoff=round(float(final_score) * float(player.session.config['real_world_currency_per_point']), 2),
            participation_fee=float(player.session.config['participation_fee']),
            has_crt='CRT' in player.session.config['app_sequence'],
            crt_question_count=participant.vars.get('crt_question_count', 4),
            crt_correct_count=participant.vars.get('crt_correct_count', 0),
            crt_payoff_yen=participant.vars.get('crt_payoff_yen', 0),
            has_risk='risk_payoff_yen' in participant.vars,
            risk_text=CRT_TEXT,
            risk_investment_yen=participant.vars.get('risk_investment_yen', 0),
            risk_payoff_yen=participant.vars.get('risk_payoff_yen', 0),
            risk_outcome=CRT_TEXT['risk_won'] if participant.vars.get('risk_success') else CRT_TEXT['risk_lost'],
            additional_payoff=participant.payoff.to_real_world_currency(player.session),
            total_payoff=total_payoff,
            rounded_payoff=rounded_payoff,
        )


class Thanks(Page):
    pass


page_sequence = [FinalResults, Thanks]
