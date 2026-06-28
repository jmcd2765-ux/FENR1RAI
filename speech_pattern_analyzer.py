import re
import logging
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Set

class SpeechPatternAnalyzer:
    """Analyzes and stores user speech patterns to enable accurate response emulation."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_patterns = defaultdict(lambda: {
            "vocabulary": Counter(),
            "sentence_patterns": [],
            "punctuation_habits": Counter(),
            "emoji_usage": Counter(),
            "phrase_signatures": [],
            "word_frequency": Counter(),
            "avg_message_length": 0,
            "capitalization_style": "normal",
            "common_interjections": Counter(),
            "response_templates": [],
            "sentiment_markers": Counter(),
            "message_count": 0,
            "samples": []
        })
        self.alpha_patterns = None

    def analyze_message(self, username: str, content: str, is_alpha: bool = False):
        """Extract and store speech patterns from a message."""
        if not content or len(content.strip()) < 3:
            return

        profile = self.user_patterns[username]
        profile["message_count"] += 1
        profile["samples"].append(content)
        
        # Keep only recent samples to avoid memory issues
        if len(profile["samples"]) > 100:
            profile["samples"] = profile["samples"][-100:]

        # Extract patterns
        self._extract_vocabulary(content, profile)
        self._extract_punctuation(content, profile)
        self._extract_emojis(content, profile)
        self._extract_sentence_patterns(content, profile)
        self._extract_interjections(content, profile)
        self._extract_sentiment_markers(content, profile)
        self._update_capitalization_style(content, profile)
        self._extract_phrase_signatures(content, profile)

        # Update average message length
        profile["avg_message_length"] = (
            (profile["avg_message_length"] * (profile["message_count"] - 1) + len(content)) 
            / profile["message_count"]
        )

        if is_alpha:
            self.alpha_patterns = profile

        self.logger.debug(f"Analyzed message from {username}: {len(content)} chars, pattern count: {profile['message_count']}")

    def _extract_vocabulary(self, content: str, profile: Dict):
        """Extract and track vocabulary usage."""
        words = re.findall(r"\b[a-zA-Z0-9_]+\b", content.lower())
        profile["vocabulary"].update(words)
        profile["word_frequency"].update(words)

    def _extract_punctuation(self, content: str, profile: Dict):
        """Track punctuation habits."""
        punctuation = re.findall(r"[!?.,;:\-()\"']+", content)
        profile["punctuation_habits"].update(punctuation)

    def _extract_emojis(self, content: str, profile: Dict):
        """Detect and track emoji usage."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(content)
        profile["emoji_usage"].update(emojis)

    def _extract_sentence_patterns(self, content: str, profile: Dict):
        """Extract sentence structure patterns."""
        sentences = re.split(r"[.!?]+", content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 3:
                # Store pattern: first 3 words and structure
                words = sentence.split()[:3]
                pattern = " ".join(words).lower()
                if pattern and len(pattern) > 2:
                    profile["sentence_patterns"].append(pattern)

    def _extract_interjections(self, content: str, profile: Dict):
        """Track interjections and expressions."""
        interjections = re.findall(
            r"\b(yeah|yep|nope|lol|omg|wtf|bruh|dude|hey|yo|wow|no|yes|so|like|uh|hmm|haha|lmao)\b",
            content.lower()
        )
        profile["common_interjections"].update(interjections)

    def _extract_sentiment_markers(self, content: str, profile: Dict):
        """Track emotional/sentiment markers."""
        positive = ["good", "great", "awesome", "love", "nice", "cool", "best", "perfect", "amazing"]
        negative = ["bad", "hate", "sucks", "worst", "terrible", "awful", "poor", "wrong"]
        neutral = ["okay", "fine", "alright", "meh", "dunno", "whatever"]

        for marker in positive:
            if marker in content.lower():
                profile["sentiment_markers"][f"+{marker}"] += 1
        for marker in negative:
            if marker in content.lower():
                profile["sentiment_markers"][f"-{marker}"] += 1
        for marker in neutral:
            if marker in content.lower():
                profile["sentiment_markers"][f"~{marker}"] += 1

    def _update_capitalization_style(self, content: str, profile: Dict):
        """Determine user's capitalization style."""
        lowercase_ratio = sum(1 for c in content if c.islower()) / max(len(content), 1)
        if lowercase_ratio > 0.9:
            profile["capitalization_style"] = "lowercase"
        elif any(c.isupper() for c in content[1:]):
            profile["capitalization_style"] = "mixed"
        else:
            profile["capitalization_style"] = "normal"

    def _extract_phrase_signatures(self, content: str, profile: Dict):
        """Extract distinctive phrase patterns."""
        # Common connectors and how they're used
        phrases = re.findall(r"\b(?:but|and|because|so|if|when|like|think|mean|know)\b", content.lower())
        profile["phrase_signatures"].extend(phrases)

    def get_user_pattern_summary(self, username: str) -> str:
        """Generate a pattern summary for prompt injection."""
        if username not in self.user_patterns or self.user_patterns[username]["message_count"] == 0:
            return ""

        profile = self.user_patterns[username]
        msg_count = profile["message_count"]
        
        summary_parts = []

        # Top vocabulary
        if profile["vocabulary"]:
            top_words = [word for word, _ in profile["vocabulary"].most_common(5)]
            summary_parts.append(f"Favorite words: {', '.join(top_words)}")

        # Punctuation style
        if profile["punctuation_habits"]:
            top_punct = profile["punctuation_habits"].most_common(3)
            punct_str = ", ".join([f'"{p}"' for p, _ in top_punct])
            summary_parts.append(f"Often uses: {punct_str}")

        # Emojis
        if profile["emoji_usage"]:
            top_emojis = "".join([emoji for emoji, _ in profile["emoji_usage"].most_common(3)])
            summary_parts.append(f"Emoji style: {top_emojis}")

        # Interjections
        if profile["common_interjections"]:
            interjections = [w for w, _ in profile["common_interjections"].most_common(3)]
            summary_parts.append(f"Often says: {', '.join(interjections)}")

        # Message style
        cap_style = profile["capitalization_style"]
        avg_len = int(profile["avg_message_length"])
        summary_parts.append(f"Style: {cap_style} text, ~{avg_len} chars per message")

        # Sentiment tendency
        if profile["sentiment_markers"]:
            sentiments = profile["sentiment_markers"].most_common(3)
            sentiment_str = ", ".join([marker for marker, _ in sentiments])
            summary_parts.append(f"Sentiment: {sentiment_str}")

        return f"User {username}'s speech pattern ({msg_count} messages analyzed): {'; '.join(summary_parts)}"

    def get_alpha_instruction(self) -> str:
        """Generate instruction block for The Alpha's speech patterns."""
        if not self.alpha_patterns or self.alpha_patterns["message_count"] == 0:
            return "Emulate The Alpha's communication style when responding to them or about them."

        profile = self.alpha_patterns

        style_elements = []

        # Top words
        if profile["vocabulary"]:
            top_words = [word for word, _ in profile["vocabulary"].most_common(5)]
            style_elements.append(f"Uses these words often: {', '.join(top_words)}")

        # Interjections
        if profile["common_interjections"]:
            interjections = [w for w, _ in profile["common_interjections"].most_common(3)]
            style_elements.append(f"Favorite expressions: {', '.join(interjections)}")

        # Emoji tendency
        emoji_count = sum(profile["emoji_usage"].values())
        if emoji_count > 0:
            style_elements.append("Uses emojis frequently")

        # Capitalization
        if profile["capitalization_style"] == "lowercase":
            style_elements.append("Prefers lowercase text")
        elif profile["capitalization_style"] == "mixed":
            style_elements.append("Uses mixed case naturally")

        # Message length
        avg_len = int(profile["avg_message_length"])
        if avg_len < 30:
            style_elements.append("Keeps messages short and snappy")
        elif avg_len > 100:
            style_elements.append("Often writes longer, detailed messages")

        if not style_elements:
            return "Emulate The Alpha's authentic communication style."

        instruction = (
            f"When responding to or about The Alpha, emulate their communication style: "
            f"{'; '.join(style_elements)}. "
            f"Maintain their personality and speech patterns while staying in character as FENR1R."
        )
        return instruction

    def get_pattern_injection(self, username: str) -> str:
        """Generate a prompt injection to encourage pattern matching."""
        if username not in self.user_patterns or self.user_patterns[username]["message_count"] < 5:
            return ""

        profile = self.user_patterns[username]
        if profile["message_count"] == 0:
            return ""

        pattern_desc = self.get_user_pattern_summary(username)
        
        return (
            f"Remember this about {username}: {pattern_desc}. "
            f"Try to mirror their communication style subtly in your responses to create rapport."
        )

    def extract_speech_template(self, username: str) -> Optional[str]:
        """Extract a representative speech template from user's messages."""
        if username not in self.user_patterns or not self.user_patterns[username]["samples"]:
            return None

        samples = self.user_patterns[username]["samples"]
        if not samples:
            return None

        # Return a random recent sample as template
        return samples[-1] if samples else None

    def get_all_patterns_summary(self) -> str:
        """Generate a summary of all tracked patterns."""
        summaries = []
        for username, profile in self.user_patterns.items():
            if profile["message_count"] > 0:
                summaries.append(self.get_user_pattern_summary(username))

        return "\n".join(summaries) if summaries else ""
