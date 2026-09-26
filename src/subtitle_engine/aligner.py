import os
from pathlib import Path

class SubtitleAligner:
    """Generates word-level ASS/SRT subtitles aligned with TTS audio tracks."""
    def __init__(self, font_name: str = "Impact", font_size: int = 28):
        self.font_name = font_name
        self.font_size = font_size

    def generate_ass_subtitle(self, audio_scenes: list, output_ass_path: Path) -> Path:
        """
        Creates ASS formatted subtitle file with timed text chunks.
        `audio_scenes` is a list of dicts containing: {'narration': str, 'start_time': float, 'duration': float}
        """
        output_ass_path = Path(output_ass_path)
        output_ass_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"""[Script Info]
Title: Manhwa Recap Auto Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.font_name},{self.font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,20,20,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        for scene in audio_scenes:
            start_str = self._format_ass_time(scene['start_time'])
            end_str = self._format_ass_time(scene['start_time'] + scene['duration'])
            text = scene['narration'].replace("\n", " ")
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")

        return output_ass_path

    def _format_ass_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        if cs >= 100:
            cs = 99
            secs += 1
        return f"{hours:01d}:{minutes:02d}:{secs:02d}.{cs:02d}"
