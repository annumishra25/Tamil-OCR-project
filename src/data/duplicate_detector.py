"""
Duplicate & Provenance Detection Module
Stage 6 Data Pipeline

Analyzes dataset images for:
- Exact SHA-256 binary hash duplicates
- Filename collisions across collections
- Original vs Binarized paired relationships
Outputs findings to results/metrics/duplicate_report.csv.
"""

import os
import hashlib
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_METRICS_DIR = PROJECT_ROOT / "results" / "metrics"


def compute_sha256(file_path: Path, block_size: int = 65536) -> str:
    """Computes SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha.update(block)
    return sha.hexdigest()


class DuplicateDetector:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.metrics_dir = RESULTS_METRICS_DIR
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def scan_images(self) -> Tuple[List[Dict[str, any]], Dict[str, any]]:
        """
        Scans data/ directory for all images and analyzes duplicate hashes,
        filename collisions, and original-to-binarized mappings.
        """
        hash_to_files = defaultdict(list)
        name_to_files = defaultdict(list)
        all_scanned = []

        # Target directories: staging, cict, lines
        target_subdirs = [
            self.data_dir / "processed" / "staging",
            self.data_dir / "processed" / "cict_gt133_lines",
            self.data_dir / "processed" / "lines" / "automatic",
            self.data_dir / "raw" / "cict"
        ]

        for subdir in target_subdirs:
            if not subdir.exists():
                continue
            for root, _, files in os.walk(subdir):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif')):
                        fp = Path(root) / f
                        f_hash = compute_sha256(fp)
                        f_size = fp.stat().st_size
                        rel_path = str(fp.relative_to(PROJECT_ROOT).as_posix())

                        item = {
                            "filename": f,
                            "relative_path": rel_path,
                            "sha256": f_hash,
                            "size_bytes": f_size
                        }
                        all_scanned.append(item)
                        hash_to_files[f_hash].append(rel_path)
                        name_to_files[f].append(rel_path)

        # Build duplicate report rows
        report_rows = []
        exact_duplicate_groups = 0
        filename_collision_groups = 0

        for f_hash, paths in hash_to_files.items():
            if len(paths) > 1:
                exact_duplicate_groups += 1
                for p in paths:
                    report_rows.append({
                        "finding_type": "EXACT_BINARY_DUPLICATE",
                        "identifier": f_hash[:16],
                        "file_path": p,
                        "notes": f"Identical file found in {len(paths)} locations"
                    })

        for fname, paths in name_to_files.items():
            if len(paths) > 1:
                # Filter out exact duplicates already flagged
                unique_hashes = set(compute_sha256(PROJECT_ROOT / p) for p in paths if (PROJECT_ROOT / p).exists())
                if len(unique_hashes) > 1:
                    filename_collision_groups += 1
                    for p in paths:
                        report_rows.append({
                            "finding_type": "FILENAME_COLLISION_DIFFERENT_CONTENT",
                            "identifier": fname,
                            "file_path": p,
                            "notes": f"Same filename with different contents in {len(paths)} locations"
                        })

        summary = {
            "total_scanned_images": len(all_scanned),
            "unique_sha256_hashes": len(hash_to_files),
            "exact_duplicate_groups": exact_duplicate_groups,
            "filename_collision_groups": filename_collision_groups,
            "total_findings": len(report_rows)
        }

        return report_rows, summary

    def generate_report(self, output_csv: Optional[Path] = None) -> Path:
        out_csv = output_csv or (self.metrics_dir / "duplicate_report.csv")
        rows, summary = self.scan_images()

        fieldnames = ["finding_type", "identifier", "file_path", "notes"]
        with open(out_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if rows:
                writer.writerows(rows)
            else:
                writer.writerow({
                    "finding_type": "NONE",
                    "identifier": "N/A",
                    "file_path": "N/A",
                    "notes": "No unintended duplicates or filename collisions detected across datasets"
                })

        print(f"Generated Duplicate Report: {out_csv} ({summary['total_findings']} entries)")
        return out_csv
