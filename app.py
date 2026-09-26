import os
import streamlit as st
from pathlib import Path
from PIL import Image

from src.config import config
from src.scraper import SampleGenerator, ManhwaScraper
from src.inpainter import LaMaInpainter
from src.enhancer import ImageUpscaler
from src.script_engine import ScriptGenerator
from src.tts_engine import KokoroTTSEngine
from src.renderer import VideoComposer

st.set_page_config(page_title="AI Manhwa Recap Engine", page_icon="🎬", layout="wide")

st.title("🎬 AI Manhwa Recap YouTube Videos Engine")
st.markdown("Automated AI pipeline for fetching Manhwa, removing speech text, generating human-like voiceovers, and rendering 2.5D recap videos.")

# Sidebar Settings
st.sidebar.header("⚙️ GPU & Pipeline Settings")
voice = st.sidebar.selectbox("Human Voice Selection (TTS)", ["af_heart", "am_adam", "af_bella", "am_michael"], index=0)
upscale_factor = st.sidebar.slider("Image Upscale Factor", 1, 4, 2)
target_gpu = st.sidebar.selectbox("Cloud GPU Environment", ["NVIDIA L4 (24GB)", "NVIDIA A100 (40GB)"], index=0)

tab1, tab2, tab3 = st.tabs(["1. Acquisition & Inpainting", "2. Script & Voiceover", "3. Video Render & Export"])

temp_dir = Path(config.get("project", "temp_dir")) / "app_session"
raw_dir = temp_dir / "raw"
inpainted_dir = temp_dir / "inpainted"

with tab1:
    st.subheader("Chapter Downloader & AI Text Bubble Inpainting")
    col1, col2 = st.columns([3, 1])
    with col1:
        chapter_url = st.text_input("Manhwa Chapter URL (Leave blank to generate test sample):", "")
    with col2:
        st.write("")
        st.write("")
        btn_fetch = st.button("Fetch & Inpaint Panels", type="primary")

    if btn_fetch or raw_dir.exists():
        if btn_fetch:
            with st.spinner("Downloading chapter & running LaMa Inpainting..."):
                raw_dir.mkdir(parents=True, exist_ok=True)
                if not chapter_url:
                    SampleGenerator.generate_sample_chapter(raw_dir)
                else:
                    scraper = ManhwaScraper(output_dir=temp_dir)
                    import asyncio
                    asyncio.run(scraper.download_chapter(chapter_url, "raw"))
                
                inpainter = LaMaInpainter()
                inpainter.inpaint_folder(raw_dir, inpainted_dir)
                st.success("Panels processed successfully!")

        if inpainted_dir.exists():
            st.markdown("### 🖼️ Original vs. AI Inpainted Panels")
            raw_files = sorted([f for f in raw_dir.glob("*") if f.suffix.lower() in [".jpg", ".png", ".webp"]])
            inpaint_files = sorted([f for f in inpainted_dir.glob("*") if f.suffix.lower() in [".jpg", ".png", ".webp"]])

            for idx in range(min(len(raw_files), len(inpaint_files))):
                c1, c2 = st.columns(2)
                with c1:
                    st.image(str(raw_files[idx]), caption=f"Raw Panel #{idx+1}", use_container_width=True)
                with c2:
                    st.image(str(inpaint_files[idx]), caption=f"Inpainted Panel #{idx+1} (Text Removed)", use_container_width=True)

with tab2:
    st.subheader("Recap Story Script & Voiceover Preview")
    if not inpainted_dir.exists():
        st.warning("Please process panels in Tab 1 first.")
    else:
        script_gen = ScriptGenerator()
        script_data = script_gen.generate_script(raw_dir)
        
        st.markdown(f"**Title**: {script_data.get('title')}")
        
        edited_scenes = []
        for sc in script_data.get("scenes", []):
            st.markdown(f"#### Scene {sc['scene_id']} ({sc['panel_name']})")
            narration_text = st.text_area(f"Narration for Scene {sc['scene_id']}:", value=sc['narration'], key=f"nar_{sc['scene_id']}")
            motion = st.selectbox(f"Motion Effect:", ["zoom_in", "zoom_out", "pan_down", "pan_right"], index=0, key=f"mot_{sc['scene_id']}")
            
            if st.button(f"🔊 Preview Voiceover for Scene {sc['scene_id']}", key=f"btn_voice_{sc['scene_id']}"):
                with st.spinner("Synthesizing voice..."):
                    tts = KokoroTTSEngine(voice=voice)
                    preview_audio = temp_dir / f"preview_{sc['scene_id']}.wav"
                    tts.generate_speech(narration_text, preview_audio)
                    st.audio(str(preview_audio))
            
            edited_scenes.append({
                "scene_id": sc['scene_id'],
                "panel_name": sc['panel_name'],
                "narration": narration_text,
                "motion_type": motion
            })
        st.session_state['edited_script'] = {"title": script_data.get('title'), "scenes": edited_scenes}

with tab3:
    st.subheader("Render Final Recap Video")
    if not inpainted_dir.exists():
        st.warning("Please complete previous steps first.")
    else:
        if st.button("🚀 Render Recap Video (1080p 60fps)", type="primary"):
            with st.spinner("Rendering video clips, TTS audio & syncing subtitles..."):
                upscaler = ImageUpscaler(scale_factor=upscale_factor)
                upscaled_dir = temp_dir / "upscaled"
                upscaler.upscale_folder(inpainted_dir, upscaled_dir)

                script_data = st.session_state.get('edited_script', script_gen.generate_script(raw_dir))
                tts = KokoroTTSEngine(voice=voice)
                composer = VideoComposer()
                
                final_mp4 = Path(config.get("project", "output_dir")) / "app_recap_video.mp4"
                composer.render_full_recap(script_data, upscaled_dir, final_mp4, tts)
                
                st.success(f"Video exported to: {final_mp4}")
                st.video(str(final_mp4))
