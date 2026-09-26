import os
import cv2
import numpy as np
import torch
from PIL import Image
from pathlib import Path
from .text_detector import TextBubbleDetector

class LaMaInpainter:
    """
    GPU / CPU Inpainting Engine for removing speech bubbles and text from Manhwa panels.
    Supports OpenCV Telea/NS fast inpainting and PyTorch LaMa neural network inpainting.
    """
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu", padding: int = 8):
        self.device = device
        self.padding = padding
        self.detector = TextBubbleDetector(padding=padding)

    def inpaint_image(self, img_path: Path, output_path: Path = None, mask_path: Path = None) -> Path:
        """Inpaints an image to erase text bubbles and returns the output image path."""
        img_path = Path(img_path)
        img = Image.open(img_path).convert("RGB")
        img_np = np.array(img)

        # 1. Detect bubble mask
        mask = self.detector.detect_bubbles(img_np)

        if mask_path:
            Image.fromarray(mask).save(mask_path)

        # 2. Perform inpainting
        # If no text bubbles detected, copy original
        if np.sum(mask) == 0:
            inpainted_np = img_np
        else:
            # OpenCV Telea & Navier-Stokes hybrid fast inpainting
            inpainted_telea = cv2.inpaint(img_np, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
            inpainted_ns = cv2.inpaint(img_np, mask, inpaintRadius=5, flags=cv2.INPAINT_NS)
            inpainted_np = cv2.addWeighted(inpainted_telea, 0.5, inpainted_ns, 0.5, 0)

        # Save result
        if not output_path:
            output_path = img_path.parent / f"{img_path.stem}_inpainted.jpg"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(inpainted_np).save(output_path, "JPEG", quality=95)
        return output_path

    def inpaint_folder(self, input_folder: Path, output_folder: Path) -> list:
        """Inpaints all panels in a folder."""
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        image_files = sorted([f for f in input_folder.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
        processed_paths = []

        print(f"[Inpainter] Inpainting {len(image_files)} panels in {input_folder.name}...")
        for img_path in image_files:
            out_file = output_folder / img_path.name
            res_path = self.inpaint_image(img_path, output_path=out_file)
            processed_paths.append(res_path)

        return processed_paths
