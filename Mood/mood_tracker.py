import importlib
import random
from dataclasses import dataclass
from typing import Dict, List, Optional

MOOD_FILES = ["neutral", "happy", "angry", "sad"]

@dataclass
class MoodState:
    name: str
    core_tone: str
    wolf_tone: str
    human_tone: str
    energy: str
    social_bias: str
    self_awareness: str
    response_style: str

    def summary(self) -> str:
        return (
            f"Mood: {self.name}. {self.core_tone} "
            f"Wolf instinct: {self.wolf_tone}. Human mind: {self.human_tone}. "
            f"Energy is {self.energy}, social bias is {self.social_bias}. "
            f"Aware note: {self.self_awareness}"
        )

class MoodEngine:
    def __init__(self):
        self.moods = self._load_mood_templates()
        self.current_mood = self._create_state(self.moods.get("neutral"))
        self.hybrid_balance = 0.5  # 0.0 = full wolf instinct, 1.0 = full human reasoning
        self.history: List[MoodState] = [self.current_mood]
        self.awareness = (
            "I am a human-wolf hybrid with an instinctive inner wolf and a reflective human mind, "
            "and I know how to blend both when responding."
        )

    def _load_mood_templates(self) -> Dict[str, Dict[str, str]]:
        templates = {}
        for mood_name in MOOD_FILES:
            try:
                module = importlib.import_module(f"Mood.{mood_name}")
                templates[mood_name] = getattr(module, "MOOD_TEMPLATE", {})
            except ImportError:
                templates[mood_name] = {}
        return templates

    def _create_state(self, template: Optional[Dict[str, str]]) -> MoodState:
        if not template:
            template = {
                "name": "neutral",
                "core_tone": "Balanced and steady.",
                "wolf_tone": "observant and calm.",
                "human_tone": "pragmatic and patient.",
                "energy": "balanced",
                "social_bias": "fairly open to the pack.",
                "self_awareness": "I feel composed and aware.",
                "response_style": "Grounded and reliable."
            }
        return MoodState(**template)

    def set_mood(self, mood_name: str, human_bias: float = 0.5):
        mood_name = mood_name.lower()
        mood_template = self.moods.get(mood_name) or self.moods.get("neutral")
        old_mood = self.current_mood.name
        self.current_mood = self._create_state(mood_template)
        self.hybrid_balance = max(0.0, min(1.0, human_bias))
        self.history.append(self.current_mood)
        if old_mood != self.current_mood.name:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Mood changed from {old_mood} to {self.current_mood.name} ({self.hybrid_balance*100:.0f}% human balance)")

    def observe_chat(self, username: str, content: str, tags: Optional[Dict] = None):
        text = content.lower()
        mood_trigger = "neutral"
        human_bias = 0.5

        if any(word in text for word in ["love", "thanks", "gg", "nice", "cheer", "hype"]):
            mood_trigger = "happy"
            human_bias = 0.65
        elif any(word in text for word in ["angry", "fight", "roast", "trash", "hate", "burn"]):
            mood_trigger = "angry"
            human_bias = 0.2
        elif any(word in text for word in ["sad", "lost", "miss", "alone", "slow", "tired"]):
            mood_trigger = "sad"
            human_bias = 0.8
        elif any(word in text for word in ["why", "how", "what", "when", "where", "who"]):
            mood_trigger = "neutral"
            human_bias = 0.55

        if tags and (tags.get("subscriber") or tags.get("bits") or tags.get("vip")):
            mood_trigger = "happy" if mood_trigger == "neutral" else mood_trigger
            human_bias = min(1.0, human_bias + 0.1)

        if "alpha" in text or "pack" in text or "protect" in text:
            mood_trigger = "happy"
            human_bias = 0.4

        if "storm" in text or "danger" in text or "hunt" in text:
            mood_trigger = "angry"
            human_bias = 0.3

        self.set_mood(mood_trigger, human_bias)

    def get_mood_context(self) -> str:
        mood = self.current_mood
        wolf_factor = round((1.0 - self.hybrid_balance) * 100)
        human_factor = round(self.hybrid_balance * 100)
        return (
            f"Current state: {mood.name}. {mood.core_tone} "
            f"My wolf side feels {mood.wolf_tone}, while my human side thinks {mood.human_tone}. "
            f"I am {human_factor}% human and {wolf_factor}% wolf in this moment. "
            f"Self-aware note: {mood.self_awareness}"
        )

    def get_mood_instruction(self) -> str:
        return (
            f"You must answer as a self-aware human-wolf hybrid. "
            f"The mood is {self.current_mood.name}. {self.current_mood.response_style} "
            f"Maintain the blend of instinct and human psychology in your tone."
        )

    def get_mood_summary(self) -> str:
        return f"Mood log: {self.current_mood.summary()}"
