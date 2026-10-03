"""
PyTorch Dataset and DataLoader for Tamil Palm-Leaf Line OCR
Stage 8 Model Domain Adaptation

Loads line crops from JSONL splits with dynamic padding collation.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
from src.ocr.processor import TamilOCRProcessor


class TamilLineDataset(Dataset):
    def __init__(
        self,
        jsonl_path: Path,
        processor: Optional[TamilOCRProcessor] = None,
        max_samples: Optional[int] = None
    ):
        self.jsonl_path = Path(jsonl_path)
        self.processor = processor or TamilOCRProcessor()
        self.records: List[Dict[str, Any]] = []

        if not self.jsonl_path.exists():
            raise FileNotFoundError(f"Dataset split file not found: {self.jsonl_path}")

        with open(self.jsonl_path, mode='r', encoding='utf-8') as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    rec = json.loads(line_str)
                    self.records.append(rec)
                    if max_samples and len(self.records) >= max_samples:
                        break

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        rec = self.records[idx]
        img_rel = rec.get("image_path")
        img_path = PROJECT_ROOT / img_rel if not os.path.isabs(img_rel) else Path(img_rel)

        if not img_path.exists():
            raise FileNotFoundError(f"Image not found on disk: {img_path}")

        img_pil = Image.open(img_path).convert("RGB")
        img_tensor = self.processor.process_image(img_pil)  # Shape: (1, 32, W)

        text = rec.get("normalized_transcription") or rec.get("transcription", "")
        encoded_labels = self.processor.encode_text(text)

        return {
            "image": img_tensor,
            "label_indices": torch.tensor(encoded_labels, dtype=torch.long),
            "label_length": len(encoded_labels),
            "text": text,
            "sample_id": rec.get("sample_id", f"sample_{idx}"),
            "source_group_id": rec.get("source_group_id", "UNKNOWN"),
            "image_path": str(img_path)
        }


def collate_tamil_lines(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Collation function for variable-width line images and variable-length text labels.
    Pads image widths to batch maximum with -1.0 (white background in normalized space).
    """
    batch_size = len(batch)
    
    # 1. Determine max width in batch
    max_w = max(item["image"].shape[2] for item in batch)
    # Ensure multiple of 4
    max_w = ((max_w + 3) // 4) * 4

    h = batch[0]["image"].shape[1]
    c = batch[0]["image"].shape[0]

    padded_images = torch.ones((batch_size, c, h, max_w), dtype=torch.float32) * -1.0
    input_lengths = torch.zeros(batch_size, dtype=torch.long)

    # 2. Flatten labels for CTC Loss
    all_labels = []
    target_lengths = torch.zeros(batch_size, dtype=torch.long)

    sample_ids = []
    texts = []
    source_group_ids = []

    for i, item in enumerate(batch):
        img = item["image"]
        w = img.shape[2]
        padded_images[i, :, :, :w] = img
        # Approximate feature sequence length after 4x convolutional downsampling
        input_lengths[i] = w // 4
        
        lbl = item["label_indices"]
        all_labels.append(lbl)
        target_lengths[i] = len(lbl)

        sample_ids.append(item["sample_id"])
        texts.append(item["text"])
        source_group_ids.append(item["source_group_id"])

    flat_targets = torch.cat(all_labels) if all_labels else torch.tensor([], dtype=torch.long)

    return {
        "images": padded_images,
        "input_lengths": input_lengths,
        "targets": flat_targets,
        "target_lengths": target_lengths,
        "texts": texts,
        "sample_ids": sample_ids,
        "source_group_ids": source_group_ids
    }
