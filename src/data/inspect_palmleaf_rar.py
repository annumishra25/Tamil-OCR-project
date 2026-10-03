"""
Inspect Structure, Classes, and Counts in palmleaf-tamil.rar
Stage 3 palmleaf-tamil Analysis
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
RAR_PATH = PROJECT_ROOT / "palmleaf-tamil.rar"

def analyze_rar():
    print(f"Analyzing {RAR_PATH} ({RAR_PATH.stat().st_size / (1024*1024):.2f} MB)...")
    
    # Run tar -tf palmleaf-tamil.rar
    cmd = ["tar", "-tf", str(RAR_PATH)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    
    total_entries = 0
    total_images = 0
    extensions = Counter()
    class_counts = Counter()
    classes = set()
    sample_files = []
    
    for line in proc.stdout:
        entry = line.strip()
        if not entry:
            continue
        total_entries += 1
        ext = os.path.splitext(entry)[1].lower()
        if ext:
            extensions[ext] += 1
        
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            total_images += 1
            # Check class folder path, e.g., FINAL DATASET/DATASET/1/Letter1_1.png
            parts = entry.replace("\\", "/").split("/")
            if len(parts) >= 3 and parts[-2] not in ["DATASET", "FINAL DATASET"]:
                cls_name = parts[-2]
                class_counts[cls_name] += 1
                classes.add(cls_name)
            if len(sample_files) < 10:
                sample_files.append(entry)
                
    proc.wait()
    
    print(f"\n=== palmleaf-tamil Dataset Summary ===")
    print(f"Total Entries: {total_entries}")
    print(f"Total Image Files: {total_images}")
    print(f"File Extensions: {dict(extensions)}")
    print(f"Total Unique Character Classes: {len(classes)}")
    print(f"Classes list: {sorted(list(classes), key=lambda x: int(x) if x.isdigit() else x)}")
    print(f"\nSample Class Distribution (First 15 classes):")
    for c in sorted(list(classes), key=lambda x: int(x) if x.isdigit() else x)[:15]:
        print(f"  Class '{c}': {class_counts[c]} character images")
    
    print(f"\nSample File Paths (First 10):")
    for s in sample_files:
        print(f"  {s}")

    return {
        "total_entries": total_entries,
        "total_images": total_images,
        "classes_count": len(classes),
        "classes": sorted(list(classes), key=lambda x: int(x) if x.isdigit() else x),
        "class_counts": dict(class_counts),
        "sample_files": sample_files
    }

if __name__ == "__main__":
    analyze_rar()
