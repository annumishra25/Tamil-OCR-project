"""
THPLMD Manuscript Dataset Loader & Adapter
Stage 6 Data Pipeline

Loads and validates THPLMD full-folio images and automatically segmented candidate lines.
Strictly classifies all THPLMD images as UNLABELED for text transcription.
"""

import os
import csv
from pathlib import Path
from typing import List, Dict, Optional

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
THPLMD_STAGING_DIR = PROJECT_ROOT / "data" / "processed" / "staging" / "thplmd"
AUTO_LINES_CSV = PROJECT_ROOT / "data" / "processed" / "lines" / "automatic" / "thplmd_automatic_lines.csv"


class THPLMDDatasetLoader:
    def __init__(self, staging_dir: Optional[Path] = None, auto_lines_csv: Optional[Path] = None):
        self.staging_dir = staging_dir or THPLMD_STAGING_DIR
        self.auto_lines_csv = auto_lines_csv or AUTO_LINES_CSV
        self.dataset_id = "THPLMD"
        self.license = "Academic Research / CC BY-NC 4.0"

    def load_folios(self) -> List[Dict[str, any]]:
        """
        Loads all 158 THPLMD folio image records.
        Classified as FOLIO_LEVEL, IMAGE_ONLY, UNLABELED (no ground-truth transcription).
        """
        if not self.staging_dir.exists():
            raise FileNotFoundError(f"THPLMD staging directory not found at: {self.staging_dir}")

        collections = {
            "naladiyar": "Naladiyar",
            "thirikadugam": "Thirikadugam",
            "tholkappiyam": "Tholkappiyam"
        }

        folio_records = []
        for coll_key, coll_name in collections.items():
            coll_dir = self.staging_dir / coll_key
            if not coll_dir.exists():
                continue
                
            for root, _, files in os.walk(coll_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        img_path = Path(root) / file
                        folio_id = img_path.stem
                        
                        # Generate unique source group id across original/binarized versions
                        # e.g., THPLMD_NALADIYAR_176
                        source_group_id = f"THPLMD_{coll_name.upper()}_{folio_id}"
                        
                        record = {
                            "sample_id": f"THPLMD_{coll_name}_{folio_id}",
                            "dataset": "THPLMD",
                            "collection": coll_name,
                            "source_group_id": source_group_id,
                            "folio_id": folio_id,
                            "line_id": "NOT_AVAILABLE",
                            "image_path": str(img_path.relative_to(PROJECT_ROOT).as_posix()),
                            "image_exists": img_path.exists(),
                            "label_path": "NOT_AVAILABLE",
                            "transcription": "NOT_AVAILABLE",
                            "normalized_transcription": "NOT_AVAILABLE",
                            "data_level": "FOLIO_LEVEL",
                            "label_status": "UNLABELED",
                            "line_type": "full_folio",
                            "reading_order": 0,
                            "split": "unlabeled_pool",
                            "preprocessing_variant": "binarized" if "binarized" in str(img_path).lower() else "raw",
                            "synthetic_variant": "none",
                            "license": self.license,
                            "notes": f"Full-folio palm-leaf image from {coll_name} (Dimensions: 3996x600 px)"
                        }
                        folio_records.append(record)

        return folio_records

    def load_automatic_candidate_lines(self) -> List[Dict[str, any]]:
        """
        Loads the candidate line crops detected in Stage 5.
        Strictly labeled as AUTOMATICALLY_SEGMENTED without transcription text.
        """
        if not self.auto_lines_csv.exists():
            return []

        line_records = []
        with open(self.auto_lines_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                coll = row.get("collection", "THPLMD")
                folio_id = row.get("source_folio", "").split(".")[0]
                line_id = row.get("line_id", "")
                crop_path_str = row.get("crop_path", "")
                crop_path = PROJECT_ROOT / crop_path_str if crop_path_str else Path("")
                
                source_group_id = f"THPLMD_{coll.upper()}_{folio_id}"
                
                record = {
                    "sample_id": f"THPLMD_AUTO_{line_id}",
                    "dataset": "THPLMD",
                    "collection": coll,
                    "source_group_id": source_group_id,
                    "folio_id": folio_id,
                    "line_id": line_id,
                    "image_path": crop_path_str,
                    "image_exists": crop_path.exists() if crop_path else False,
                    "label_path": "NOT_AVAILABLE",
                    "transcription": "NOT_AVAILABLE",
                    "normalized_transcription": "NOT_AVAILABLE",
                    "data_level": "LINE_LEVEL",
                    "label_status": "AUTOMATICALLY_SEGMENTED",
                    "line_type": "candidate_line",
                    "reading_order": int(row.get("reading_order", 0)),
                    "split": "unlabeled_pool",
                    "preprocessing_variant": "clahe_hpp_crop",
                    "synthetic_variant": "none",
                    "license": self.license,
                    "notes": "Candidate line crop from Stage 5 HPP segmenter. Awaiting manual human transcription."
                }
                line_records.append(record)

        return line_records

    def get_summary(self) -> Dict[str, any]:
        folios = self.load_folios()
        lines = self.load_automatic_candidate_lines()
        coll_counts = {}
        for f in folios:
            c = f["collection"]
            coll_counts[c] = coll_counts.get(c, 0) + 1
            
        return {
            "dataset": self.dataset_id,
            "total_folios": len(folios),
            "collection_counts": coll_counts,
            "automatic_candidate_lines": len(lines),
            "data_level": "FOLIO_LEVEL / LINE_LEVEL",
            "label_status": "UNLABELED (folios) / AUTOMATICALLY_SEGMENTED (candidate lines)",
            "license": self.license
        }
