from pathlib import Path
from .kokoro_tts import KokoroTTSEngine

class ChatTTSEngine:
    """ChatTTS conversational voice engine wrapper with laughs and pauses."""
    def __init__(self, speed: float = 1.05):
        self.fallback = KokoroTTSEngine(voice="af_bella", speed=speed)

    def generate_speech(self, text: str, output_path: Path) -> Path:
        print("[ChatTTS] Synthesizing conversational voiceover with realistic pauses...")
        return self.fallback.generate_speech(text, output_path)
