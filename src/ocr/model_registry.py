"""
OCR / HTR Model Registry
Stage 8 Model Domain Adaptation

Maintains metadata, architectures, parameter counts, and VRAM profiles
for evaluated open-source Tamil OCR models.
"""

from typing import Dict, Any, List

MODELS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "easyocr_tamil_crnn": {
        "model_id": "easyocr_tamil_crnn",
        "name": "EasyOCR Tamil Sequence Recognizer (ResNet-BiLSTM-CTC)",
        "architecture": "ResNet-34 Feature Extractor + 2-layer BiLSTM + CTC Sequence Decoder",
        "framework": "PyTorch (Native)",
        "license": "Apache 2.0",
        "language_support": ["Tamil (ta)"],
        "vocabulary_size": 142, # Full Tamil unicode character set with combining vowel signs
        "input_height": 32,
        "input_channels": 1,
        "parameter_count": 8_420_000,
        "vram_footprint_mb": 1200,
        "supports_fine_tuning": True,
        "supports_confidence_scores": True,
        "checkpoint_url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/tamil.pth",
        "description": "Lightweight sequence-level CTC recognizer directly compatible with RTX 4050 6GB VRAM."
    },
    "trocr_small_indic": {
        "model_id": "trocr_small_indic",
        "name": "VisionEncoderDecoder / TrOCR Small (ViT + Transformer Decoder)",
        "architecture": "DeiT-small Vision Encoder (12 layers) + RoBERTa Decoder (6 layers)",
        "framework": "HuggingFace Transformers / PyTorch",
        "license": "MIT / Apache 2.0",
        "language_support": ["Multilingual / Indic Adapted"],
        "vocabulary_size": 50265,
        "input_height": 384,
        "input_width": 384,
        "input_channels": 3,
        "parameter_count": 62_000_000,
        "vram_footprint_mb": 3400,
        "supports_fine_tuning": True,
        "supports_confidence_scores": True,
        "checkpoint_url": "microsoft/trocr-small-printed",
        "description": "Autoregressive vision-to-text sequence model for end-to-end line OCR."
    }
}


def get_model_info(model_id: str) -> Dict[str, Any]:
    if model_id not in MODELS_REGISTRY:
        raise KeyError(f"Model ID '{model_id}' not found in registry. Available: {list(MODELS_REGISTRY.keys())}")
    return MODELS_REGISTRY[model_id]


def list_available_models() -> List[Dict[str, Any]]:
    return list(MODELS_REGISTRY.values())
