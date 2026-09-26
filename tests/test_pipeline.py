import pytest
import os
import shutil
from pathlib import Path

from src.scraper import SampleGenerator
from src.inpainter import LaMaInpainter, TextBubbleDetector
from src.enhancer import ImageUpscaler, MotionGenerator
from src.script_engine import ScriptGenerator
from src.tts_engine import KokoroTTSEngine
from src.renderer import VideoComposer

TEMP_TEST_DIR = Path("./temp/pytest_env")

@pytest.fixture(scope="module")
def sample_chapter():
    if TEMP_TEST_DIR.exists():
        shutil.rmtree(TEMP_TEST_DIR)
    chap_dir = TEMP_TEST_DIR / "sample_raw"
    SampleGenerator.generate_sample_chapter(chap_dir, num_panels=2)
    yield chap_dir
    if TEMP_TEST_DIR.exists():
        shutil.rmtree(TEMP_TEST_DIR)

def test_sample_generator(sample_chapter):
    assert sample_chapter.exists()
    panels = list(sample_chapter.glob("*.jpg"))
    assert len(panels) == 2

def test_text_inpainting(sample_chapter):
    inpainter = LaMaInpainter(device="cpu")
    out_dir = TEMP_TEST_DIR / "inpainted"
    results = inpainter.inpaint_folder(sample_chapter, out_dir)
    assert len(results) == 2
    assert results[0].exists()

def test_image_upscaler(sample_chapter):
    upscaler = ImageUpscaler(scale_factor=2)
    out_dir = TEMP_TEST_DIR / "upscaled"
    results = upscaler.upscale_folder(sample_chapter, out_dir)
    assert len(results) == 2
    assert results[0].exists()

def test_script_generator(sample_chapter):
    gen = ScriptGenerator()
    script = gen.generate_script(sample_chapter)
    assert "scenes" in script
    assert len(script["scenes"]) >= 2

def test_tts_engine():
    tts = KokoroTTSEngine(voice="af_heart")
    out_wav = TEMP_TEST_DIR / "test_voice.wav"
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    res = tts.generate_speech("Testing human voiceover for manhwa recap engine.", out_wav)
    assert res.exists()
    assert res.stat().st_size > 0

def test_motion_generator(sample_chapter):
    motion = MotionGenerator(target_width=640, target_height=360, fps=15)
    img_path = list(sample_chapter.glob("*.jpg"))[0]
    out_mp4 = TEMP_TEST_DIR / "motion_clip.mp4"
    res = motion.render_panel_clip(img_path, out_mp4, duration_sec=1.5, motion_type="zoom_in")
    assert res.exists()
