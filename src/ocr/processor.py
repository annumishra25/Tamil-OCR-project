"""
Tamil OCR Text & Image Processor
Stage 8 Model Domain Adaptation

Handles:
- Complete Tamil character vocabulary encoding & CTC decoding
- Preservation of all 142 Tamil glyphs, combining signs, pulli marks, and numerals
- Aspect-ratio preserving line image tensor resizing & normalization
"""

import math
from typing import List, Dict, Tuple, Optional
import numpy as np
import torch
from PIL import Image

from src.data.normalization import normalize_tamil_unicode

# Comprehensive Tamil OCR 142-character lexicon
# Index 0 is reserved for CTC blank token [CTC_BLANK]
TAMIL_VOCABULARY = [
    "[CTC_BLANK]",
    " ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/",
    ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "ஃ", "அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ",
    "க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன",
    "ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ",
    "ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ", "்",
    "௦", "௧", "௨", "௩", "௪", "௫", "௬", "௭", "௮", "௯", "௰", "௱", "௲",
    "௳", "௴", "௵", "௶", "௷", "௸", "௹", "௺"
]

# Build lookup maps
CHAR_TO_IDX: Dict[str, int] = {char: idx for idx, char in enumerate(TAMIL_VOCABULARY)}
IDX_TO_CHAR: Dict[int, str] = {idx: char for idx, char in enumerate(TAMIL_VOCABULARY)}


class TamilOCRProcessor:
    def __init__(self, target_height: int = 32, max_width: int = 800):
        self.target_height = target_height
        self.max_width = max_width
        self.vocab = TAMIL_VOCABULARY
        self.vocab_size = len(TAMIL_VOCABULARY)
        self.char_to_idx = CHAR_TO_IDX
        self.idx_to_char = IDX_TO_CHAR

    def encode_text(self, text: str) -> List[int]:
        """
        Converts Tamil Unicode string into list of vocabulary integer indices.
        Unrecognized characters are mapped to space (index 1).
        """
        norm = normalize_tamil_unicode(text)
        indices = []
        for char in norm:
            if char in self.char_to_idx:
                indices.append(self.char_to_idx[char])
            else:
                # Fallback to space
                indices.append(1)
        return indices

    def decode_indices(self, indices: List[int], merge_repeated: bool = True) -> str:
        """
        Decodes sequence of integer indices into Tamil Unicode text.
        Applies CTC greedy collapsing if merge_repeated is True.
        """
        if not indices:
            return ""

        decoded_chars = []
        prev_idx = None

        for idx in indices:
            if idx == 0:  # CTC Blank
                prev_idx = idx
                continue
            if merge_repeated and idx == prev_idx:
                continue
            if idx in self.idx_to_char:
                decoded_chars.append(self.idx_to_char[idx])
            prev_idx = idx

        raw_str = "".join(decoded_chars)
        return normalize_tamil_unicode(raw_str)

    def process_image(self, img_pil: Image.Image) -> torch.Tensor:
        """
        Converts PIL line crop into normalized PyTorch Tensor:
        Shape: (1, 32, W) with pixel values in [-1, 1]
        """
        img_gray = img_pil.convert("L")
        w, h = img_gray.size

        # Compute aspect ratio preserving width
        ratio = w / float(h)
        new_w = max(32, min(self.max_width, int(math.ceil(self.target_height * ratio))))
        # Round to multiple of 4 for convolutional downsampling
        new_w = (new_w // 4) * 4
        new_w = max(32, new_w)

        resized = img_gray.resize((new_w, self.target_height), Image.BILINEAR)
        img_np = np.array(resized, dtype=np.float32)

        # Normalize to [-1, 1]
        img_norm = (img_np / 127.5) - 1.0
        # Add channel dimension: (1, H, W)
        tensor = torch.from_numpy(img_norm).unsqueeze(0)
        return tensor
