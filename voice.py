import asyncio
import importlib
import pyttsx3
import logging
from pythonosc import udp_client

# Dynamic imports for optional dependencies
try:
    numpy = importlib.import_module("numpy")
    np = numpy
except ImportError:
    np = None

try:
    pyaudio = importlib.import_module("pyaudio")
except ImportError:
    pyaudio = None

try:
    transformers = importlib.import_module("transformers")
    pipeline = transformers.pipeline
except ImportError:
    pipeline = None

class VoiceEngine:
    def __init__(self, config, mood_engine=None):
        self.config = config
        self.mood_engine = mood_engine
        self.logger = logging.getLogger(__name__)

        # TTS: Use pyttsx3 for feminine, cute voice
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        # Try to set female voice
        female_set = False
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                female_set = True
                self.logger.info(f"Set female voice: {voice.name}")
                break
        if not female_set:
            self.logger.warning("Female voice not found, using default.")
        self.tts_engine.setProperty('rate', self.config.get("voice_rate"))
        self.tts_engine.setProperty('volume', self.config.get("voice_volume"))
        self.pitch_supported = True
        try:
            self.tts_engine.setProperty('pitch', self.config.get("voice_pitch"))
        except Exception as e:
            self.pitch_supported = False
            self.logger.warning(f"TTS engine does not support pitch adjustment: {e}")

        # STT: Whisper via Hugging Face
        if pipeline:
            try:
                self.stt = pipeline("automatic-speech-recognition", model=self.config.get("whisper_model"), device="cpu")
            except Exception as e:
                self.logger.error(f"Failed to load Whisper: {e}")
                self.stt = None
        else:
            self.stt = None
            self.logger.warning("transformers not available, STT will be disabled.")

        # Audio settings
        if pyaudio:
            self.audio = pyaudio.PyAudio()
            self.stream = None
            self.chunk = 1024
            self.format = pyaudio.paInt16
            self.channels = 1
            self.rate = 16000
        else:
            self.audio = None
            self.stream = None
            self.chunk = 1024
            self.format = None
            self.channels = 1
            self.rate = 16000
            self.logger.warning("pyaudio not available, STT will be disabled.")

        # VTube Studio OSC
        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", self.config.get("vts_port"))

    def start_listening(self):
        if not self.audio:
            self.logger.error("Audio not available (pyaudio not installed)")
            return
        try:
            self.stream = self.audio.open(format=self.format, channels=self.channels,
                                          rate=self.rate, input=True, frames_per_buffer=self.chunk)
            self.logger.info("Audio listening started.")
        except Exception as e:
            self.logger.error(f"Failed to start audio: {e}")

    def stop_listening(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        self.logger.info("Audio listening stopped.")

    def record_audio(self, duration=None):
        if not duration:
            duration = self.config.get("audio_duration")
        frames = []
        try:
            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = self.stream.read(self.chunk)
                frames.append(data)
            return b''.join(frames)
        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            return b''

    def transcribe(self, audio_data):
        if not self.stt or not np:
            return ""
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = self.stt(audio_np, sampling_rate=self.rate)
            return result["text"]
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return ""

    def speak(self, text: str):
        try:
            if self.mood_engine:
                mood_rate = 0
                if self.mood_engine.current_mood.energy == "heated":
                    mood_rate = 20
                elif self.mood_engine.current_mood.energy == "low":
                    mood_rate = -10
                elif self.mood_engine.current_mood.energy == "balanced":
                    mood_rate = 0
                current_rate = self.config.get("voice_rate") + mood_rate
                self.tts_engine.setProperty('rate', max(100, min(260, current_rate)))

                mood_pitch = 0
                if self.mood_engine.current_mood.energy == "heated":
                    mood_pitch = 4
                elif self.mood_engine.current_mood.energy == "low":
                    mood_pitch = -4
                elif self.mood_engine.current_mood.energy == "balanced":
                    mood_pitch = 0
                pitch_value = self.config.get("voice_pitch") + mood_pitch
                if self.pitch_supported:
                    try:
                        self.tts_engine.setProperty('pitch', max(-12, min(12, pitch_value)))
                    except Exception as e:
                        self.logger.warning(f"Pitch adjustment failed while speaking: {e}")
                        self.pitch_supported = False

            # Speak with TTS
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

            # Send to VTube for lip sync
            self.osc_client.send_message("/chatbox/input", [text, True])
            self.logger.info(f"Spoke: {text}")
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")

    async def listen_and_respond(self, personality_engine, memory, security, learning, source="voice"):
        self.start_listening()
        self.logger.info("Voice listening started")
        try:
            while True:
                audio_data = self.record_audio()
                transcription = self.transcribe(audio_data)
                if transcription.strip():
                    self.logger.info(f"Voice input transcribed: {transcription}")
                    learning.observe_message("streamer", transcription, {})
                    memory_context = memory.get_recent_context(source)
                    raw_response = await personality_engine.reply_to_chat(
                        transcription,
                        memory_context,
                        user_name="streamer"
                    )
                    safe_response = security.filter_response(raw_response)
                    if safe_response:
                        self.speak(safe_response)
                        self.logger.info(f"Voice response: {safe_response[:80]}...")
                        memory.add_message(source, f"User: {transcription}")
                        memory.add_message(source, f"FENR1R: {safe_response}")
                await asyncio.sleep(1)  # Pause before next listen
        except KeyboardInterrupt:
            self.logger.info("Voice listening stopped by user")
            self.stop_listening()
        except Exception as e:
            self.logger.error(f"Voice loop error: {e}", exc_info=True)
            self.stop_listening()
        # For lip sync, might need to integrate with phoneme data or use VTube's lip sync feature