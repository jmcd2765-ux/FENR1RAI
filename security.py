import re
import logging

class SecurityFilter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deny_patterns = [
            r'\b(hate|racist|sexist|violent|threat|dox|explicit|self[- ]harm|suicide|bully|harass|abuse)\b',
            r'\b(fuck|shit|cunt|asshole|damn|bitch|die|kill|punch|slap)\b',
        ]

    def filter_response(self, response: str) -> str:
        for pattern in self.deny_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                self.logger.warning(f"Blocked response due to pattern: {pattern}")
                return ""  # Block the response
        self.logger.debug(f"Response passed security: {response[:60]}...")
        return response