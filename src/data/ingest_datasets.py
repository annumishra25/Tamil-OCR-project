"""
Dataset Ingestion, Verification, and Manifest Generation for Tamil Palm-Leaf OCR
Stage 2 Pipeline
"""

import os
import sys
import json
import csv
import hashlib
import zipfile
import shutil
import urllib.request
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_ANNOTATIONS = PROJECT_ROOT / "data" / "annotations"
METADATA_DIR = DATA_ANNOTATIONS / "metadata"

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def ensure_dirs():
    (DATA_RAW / "thplmd").mkdir(parents=True, exist_ok=True)
    (DATA_RAW / "cict").mkdir(parents=True, exist_ok=True)
    (DATA_RAW / "iiit_tamil").mkdir(parents=True, exist_ok=True)
    (DATA_PROCESSED / "staging" / "thplmd").mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

def copy_raw_archives_and_meta():
    print("--- 1. Copying Raw Source Files into data/raw/ (Immutable Archive Copies) ---")
    archives = [
        "Naladiyar.zip",
        "THIRIKADUGAM.zip",
        "THOLKAPPIYAM BINARIZED - (2).zip"
    ]
    for arch in archives:
        src = PROJECT_ROOT / arch
        dst = DATA_RAW / "thplmd" / arch
        if src.exists() and not dst.exists():
            print(f"Copying {src.name} -> {dst}")
            shutil.copy2(src, dst)
        elif dst.exists():
            print(f"Archive copy already exists at {dst}")

    # Copy CICT metadata
    for cict_file in ["CICT-PLM-GT-133.json", "CICT-PLM-GT-133.xml"]:
        src = PROJECT_ROOT / cict_file
        dst = DATA_RAW / "cict" / cict_file
        if src.exists() and not dst.exists():
            print(f"Copying {src.name} -> {dst}")
            shutil.copy2(src, dst)
        elif dst.exists():
            print(f"CICT file already exists at {dst}")

def extract_archives_to_staging():
    print("\n--- 2. Extracting Archives to data/processed/staging/thplmd/ ---")
    staging_base = DATA_PROCESSED / "staging" / "thplmd"
    
    # 1. Naladiyar
    naladiyar_zip = PROJECT_ROOT / "Naladiyar.zip"
    naladiyar_out = staging_base / "naladiyar"
    if naladiyar_zip.exists():
        print(f"Extracting {naladiyar_zip.name} -> {naladiyar_out}")
        with zipfile.ZipFile(naladiyar_zip, 'r') as zf:
            zf.extractall(naladiyar_out)

    # 2. THIRIKADUGAM
    thirikadugam_zip = PROJECT_ROOT / "THIRIKADUGAM.zip"
    thirikadugam_out = staging_base / "thirikadugam"
    if thirikadugam_zip.exists():
        print(f"Extracting {thirikadugam_zip.name} -> {thirikadugam_out}")
        with zipfile.ZipFile(thirikadugam_zip, 'r') as zf:
            zf.extractall(thirikadugam_out)

    # 3. THOLKAPPIYAM
    tholkappiyam_zip = PROJECT_ROOT / "THOLKAPPIYAM BINARIZED - (2).zip"
    tholkappiyam_out = staging_base / "tholkappiyam"
    if tholkappiyam_zip.exists():
        print(f"Extracting {tholkappiyam_zip.name} -> {tholkappiyam_out}")
        with zipfile.ZipFile(tholkappiyam_zip, 'r') as zf:
            zf.extractall(tholkappiyam_out)

def download_cict_gt_image():
    print("\n--- 3. Fetching CICT GT-133 Reference Image from Zenodo IIIF ---")
    cict_raw = DATA_RAW / "cict"
    target_img = cict_raw / "CICT-PLM-GT-133.jpg"
    
    # Check JSON for URL
    json_path = PROJECT_ROOT / "CICT-PLM-GT-133.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            cict_meta = json.load(f)
        full_res_url = cict_meta.get("image", {}).get("fullResolution")
        fallback_url = cict_meta.get("image", {}).get("filename")
        
        if not target_img.exists() and (full_res_url or fallback_url):
            url_to_try = full_res_url or fallback_url
            print(f"Attempting download from Zenodo IIIF: {url_to_try}")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                req = urllib.request.Request(url_to_try, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp, open(target_img, 'wb') as out_f:
                    shutil.copyfileobj(resp, out_f)
                print(f"Successfully downloaded CICT image ({target_img.stat().st_size} bytes)")
            except Exception as e:
                print(f"Notice: Could not fetch from primary IIIF URL ({e}). Trying fallback...")
                if fallback_url and fallback_url != url_to_try:
                    try:
                        req = urllib.request.Request(fallback_url, headers=headers)
                        with urllib.request.urlopen(req, timeout=30) as resp, open(target_img, 'wb') as out_f:
                            shutil.copyfileobj(resp, out_f)
                        print(f"Successfully downloaded CICT image from fallback ({target_img.stat().st_size} bytes)")
                    except Exception as e2:
                        print(f"Fallback download failed: {e2}")
        elif target_img.exists():
            print(f"CICT reference image already present at {target_img}")
    else:
        print("CICT-PLM-GT-133.json not found.")

def analyze_all_and_build_manifest():
    print("\n--- 4. Comprehensive Dataset Analysis & Manifest Formulation ---")
    manifest_records = []
    
    # Track hashes to detect duplicates and identical files
    hash_to_files = {}

    # Inspect Staging Directory
    staging_base = DATA_PROCESSED / "staging" / "thplmd"
    
    for root, dirs, files in os.walk(staging_base):
        for fname in files:
            fpath = Path(root) / fname
            # Skip nested zip archives if any
            if fname.lower().endswith(".zip"):
                continue
            
            ext = fpath.suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]:
                continue

            # Determine dataset and collection
            rel_path = fpath.relative_to(PROJECT_ROOT).as_posix()
            file_size = fpath.stat().st_size
            sha = compute_sha256(fpath)

            if sha not in hash_to_files:
                hash_to_files[sha] = []
            hash_to_files[sha].append(rel_path)

            # Image metadata via PIL
            width, height, mode, format_name = None, None, None, None
            try:
                with Image.open(fpath) as img:
                    width, height = img.size
                    mode = img.mode
                    format_name = img.format
            except Exception as e:
                print(f"Error opening image {fpath}: {e}")

            # Classify collection and modality
            col_name = "THPLMD"
            source_arch = "UNKNOWN"
            is_binarized = "UNKNOWN"
            
            if "naladiyar" in rel_path.lower():
                col_name = "THPLMD_Naladiyar"
                source_arch = "Naladiyar.zip"
                if "binarized" in rel_path.lower():
                    is_binarized = "BINARIZED"
                elif "original" in rel_path.lower():
                    is_binarized = "ORIGINAL_COLOR_GRAYSCALE"
            elif "thirikadugam" in rel_path.lower():
                col_name = "THPLMD_Thirikadugam"
                source_arch = "THIRIKADUGAM.zip"
                if "binarized" in rel_path.lower():
                    is_binarized = "BINARIZED"
                elif "origianal" in rel_path.lower() or "original" in rel_path.lower():
                    is_binarized = "ORIGINAL_COLOR_GRAYSCALE"
            elif "tholkappiyam" in rel_path.lower():
                col_name = "THPLMD_Tholkappiyam"
                source_arch = "THOLKAPPIYAM BINARIZED - (2).zip"
                is_binarized = "BINARIZED"

            image_id = f"{col_name}_{Path(fname).stem}"

            record = {
                "dataset": col_name,
                "source_archive": source_arch,
                "source_file": fname,
                "image_id": image_id,
                "image_path": rel_path,
                "image_format": format_name or ext.replace(".", "").upper(),
                "width": width or "UNKNOWN",
                "height": height or "UNKNOWN",
                "color_mode": mode or "UNKNOWN",
                "file_size_bytes": file_size,
                "sha256": sha,
                "level": "PAGE_OR_FOLIO",
                "original_or_binarized": is_binarized,
                "label_available": False,
                "label_type": "NONE",
                "transcription_available": False,
                "transcription_path": "NONE",
                "unicode_text_available": False,
                "annotation_available": False,
                "annotation_format": "NONE",
                "license": "Research Use / Non-Commercial",
                "source_url": "THPLMD Kaggle / Open Repository",
                "duplicate_group": "NONE",
                "classification_category": "IMAGE_ONLY",
                "usable_for_training": False, # Requires transcription for supervised OCR
                "usable_for_evaluation": False, # Requires ground truth
                "notes": "Palm-leaf manuscript image without aligned transcription in archive."
            }
            manifest_records.append(record)

    # Inspect CICT Ground Truth
    cict_raw = DATA_RAW / "cict"
    cict_json = PROJECT_ROOT / "CICT-PLM-GT-133.json"
    cict_xml = PROJECT_ROOT / "CICT-PLM-GT-133.xml"
    cict_img = cict_raw / "CICT-PLM-GT-133.jpg"

    if cict_json.exists():
        with open(cict_json, 'r', encoding='utf-8') as f:
            cdata = json.load(f)
        
        img_present = cict_img.exists()
        sha = compute_sha256(cict_img) if img_present else "NOT_DOWNLOADED"
        width = cdata.get("image", {}).get("width", 2762)
        height = cdata.get("image", {}).get("height", 459)
        if img_present:
            try:
                with Image.open(cict_img) as img:
                    width, height = img.size
            except Exception:
                pass

        cict_record = {
            "dataset": "CICT_Tirukkural",
            "source_archive": "CICT-PLM-GT-133",
            "source_file": "CICT-PLM-GT-133.jpg" if img_present else "20217_135.jpg (Remote)",
            "image_id": "CICT_PLM_GT_133",
            "image_path": cict_img.relative_to(PROJECT_ROOT).as_posix() if img_present else "data/raw/cict/CICT-PLM-GT-133.jpg",
            "image_format": "JPEG",
            "width": width,
            "height": height,
            "color_mode": "RGB" if img_present else "UNKNOWN",
            "file_size_bytes": cict_img.stat().st_size if img_present else 0,
            "sha256": sha,
            "level": "PAGE_OR_FOLIO_WITH_10_LINES",
            "original_or_binarized": "ORIGINAL_COLOR_GRAYSCALE",
            "label_available": True,
            "label_type": "LINE_LEVEL_AND_MARGINALIA",
            "transcription_available": True,
            "transcription_path": "CICT-PLM-GT-133.xml",
            "unicode_text_available": True,
            "annotation_available": True,
            "annotation_format": "PAGE_XML_2019_AND_JSON",
            "license": "CC BY 4.0",
            "source_url": "https://doi.org/10.5281/zenodo.21337086",
            "duplicate_group": "NONE",
            "classification_category": "IMAGE_AND_PAGE_XML" if img_present else "METADATA_ONLY",
            "usable_for_training": True if img_present else False,
            "usable_for_evaluation": True if img_present else False,
            "notes": "Tirukkural Chapter 133 (couplets 1321-1330). 10 aligned body lines + 3 marginalia lines."
        }
        manifest_records.append(cict_record)

    # Assign duplicate group identifiers based on identical hashes
    dup_group_counter = 1
    for sha, paths in hash_to_files.items():
        if len(paths) > 1:
            group_name = f"DUP_GROUP_{dup_group_counter:03d}"
            dup_group_counter += 1
            for r in manifest_records:
                if r["sha256"] == sha:
                    r["duplicate_group"] = group_name
                    r["notes"] += f" Identical binary duplicate of {len(paths)} files."

    # Write Manifest CSV
    csv_path = METADATA_DIR / "dataset_manifest.csv"
    if manifest_records:
        keys = list(manifest_records[0].keys())
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(manifest_records)
        print(f"Generated Manifest CSV: {csv_path} ({len(manifest_records)} records)")

    # Write Manifest JSON
    json_path = METADATA_DIR / "dataset_manifest.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_records, f, indent=2, ensure_ascii=False)
    print(f"Generated Manifest JSON: {json_path}")

    return manifest_records

if __name__ == "__main__":
    ensure_dirs()
    copy_raw_archives_and_meta()
    extract_archives_to_staging()
    download_cict_gt_image()
    records = analyze_all_and_build_manifest()
    print(f"\nIngestion & Manifest Generation Completed! Total records: {len(records)}")
