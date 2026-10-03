"""
CICT GT-133 Ground-Truth Line Dataset Loader
Stage 6 Data Pipeline

Loads and validates verified ground-truth line crops and transcriptions
from CICT-PLM-GT-133 PAGE XML and processed slice manifest.
"""

import os
import csv
from pathlib import Path
from typing import List, Dict, Optional

from src.data.normalization import normalize_tamil_unicode, compare_transcription_normalization

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
CICT_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines.csv"
CICT_CROPS_DIR = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines"


class CICTDatasetLoader:
    def __init__(self, csv_path: Optional[Path] = None, crops_dir: Optional[Path] = None):
        self.csv_path = csv_path or CICT_CSV_PATH
        self.crops_dir = crops_dir or CICT_CROPS_DIR
        self.dataset_id = "CICT-PLM-GT-133"
        self.source_group_id = "CICT_GT133_FOLIO_87"
        self.license = "CC BY 4.0 (CICT Chennai)"

    def load_records(self) -> List[Dict[str, any]]:
        """
        Loads all verified CICT ground-truth line records with normalized and original transcriptions.
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CICT manifest not found at: {self.csv_path}")

        records = []
        with open(self.csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                line_id = row.get("line_id")
                image_filename = row.get("image_filename")
                if image_filename:
                    crop_path = (self.crops_dir / image_filename).resolve()
                else:
                    raw_crop_path = row.get("image_path", "")
                    crop_path = (PROJECT_ROOT / raw_crop_path).resolve() if raw_crop_path else Path("")
                
                raw_transcription = row.get("transcription", "")
                norm_transcription = normalize_tamil_unicode(raw_transcription)
                
                record = {
                    "sample_id": f"CICT_{line_id}",
                    "dataset": self.dataset_id,
                    "source_group_id": self.source_group_id,
                    "folio_id": "87_Recto",
                    "line_id": line_id,
                    "image_path": str(crop_path.relative_to(PROJECT_ROOT).as_posix()) if crop_path.exists() else str(crop_path),
                    "image_exists": crop_path.exists(),
                    "label_path": "CICT-PLM-GT-133.xml",
                    "transcription": raw_transcription,
                    "normalized_transcription": norm_transcription,
                    "data_level": "LINE_LEVEL",
                    "label_status": "VERIFIED_GROUND_TRUTH",
                    "line_type": row.get("line_type", "paragraph"),
                    "reading_order": int(row.get("reading_order", 0)),
                    "split": "external_test",
                    "preprocessing_variant": "raw_crop",
                    "synthetic_variant": "none",
                    "license": self.license,
                    "notes": f"Couplet line from Tirukkural Ch 133 (Kural {row.get('kural_number', 'N/A')})"
                }
                records.append(record)

        return records

    def get_summary(self) -> Dict[str, any]:
        records = self.load_records()
        line_types = {}
        for r in records:
            lt = r["line_type"]
            line_types[lt] = line_types.get(lt, 0) + 1
            
        return {
            "dataset": self.dataset_id,
            "source_group_id": self.source_group_id,
            "total_lines": len(records),
            "line_types": line_types,
            "data_level": "LINE_LEVEL",
            "label_status": "VERIFIED_GROUND_TRUTH",
            "split_assignment": "external_test",
            "license": self.license
        }
