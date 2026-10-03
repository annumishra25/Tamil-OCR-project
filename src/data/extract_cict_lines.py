"""
Extract Gold-Standard Line Crops from CICT-PLM-GT-133 PAGE XML
Stage 3 Ground Truth Preparation
"""

import sys
import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
CICT_IMG_PATH = PROJECT_ROOT / "data" / "raw" / "cict" / "CICT-PLM-GT-133.jpg"
CICT_XML_PATH = PROJECT_ROOT / "data" / "raw" / "cict" / "CICT-PLM-GT-133.xml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines"
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines.csv"

def parse_points(points_str):
    # e.g., "359,30 2499,30 2499,67 359,67"
    pts = []
    for pair in points_str.strip().split():
        if "," in pair:
            x, y = map(int, pair.split(","))
            pts.append((x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return min_x, min_y, max_x, max_y, pts

def extract_lines():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CICT_IMG_PATH.exists():
        print(f"Error: {CICT_IMG_PATH} not found!")
        return []
    if not CICT_XML_PATH.exists():
        print(f"Error: {CICT_XML_PATH} not found!")
        return []

    print(f"Opening CICT image: {CICT_IMG_PATH}")
    full_img = Image.open(CICT_IMG_PATH).convert("RGB")
    img_w, img_h = full_img.size
    print(f"Full Image Size: {img_w} x {img_h}")

    tree = ET.parse(CICT_XML_PATH)
    root = tree.getroot()
    ns = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15'}

    lines_metadata = []
    line_idx = 1

    regions = root.findall('.//p:TextRegion', ns)
    for r in regions:
        reg_id = r.get('id', 'unknown_region')
        reg_type = r.get('type', 'paragraph')
        text_lines = r.findall('p:TextLine', ns)

        for tl in text_lines:
            lid = tl.get('id')
            coords_el = tl.find('p:Coords', ns)
            if coords_el is None or 'points' not in coords_el.attrib:
                continue
            
            pts_str = coords_el.attrib['points']
            min_x, min_y, max_x, max_y, pts = parse_points(pts_str)
            
            # Baseline if present
            baseline_el = tl.find('p:Baseline', ns)
            baseline_pts = baseline_el.attrib.get('points', '') if baseline_el is not None else ''

            # Unicode ground truth text
            txt_el = tl.find('p:TextEquiv/p:Unicode', ns)
            unicode_text = txt_el.text if txt_el is not None and txt_el.text else ""

            # Ensure coordinates within image bounds
            min_x = max(0, min_x)
            min_y = max(0, min_y)
            max_x = min(img_w, max_x)
            max_y = min(img_h, max_y)

            # Crop sub-image
            crop_img = full_img.crop((min_x, min_y, max_x, max_y))
            out_filename = f"line_{line_idx:03d}_{lid}.png"
            out_path = OUTPUT_DIR / out_filename
            crop_img.save(out_path, format="PNG")

            rec = {
                "line_index": line_idx,
                "line_id": lid,
                "region_id": reg_id,
                "line_type": reg_type,
                "image_filename": out_filename,
                "image_path": out_path.relative_to(PROJECT_ROOT).as_posix(),
                "crop_width": crop_img.width,
                "crop_height": crop_img.height,
                "bbox_x": min_x,
                "bbox_y": min_y,
                "bbox_width": max_x - min_x,
                "bbox_height": max_y - min_y,
                "polygon_points": pts_str,
                "baseline_points": baseline_pts,
                "transcription": unicode_text,
                "source_folio": "CICT_20217_135_GT133",
                "split_status": "GOLD_EVALUATION_BENCHMARK"
            }
            lines_metadata.append(rec)
            print(f"[{line_idx:02d}] {lid} ({reg_type}): size={crop_img.size}, text='{unicode_text}' -> {out_filename}")
            line_idx += 1

    # Save to CSV
    if lines_metadata:
        keys = list(lines_metadata[0].keys())
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(lines_metadata)
        print(f"\nGenerated {CSV_PATH} with {len(lines_metadata)} gold-standard lines!")

    return lines_metadata

if __name__ == "__main__":
    extract_lines()
