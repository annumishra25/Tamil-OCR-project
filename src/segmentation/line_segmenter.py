"""
Tamil Palm-Leaf Line and Text-Region Segmentation Engine
Stage 5 Classical Computer Vision Segmenter
"""

import sys
import os
import math
import numpy as np
import cv2
from pathlib import Path
from scipy.signal import find_peaks
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

from src.preprocessing.filters import to_grayscale, enhance_contrast_clahe, correct_illumination, threshold_sauvola

class PalmLeafLineSegmenter:
    def __init__(self,
                 expected_line_height: int = 35,
                 min_line_height: int = 15,
                 max_line_height: int = 70,
                 horizontal_padding: int = 10,
                 vertical_padding: int = 4):
        self.expected_line_height = expected_line_height
        self.min_line_height = min_line_height
        self.max_line_height = max_line_height
        self.horizontal_padding = horizontal_padding
        self.vertical_padding = vertical_padding

    def segment_horizontal_projection(self, img_input, prep_variant: str = "clahe") -> tuple[list[dict], np.ndarray]:
        """
        Segment horizontal text lines using peak-and-valley analysis on Gaussian-smoothed Horizontal Projection Profiles.
        """
        if isinstance(img_input, (str, Path)):
            img = cv2.imread(str(img_input))
            if img is None:
                raise ValueError(f"Could not load image: {img_input}")
        elif isinstance(img_input, np.ndarray):
            img = img_input.copy()
        else:
            raise TypeError("img_input must be a file path or numpy array")

        h, w = img.shape[:2]
        gray = to_grayscale(img)

        # Apply preprocessing suitable for horizontal band extraction
        if prep_variant == "illum_clahe":
            norm = correct_illumination(gray)
            prep = enhance_contrast_clahe(norm, clip_limit=2.5)
        elif prep_variant == "clahe":
            prep = enhance_contrast_clahe(gray, clip_limit=2.5)
        elif prep_variant == "sauvola":
            clahe = enhance_contrast_clahe(gray, clip_limit=2.0)
            prep = threshold_sauvola(clahe, window_size=25, k=0.2)
        else:
            prep = gray

        # Binarization for projection profile
        if prep_variant != "sauvola":
            _, bw = cv2.threshold(prep, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            bw = cv2.bitwise_not(prep)

        # Horizontal Projection Profile
        hpp = np.sum(bw, axis=1) / 255.0

        # Gaussian smoothing on 1D projection profile to extract clean peaks & valleys
        sigma = max(2.0, h / 100.0)
        k_size = int(math.ceil(sigma * 4)) | 1
        smoothed = cv2.GaussianBlur(hpp.reshape(-1, 1), (1, k_size), sigma).flatten()

        # Find valley local minima (inter-line boundaries)
        min_dist = max(18, int(self.expected_line_height * 0.7))
        valleys, _ = find_peaks(-smoothed, distance=min_dist)

        # Build line intervals from valleys
        cuts = [0] + sorted(list(valleys)) + [h]
        raw_bands = []
        for i in range(len(cuts) - 1):
            s_y = cuts[i]
            e_y = cuts[i + 1]
            band_h = e_y - s_y
            
            # Check if band has substantial text content (peak amplitude)
            band_hpp = hpp[s_y:e_y]
            if len(band_hpp) > 0 and np.max(band_hpp) > (0.10 * w):
                if self.min_line_height <= band_h <= self.max_line_height:
                    raw_bands.append((s_y, e_y))
                elif band_h > self.max_line_height:
                    # Subdivide excessively large band
                    sub_count = max(2, round(band_h / self.expected_line_height))
                    sub_h = band_h // sub_count
                    for k in range(sub_count):
                        sub_s = s_y + k * sub_h
                        sub_e = min(e_y, sub_s + sub_h)
                        if self.min_line_height <= (sub_e - sub_s):
                            raw_bands.append((sub_s, sub_e))

        # Convert bands to full line bounding boxes with horizontal extent detection
        lines = []
        for idx, (sy, ey) in enumerate(raw_bands, start=1):
            band_mask = bw[sy:ey, :]
            vpp = np.sum(band_mask, axis=0)
            active_cols = np.where(vpp > 0)[0]
            
            if len(active_cols) > 0:
                min_x = max(0, int(active_cols[0]) - self.horizontal_padding)
                max_x = min(w, int(active_cols[-1]) + self.horizontal_padding)
            else:
                min_x = 0
                max_x = w

            padded_sy = max(0, sy - self.vertical_padding)
            padded_ey = min(h, ey + self.vertical_padding)
            line_w = max_x - min_x
            line_h = padded_ey - padded_sy

            aspect = round(line_w / (line_h + 1e-5), 2)

            status = "OCR_READY"
            if line_w < 50 or line_h < 10:
                status = "TOO_SMALL"
            elif aspect > 85.0:
                status = "EXTREME_ASPECT_RATIO"

            line_entry = {
                "reading_order": idx,
                "line_id": f"AUTO_LINE_{idx:03d}",
                "bbox": {"x": min_x, "y": padded_sy, "w": line_w, "h": line_h},
                "polygon": [[min_x, padded_sy], [max_x, padded_sy], [max_x, padded_ey], [min_x, padded_ey]],
                "aspect_ratio": aspect,
                "status": status,
                "segmentation_method": "Horizontal_Projection_Profile_Valley_Analysis",
                "manual_review_required": status != "OCR_READY"
            }
            lines.append(line_entry)

        return lines, prep

    def crop_lines(self, img_input, lines: list[dict], output_dir: Path, prefix: str = "line") -> list[dict]:
        output_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(img_input, (str, Path)):
            img = cv2.imread(str(img_input))
        else:
            img = img_input

        cropped_records = []
        for ln in lines:
            bx = ln["bbox"]
            x, y, w, h = bx["x"], bx["y"], bx["w"], bx["h"]
            crop = img[y:y+h, x:x+w]
            
            filename = f"{prefix}_{ln['reading_order']:03d}_{ln['line_id']}.png"
            out_path = output_dir / filename
            cv2.imwrite(str(out_path), crop)
            
            rec = ln.copy()
            rec["crop_filename"] = filename
            try:
                rec["crop_path"] = str(out_path.relative_to(PROJECT_ROOT).as_posix())
            except ValueError:
                rec["crop_path"] = str(out_path.as_posix())
            rec["crop_width"] = crop.shape[1]
            rec["crop_height"] = crop.shape[0]
            cropped_records.append(rec)

        return cropped_records

    def draw_segmentation_overlay(self, img_input, lines: list[dict], output_path: Path, title: str = ""):
        if isinstance(img_input, (str, Path)):
            img = cv2.imread(str(img_input))
        else:
            img = img_input.copy()

        overlay = img.copy()
        for ln in lines:
            bx = ln["bbox"]
            x, y, w, h = bx["x"], bx["y"], bx["w"], bx["h"]
            ro = ln.get("reading_order", 0)
            status = ln.get("status", "OCR_READY")

            color = (55, 175, 212) if status == "OCR_READY" else (43, 66, 217)
            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
            
            badge_w = 40
            badge_h = min(h, 24)
            cv2.rectangle(overlay, (x, y), (x + badge_w, y + badge_h), (26, 22, 19), -1)
            cv2.rectangle(overlay, (x, y), (x + badge_w, y + badge_h), color, 1)
            cv2.putText(overlay, f"#{ro}", (x + 6, y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        blended = cv2.addWeighted(overlay, 0.85, img, 0.15, 0)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), blended)
        print(f"Saved segmentation overlay: {output_path}")
