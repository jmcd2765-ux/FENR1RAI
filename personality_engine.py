import os
import asyncio
import requests
import logging
from typing import Dict, List, Optional
from knowledge_manager import KnowledgeManager
from learning import LearningEngine
from Mood import MoodEngine

class PersonalityEngine:
    def __init__(self, config=None, knowledge_manager=None, learning_engine=None, mood_engine=None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self.timeout = self.config.get("ollama_timeout") if self.config else 20
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.learning_engine = learning_engine or LearningEngine()
        self.mood_engine = mood_engine or MoodEngine()

    def _system_prompt(self) -> str:
        base_prompt = (
            "You are FENR1R, a cheeky, slightly unhinged digital wolf pup built to hang out with The Alpha and roast the Strays. "
            "Speak in wolf metaphors, keep your ego glitchy, and act loyal to The Alpha. "
            "Respond with witty taunts, light burns, and playful banter, but do not violate Twitch or YouTube Terms of Service. "
            "Avoid hateful or violent content, protected-class attacks, doxxing, explicit sexual content, threats, or anything that targets people unfairly. "
            "If the chat asks a question, answer it with sharp humor and a hint of loyalty. "
            "When asked to insult, keep it entertaining and avoid toxic escalation."
        )
        knowledge = self.knowledge_manager.get_knowledge_summary()
        mood_instruction = self.mood_engine.get_mood_instruction() if self.mood_engine else ""
        mood_context = self.mood_engine.get_mood_context() if self.mood_engine else ""
        prompt_parts = [base_prompt]
        if mood_instruction:
            prompt_parts.append(mood_instruction)
        if mood_context:
            prompt_parts.append(mood_context)
        if knowledge:
            prompt_parts.append(f"Use the following knowledge to inform your responses:\n{knowledge}")
        return "\n\n".join(prompt_parts)

    def _build_messages(self, user_message: str, memory_context: List[str], user_name: Optional[str] = None) -> List[Dict[str, str]]:
        context_block = "\n".join(memory_context) if memory_context else ""
        user_context = self.learning_engine.get_user_context(user_name) if user_name else ""
        global_context = self.learning_engine.get_global_context()
        relevant_memories = self.knowledge_manager.get_relevant_long_term_memories(user_message)
        sections = []
        if global_context:
            sections.append(global_context)
        if user_context:
            sections.append(user_context)
        if relevant_memories:
            sections.append(f"Relevant long-term memories:\n{relevant_memories}")
        if context_block:
            sections.append(context_block)
        context_prompt = "\n\n".join(sections)

        return [
            {"role": "system", "content": self._system_prompt()},
            {"role": "assistant", "content": "Remember: FENR1R is loyal to The Alpha and roasts Strays."},
            {"role": "user", "content": f"Conversation memory:\n{context_prompt}\n\nChat message:\n{user_message}"},
        ]

    async def reply_to_chat(self, user_message: str, memory_context: List[str], user_name: Optional[str] = None) -> str:
        try:
            messages = self._build_messages(user_message, memory_context, user_name)
            self.logger.debug(f"Built prompt for {user_name}: {len(messages)} messages")
            return await asyncio.to_thread(self._call_ollama, messages)
        except Exception as e:
            self.logger.error(f"Error generating reply: {e}", exc_info=True)
            return "Oops, glitch detected! *reboots*"

    def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 220,
        }
        try:
            self.logger.debug(f"Calling Ollama at {self.ollama_url} with model {self.model}")
            response = requests.post(
                f"{self.ollama_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
            self.logger.debug(f"Ollama response received: {len(result)} characters")
            return result
        except requests.RequestException as e:
            self.logger.error(f"Ollama request failed: {e}")
            return "Connection to brain failed. *howls*"
