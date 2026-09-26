# 🎬 AI Manhwa Recap YouTube Videos Engine

An end-to-end open-source AI engine built to run on Cloud GPUs (JarvisLabs NVIDIA L4 24GB or A100 40GB) to acquire Manhwa chapters, remove text bubbles, enhance panel resolution, generate 2.5D dynamic camera movement, synthesize human-like voiceovers, and assemble YouTube-ready recap videos optimized for **Copyright Avoidance** and **YouTube Monetization Compliance**.

---

## 🌟 Key Features

1. **Open-Source Manhwa Acquisition**: Async panel downloader and vertical strip slicer.
2. **AI Speech Bubble Inpainting**: Erases text, sound effects, and dialogue bubbles using **LaMa (Large Mask Inpainting)** and OpenCV.
3. **4K Visual Upscaling & 2.5D Motion**:
   - Super-sampling panel resolution via **Real-ESRGAN (Anime 4x)**.
   - Dynamic 2.5D Ken Burns pan-zoom, tilt, and depth-aware camera movement.
4. **Hyper-Realistic Human Voiceovers**:
   - Integrates state-of-the-art open-source TTS models: **Kokoro-82M**, **F5-TTS** (Zero-shot expressive cloning), and **ChatTTS**.
   - Natural human cadence, emotional inflections, and pauses.
5. **Recap Story Script Generator**: Rewrites raw chapter translations into high-retention YouTube narrative recaps.
6. **YouTube Monetization & Copyright Defense**:
   - Text bubble removal eliminates original translation font/dialogue copyright risks.
   - Transformative script rewriting adds human-value commentary satisfying YouTube's **Reused Content Policy**.
   - 2.5D camera motion, custom color grading, sound effects, and ASS animated subtitles.

---

## 🚀 Quick Setup & Installation

### 1. Local Environment or JarvisLabs Instance Setup

```bash
git clone https://github.com/your-username/manwha_recap.git
cd manwha_recap

# Install Python dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Verify System & Run Pytest Suite

```bash
pytest tests/test_pipeline.py
```

---

## 💻 Usage

### Option A: Command-Line Interface (CLI)

```bash
# 1. Run full automated pipeline on a chapter
python cli.py process --url "https://example-manhwa-site.com/chapter-1" --voice af_heart --output ./outputs/recap_ch1.mp4

# 2. Run offline demo (synthetic panels + inpainting + TTS + video render)
python cli.py process --chapter-name demo_solo_leveling --voice am_adam --output ./outputs/demo_recap.mp4
```

### Option B: Interactive Web Dashboard (Streamlit)

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to preview inpainting, edit narration scripts per panel, test voiceover audio, and export 1080p/4K 60fps recap videos interactively.

---

## ⚡ Cloud GPU (JarvisLabs) Setup Guide

| Recommended GPU | VRAM | Recommended Models & Config |
| :--- | :--- | :--- |
| **NVIDIA L4** | **24 GB** | Kokoro-82M TTS + LaMa Inpainter + Real-ESRGAN 2x + Qwen-2.5-7B |
| **NVIDIA A100** | **40 GB** | F5-TTS / ChatTTS Zero-shot + LaMa Inpainter + Real-ESRGAN 4x + Qwen-2.5-14B |

### Running on JarvisLabs:

1. Launch an instance with PyTorch 2.x and CUDA 12 image on JarvisLabs.
2. Clone repository and run `pip install -r requirements.txt`.
3. Launch Streamlit app: `streamlit run app.py --server.port 8501 --server.address 0.0.0.0`.
4. Access the web dashboard via JarvisLabs exposed HTTP endpoint.
