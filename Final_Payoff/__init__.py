from otree.api import *


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


class FinalResults(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        is_stock_forecast = 'StockForecast' in player.session.config['app_sequence']
        if is_stock_forecast:
            selected_round = participant.sf_selected_round
            third_choice = participant.sf_round3_choice
            round_scores = [
                participant.sf_round1_score,
                participant.sf_round2_score,
                participant.sf_round3_score,
            ]
            round_ranks = [
                participant.sf_round1_rank,
                participant.sf_round2_rank,
                participant.sf_round3_rank,
            ]
            final_score = participant.sf_final_score
        else:
            selected_round = participant.cz_selected_round
            third_choice = participant.cz_round3_choice
            round_scores = [
                participant.cz_round1_score,
                participant.cz_round2_score,
                participant.cz_round3_score,
            ]
            round_ranks = [
                participant.cz_round1_rank,
                participant.cz_round2_rank,
                participant.cz_round3_rank,
            ]
            final_score = participant.cz_final_score

        cards = [
            dict(
                round_number=1,
                title='Block 1',
                scheme='Piece rate',
                score=round_scores[0],
                rank=round_ranks[0],
                selected=selected_round == 1,
            ),
            dict(
                round_number=2,
                title='Block 2',
                scheme='Tournament',
                score=round_scores[1],
                rank=round_ranks[1],
                selected=selected_round == 2,
            ),
            dict(
                round_number=3,
                title='Block 3',
                scheme=(
                    'Tournament'
                    if third_choice == 'tournament'
                    else 'Piece rate'
                ),
                score=round_scores[2],
                rank=round_ranks[2],
                selected=selected_round == 3,
            ),
        ]
        return dict(
            payoff_cards=cards,
            final_score=final_score,
        )


page_sequence = [FinalResults]
