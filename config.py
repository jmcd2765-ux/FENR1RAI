import json
import os
from pathlib import Path

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.defaults = {
            "memory_age": 600,  # seconds
            "cooldown": 10,     # seconds
            "voice_rate": 180,
            "voice_volume": 0.9,
            "voice_pitch": 0,
            "whisper_model": "openai/whisper-small",
            "ollama_timeout": 20,
            "audio_duration": 3,
            "vts_port": 9000
        }
        self.load()

    def load(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.defaults.copy()
            self.save()

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()