"""
Deep Statistical and Structural Analysis of Ingested Datasets
Stage 2 Analysis
"""

import sys
import json
import csv
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
MANIFEST_JSON = PROJECT_ROOT / "data" / "annotations" / "metadata" / "dataset_manifest.json"

with open(MANIFEST_JSON, 'r', encoding='utf-8') as f:
    records = json.load(f)

print(f"=== Total Records in Manifest: {len(records)} ===")

# Group by dataset
by_dataset = {}
for r in records:
    d = r["dataset"]
    by_dataset.setdefault(d, []).append(r)

for d, recs in by_dataset.items():
    print(f"\n--- Dataset: {d} ---")
    print(f"  Total Images: {len(recs)}")
    formats = {}
    modes = {}
    binarized_counts = {}
    widths, heights = [], []
    has_transcription = 0
    dup_count = 0
    
    for r in recs:
        fmt = r["image_format"]
        formats[fmt] = formats.get(fmt, 0) + 1
        m = r["color_mode"]
        modes[m] = modes.get(m, 0) + 1
        b = r["original_or_binarized"]
        binarized_counts[b] = binarized_counts.get(b, 0) + 1
        if isinstance(r["width"], int) and isinstance(r["height"], int):
            widths.append(r["width"])
            heights.append(r["height"])
        if r["transcription_available"]:
            has_transcription += 1
        if r["duplicate_group"] != "NONE":
            dup_count += 1
            
    print(f"  Formats: {formats}")
    print(f"  Color Modes: {modes}")
    print(f"  Modality: {binarized_counts}")
    if widths:
        print(f"  Dimensions: Width range [{min(widths)} - {max(widths)}], Height range [{min(heights)} - {max(heights)}]")
        print(f"  Sample Dimensions (First 3): {[(widths[i], heights[i]) for i in range(min(3, len(widths)))]}")
    print(f"  Transcriptions Available: {has_transcription} of {len(recs)}")
    print(f"  Duplicates in Duplicate Groups: {dup_count}")

# Check Duplicate Groups
dup_groups = {}
for r in records:
    dg = r["duplicate_group"]
    if dg != "NONE":
        dup_groups.setdefault(dg, []).append(r["image_path"])

print(f"\n=== Duplicate Groups Found: {len(dup_groups)} ===")
for g, paths in dup_groups.items():
    print(f"  {g} ({len(paths)} identical files): {paths}")

# Check for filename stem overlap across original and binarized
print("\n=== Checking Folio/Leaf Pairing (Original vs Binarized) ===")
for d, recs in by_dataset.items():
    if d == "CICT_Tirukkural":
        continue
    orig_stems = set()
    bin_stems = set()
    for r in recs:
        stem = Path(r["source_file"]).stem
        if r["original_or_binarized"] == "ORIGINAL_COLOR_GRAYSCALE":
            orig_stems.add(stem)
        elif r["original_or_binarized"] == "BINARIZED":
            bin_stems.add(stem)
    shared = orig_stems.intersection(bin_stems)
    print(f"  {d}: Original unique stems={len(orig_stems)}, Binarized unique stems={len(bin_stems)}, Shared paired stems={len(shared)}")
    if shared:
        print(f"    Sample shared pairs (folios present in both original & binarized): {sorted(list(shared))[:5]}")

# Verify CICT PAGE XML Details
print("\n=== CICT PAGE XML Deep Validation ===")
xml_path = PROJECT_ROOT / "CICT-PLM-GT-133.xml"
if xml_path.exists():
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15'}
    page = root.find('p:Page', ns)
    if page is not None:
        img_w = page.get('imageWidth')
        img_h = page.get('imageHeight')
        print(f"  PAGE XML declared size: {img_w} x {img_h}")
        regions = page.findall('p:TextRegion', ns)
        print(f"  Total Text Regions: {len(regions)}")
        total_lines = 0
        for r in regions:
            reg_id = r.get('id')
            reg_type = r.get('type')
            lines = r.findall('p:TextLine', ns)
            total_lines += len(lines)
            print(f"    Region '{reg_id}' (type={reg_type}): {len(lines)} lines")
            for l in lines:
                lid = l.get('id')
                coords = l.find('p:Coords', ns).get('points') if l.find('p:Coords', ns) is not None else "None"
                textequiv = l.find('p:TextEquiv/p:Unicode', ns)
                text = textequiv.text if textequiv is not None else ""
                print(f"      Line {lid}: text='{text}' | coords={coords}")
        print(f"  Total Ground Truth Lines in CICT GT-133: {total_lines}")
