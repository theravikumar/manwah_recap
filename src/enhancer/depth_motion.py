import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class MotionGenerator:
    """Generates 2.5D dynamic camera movements (Ken Burns pan/zoom/tilt) on Manhwa panels."""
    def __init__(self, target_width: int = 1920, target_height: int = 1080, fps: int = 30):
        self.target_w = target_width
        self.target_h = target_height
        self.fps = fps

    def compute_crop_box(self, img_w: int, img_h: int, progress: float, motion_type: str = "zoom_in") -> tuple:
        """
        Calculates bounding box for cropping based on progress (0.0 to 1.0) and motion type.
        motion_type options: 'zoom_in', 'zoom_out', 'pan_down', 'pan_up', 'pan_right'
        """
        target_aspect = self.target_w / self.target_h
        img_aspect = img_w / img_h

        # Standard base cropping rectangle to match target aspect ratio
        if img_aspect > target_aspect:
            base_h = img_h
            base_w = int(img_h * target_aspect)
        else:
            base_w = img_w
            base_h = int(img_w / target_aspect)

        # Apply motion parameters
        if motion_type == "zoom_in":
            scale = 1.0 - (0.15 * progress) # 1.0 down to 0.85
            crop_w = int(base_w * scale)
            crop_h = int(base_h * scale)
            x1 = (img_w - crop_w) // 2
            y1 = (img_h - crop_h) // 2
        elif motion_type == "zoom_out":
            scale = 0.85 + (0.15 * progress)
            crop_w = int(base_w * scale)
            crop_h = int(base_h * scale)
            x1 = (img_w - crop_w) // 2
            y1 = (img_h - crop_h) // 2
        elif motion_type == "pan_down":
            scale = 0.85
            crop_w = int(base_w * scale)
            crop_h = int(base_h * scale)
            x1 = (img_w - crop_w) // 2
            max_y = img_h - crop_h
            y1 = int(max_y * progress)
        elif motion_type == "pan_up":
            scale = 0.85
            crop_w = int(base_w * scale)
            crop_h = int(base_h * scale)
            x1 = (img_w - crop_w) // 2
            max_y = img_h - crop_h
            y1 = int(max_y * (1.0 - progress))
        else: # pan_right
            scale = 0.85
            crop_w = int(base_w * scale)
            crop_h = int(base_h * scale)
            max_x = img_w - crop_w
            x1 = int(max_x * progress)
            y1 = (img_h - crop_h) // 2

        x2 = x1 + crop_w
        y2 = y1 + crop_h
        return max(0, x1), max(0, y1), min(img_w, x2), min(img_h, y2)

    def render_panel_clip(self, img_path: Path, output_video_path: Path, duration_sec: float = 5.0, motion_type: str = "zoom_in"):
        """Renders a single panel into a pan-zoom video clip."""
        img_path = Path(img_path)
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)

        img = cv2.imread(str(img_path))
        img_h, img_w, _ = img.shape

        total_frames = int(duration_sec * self.fps)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_video_path), fourcc, self.fps, (self.target_w, self.target_h))

        for f in range(total_frames):
            progress = f / float(max(1, total_frames - 1))
            x1, y1, x2, y2 = self.compute_crop_box(img_w, img_h, progress, motion_type=motion_type)
            
            crop = img[y1:y2, x1:x2]
            resized_frame = cv2.resize(crop, (self.target_w, self.target_h), interpolation=cv2.INTER_CUBIC)
            writer.write(resized_frame)

        writer.release()
        return output_video_path
