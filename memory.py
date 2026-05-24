import time
from collections import deque, defaultdict
import logging
from typing import List

class MemoryBuffer:
    def __init__(self, max_age=600):  # 10 minutes in seconds
        self.buffers = defaultdict(lambda: deque())  # Dict of deques per source
        self.max_age = max_age
        self.logger = logging.getLogger(__name__)

    def add_message(self, source: str, message: str):
        timestamp = time.time()
        self.buffers[source].append((timestamp, message))
        self._cleanup(source)

    def get_recent_context(self, source: str) -> List[str]:
        self._cleanup(source)
        return [msg for _, msg in self.buffers[source]]

    def _cleanup(self, source: str):
        current_time = time.time()
        initial_len = len(self.buffers[source])
        while self.buffers[source] and current_time - self.buffers[source][0][0] > self.max_age:
            self.buffers[source].popleft()
        removed = initial_len - len(self.buffers[source])
        if removed > 0:
            self.logger.debug(f"Cleaned {removed} old messages from {source}")