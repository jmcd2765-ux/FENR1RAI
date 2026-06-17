import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Optional

GAME_TERMS = [
    "valorant", "league of legends", "fortnite", "apex", "minecraft", "elden ring",
    "overwatch", "dota", "call of duty", "warcraft", "pokemon", "zelda", "hades",
    "cyberpunk", "skyrim", "minecraft", "among us", "roblox", "gta", "fall guys"
]

class LearningEngine:
    def __init__(self, knowledge_manager=None):
        self.user_profiles = defaultdict(lambda: {
            "messages": [],
            "favorite_games": set(),
            "loyalty_score": 0,
            "tags": set(),
            "recent_topics": [],
            "communication_style": Counter(),
            "sentiment_trend": 0.0,  # -1.0 to 1.0
            "interaction_frequency": 0,
            "preferred_response_style": "balanced"
        })
        self.global_topics = defaultdict(int)
        self.knowledge_manager = knowledge_manager
        self.sentiment_keywords = {
            "positive": ["love", "amazing", "awesome", "great", "good", "nice", "cool", "best"],
            "negative": ["hate", "bad", "terrible", "awful", "worst", "sucks", "trash"],
            "neutral": ["okay", "fine", "alright", "normal", "regular", "standard"]
        }

    def observe_message(self, username: str, content: str, tags: Optional[Dict] = None):
        profile = self.user_profiles[username]
        profile["messages"].append(content)
        profile["interaction_frequency"] += 1
        
        import logging
        logger = logging.getLogger(__name__)
        
        if tags:
            if tags.get("subscriber"):
                profile["loyalty_score"] += 2
                profile["tags"].add("subscriber")
                logger.info(f"Subscriber {username} sent message: +2 loyalty (total: {profile['loyalty_score']})")
            if tags.get("bits"):
                profile["loyalty_score"] += 1
                profile["tags"].add("bits")
                logger.info(f"Bits from {username}: +1 loyalty (total: {profile['loyalty_score']})")
            if tags.get("vip"):
                profile["tags"].add("vip")
                logger.info(f"VIP {username} participated in chat")
        
        found_games = self._extract_games(content)
        profile["favorite_games"].update(found_games)
        for game in found_games:
            self.global_topics[game] += 1
            logger.debug(f"Game mentioned: {game}")
        
        topics = self._extract_topics(content)
        profile["recent_topics"].extend(topics)
        for topic in topics:
            self.global_topics[topic] += 1

        # Track communication style patterns
        self._analyze_communication_style(content, profile)
        
        # Track sentiment trend
        self._update_sentiment_trend(content, profile)

        # Auto-save important knowledge
        self._auto_save_important_knowledge(username, content, tags)

    def _auto_save_important_knowledge(self, username: str, content: str, tags: Optional[Dict] = None):
        """Automatically save important knowledge to long-term memory."""
        if not self.knowledge_manager:
            return

        # Save if user has high loyalty and mentions games
        profile = self.user_profiles[username]
        if profile["loyalty_score"] > 5 and self._extract_games(content):
            entry = f"User {username} (loyalty: {profile['loyalty_score']}) shared: '{content}'"
            self.knowledge_manager.save_long_term_memory(entry, "User_Insights")

        # Save trending topics if they reach a threshold
        for topic, count in self.global_topics.items():
            if count >= 10 and not hasattr(self, f"_saved_{topic}"):
                setattr(self, f"_saved_{topic}", True)
                entry = f"Trending topic '{topic}' mentioned {count} times in chat."
                self.knowledge_manager.save_long_term_memory(entry, "Trending_Topics")

        # Save if message contains teaching-like content
        if any(word in content.lower() for word in ["learn", "remember", "fact", "tip", "guide"]):
            entry = f"Knowledge from {username}: {content}"
            self.knowledge_manager.save_long_term_memory(entry, "Learned_Facts")

    def _extract_games(self, content: str) -> Set[str]:
        content_lower = content.lower()
        found = {term for term in GAME_TERMS if term in content_lower}
        return found

    def _extract_topics(self, content: str) -> List[str]:
        words = re.findall(r"[a-zA-Z0-9']+", content.lower())
        topics = [word for word in words if len(word) > 4]
        return topics[-5:]

    def _analyze_communication_style(self, content: str, profile: Dict):
        """Analyze and track user's communication style patterns."""
        # Track message length
        length_category = "short" if len(content) < 20 else "medium" if len(content) < 100 else "long"
        profile["communication_style"][f"length_{length_category}"] += 1
        
        # Track capitalization
        if content.isupper():
            profile["communication_style"]["all_caps"] += 1
        elif content[0].isupper():
            profile["communication_style"]["capitalized"] += 1
        else:
            profile["communication_style"]["lowercase"] += 1
        
        # Track punctuation
        if "!" in content:
            profile["communication_style"]["uses_exclamation"] += 1
        if "?" in content:
            profile["communication_style"]["uses_questions"] += 1
        if "..." in content or ".." in content:
            profile["communication_style"]["uses_ellipsis"] += 1
        
        # Track emoji usage (basic)
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', content))
        if emoji_count > 0:
            profile["communication_style"]["uses_emojis"] += 1

    def _update_sentiment_trend(self, content: str, profile: Dict):
        """Update user's overall sentiment trend."""
        content_lower = content.lower()
        sentiment_score = 0.0
        
        # Count sentiment indicators
        for word in self.sentiment_keywords["positive"]:
            if word in content_lower:
                sentiment_score += 0.3
        
        for word in self.sentiment_keywords["negative"]:
            if word in content_lower:
                sentiment_score -= 0.3
        
        # Update trend (exponential moving average)
        profile["sentiment_trend"] = 0.8 * profile["sentiment_trend"] + 0.2 * sentiment_score
        
        # Determine preferred response style based on trend
        if profile["sentiment_trend"] > 0.3:
            profile["preferred_response_style"] = "upbeat"
        elif profile["sentiment_trend"] < -0.3:
            profile["preferred_response_style"] = "supportive"
        else:
            profile["preferred_response_style"] = "balanced"

    def get_user_context(self, username: str) -> str:
        if username not in self.user_profiles:
            return ""
        profile = self.user_profiles[username]
        games = ", ".join(sorted(profile["favorite_games"])) or "none yet"
        tags = ", ".join(sorted(profile["tags"])) or "no special tags"
        recent = "; ".join(profile["recent_topics"][-5:]) or "no recent topics"
        
        # Add communication style insights
        style_insights = []
        if profile["communication_style"]:
            top_styles = profile["communication_style"].most_common(3)
            style_insights = [style for style, _ in top_styles]
        
        style_str = f" Communication style: {', '.join(style_insights)}." if style_insights else ""
        sentiment_str = f" Overall sentiment: {profile['sentiment_trend']:+.2f} ({profile['preferred_response_style']})." if abs(profile['sentiment_trend']) > 0.1 else ""
        
        return (
            f"User summary for {username}: favorite games: {games}. "
            f"Loyalty score: {profile['loyalty_score']}. Tags: {tags}. "
            f"Recent topics: {recent}. Interactions: {profile['interaction_frequency']}{style_str}{sentiment_str}"
        )

    def get_global_context(self) -> str:
        if not self.global_topics:
            return ""
        sorted_topics = sorted(self.global_topics.items(), key=lambda item: item[1], reverse=True)
        top = ", ".join([f"{topic}({count})" for topic, count in sorted_topics[:8]])
        return f"Trending chat topics and games: {top}."
