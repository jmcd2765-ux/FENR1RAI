#!/usr/bin/env python3
"""
FENR1R Setup Script
Quick setup for FENR1R AI Streamer Companion.
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from config import Config

def run_command(cmd, shell=True):
    """Run a command and return success."""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required.")
        sys.exit(1)
    print(f"Python version: {sys.version}")

def setup_virtual_env():
    """Ensure virtual environment is set up."""
    if not Path(".venv").exists():
        print("Creating virtual environment...")
        success, _, err = run_command("python -m venv .venv")
        if not success:
            print(f"Failed to create venv: {err}")
            sys.exit(1)
    print("Virtual environment ready.")

def activate_and_install():
    """Activate venv and install requirements."""
    print("Activating venv and installing requirements...")
    success, _, err = run_command(r".\.venv\Scripts\Activate.ps1 ; pip install -r requirements.txt")
    if not success:
        print(f"Failed to install: {err}")
        sys.exit(1)
    print("Dependencies installed.")

def setup_env():
    """Setup .env file with user input."""
    env_path = Path(".env")
    if env_path.exists():
        overwrite = input(".env already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            return

    print("Setting up .env file...")
    twitch_token = input("Enter Twitch OAuth token (from https://twitchtokengenerator.com/): ")
    twitch_client_id = input("Enter Twitch Client ID: ")
    twitch_nick = input("Enter bot nickname: ")
    twitch_channel = input("Enter channel name (e.g., TheCanidGamer): ")
    ollama_url = input("Enter Ollama URL (default http://127.0.0.1:11434): ") or "http://127.0.0.1:11434"
    ollama_model = input("Enter Ollama model (default llama3): ") or "llama3"

    with open(env_path, 'w') as f:
        f.write(f"TWITCH_TOKEN={twitch_token}\n")
        f.write(f"TWITCH_CLIENT_ID={twitch_client_id}\n")
        f.write(f"TWITCH_NICK={twitch_nick}\n")
        f.write(f"TWITCH_CHANNEL={twitch_channel}\n")
        f.write(f"OLLAMA_URL={ollama_url}\n")
        f.write(f"OLLAMA_MODEL={ollama_model}\n")
    print(".env created.")

def check_ollama():
    """Check and setup Ollama."""
    print("Checking Ollama...")
    success, _, _ = run_command("ollama --version")
    if not success:
        print("Ollama not found. Please install from https://ollama.ai/ and run 'ollama serve'.")
        input("Press Enter after installing Ollama...")
        success, _, _ = run_command("ollama --version")
        if not success:
            print("Ollama still not found. Exiting.")
            sys.exit(1)

    # Pull model
    model = input("Enter model to pull (default llama3): ") or "llama3"
    print(f"Pulling model {model}...")
    success, _, err = run_command(f"ollama pull {model}")
    if not success:
        print(f"Failed to pull model: {err}")
        sys.exit(1)
    print("Model ready.")

def check_audio():
    """Check audio devices."""
    print("Checking audio devices...")
    try:
        import importlib
        pyaudio = importlib.import_module("pyaudio")
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"Found {device_count} audio devices.")
        for i in range(device_count):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"Input device {i}: {info['name']}")
        audio.terminate()
    except ModuleNotFoundError:
        print("pyaudio not installed yet. Will be after requirements.")
    except Exception as e:
        print(f"Audio check failed: {e}")

def adjust_settings():
    """Allow adjusting features."""
    config = Config()
    print("Adjusting settings...")
    memory_age = input(f"Memory buffer age in minutes (current {config.get('memory_age')//60}): ") or str(config.get('memory_age')//60)
    config.set("memory_age", int(memory_age) * 60)
    cooldown = input(f"Response cooldown in seconds (current {config.get('cooldown')}): ") or str(config.get('cooldown'))
    config.set("cooldown", int(cooldown))
    voice_rate = input(f"TTS voice rate (current {config.get('voice_rate')}): ") or str(config.get('voice_rate'))
    config.set("voice_rate", int(voice_rate))
    voice_pitch = input(f"TTS voice pitch shift in semitones (current {config.get('voice_pitch')}): ") or str(config.get('voice_pitch'))
    config.set("voice_pitch", int(voice_pitch))
    print("Settings saved to config.json")

def locate_vtube():
    """Guide to locate VTube Studio."""
    print("VTube Studio setup:")
    print("- Install VTube Studio from https://denchisoft.com/")
    print("- Enable OSC in settings (port 9000).")
    input("Press Enter when ready...")

def run_ai():
    """Option to run the AI."""
    run_now = input("Run FENR1R now? (y/n): ").lower()
    if run_now == 'y':
        print("Starting FENR1R...")
        os.system("python main.py")

def main():
    print("Welcome to FENR1R Setup!")
    check_python_version()
    setup_virtual_env()
    activate_and_install()
    setup_env()
    check_ollama()
    check_audio()
    adjust_settings()
    locate_vtube()
    run_ai()
    print("Setup complete!")

if __name__ == "__main__":
    main()