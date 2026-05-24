# FENR1R — Twitch AI Companion

FENR1R is an interactive Ai that will costream on Twitch, built as a Python framework. It is designed to behave like a cheeky, slightly unhinged digital wolf pup who protects and roasts chat while staying loyal to the streamer, The Alpha.

## Features
- **Personality Engine**: LLM-powered responses with wolf-themed persona.
- **Twitch Integration**: Real-time chat monitoring with priority and cooldown systems.
- **Voice & STT**: Whisper for speech-to-text, pyttsx3 for feminine TTS.
- **Memory**: Short-term context for conversations.
- **Security**: Filters for TOS compliance.
- **Configurable**: JSON-based settings for easy adjustments.
- **Logging**: Comprehensive logging for debugging.

## Architecture Overview

### 1. Personality Engine
- `personality_engine.py`: Builds LLM system prompt enforcing Canid identity.
- Uses Ollama for local inference (free).
- Enforces security and persona.

### 2. Twitch Integration
- `twitch_bot.py`: Connects to Twitch chat via twitchio.
- Priority: High for mentions/questions/bits/subs.
- Cooldown to prevent spam.

### 3. Voice / Visuals (TTS / STT)
- `voice.py`: Whisper (Hugging Face) for STT, pyttsx3 for TTS.
- Feminine voice selection, OSC to VTube Studio.

### 4. Memory & Context
- `memory.py`: Per-source buffers for chat/voice.

### 5. Security Measures
- `security.py`: Regex filters for unsafe content.

### 6. Configuration
- `config.py`: JSON settings for all parameters.

### 7. Logging
- `logging_config.py`: File and console logging.

## Setup

1. Run the setup script: `python setup.py`
   - Guides through .env, Ollama, audio, settings, VTube.

2. Manual setup:
   - Venv: `python -m venv .venv`
   - Activate: `.\.venv\Scripts\Activate.ps1`
   - Install: `pip install -r requirements.txt`
   - .env: Copy `.env.example`, fill secrets.
   - Ollama: Install, `ollama serve`, `ollama pull llama3`
   - Run: `python main.py`

## Configuration
Edit `config.json` to adjust:
- memory_age: Buffer duration (seconds)
- cooldown: Response delay (seconds)
- voice_rate: TTS speed
- whisper_model: STT model
- etc.

## Troubleshooting
- Check `fenr1r.log` for errors.
- Ensure Ollama is running.
- Verify audio devices for voice input.

## Free Tools Used
- Ollama (LLM)
- twitchio (Twitch)
- pyttsx3 (TTS)
- Whisper (STT)
- python-osc (VTube)

```powershell
python main.py
```

## Secure API Key Handling

- Store all sensitive values in `.env`.
- Do not commit `.env` to source control.
- Use `.gitignore` to exclude `.env`.
- In production, prefer secret managers or environment variables instead of plain text files.

## Notes

- This scaffold is intentionally lightweight so you can replace the LLM or TTS backend later.
- `personality_engine.py` uses a strong system prompt and a policy guard to keep FENR1R within acceptable boundaries.
- The priority / cooldown system ensures FENR1R is sparing with responses and stays chat-friendly.
