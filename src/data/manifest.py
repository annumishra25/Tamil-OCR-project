"""
Unified Dataset Manifest Builder
Stage 6 Data Pipeline

Aggregates all dataset records into:
- data/splits/unified_manifest.csv
- data/splits/train.jsonl
- data/splits/val.jsonl
- data/splits/test.jsonl
- data/splits/external_test.jsonl
- results/metrics/dataset_hierarchy_summary.json
"""

import sys
import os
import csv
import json
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

from src.data.cict_loader import CICTDatasetLoader
from src.data.thplmd_loader import THPLMDDatasetLoader
from src.data.palmleaf_tamil_loader import PalmleafTamilLoader
from src.data.splits import SplitManager
from src.data.duplicate_detector import DuplicateDetector

SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
METRICS_DIR = PROJECT_ROOT / "results" / "metrics"


def build_unified_manifest():
    print("\n=======================================================")
    print("--- Stage 6: Formulating Unified Manifest & Splits ---")
    print("=======================================================")

    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load CICT Ground Truth
    cict_loader = CICTDatasetLoader()
    cict_records = cict_loader.load_records()
    print(f"Loaded CICT GT-133: {len(cict_records)} verified ground-truth line records.")

    # 2. Load THPLMD Unlabeled folios and automatic lines
    thplmd_loader = THPLMDDatasetLoader()
    thplmd_folios = thplmd_loader.load_folios()
    thplmd_auto_lines = thplmd_loader.load_automatic_candidate_lines()
    print(f"Loaded THPLMD: {len(thplmd_folios)} full folios (UNLABELED) and {len(thplmd_auto_lines)} automatic candidate lines.")

    # 3. Load palmleaf-tamil Character Dataset
    plt_loader = PalmleafTamilLoader()
    plt_summary = plt_loader.inspect_archive()
    plt_records = plt_loader.generate_character_records()
    print(f"Loaded palmleaf-tamil: {len(plt_records)} character records across {plt_summary.get('classes_count', 0)} classes.")

    # 4. Aggregate all records into Unified Manifest CSV
    all_records = []
    all_records.extend(cict_records)
    all_records.extend(thplmd_folios)
    all_records.extend(thplmd_auto_lines)
    all_records.extend(plt_records)

    fieldnames = [
        "sample_id", "dataset", "collection", "source_group_id", "folio_id",
        "line_id", "image_path", "label_path", "transcription",
        "normalized_transcription", "data_level", "label_status", "line_type",
        "reading_order", "split", "preprocessing_variant", "synthetic_variant",
        "license", "notes"
    ]

    manifest_csv = SPLITS_DIR / "unified_manifest.csv"
    with open(manifest_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_records)
    print(f"\nCreated Unified Manifest CSV: {manifest_csv} ({len(all_records)} total items)")

    # 5. Build Leakage-Safe Splits
    split_mgr = SplitManager(splits_dir=SPLITS_DIR)
    splits = {
        "train": [],
        "val": [],
        "test": [],
        "external_test": cict_records,
        "character_pool": plt_records,
        "unlabeled_pool": thplmd_folios + thplmd_auto_lines
    }

    # Validate leakage
    is_valid, violations = split_mgr.validate_no_leakage(splits)
    if not is_valid:
        print("ERROR: Split leakage detected!")
        for v in violations:
            print(" ", v)
        raise ValueError("Leakage validation failed")
    else:
        print("Zero Data Leakage Verified: All source_group_ids are strictly isolated across splits.")

    split_mgr.export_jsonl_splits(splits)

    # 6. Run Duplicate Detector
    dup_detector = DuplicateDetector()
    dup_report_csv = dup_detector.generate_report()

    # 7. Generate Data Hierarchy Summary JSON
    hierarchy_summary = {
        "stage": "Stage 6 Training-Pair Formulation & Splits",
        "data_hierarchy": {
            "Level_1_Pretrained_OCR": "Indic TrOCR / EasyOCR Tamil (Weights & Lexicon available)",
            "Level_2_Character_Data": {
                "dataset": "palmleaf-tamil",
                "count": len(plt_records),
                "classes": plt_summary.get("classes_count", 0),
                "role": "CHARACTER_LEVEL / Pre-adaptation & Glyph Morphology"
            },
            "Level_3_Supervised_Lines": {
                "dataset": "CICT-PLM-GT-133",
                "count": len(cict_records),
                "role": "LINE_LEVEL / EXTERNAL GOLD STANDARD BENCHMARK",
                "label_status": "VERIFIED_GROUND_TRUTH"
            },
            "Level_4_Synthetic_Lines": {
                "status": "Scheduled for Stage 7",
                "role": "LINE_LEVEL / Physics-degraded Tamil palm-leaf synthesis"
            },
            "Level_5_Unlabeled_Folios": {
                "dataset": "THPLMD",
                "folios_count": len(thplmd_folios),
                "auto_candidate_lines_count": len(thplmd_auto_lines),
                "role": "FOLIO_LEVEL / Unlabeled Visual Adaptation & Preprocessing Reference"
            }
        },
        "total_manifest_records": len(all_records),
        "splits_summary": {
            "train_jsonl_count": len(splits["train"]),
            "val_jsonl_count": len(splits["val"]),
            "test_jsonl_count": len(splits["test"]),
            "external_test_jsonl_count": len(splits["external_test"]),
            "character_pool_count": len(splits["character_pool"]),
            "unlabeled_pool_count": len(splits["unlabeled_pool"])
        },
        "iiit_tamil_status": "NOT_AVAILABLE_LOCALLY (External/Awaiting)"
    }

    summary_json = METRICS_DIR / "dataset_hierarchy_summary.json"
    with open(summary_json, mode='w', encoding='utf-8') as f:
        json.dump(hierarchy_summary, f, indent=2, ensure_ascii=False)
    print(f"Saved Hierarchy Summary: {summary_json}")

    return hierarchy_summary


if __name__ == "__main__":
    build_unified_manifest()
