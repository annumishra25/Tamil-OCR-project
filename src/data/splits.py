"""
Leakage-Safe Split Manager
Stage 6 Data Pipeline

Enforces strict source-group isolation across manuscript partitions:
- Zero folio/manuscript overlap between Train, Validation, and Test
- Ensures CICT GT-133 (single folio) is placed exclusively in external_test.jsonl
- Prevents cross-contamination from identical folios with multiple preprocessing variants
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"


class SplitManager:
    def __init__(self, splits_dir: Path = SPLITS_DIR):
        self.splits_dir = splits_dir
        self.splits_dir.mkdir(parents=True, exist_ok=True)

    def validate_no_leakage(self, splits: Dict[str, List[Dict[str, any]]]) -> Tuple[bool, List[str]]:
        """
        Validates that no source_group_id is shared between distinct splits (e.g. train vs test).
        Returns (is_valid, list_of_violations).
        """
        group_to_split: Dict[str, str] = {}
        violations = []

        for split_name, records in splits.items():
            for rec in records:
                group_id = rec.get("source_group_id")
                if not group_id or group_id == "NOT_AVAILABLE":
                    continue
                
                if group_id in group_to_split:
                    existing_split = group_to_split[group_id]
                    if existing_split != split_name:
                        violations.append(
                            f"LEAKAGE DETECTED: source_group_id '{group_id}' appears in both '{existing_split}' and '{split_name}' (Sample: {rec.get('sample_id')})"
                        )
                else:
                    group_to_split[group_id] = split_name

        is_valid = (len(violations) == 0)
        return is_valid, violations

    def export_jsonl_splits(self, splits: Dict[str, List[Dict[str, any]]]):
        """
        Exports records to individual JSONL files:
        train.jsonl, val.jsonl, test.jsonl, external_test.jsonl
        """
        is_valid, violations = self.validate_no_leakage(splits)
        if not is_valid:
            error_msg = "\n".join(violations)
            raise ValueError(f"Cannot export splits due to data leakage violations:\n{error_msg}")

        for split_name, records in splits.items():
            file_path = self.splits_dir / f"{split_name}.jsonl"
            with open(file_path, mode='w', encoding='utf-8') as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"Exported {len(records)} records to {file_path}")

    def create_baseline_splits(self, cict_records: List[Dict[str, any]], thplmd_records: List[Dict[str, any]]) -> Dict[str, List[Dict[str, any]]]:
        """
        Creates the Stage 6 baseline partition structure:
        - CICT GT-133 (all 23 lines) -> external_test (GOLD STANDARD TEST)
        - THPLMD folios & candidate lines -> unlabeled_pool (UNLABELED)
        - train / val / test -> empty provisional (awaiting Stage 7 synthetic lines & supervised pairs)
        """
        splits = {
            "train": [],
            "val": [],
            "test": [],
            "external_test": cict_records,
            "unlabeled_pool": thplmd_records
        }
        return splits
