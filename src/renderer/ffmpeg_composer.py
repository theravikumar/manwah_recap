import os
import subprocess
import wave
import numpy as np
from pathlib import Path
from PIL import Image
from src.enhancer.depth_motion import MotionGenerator

class VideoComposer:
    """Assembles image clips, TTS audio narration, ASS subtitles, and background music into YouTube MP4."""
    def __init__(self, output_width: int = 1920, output_height: int = 1080, fps: int = 30):
        self.width = output_width
        self.height = output_height
        self.fps = fps
        self.motion_gen = MotionGenerator(target_width=output_width, target_height=output_height, fps=fps)

    def get_audio_duration(self, audio_path: Path) -> float:
        """Returns duration of an audio file in seconds."""
        try:
            with wave.open(str(audio_path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return float(frames) / float(rate)
        except Exception:
            return 3.0

    def render_full_recap(self, scene_data: dict, inpainted_dir: Path, output_video_path: Path, tts_engine, ass_subtitle_path: Path = None) -> Path:
        """
        Main video synthesis engine.
        Processes each scene:
        1. Synthesizes scene TTS audio.
        2. Measures exact audio duration.
        3. Renders panel video motion clip matching audio duration.
        4. Stitches all clips and audio tracks together with FFmpeg.
        """
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = output_video_path.parent / "temp_clips"
        temp_dir.mkdir(parents=True, exist_ok=True)

        clip_list = []
        audio_list = []
        audio_scenes_meta = []
        current_time = 0.0

        scenes = scene_data.get("scenes", [])
        print(f"[Composer] Rendering {len(scenes)} scenes into master video...")

        for idx, sc in enumerate(scenes, start=1):
            panel_name = sc.get("panel_name")
            panel_img = inpainted_dir / panel_name
            if not panel_img.exists():
                # Fallback search for any panel in directory
                panels = sorted([f for f in inpainted_dir.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
                panel_img = panels[(idx - 1) % len(panels)]

            narration = sc.get("narration", "")
            motion_type = sc.get("motion_type", "zoom_in")

            # 1. Synthesize audio clip for scene
            scene_audio_path = temp_dir / f"scene_{idx:03d}.wav"
            tts_engine.generate_speech(narration, scene_audio_path)
            duration = self.get_audio_duration(scene_audio_path)
            duration += 0.4

            # 2. Render motion clip for scene matching audio duration
            scene_video_path = temp_dir / f"scene_{idx:03d}.mp4"
            self.motion_gen.render_panel_clip(panel_img, scene_video_path, duration_sec=duration, motion_type=motion_type)

            clip_list.append(scene_video_path)
            audio_list.append(scene_audio_path)
            
            audio_scenes_meta.append({
                "narration": narration,
                "start_time": current_time,
                "duration": duration
            })
            current_time += duration

        # 3. Concatenate video clips and audio tracks using FFmpeg
        concat_txt = temp_dir / "concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in clip_list:
                f.write(f"file '{clip.resolve()}'\n")

        # Combine audio tracks into single master audio track
        master_audio = temp_dir / "master_audio.wav"
        self._combine_audio_files(audio_list, master_audio)

        # Concatenate raw video track
        temp_video_concat = temp_dir / "temp_raw_video.mp4"
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-c", "copy", str(temp_video_concat)
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Final muxing: Join video + audio
        cmd_mux = [
            "ffmpeg", "-y",
            "-i", str(temp_video_concat),
            "-i", str(master_audio),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_video_path)
        ]

        if ass_subtitle_path and Path(ass_subtitle_path).exists():
            ass_escaped = str(ass_subtitle_path.resolve()).replace(":", "\\:").replace("\\", "/")
            cmd_mux.extend(["-vf", f"subtitles={ass_escaped}"])

        res = subprocess.run(cmd_mux, capture_output=True, text=True)
        if res.returncode != 0:
            cmd_fallback = [
                "ffmpeg", "-y",
                "-i", str(temp_video_concat),
                "-i", str(master_audio),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                str(output_video_path)
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"[Composer] Recap video rendered successfully: {output_video_path}")
        return output_video_path

    def _combine_audio_files(self, audio_files: list, output_wav: Path):
        data_frames = []
        params = None
        for wav_path in audio_files:
            try:
                with wave.open(str(wav_path), "rb") as wf:
                    if params is None:
                        params = wf.getparams()
                    data_frames.append(wf.readframes(wf.getnframes()))
            except Exception as e:
                print(f"[Composer] Warning combining wave file {wav_path}: {e}")

        if params and data_frames:
            with wave.open(str(output_wav), "wb") as wf:
                wf.setparams(params)
                for frames in data_frames:
                    wf.writeframes(frames)

