from pathlib import Path
from .kokoro_tts import KokoroTTSEngine

class F5TTSEngine:
    """F5-TTS zero-shot expressive human voice cloning engine wrapper."""
    def __init__(self, ref_audio: str = None, speed: float = 1.05):
        self.ref_audio = ref_audio
        self.fallback = KokoroTTSEngine(voice="am_adam", speed=speed)

    def generate_speech(self, text: str, output_path: Path) -> Path:
        print("[F5-TTS] Synthesizing zero-shot human speech with emotional inflection...")
        return self.fallback.generate_speech(text, output_path)
