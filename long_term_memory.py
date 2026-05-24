import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class LongTermMemory:
    def __init__(self, log_dir="LongTermMemoryLog"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.entries = []
        self.load_all_logs()

    def load_all_logs(self):
        """Load all long-term memory entries from log files."""
        self.entries = []
        for file_path in self.log_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.entries.append({
                            "filename": file_path.name,
                            "content": content,
                            "date": self._extract_date(content)
                        })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def _extract_date(self, content: str) -> str:
        """Extract date from content if present."""
        for line in content.split('\n'):
            if line.startswith("Date:"):
                return line.split("Date:")[1].strip()
        return datetime.now().strftime("%Y-%m-%d")

    def save_entry(self, entry: str, category: str = "General"):
        """Save a new long-term memory entry."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{category}_Memory--FENR1R.txt"
        filepath = self.log_dir / filename

        content = f"Long-Term Memory Entry: {category}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{entry}\n\nCitation: Auto-saved from chat interaction."

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.entries.append({
                "filename": filename,
                "content": content,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            print(f"Saved long-term memory: {filename}")
        except Exception as e:
            print(f"Error saving long-term memory: {e}")

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[str]:
        """Retrieve relevant long-term memories based on query."""
        # Simple keyword matching; could be improved with embeddings
        relevant = []
        query_lower = query.lower()
        for entry in self.entries:
            if any(word in entry["content"].lower() for word in query_lower.split()):
                relevant.append(entry["content"])
                if len(relevant) >= limit:
                    break
        return relevant

    def get_all_summaries(self) -> str:
        """Get a summary of all long-term memories."""
        if not self.entries:
            return "No long-term memories available."
        summaries = [f"Memory {i+1} ({entry['date']}): {entry['content'][:200]}..." for i, entry in enumerate(self.entries)]
        return "\n".join(summaries)