"""
Synthetic Palm-Leaf Dataset Generation & Partitioning Engine
Stage 7 Synthetic Data Engine

Orchestrates clean Tamil line rendering, physics-based degradation,
leakage-safe split partitioning, automatic quality auditing,
and visualization comparison exports.
"""

import sys
import os
import json
import csv
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

from src.augmentation.text_renderer import TamilTextRenderer
from src.augmentation.palmleaf_degradation import degrade_palmleaf_image
from src.data.normalization import normalize_tamil_unicode

CORPUS_JSON_PATH = PROJECT_ROOT / "data" / "corpus" / "tamil_literary_lines.json"
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"
CLEAN_IMG_DIR = SYNTHETIC_DIR / "clean"
DEGRADED_IMG_DIR = SYNTHETIC_DIR / "degraded"
MANIFEST_DIR = SYNTHETIC_DIR / "manifests"
VISUALIZATIONS_DIR = PROJECT_ROOT / "results" / "visualizations" / "synthetic"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments" / "synthetic"


class SyntheticDatasetGenerator:
    def __init__(self, corpus_path: Path = CORPUS_JSON_PATH, base_seed: int = 42):
        self.corpus_path = corpus_path
        self.base_seed = base_seed
        self.renderer = TamilTextRenderer()
        
        # Ensure directories exist
        CLEAN_IMG_DIR.mkdir(parents=True, exist_ok=True)
        DEGRADED_IMG_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)
        EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    def load_clean_corpus(self) -> List[Dict[str, Any]]:
        """
        Loads and flattens literary lines from corpus JSON with group-level tracking.
        """
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}")

        with open(self.corpus_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)

        flat_lines = []
        for group in data:
            grp_id = group["source_group_id"]
            work = group.get("work", "Tamil Literature")
            for idx, line in enumerate(group["lines"]):
                flat_lines.append({
                    "source_group_id": grp_id,
                    "work": work,
                    "line_index": idx + 1,
                    "text": normalize_tamil_unicode(line)
                })

        return flat_lines

    def partition_corpus(
        self,
        flat_lines: List[Dict[str, Any]],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Partitions lines strictly by source_group_id to guarantee ZERO text leakage.
        """
        unique_groups = list(dict.fromkeys(item["source_group_id"] for item in flat_lines))
        
        # Deterministic shuffle
        rng = np.random.RandomState(self.base_seed)
        shuffled_groups = list(unique_groups)
        rng.shuffle(shuffled_groups)

        n_total = len(shuffled_groups)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        train_groups = set(shuffled_groups[:n_train])
        val_groups = set(shuffled_groups[n_train:n_train + n_val])
        test_groups = set(shuffled_groups[n_train + n_val:])

        splits = {"train": [], "val": [], "test": []}
        for item in flat_lines:
            grp = item["source_group_id"]
            if grp in train_groups:
                splits["train"].append(item)
            elif grp in val_groups:
                splits["val"].append(item)
            else:
                splits["test"].append(item)

        return splits

    def audit_quality(self, img_pil: Image.Image) -> Dict[str, Any]:
        """
        Evaluates optical quality and flags problematic images.
        """
        arr = np.array(img_pil.convert("L"))
        h, w = arr.shape

        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr))
        
        flags = []
        if w < 50 or h < 15:
            flags.append("TOO_SMALL")
        if mean_val < 30:
            flags.append("EXTREME_DARK")
        if mean_val > 245:
            flags.append("EXTREME_BRIGHT")
        if std_val < 5.0:
            flags.append("LOW_CONTRAST")

        return {
            "mean_luminance": round(mean_val, 2),
            "contrast_std": round(std_val, 2),
            "width": w,
            "height": h,
            "flags": flags,
            "passed": len(flags) == 0
        }

    def generate_dataset(
        self,
        samples_per_split: Dict[str, int] = {"train": 100, "val": 25, "test": 25}
    ) -> Dict[str, Any]:
        """
        Generates synthetic line samples across train, val, and test partitions.
        """
        print("\n=======================================================")
        print("--- Stage 7: Running Synthetic Palm-Leaf Generator ---")
        print("=======================================================")

        flat_lines = self.load_clean_corpus()
        print(f"Loaded {len(flat_lines)} clean Tamil literary lines.")

        splits = self.partition_corpus(flat_lines)
        print(f"Group Partition: {len(splits['train'])} train lines, {len(splits['val'])} val lines, {len(splits['test'])} test lines.")

        presets = ["LIGHT", "MEDIUM", "HEAVY", "EXTREME"]
        manifest_records = []
        split_records = {"train": [], "val": [], "test": []}
        rejected_count = 0
        t0 = time.time()

        sample_counter = 0

        for split_name, lines_pool in splits.items():
            target_count = samples_per_split.get(split_name, 50)
            print(f"\nGenerating [{split_name.upper()}] partition ({target_count} target samples)...")

            for i in range(target_count):
                sample_counter += 1
                seed = self.base_seed + sample_counter
                rng = np.random.RandomState(seed)

                # Pick a source text from the allocated split pool
                line_item = rng.choice(lines_pool)
                text = line_item["text"]
                source_group_id = line_item["source_group_id"]
                
                # Pick a preset and font
                preset = rng.choice(presets, p=[0.25, 0.40, 0.25, 0.10])
                font_size = rng.randint(24, 30)

                # 1. Render clean image
                clean_img, clean_meta = self.renderer.render_line(
                    text=text,
                    font_size=font_size,
                    padding_x=rng.randint(18, 28),
                    padding_y=rng.randint(6, 12)
                )

                # 2. Apply degradation
                deg_img, deg_params = degrade_palmleaf_image(
                    clean_pil_img=clean_img,
                    preset=preset,
                    seed=seed
                )

                # 3. Quality audit
                audit = self.audit_quality(deg_img)
                if not audit["passed"]:
                    rejected_count += 1
                    status = "FLAGGED_REVIEW"
                else:
                    status = "ACCEPTED"

                sample_id = f"SYNTH_{split_name.upper()}_{sample_counter:05d}"
                clean_filename = f"{sample_id}_clean.png"
                deg_filename = f"{sample_id}_degraded.png"

                clean_path = CLEAN_IMG_DIR / clean_filename
                deg_path = DEGRADED_IMG_DIR / deg_filename

                clean_img.save(clean_path, format="PNG")
                deg_img.save(deg_path, format="PNG")

                rec = {
                    "sample_id": sample_id,
                    "dataset": "SYNTHETIC_PALMLEAF_TAMIL",
                    "source_group_id": source_group_id,
                    "source_work": line_item["work"],
                    "split": split_name,
                    "clean_image_path": str(clean_path.relative_to(PROJECT_ROOT).as_posix()),
                    "image_path": str(deg_path.relative_to(PROJECT_ROOT).as_posix()),
                    "transcription": text,
                    "normalized_transcription": text,
                    "font_name": clean_meta["font_name"],
                    "font_size": font_size,
                    "degradation_preset": preset,
                    "seed": seed,
                    "data_level": "LINE_LEVEL",
                    "label_status": "SYNTHETIC",
                    "quality_status": status,
                    "mean_luminance": audit["mean_luminance"],
                    "contrast_std": audit["contrast_std"],
                    "synthetic": True
                }
                # Merge degradation parameters
                rec.update(deg_params)

                manifest_records.append(rec)
                split_records[split_name].append(rec)

        # 4. Export JSONL splits
        for s_name, recs in split_records.items():
            jsonl_path = SYNTHETIC_DIR / f"synthetic_{s_name}.jsonl"
            with open(jsonl_path, mode='w', encoding='utf-8') as f:
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"Exported {len(recs)} records to {jsonl_path}")

        # 5. Export Master Synthetic CSV Manifest
        manifest_csv = MANIFEST_DIR / "synthetic_manifest.csv"
        if manifest_records:
            fieldnames = list(manifest_records[0].keys())
            with open(manifest_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(manifest_records)
            print(f"Exported Synthetic Manifest CSV: {manifest_csv} ({len(manifest_records)} records)")

        # 6. Generate Visual Comparison Grids
        self.generate_comparison_grids(splits["val"])

        elapsed = time.time() - t0
        summary = {
            "total_generated": len(manifest_records),
            "split_counts": {s: len(r) for s, r in split_records.items()},
            "rejected_samples": rejected_count,
            "elapsed_seconds": round(elapsed, 2),
            "base_seed": self.base_seed,
            "clean_lines_count": len(flat_lines),
            "fonts_used": [f["font_name"] for f in self.renderer.fonts]
        }

        # Save experiment log
        with open(EXPERIMENTS_DIR / "synthetic_generation_report.json", mode='w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"\nSynthetic Generation Completed in {elapsed:.2f}s (Total: {len(manifest_records)} samples)")
        return summary

    def generate_comparison_grids(self, val_lines: List[Dict[str, Any]]):
        """
        Creates clean -> LIGHT -> MEDIUM -> HEAVY -> EXTREME visual comparison diagnostics.
        """
        print("\nGenerating Visual Comparison Grids in results/visualizations/synthetic/...")
        presets = ["LIGHT", "MEDIUM", "HEAVY", "EXTREME"]

        for idx, item in enumerate(val_lines[:3]):
            text = item["text"]
            clean_img, _ = self.renderer.render_line(text, font_size=26)
            
            panel_images = [("CLEAN ORIGINAL", clean_img)]
            for p in presets:
                deg_img, _ = degrade_palmleaf_image(clean_img, preset=p, seed=self.base_seed + idx * 10)
                panel_images.append((p, deg_img))

            # Stack horizontally into a multi-panel comparison image
            max_w = max(img.width for _, img in panel_images)
            total_h = sum(img.height + 25 for _, img in panel_images)
            
            comp_img = Image.new("RGB", (max_w + 40, total_h + 30), color=(18, 15, 12))
            draw = ImageDraw.Draw(comp_img)
            
            curr_y = 15
            for title, img in panel_images:
                draw.text((20, curr_y), f"[{title}]", fill=(212, 168, 83))
                comp_img.paste(img, (20, curr_y + 18))
                curr_y += img.height + 26

            out_path = VISUALIZATIONS_DIR / f"synthetic_comparison_sample_{idx + 1:02d}.png"
            comp_img.save(out_path)
            print(f"  Saved comparison grid: {out_path}")


def main():
    generator = SyntheticDatasetGenerator()
    summary = generator.generate_dataset(samples_per_split={"train": 150, "val": 35, "test": 35})
    print("\nStage 7 Synthetic Engine Execution Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
