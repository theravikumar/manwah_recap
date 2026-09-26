import os
import re
import asyncio
import httpx
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class ManhwaScraper:
    """Async scraper to download Manhwa chapter pages and slice webtoons into panels."""
    def __init__(self, output_dir: str = "./temp/raw_chapters", user_agent: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def fetch_chapter_images(self, chapter_url: str) -> list:
        """Fetch image URLs from a chapter page."""
        image_urls = []
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0) as client:
                res = await client.get(chapter_url)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # Generic selector for common manga/webtoon readers
                    for img in soup.find_all("img"):
                        src = img.get("data-src") or img.get("src") or img.get("data-original")
                        if src and any(ext in src.lower() for ext in [".png", ".jpg", ".jpeg", ".webp"]):
                            if src.startswith("//"):
                                src = "https:" + src
                            image_urls.append(src)
        except Exception as e:
            print(f"[Scraper] Warning: Failed to scrape {chapter_url}: {e}")
        return image_urls

    async def download_chapter(self, chapter_url: str, chapter_name: str = "chapter_01") -> Path:
        """Download images for a chapter and return local folder path."""
        chap_dir = self.output_dir / chapter_name
        chap_dir.mkdir(parents=True, exist_ok=True)
        
        urls = await self.fetch_chapter_images(chapter_url)
        if not urls:
            print(f"[Scraper] No remote images found. Generating sample panel set in {chap_dir}...")
            return SampleGenerator.generate_sample_chapter(chap_dir)

        print(f"[Scraper] Found {len(urls)} images. Downloading to {chap_dir}...")
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            for idx, url in enumerate(urls, start=1):
                try:
                    res = await client.get(url)
                    if res.status_code == 200:
                        ext = url.split(".")[-1].split("?")[0]
                        if ext not in ["jpg", "jpeg", "png", "webp"]:
                            ext = "jpg"
                        save_path = chap_dir / f"panel_{idx:03d}.{ext}"
                        with open(save_path, "wb") as f:
                            f.write(res.content)
                except Exception as e:
                    print(f"[Scraper] Error downloading image {idx} ({url}): {e}")
        
        # Split vertical webtoon strips if present
        self.slice_vertical_strips(chap_dir)
        return chap_dir

    def slice_vertical_strips(self, chapter_dir: Path, max_panel_height: int = 1600):
        """Slices long vertical webtoon strips into discrete panel frames."""
        image_files = sorted([f for f in chapter_dir.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
        sliced_count = 0
        for img_path in image_files:
            try:
                with Image.open(img_path) as img:
                    w, h = img.size
                    if h > max_panel_height:
                        # Slice into chunks
                        num_chunks = int(np.ceil(h / max_panel_height))
                        chunk_h = h // num_chunks
                        for i in range(num_chunks):
                            box = (0, i * chunk_h, w, min((i + 1) * chunk_h, h))
                            crop_img = img.crop(box)
                            out_name = chapter_dir / f"{img_path.stem}_part_{i+1:02d}.jpg"
                            crop_img.save(out_name, "JPEG", quality=95)
                        sliced_count += 1
                        img_path.unlink() # remove original strip
            except Exception as e:
                print(f"[Scraper] Error slicing strip {img_path}: {e}")


class SampleGenerator:
    """Generates synthetic Manhwa panel images with speech bubbles for offline testing and verification."""
    @staticmethod
    def generate_sample_chapter(output_dir: Path, num_panels: int = 4) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        colors = [
            (240, 240, 245), # Light silver background
            (230, 240, 250), # Light blue tint
            (250, 240, 230), # Warm peach tint
            (235, 235, 240)  # Neutral background
        ]
        
        narrations = [
            "In a world dominated by shadow hunters, Sung Jinwoo was known as the weakest of all.",
            "Surrounded by rank-S monsters inside the double dungeon, despair took over.",
            "Suddenly, a glowing blue quest window appeared right before his eyes!",
            "Welcome Player. You have unlocked the System of the Shadow Monarch."
        ]
        
        dialogues = [
            ("Wait... is that a hidden door?!", (250, 180)),
            ("Run! It's a high rank statue monster!", (220, 250)),
            ("I won't die here... I will become stronger!", (200, 300)),
            ("Arise... my shadows!", (280, 220))
        ]

        for i in range(num_panels):
            img_w, img_h = 1080, 1440
            img = Image.new("RGB", (img_w, img_h), colors[i % len(colors)])
            draw = ImageDraw.Draw(img)

            # Draw action background elements (manga speed lines / shapes)
            for line in range(0, img_h, 40):
                draw.line([(0, line), (img_w, line + 100)], fill=(210, 210, 220), width=2)

            # Draw character outline box / shadow
            char_box = (250, 400, 830, 1200)
            draw.rectangle(char_box, fill=(70, 80, 120), outline=(20, 20, 40), width=5)
            draw.text((380, 750), f"[ MANHWA CHARACTER #{i+1} ]", fill=(255, 255, 255))

            # Draw speech bubble (White oval with black outline)
            text, pos = dialogues[i % len(dialogues)]
            bubble_box = (pos[0] - 20, pos[1] - 20, pos[0] + 620, pos[1] + 160)
            draw.ellipse(bubble_box, fill=(255, 255, 255), outline=(0, 0, 0), width=4)
            # Bubble tail
            draw.polygon([(pos[0] + 150, pos[1] + 150), (pos[0] + 180, pos[1] + 210), (pos[0] + 220, pos[1] + 150)], fill=(255, 255, 255), outline=(0, 0, 0))

            # Text inside bubble
            draw.text((pos[0] + 30, pos[1] + 45), text, fill=(0, 0, 0))

            # Save sample panel
            out_file = output_dir / f"panel_{i+1:03d}.jpg"
            img.save(out_file, "JPEG", quality=95)
            
            # Save associated narration metadata file
            meta_file = output_dir / f"panel_{i+1:03d}.txt"
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(narrations[i % len(narrations)])

        return output_dir
