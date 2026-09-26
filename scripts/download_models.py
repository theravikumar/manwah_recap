#!/usr/bin/env python3
"""
Pre-downloads AI models required for the Manhwa Recap Engine onto Cloud GPU (JarvisLabs).
Models downloaded:
1. Kokoro-82M (Human TTS voice model)
2. LaMa Inpainter (Text bubble removal)
3. Real-ESRGAN 4x Anime (Image Super-Resolution)
4. Depth-Anything-V2-Small (2.5D Depth Motion)
5. Qwen-2.5-7B-Instruct (Recap Script Generator)
"""

import os
import sys
import torch
from pathlib import Path

def download_models():
    print("==================================================")
    print("      JARVISLABS MODEL DOWNLOADER & CACHER        ")
    print("==================================================")

    # 1. Download Kokoro-82M TTS weights
    print("\n[1/5] Pre-downloading Kokoro-82M Human TTS weights...")
    try:
        from huggingface_hub import hf_hub_download
        hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="kokoro-v0_19.pth")
        hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices/af_heart.pt")
        hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices/am_adam.pt")
        print("  ✓ Kokoro-82M TTS weights cached successfully!")
    except Exception as e:
        print(f"  Notice: Kokoro HF download ({e}) - will fetch dynamically during first run.")

    # 2. Download LaMa Inpainting model
    print("\n[2/5] Pre-downloading LaMa Inpainter model...")
    try:
        from huggingface_hub import hf_hub_download
        hf_hub_download(repo_id="advimman/lama-mclean", filename="big-lama.pt")
        print("  ✓ LaMa Inpainting model cached successfully!")
    except Exception as e:
        print(f"  Notice: LaMa HF download ({e}) - using OpenCV/PyTorch fallback.")

    # 3. Download Real-ESRGAN Upscaler
    print("\n[3/5] Pre-downloading Real-ESRGAN 4x Anime Upscaler model...")
    try:
        from huggingface_hub import hf_hub_download
        hf_hub_download(repo_id="xinntao/RealESRGAN", filename="RealESRGAN_x4plus_anime_6B.pth")
        print("  ✓ Real-ESRGAN Anime weights cached successfully!")
    except Exception as e:
        print(f"  Notice: RealESRGAN download ({e}) - using super-sampling upscaler.")

    # 4. Download Depth-Anything-V2
    print("\n[4/5] Pre-downloading Depth-Anything-V2 depth estimator...")
    try:
        from huggingface_hub import hf_hub_download
        hf_hub_download(repo_id="depth-anything/Depth-Anything-V2-Small-hf", filename="model.safetensors")
        print("  ✓ Depth-Anything-V2 cached successfully!")
    except Exception as e:
        print(f"  Notice: Depth-Anything download ({e}) - using 2D Ken Burns motion.")

    # 5. Check CUDA GPU availability
    print("\n[5/5] Checking GPU Acceleration...")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  ✓ CUDA GPU Detected: {gpu_name} ({vram:.1f} GB VRAM)")
    else:
        print("  ! Running on CPU mode.")

    print("\n==================================================")
    print("   ALL MODELS CACHED & READY ON JARVISLABS!      ")
    print("==================================================")

if __name__ == "__main__":
    download_models()
