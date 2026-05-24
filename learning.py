import re
from collections import defaultdict
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
            "recent_topics": []
        })
        self.global_topics = defaultdict(int)
        self.knowledge_manager = knowledge_manager

    def observe_message(self, username: str, content: str, tags: Optional[Dict] = None):
        profile = self.user_profiles[username]
        profile["messages"].append(content)
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

    def get_user_context(self, username: str) -> str:
        if username not in self.user_profiles:
            return ""
        profile = self.user_profiles[username]
        games = ", ".join(sorted(profile["favorite_games"])) or "none yet"
        tags = ", ".join(sorted(profile["tags"])) or "no special tags"
        recent = "; ".join(profile["recent_topics"][-5:]) or "no recent topics"
        return (
            f"User summary for {username}: favorite games: {games}. "
            f"Loyalty score: {profile['loyalty_score']}. Tags: {tags}. "
            f"Recent topics: {recent}."
        )

    def get_global_context(self) -> str:
        if not self.global_topics:
            return ""
        sorted_topics = sorted(self.global_topics.items(), key=lambda item: item[1], reverse=True)
        top = ", ".join([f"{topic}({count})" for topic, count in sorted_topics[:8]])
        return f"Trending chat topics and games: {top}."
