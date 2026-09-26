import json
import re
from pathlib import Path

class ScriptGenerator:
    """Generates engaging YouTube recapper scripts from chapter panel metadata."""
    def __init__(self, provider: str = "fallback", model_name: str = "Qwen/Qwen2.5-7B-Instruct"):
        self.provider = provider
        self.model_name = model_name

    def generate_script(self, chapter_dir: Path) -> dict:
        """
        Reads chapter panels, extracts narration text files if available,
        and builds a high-retention recapper script JSON.
        """
        chapter_dir = Path(chapter_dir)
        panel_files = sorted([f for f in chapter_dir.glob("*.txt") if not f.name.endswith("_inpainted.txt")])
        
        narrations = []
        for p in panel_files:
            with open(p, "r", encoding="utf-8") as f:
                narrations.append((p.stem, f.read().strip()))

        if not narrations:
            # Fallback default story generator if no text files found
            return self._build_default_script(chapter_dir)

        scenes = []
        for idx, (stem, raw_text) in enumerate(narrations, start=1):
            scene = {
                "scene_id": idx,
                "panel_name": f"{stem}.jpg",
                "narration": self._enhance_narration(raw_text, idx),
                "emotion": "intense" if "monster" in raw_text.lower() or "die" in raw_text.lower() else "dramatic",
                "motion_type": ["zoom_in", "pan_down", "pan_right", "zoom_out"][idx % 4]
            }
            scenes.append(scene)

        script_data = {
            "title": f"The Shadow Monarch Awakens - {chapter_dir.name.capitalize()} Recap",
            "scenes": scenes
        }
        return script_data

    def _enhance_narration(self, raw_text: str, index: int) -> str:
        """Punches up raw translation text into YouTube recap voiceover style."""
        if index == 1:
            return f"Welcome back, hunters! {raw_text} But today, everything changes."
        return raw_text

    def _build_default_script(self, chapter_dir: Path) -> dict:
        image_files = sorted([f for f in chapter_dir.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
        scenes = []
        
        default_narrations = [
            "In a world where mysterious dungeons suddenly opened, Jinwoo was known as the weakest hunter of all time.",
            "Trapped inside a double dungeon surrounded by giant killer statues, death was creeping closer.",
            "Just as all hope seemed lost, a glowing quest system window appeared before his eyes!",
            "He accepts the secret trial... and unlocks the power of the legendary Shadow Monarch!"
        ]

        for idx, img_file in enumerate(image_files, start=1):
            text = default_narrations[(idx - 1) % len(default_narrations)]
            scenes.append({
                "scene_id": idx,
                "panel_name": img_file.name,
                "narration": text,
                "emotion": "intense",
                "motion_type": ["zoom_in", "pan_down", "pan_right", "zoom_out"][(idx - 1) % 4]
            })

        return {
            "title": f"Manhwa Recap - {chapter_dir.name}",
            "scenes": scenes
        }
