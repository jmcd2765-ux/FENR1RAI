import importlib
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

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
        
        # Enhanced mood stabilization attributes
        self.mood_strength = 0.5  # 0.0-1.0, intensity of current mood
        self.mood_timestamp = time.time()  # When mood was last updated
        self.mood_decay_rate = 0.02  # How quickly moods fade (per second)
        self.mood_inertia = 2.0  # How many contradictory signals needed to shift mood
        self.conflicting_signals = 0  # Counter for mood shift attempts
        self.mood_triggers_history = []  # Recent triggers that affected mood
        self.emotional_momentum = 0.0  # -1.0 to 1.0, directional emotional trend
        self.logger = logging.getLogger(__name__)

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

    def _apply_mood_decay(self):
        """Apply emotional decay over time - emotions naturally fade."""
        current_time = time.time()
        time_elapsed = current_time - self.mood_timestamp
        
        # Decay the mood strength
        decay = self.mood_decay_rate * time_elapsed
        new_strength = max(0.3, self.mood_strength - decay)  # Don't go below 0.3 (always some emotion)
        
        if new_strength < self.mood_strength:
            self.mood_strength = new_strength
            self.mood_timestamp = current_time
            
            # If mood has decayed significantly, drift toward neutral
            if self.mood_strength < 0.4 and self.current_mood.name != "neutral":
                self.logger.debug(f"Mood strength low ({self.mood_strength:.2f}), drifting toward neutral")
                self._drift_toward_mood("neutral", intensity=0.15)

    def _drift_toward_mood(self, target_mood: str, intensity: float = 0.1):
        """Smoothly transition toward a mood without hard switch."""
        if self.current_mood.name == target_mood:
            return

        target_template = self.moods.get(target_mood)
        if not target_template:
            target_template = self.moods.get("neutral")

        target_state = self._create_state(target_template)
        
        # Blend current and target state based on intensity
        blended = {
            "name": target_mood,
            "core_tone": f"{self.current_mood.core_tone} (shifting toward: {target_state.core_tone})",
            "wolf_tone": f"{self.current_mood.wolf_tone} + {target_state.wolf_tone}",
            "human_tone": f"{self.current_mood.human_tone} + {target_state.human_tone}",
            "energy": f"{self.current_mood.energy} (becoming {target_state.energy})",
            "social_bias": f"{self.current_mood.social_bias}",
            "self_awareness": f"Transitioning from {self.current_mood.name} to {target_mood}",
            "response_style": f"{self.current_mood.response_style}"
        }
        
        self.current_mood = MoodState(**blended)
        self.mood_strength += intensity
        self.logger.debug(f"Drifting from {self.history[-1].name} toward {target_mood} (intensity: {intensity})")

    def set_mood(self, mood_name: str, human_bias: float = 0.5, intensity: float = 1.0, from_alpha: bool = False):
        """Set mood with emotional inertia and stabilization.
        
        Args:
            mood_name: Target mood
            human_bias: How human vs wolf (0-1)
            intensity: Strength of mood change (0-1)
            from_alpha: Whether this signal came from The Alpha (weights heavier)
        """
        mood_name = mood_name.lower()
        
        # Apply mood decay first
        self._apply_mood_decay()
        
        # Weight Alpha's mood signals more heavily
        if from_alpha:
            intensity = min(1.0, intensity * 1.5)
        
        # Check if this is conflicting with current mood
        if self.current_mood.name != mood_name:
            self.conflicting_signals += 1
        else:
            self.conflicting_signals = max(0, self.conflicting_signals - 1)
        
        # Apply emotional inertia - don't switch moods too quickly
        if self.conflicting_signals < self.mood_inertia and self.current_mood.name != mood_name:
            self.logger.debug(
                f"Mood change blocked by inertia: {self.conflicting_signals:.1f}/{self.mood_inertia} signals. "
                f"Current: {self.current_mood.name}, Requested: {mood_name}"
            )
            # Soft drift instead of hard switch
            self._drift_toward_mood(mood_name, intensity=intensity * 0.3)
            return
        
        # Reset conflicting signals after successful mood change
        if self.current_mood.name != mood_name:
            self.conflicting_signals = 0
        
        old_mood = self.current_mood.name
        mood_template = self.moods.get(mood_name) or self.moods.get("neutral")
        self.current_mood = self._create_state(mood_template)
        self.hybrid_balance = max(0.0, min(1.0, human_bias))
        self.mood_strength = max(0.3, min(1.0, intensity))
        self.mood_timestamp = time.time()
        
        # Update emotional momentum
        mood_values = {"sad": -1.0, "angry": 0.5, "neutral": 0.0, "happy": 1.0}
        new_momentum = mood_values.get(mood_name, 0.0)
        self.emotional_momentum = 0.7 * self.emotional_momentum + 0.3 * new_momentum
        
        self.history.append(self.current_mood)
        self.mood_triggers_history.append((mood_name, time.time()))
        
        # Keep trigger history limited
        if len(self.mood_triggers_history) > 50:
            self.mood_triggers_history = self.mood_triggers_history[-50:]
        
        if old_mood != self.current_mood.name:
            self.logger.info(
                f"Mood changed from {old_mood} to {self.current_mood.name} "
                f"({self.hybrid_balance*100:.0f}% human, intensity: {self.mood_strength:.2f})"
            )

    def observe_chat(self, username: str, content: str, tags: Optional[Dict] = None):
        """Analyze chat and determine mood influence."""
        text = content.lower()
        mood_trigger = None
        human_bias = 0.5
        intensity = 0.6
        
        is_alpha = username.lower() == os.getenv("TWITCH_CHANNEL", "").lower()
        
        # Multi-level sentiment analysis
        very_positive = ["love", "amazing", "awesome", "incredible", "perfect"]
        positive = ["thanks", "gg", "nice", "cheer", "hype", "cool", "great"]
        very_negative = ["hate", "trash", "toxic", "worst", "terrible"]
        negative = ["angry", "fight", "roast", "burn"]
        very_sad = ["rip", "lost", "dead"]
        sad = ["sad", "miss", "alone", "slow", "tired"]
        wolf_related = ["alpha", "pack", "protect", "hunt", "howl", "den", "wolf"]
        
        if any(word in text for word in very_positive):
            mood_trigger = "happy"
            human_bias = 0.7
            intensity = 0.9
        elif any(word in text for word in positive):
            mood_trigger = "happy"
            human_bias = 0.65
            intensity = 0.7
        elif any(word in text for word in very_negative):
            mood_trigger = "angry"
            human_bias = 0.15
            intensity = 0.85
        elif any(word in text for word in negative):
            mood_trigger = "angry"
            human_bias = 0.25
            intensity = 0.6
        elif any(word in text for word in very_sad):
            mood_trigger = "sad"
            human_bias = 0.85
            intensity = 0.8
        elif any(word in text for word in sad):
            mood_trigger = "sad"
            human_bias = 0.75
            intensity = 0.55
        elif any(word in text for word in ["why", "how", "what", "when", "where", "who"]):
            mood_trigger = "neutral"
            human_bias = 0.55
            intensity = 0.4
        
        # Wolf-related context increases loyalty/happiness
        if any(word in text for word in wolf_related):
            if mood_trigger != "angry":
                mood_trigger = "happy"
                human_bias = 0.4
                intensity = max(intensity, 0.5)
        
        # VIP/Subscriber/Bits boost mood positivity
        if tags and (tags.get("subscriber") or tags.get("bits") or tags.get("vip")):
            intensity = min(1.0, intensity + 0.15)
            if mood_trigger not in ["angry", "sad"]:
                mood_trigger = "happy"
                human_bias = min(1.0, human_bias + 0.1)
        
        # Apply the mood
        if mood_trigger:
            self.set_mood(mood_trigger, human_bias, intensity, from_alpha=is_alpha)

    def get_mood_context(self) -> str:
        """Get contextual mood description for LLM."""
        self._apply_mood_decay()
        
        mood = self.current_mood
        wolf_factor = round((1.0 - self.hybrid_balance) * 100)
        human_factor = round(self.hybrid_balance * 100)
        
        strength_desc = "overwhelming" if self.mood_strength > 0.8 else \
                       "strong" if self.mood_strength > 0.6 else \
                       "moderate" if self.mood_strength > 0.4 else "subtle"
        
        momentum_desc = "increasingly happy" if self.emotional_momentum > 0.3 else \
                       "increasingly upset" if self.emotional_momentum < -0.3 else \
                       "emotionally stable"
        
        return (
            f"Current state: {mood.name} ({strength_desc} feeling, {momentum_desc}). {mood.core_tone} "
            f"My wolf side feels {mood.wolf_tone}, while my human side thinks {mood.human_tone}. "
            f"I am {human_factor}% human and {wolf_factor}% wolf in this moment. "
            f"Self-aware note: {mood.self_awareness}"
        )

    def get_mood_instruction(self) -> str:
        """Get mood-based instruction for response generation."""
        self._apply_mood_decay()
        
        strength_modifier = (
            "very intense and emphatic" if self.mood_strength > 0.8 else
            "definitely" if self.mood_strength > 0.6 else
            "somewhat" if self.mood_strength > 0.4 else
            "slightly"
        )
        
        return (
            f"You must answer as a self-aware human-wolf hybrid. "
            f"Your current mood is {self.current_mood.name} ({strength_modifier}). "
            f"{self.current_mood.response_style} "
            f"Maintain the blend of instinct and human psychology in your tone. "
            f"Let your emotional state subtly flavor your response without overwhelming your core personality."
        )

    def get_mood_summary(self) -> str:
        """Get a summary of current mood state."""
        self._apply_mood_decay()
        return (
            f"Mood log: {self.current_mood.summary()} "
            f"(Strength: {self.mood_strength:.2f}, Momentum: {self.emotional_momentum:+.2f})"
        )

    def get_mood_stability_report(self) -> str:
        """Get a report on mood stability for debugging."""
        if not self.mood_triggers_history:
            return "No mood triggers recorded yet."
        
        recent_triggers = self.mood_triggers_history[-10:]
        unique_moods = set(mood for mood, _ in recent_triggers)
        
        report = (
            f"Mood Stability Report:\n"
            f"  Current mood: {self.current_mood.name}\n"
            f"  Strength: {self.mood_strength:.2f}\n"
            f"  Emotional momentum: {self.emotional_momentum:+.2f}\n"
            f"  Recent moods: {', '.join(unique_moods)}\n"
            f"  Conflicting signals: {self.conflicting_signals:.1f}/{self.mood_inertia}\n"
            f"  Recent triggers: {len(recent_triggers)} in last ~{int((time.time() - recent_triggers[0][1]))} seconds"
        )
        return report

import os
