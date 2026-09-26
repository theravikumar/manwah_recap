import os
import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

class ConfigManager:
    """Manages system configurations and paths."""
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self._ensure_directories()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            return self._default_config()

    def _default_config(self) -> dict:
        return {
            "project": {"name": "Manhwa Recap Engine", "output_dir": "./outputs", "temp_dir": "./temp"},
            "hardware": {"device": "cuda", "target_gpu": "L4", "fp16": True},
            "scraper": {"user_agent": "Mozilla/5.0", "timeout": 30},
            "inpainter": {"model_type": "lama", "padding": 8},
            "enhancer": {"scale_factor": 2, "enable_motion": True, "fps": 30},
            "tts": {"engine": "kokoro", "voice": "af_heart", "speed": 1.05},
            "renderer": {"width": 1920, "height": 1080, "fps": 30, "bgm_volume": 0.12}
        }

    def _ensure_directories(self):
        out_dir = Path(self.config.get("project", {}).get("output_dir", "./outputs"))
        tmp_dir = Path(self.config.get("project", {}).get("temp_dir", "./temp"))
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

    def get(self, section: str, key: str = None, default=None):
        sec = self.config.get(section, {})
        if key is None:
            return sec
        return sec.get(key, default)

config = ConfigManager()
