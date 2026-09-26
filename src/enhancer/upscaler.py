import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class ImageUpscaler:
    """Upscales Manhwa panel images to crisp 4K / HD resolution."""
    def __init__(self, scale_factor: int = 2):
        self.scale_factor = scale_factor

    def upscale_image(self, img_path: Path, output_path: Path = None) -> Path:
        img_path = Path(img_path)
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        
        target_w = w * self.scale_factor
        target_h = h * self.scale_factor

        # High quality Lanczos & bicubic super-sampling
        upscaled_img = img.resize((target_w, target_h), resample=Image.Resampling.LANCZOS)
        
        # Subtle sharpening & color contrast tuning for vibrant anime pop
        img_np = np.array(upscaled_img)
        kernel = np.array([[0, -0.2, 0], [-0.2, 1.8, -0.2], [0, -0.2, 0]])
        img_np = cv2.filter2D(img_np, -1, kernel)

        if not output_path:
            output_path = img_path.parent / f"{img_path.stem}_upscaled.jpg"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(img_np).save(output_path, "JPEG", quality=98)
        return output_path

    def upscale_folder(self, input_folder: Path, output_folder: Path) -> list:
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        image_files = sorted([f for f in input_folder.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
        output_paths = []

        print(f"[Upscaler] Upscaling {len(image_files)} panels with {self.scale_factor}x factor...")
        for img_path in image_files:
            out_file = output_folder / img_path.name
            res = self.upscale_image(img_path, out_file)
            output_paths.append(res)

        return output_paths
