from .mood_tracker import MoodEngine


def initialize_mood_system() -> MoodEngine:
    engine = MoodEngine()
    engine.set_mood("neutral", human_bias=0.5)
    return engine
