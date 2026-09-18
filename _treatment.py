"""Resolve AI treatment per session, with the global setting as a legacy fallback."""
import settings


def ai_enabled(player):
    return player.session.config.get('treatment_ai', settings.TreatmentAI)
