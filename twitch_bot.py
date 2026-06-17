import os
import asyncio
import logging
import sys
from pathlib import Path
from twitchio.ext import commands
from personality_engine import PersonalityEngine
from memory import MemoryBuffer
from security import SecurityFilter
from voice import VoiceEngine
from config import Config
from knowledge_manager import KnowledgeManager
from learning import LearningEngine
from Mood import MoodEngine
from response_quality_enhancer import ResponseQualityEnhancer

class FENR1RBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        self.knowledge = KnowledgeManager()
        self.learning = LearningEngine(knowledge_manager=self.knowledge)
        self.mood = MoodEngine()
        
        # Validate required environment variables
        token = os.getenv("TWITCH_ACCESS_TOKEN")
        channel = os.getenv("TWITCH_CHANNEL")
        
        if not token:
            raise ValueError(
                "TWITCH_ACCESS_TOKEN not set. "
                "Please set it in .env file or as environment variable."
            )
        if not channel:
            raise ValueError(
                "TWITCH_CHANNEL not set. "
                "Please set it in .env file or as environment variable."
            )
        
        super().__init__(
            token=token,
            prefix="!",
            initial_channels=[channel]
        )
        self.personality = PersonalityEngine(
            config=self.config,
            knowledge_manager=self.knowledge,
            learning_engine=self.learning,
            mood_engine=self.mood
        )
        self.quality_enhancer = ResponseQualityEnhancer(
            mood_engine=self.mood,
            speech_analyzer=self.personality.speech_analyzer
        )
        self.memory = MemoryBuffer(max_age=self.config.get("memory_age"))
        self.security = SecurityFilter()
        self.voice = VoiceEngine(self.config, mood_engine=self.mood)
        self.cooldown = self.config.get("cooldown")
        self.last_response_time = 0
        self.logger = logging.getLogger(__name__)

    async def event_ready(self):
        self.logger.info(f"Logged in as {self.nick}")
        self.logger.info(f"Connected to channel: {self.channel.name}")
        self.logger.info("Knowledge and learning engines loaded.")
        self.logger.info(f"Mood engine initialized with state: {self.mood.current_mood.name}")
        self.logger.info("FENR1R Bot online and ready to interact with chat.")
        # Start voice listening in background
        asyncio.create_task(self.voice.listen_and_respond(
            self.personality,
            self.memory,
            self.security,
            self.learning,
            source="voice"
        ))

    async def event_message(self, message):
        if message.echo:
            return

        # Priority system: respond to subs, bits, mentions, questions
        priority = self._calculate_priority(message)
        if priority < 1:
            return

        # Cooldown check
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_response_time < self.cooldown:
            return

        # Process message
        user_message = message.content
        memory_context = self.memory.get_recent_context("chat")
        self.learning.observe_message(message.author.name, user_message, message.tags)
        self.logger.debug(f"Observed message from {message.author.name}: {user_message}")
        self.mood.observe_chat(message.author.name, user_message, message.tags)
        self.logger.debug(f"Mood state now: {self.mood.current_mood.name} ({self.mood.hybrid_balance*100:.0f}% human)")

        try:
            # Get LLM response
            raw_response = await self.personality.reply_to_chat(
                user_message,
                memory_context,
                user_name=message.author.name
            )
            self.logger.debug(f"Generated response: {raw_response[:100]}...")

            # Security filter
            safe_response = self.security.filter_response(raw_response)
            if not safe_response:
                self.logger.warning(f"Response blocked by security filter from user {message.author.name}")
                return

            # Enhance response quality based on mood and speech patterns
            enhanced_response = self.quality_enhancer.enhance_response(safe_response, message.author.name)
            
            # Validate enhanced response
            if not self.quality_enhancer.validate_response(enhanced_response):
                self.logger.warning(f"Enhanced response failed validation, using original safe response")
                enhanced_response = safe_response

            # Send response to chat
            await message.channel.send(enhanced_response)
            self.logger.info(f"Responded to {message.author.name}: {enhanced_response[:80]}...")

            # Update memory
            self.memory.add_message("chat", f"User: {user_message}")
            self.memory.add_message("chat", f"FENR1R: {enhanced_response}")

            self.last_response_time = current_time
        except Exception as e:
            self.logger.error(f"Error processing message from {message.author.name}: {e}", exc_info=True)

    def _calculate_priority(self, message):
        content = message.content.lower()
        if "fenr1r" in content or "?" in content:
            return 3  # High priority
        if message.tags.get("bits"):
            return 2  # Bits
        if message.tags.get("subscriber"):
            return 2  # Sub
        return 0  # Low priority