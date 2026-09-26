import asyncio
import click
from pathlib import Path

from src.config import config
from src.scraper import ManhwaScraper, SampleGenerator
from src.inpainter import LaMaInpainter
from src.enhancer import ImageUpscaler, MotionGenerator
from src.script_engine import ScriptGenerator
from src.tts_engine import KokoroTTSEngine
from src.subtitle_engine import SubtitleAligner
from src.renderer import VideoComposer

@click.group()
def cli():
    """Manhwa Recap YouTube Videos Engine CLI"""
    pass

@cli.command()
@click.option("--url", default="", help="Manhwa chapter URL to scrape")
@click.option("--chapter-name", default="sample_chapter", help="Local directory name for scraped chapter")
def scrape(url, chapter_name):
    """Download Manhwa chapter panels or generate sample test chapter."""
    out_dir = Path(config.get("project", "temp_dir")) / "raw_chapters" / chapter_name
    if not url:
        click.echo("[CLI] No URL provided. Generating synthetic test chapter...")
        res_dir = SampleGenerator.generate_sample_chapter(out_dir)
    else:
        scraper = ManhwaScraper(output_dir=Path(config.get("project", "temp_dir")) / "raw_chapters")
        res_dir = asyncio.run(scraper.download_chapter(url, chapter_name))
    click.echo(f"[CLI] Chapter panels saved to: {res_dir}")

@cli.command()
@click.option("--input-dir", required=True, help="Input directory containing raw panel images")
@click.option("--output-dir", default="", help="Output directory for inpainted clean images")
def inpaint(input_dir, output_dir):
    """Remove speech bubbles and text from panel images using AI inpainting."""
    inp = Path(input_dir)
    out = Path(output_dir) if output_dir else inp.parent / f"{inp.name}_inpainted"
    inpainter = LaMaInpainter(device=config.get("hardware", "device"))
    res = inpainter.inpaint_folder(inp, out)
    click.echo(f"[CLI] Inpainted {len(res)} panels saved to: {out}")

@cli.command()
@click.option("--input-dir", required=True, help="Input directory containing inpainted panel images")
@click.option("--output-dir", default="", help="Output directory for upscaled images")
@click.option("--scale", default=2, help="Upscale factor (e.g. 2 for 2x, 4 for 4x)")
def enhance(input_dir, output_dir, scale):
    """Upscale and enhance panel resolution."""
    inp = Path(input_dir)
    out = Path(output_dir) if output_dir else inp.parent / f"{inp.name}_upscaled"
    upscaler = ImageUpscaler(scale_factor=scale)
    res = upscaler.upscale_folder(inp, out)
    click.echo(f"[CLI] Enhanced {len(res)} panels saved to: {out}")

@cli.command()
@click.option("--url", default="", help="Manhwa chapter URL")
@click.option("--chapter-name", default="solo_leveling_ch1", help="Chapter name identifier")
@click.option("--voice", default="af_heart", help="TTS voice selection (af_heart, am_adam, af_bella, am_michael)")
@click.option("--output", default="./outputs/final_recap.mp4", help="Path to output video file")
def process(url, chapter_name, voice, output):
    """Run full automated pipeline: Scrape -> Inpaint -> Enhance -> Script -> Voiceover -> Render."""
    click.echo("==================================================")
    click.echo("  AI MANHWA RECAP ENGINE - AUTOMATED PIPELINE   ")
    click.echo("==================================================")

    temp_base = Path(config.get("project", "temp_dir")) / chapter_name
    raw_dir = temp_base / "raw"
    inpainted_dir = temp_base / "inpainted"
    upscaled_dir = temp_base / "upscaled"

    # Step 1: Scrape / Generate panels
    click.echo("\n[Step 1/6] Acquiring Manhwa Chapter Panels...")
    if not url:
        SampleGenerator.generate_sample_chapter(raw_dir)
    else:
        scraper = ManhwaScraper(output_dir=temp_base)
        asyncio.run(scraper.download_chapter(url, "raw"))

    # Step 2: AI Bubble Inpainting
    click.echo("\n[Step 2/6] Erasing Speech Bubbles via AI Inpainting...")
    inpainter = LaMaInpainter(device=config.get("hardware", "device"))
    inpainter.inpaint_folder(raw_dir, inpainted_dir)

    # Step 3: Resolution Enhancement
    click.echo("\n[Step 3/6] Enhancing Panel Quality & Upscaling...")
    upscaler = ImageUpscaler(scale_factor=config.get("enhancer", "scale_factor", 2))
    upscaler.upscale_folder(inpainted_dir, upscaled_dir)

    # Step 4: Story Script Generation
    click.echo("\n[Step 4/6] Generating Recap Narrative Script...")
    script_gen = ScriptGenerator()
    script_data = script_gen.generate_script(raw_dir)

    # Step 5: Human Voiceover Synthesis
    click.echo(f"\n[Step 5/6] Synthesizing Human-like Voiceover (Voice: {voice})...")
    tts_engine = KokoroTTSEngine(voice=voice, speed=config.get("tts", "speed", 1.05))

    # Step 6: Audio-Visual Composition & Video Rendering
    click.echo("\n[Step 6/6] Rendering 2.5D Motion Video with Audio & Subtitles...")
    composer = VideoComposer(
        output_width=config.get("renderer", "width", 1920),
        output_height=config.get("renderer", "height", 1080),
        fps=config.get("renderer", "fps", 30)
    )
    
    out_video = Path(output)
    final_path = composer.render_full_recap(
        scene_data=script_data,
        inpainted_dir=upscaled_dir,
        output_video_path=out_video,
        tts_engine=tts_engine
    )

    click.echo("\n==================================================")
    click.echo(f" SUCCESS! Recap video ready: {final_path.resolve()}")
    click.echo("==================================================")

def main():
    cli()

if __name__ == "__main__":
    main()
