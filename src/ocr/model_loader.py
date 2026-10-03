"""
OCR Model Loader & Checkpoint Manager
Stage 8 Model Domain Adaptation

Loads pretrained Tamil OCR models and fine-tuned checkpoints onto GPU (RTX 4050).
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import torch
import urllib.request

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
PRETRAINED_DIR = PROJECT_ROOT / "models" / "pretrained"
CHECKPOINTS_DIR = PROJECT_ROOT / "models" / "checkpoints" / "stage8"

from src.ocr.crnn_model import TamilCRNN
from src.ocr.processor import TamilOCRProcessor

EASYOCR_TAMIL_URL = "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/tamil.pth"
LOCAL_PRETRAINED_PATH = PRETRAINED_DIR / "tamil_pretrained.pth"


def download_pretrained_weights(dest_path: Path = LOCAL_PRETRAINED_PATH) -> Path:
    """
    Downloads official pretrained Tamil recognizer weights if not present locally.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if not dest_path.exists():
        print(f"Downloading pretrained Tamil recognizer weights to: {dest_path}...")
        try:
            home_cache = Path.home() / ".EasyOCR" / "model" / "tamil.pth"
            if home_cache.exists():
                import shutil
                shutil.copyfile(home_cache, dest_path)
                print(f"Copied from local EasyOCR cache: {home_cache}")
                return dest_path

            urllib.request.urlretrieve(EASYOCR_TAMIL_URL, dest_path)
            print("Download completed successfully.")
        except Exception as e:
            print(f"Notice: Could not download weights ({e}), initializing with standard PyTorch weights.")
    return dest_path


def load_tamil_crnn_model(
    checkpoint_path: Optional[Path] = None,
    device: Optional[torch.device] = None,
    vocab_size: int = 143
) -> Tuple[TamilCRNN, TamilOCRProcessor, torch.device]:
    """
    Instantiates TamilCRNN (53.79M params) and processor, loading fine-tuned or pretrained weights.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    processor = TamilOCRProcessor()
    model = TamilCRNN(in_channels=1, output_channel=512, hidden_size=512, num_class=vocab_size)

    if checkpoint_path and Path(checkpoint_path).exists():
        print(f"Loading weights from: {checkpoint_path}")
        state_dict = torch.load(checkpoint_path, map_location=device)
        if "model_state_dict" in state_dict:
            model.load_state_dict(state_dict["model_state_dict"], strict=True)
        elif any(k.startswith("module.") for k in state_dict.keys()):
            cleaned = {k.replace("module.", ""): v for k, v in state_dict.items()}
            model.net.load_state_dict(cleaned, strict=True)
            print(f"Loaded 100% of official pretrained Tamil weights ({sum(p.numel() for p in model.parameters()):,} parameters).")
        else:
            model.load_state_dict(state_dict, strict=True)
    else:
        # Load official pretrained weights
        weights_file = download_pretrained_weights()
        if weights_file.exists():
            try:
                raw_state = torch.load(weights_file, map_location="cpu")
                cleaned_state = {k.replace("module.", ""): v for k, v in raw_state.items()}
                model.net.load_state_dict(cleaned_state, strict=True)
                print(f"Loaded 100% of official pretrained Tamil weights ({sum(p.numel() for p in model.parameters()):,} parameters).")
            except Exception as e:
                print(f"Notice: Could not load full state dict ({e})")

    model.to(device)
    return model, processor, device
