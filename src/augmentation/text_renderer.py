"""
Clean Tamil Text Line Renderer
Stage 7 Synthetic Data Engine

Renders authentic Tamil Unicode text into clean line images using PIL/Pillow.
Supports multiple Tamil Unicode fonts, dynamic margin calculation, and exact metadata tracking.
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from src.data.normalization import normalize_tamil_unicode


class TamilTextRenderer:
    def __init__(self, font_paths: Optional[List[str]] = None, default_font_size: int = 28):
        self.default_font_size = default_font_size
        self.fonts = self.discover_tamil_fonts(font_paths)
        if not self.fonts:
            raise RuntimeError("No usable Tamil Unicode font discovered on the host system.")

    @staticmethod
    def discover_tamil_fonts(custom_paths: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Discovers installed Tamil Unicode fonts on Windows/Linux or local font directories.
        """
        found = []
        candidates = []

        if custom_paths:
            candidates.extend(custom_paths)

        # Standard Windows fonts
        windows_font_dir = Path("C:/Windows/Fonts")
        if windows_font_dir.exists():
            candidates.extend([
                str(windows_font_dir / "Nirmala.ttc"),
                str(windows_font_dir / "Latha.ttf"),
                str(windows_font_dir / "Vijaya.ttf")
            ])
            # Wildcard search
            for p in glob.glob("C:/Windows/Fonts/*tamil*") + glob.glob("C:/Windows/Fonts/*nirmala*"):
                if p not in candidates:
                    candidates.append(p)

        # Local project fonts
        project_font_dir = Path("data/fonts")
        if project_font_dir.exists():
            for p in glob.glob("data/fonts/*.ttf") + glob.glob("data/fonts/*.otf") + glob.glob("data/fonts/*.ttc"):
                candidates.append(p)

        # Validate that the font can render a sample Tamil character
        test_str = "தமிழ்"
        for cp in candidates:
            if not os.path.exists(cp):
                continue
            try:
                f = ImageFont.truetype(cp, 24)
                # Test render
                test_img = Image.new("RGB", (100, 50), (255, 255, 255))
                draw = ImageDraw.Draw(test_img)
                draw.text((10, 10), test_str, font=f, fill=(0, 0, 0))
                
                fname = Path(cp).stem
                found.append({
                    "font_name": fname,
                    "font_path": str(Path(cp).resolve()),
                    "font_type": Path(cp).suffix.lower()
                })
            except Exception:
                continue

        return found

    def render_line(
        self,
        text: str,
        font_name_or_path: Optional[str] = None,
        font_size: Optional[int] = None,
        padding_x: int = 24,
        padding_y: int = 8,
        bg_color: Tuple[int, int, int] = (255, 255, 255),
        text_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> Tuple[Image.Image, Dict[str, any]]:
        """
        Renders a single line of Tamil Unicode text into an RGB PIL Image.
        
        Returns:
            (PIL Image, metadata_dict)
        """
        norm_text = normalize_tamil_unicode(text)
        size = font_size or self.default_font_size

        # Select font
        selected_font_info = None
        if font_name_or_path:
            for f in self.fonts:
                if f["font_name"].lower() == font_name_or_path.lower() or f["font_path"] == font_name_or_path:
                    selected_font_info = f
                    break
        if not selected_font_info:
            selected_font_info = self.fonts[0]

        font = ImageFont.truetype(selected_font_info["font_path"], size)

        # Measure text dimensions using getbbox
        dummy_img = Image.new("RGB", (10, 10))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), norm_text, font=font)
        
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        img_w = text_w + (2 * padding_x)
        img_h = max(40, text_h + (2 * padding_y))

        # Render image
        img = Image.new("RGB", (img_w, img_h), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Position text centered vertically with horizontal padding
        draw_x = padding_x - bbox[0]
        draw_y = padding_y - bbox[1]
        draw.text((draw_x, draw_y), norm_text, font=font, fill=text_color)

        meta = {
            "text": norm_text,
            "raw_text": text,
            "font_name": selected_font_info["font_name"],
            "font_path": selected_font_info["font_path"],
            "font_size": size,
            "image_width": img_w,
            "image_height": img_h,
            "text_width": text_w,
            "text_height": text_h,
            "padding_x": padding_x,
            "padding_y": padding_y
        }

        return img, meta
