import re
import logging
from typing import Optional, Dict

class ResponseQualityEnhancer:
    """Enhances response quality by applying mood and pattern adjustments."""

    def __init__(self, mood_engine=None, speech_analyzer=None):
        self.logger = logging.getLogger(__name__)
        self.mood_engine = mood_engine
        self.speech_analyzer = speech_analyzer

    def enhance_response(self, response: str, user_name: Optional[str] = None) -> str:
        """Apply quality enhancements based on mood and patterns."""
        if not response or len(response.strip()) < 2:
            return response

        enhanced = response

        # Apply mood-based adjustments
        if self.mood_engine:
            enhanced = self._apply_mood_adjustments(enhanced)

        # Apply speech pattern adjustments
        if self.speech_analyzer and user_name:
            enhanced = self._apply_pattern_matching(enhanced, user_name)

        # Ensure response stays within length limits
        enhanced = self._trim_response(enhanced, max_length=220)

        return enhanced.strip()

    def _apply_mood_adjustments(self, response: str) -> str:
        """Adjust response tone based on current mood."""
        mood = self.mood_engine.current_mood.name
        strength = self.mood_engine.mood_strength

        # Happy mood: add more enthusiasm
        if mood == "happy" and strength > 0.6:
            # Add enthusiasm markers if not already present
            if "!" not in response:
                # Replace period at end with exclamation if appropriate
                response = re.sub(r'\.$', '!', response)
            # Add positive interjections
            if not any(word in response.lower() for word in ["yeah", "yep", "cool", "awesome"]):
                if len(response) < 150:
                    response += " *tail wags* 🐺"

        # Sad mood: be more thoughtful
        elif mood == "sad" and strength > 0.6:
            # Ensure response is empathetic
            if not any(word in response.lower() for word in ["understand", "feel", "know", "sorry"]):
                response = f"I hear you... {response}"

        # Angry mood: sharper but not mean
        elif mood == "angry" and strength > 0.6:
            # Make response snappier but keep it playful
            if "..." in response:
                response = response.replace("...", ".")
            # Ensure it's not too soft
            if response.endswith("..."):
                response = response[:-3] + "."

        # Neutral mood: balanced
        elif mood == "neutral":
            # Keep response as-is, it's already balanced
            pass

        return response

    def _apply_pattern_matching(self, response: str, user_name: str) -> str:
        """Apply user's speech patterns to make response more relatable."""
        if not self.speech_analyzer or user_name not in self.speech_analyzer.user_patterns:
            return response

        profile = self.speech_analyzer.user_patterns[user_name]
        
        if profile["message_count"] < 3:
            return response  # Need more samples to apply patterns

        # Get user's capitalization style
        cap_style = profile.get("capitalization_style", "normal")
        if cap_style == "lowercase":
            # Don't force lowercase on bot, but avoid all-caps
            response = response.replace("I'M", "I'm")
            response = response.replace("DON'T", "don't")

        # Mirror their punctuation tendency if strong
        punct_habits = profile.get("punctuation_habits", {})
        if punct_habits:
            most_used_punct = punct_habits.most_common(1)
            if most_used_punct:
                punct, count = most_used_punct[0]
                # If they use lots of exclamation marks, match that energy
                if punct == "!" and count > 5 and "!" not in response:
                    response = response.replace(".", "!", 1)

        # Add matching emojis if user uses them
        emoji_usage = profile.get("emoji_usage", {})
        if emoji_usage and len(response) < 180:
            top_emojis = emoji_usage.most_common(2)
            if top_emojis and not any(char in response for char, _ in emoji_usage.most_common(1)):
                # Add an emoji if they use them frequently
                emoji_count = sum(emoji_usage.values())
                if emoji_count > 5 and not any(ord(c) > 128 for c in response[-10:]):
                    emoji_to_add = top_emojis[0][0]
                    response += f" {emoji_to_add}"

        # Match their interjection style
        interjections = profile.get("common_interjections", {})
        if interjections:
            top_interjection = interjections.most_common(1)
            if top_interjection and len(response) < 200:
                interjection, count = top_interjection[0]
                if count > 3 and interjection not in response.lower():
                    # Naturally incorporate their favorite interjection
                    if interjection in ["yeah", "yep", "lol"]:
                        response = f"{interjection}, {response[0].lower() + response[1:]}"

        return response

    def _trim_response(self, response: str, max_length: int = 220) -> str:
        """Trim response to max length while preserving meaning."""
        if len(response) <= max_length:
            return response

        # Trim to max length
        trimmed = response[:max_length].rstrip()

        # Ensure we don't cut off mid-word or mid-sentence
        if len(response) > max_length:
            # Find the last complete sentence or natural break
            last_period = trimmed.rfind(".")
            last_exclamation = trimmed.rfind("!")
            last_question = trimmed.rfind("?")
            
            last_punct = max(last_period, last_exclamation, last_question)
            
            if last_punct > max_length * 0.7:  # If punctuation is reasonably close
                trimmed = trimmed[:last_punct + 1]
            else:
                # Find last space for word boundary
                last_space = trimmed.rfind(" ")
                if last_space > max_length * 0.7:
                    trimmed = trimmed[:last_space]

        return trimmed.strip()

    def validate_response(self, response: str) -> bool:
        """Check if response meets quality standards."""
        if not response or len(response.strip()) < 3:
            self.logger.warning("Response too short")
            return False

        # Check for common error patterns
        if response.startswith("Error") or response.startswith("Connection"):
            self.logger.warning(f"Response appears to be error: {response[:50]}")
            return False

        if len(response) > 500:
            self.logger.warning(f"Response too long: {len(response)} characters")
            return False

        return True
