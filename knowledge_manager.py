from pathlib import Path
from typing import Dict
from long_term_memory import LongTermMemory

class KnowledgeManager:
    def __init__(self, knowledge_dir="knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        self.knowledge_files = list(self.knowledge_dir.glob("*.txt"))
        self.long_term_memory = LongTermMemory()

    def load_all(self) -> Dict[str, str]:
        documents = {}
        for file_path in self.knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents[file_path.stem] = f.read().strip()
            except Exception:
                documents[file_path.stem] = ""
        return documents

    def get_knowledge_summary(self) -> str:
        docs = self.load_all()
        summary_lines = [f"Knowledge section: {name}\n{content}" for name, content in docs.items() if content]
        ltm_summary = self.long_term_memory.get_all_summaries()
        if ltm_summary:
            summary_lines.append(f"Long-Term Memory:\n{ltm_summary}")
        return "\n\n".join(summary_lines)

    def save_long_term_memory(self, entry: str, category: str = "General"):
        """Save a new long-term memory entry."""
        self.long_term_memory.save_entry(entry, category)

    def get_relevant_long_term_memories(self, query: str, limit: int = 5) -> str:
        """Get relevant long-term memories for a query."""
        memories = self.long_term_memory.get_relevant_memories(query, limit)
        if memories:
            return "\n\n".join([f"Relevant Memory: {mem}" for mem in memories])
        return ""
