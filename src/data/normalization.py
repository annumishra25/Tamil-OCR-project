"""
Tamil Unicode Text Normalization Module
Stage 6 Data Pipeline

Provides deterministic, non-destructive Tamil text normalization:
- Unicode NFC normalization (canonical composition)
- Standardizes Tamil dependent vowel signs & pulli marks
- Removes unwanted invisible/control characters while preserving Tamil punctuation & numerals
- Preserves original transcription alongside normalized version
"""

import unicodedata
import re
from typing import Dict, Tuple, Optional


def normalize_tamil_unicode(text: Optional[str], form: str = "NFC") -> str:
    """
    Normalizes Tamil Unicode string to standard canonical composition.
    
    Args:
        text: Raw Tamil string
        form: Unicode normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')
    Returns:
        Normalized Tamil string
    """
    if not text:
        return ""
    
    # 1. Standard Unicode normalization (default NFC)
    norm_text = unicodedata.normalize(form, text)
    
    # 2. Strip control characters / zero-width characters (except valid Tamil zero-width if needed)
    # Remove BOM, zero-width space, left-to-right marks
    norm_text = re.sub(r'[\u200B\u200C\u200D\uFEFF\u200E\u200F]', '', norm_text)
    
    # 3. Collapse multiple whitespace into single space and strip outer whitespace
    norm_text = re.sub(r'\s+', ' ', norm_text).strip()
    
    return norm_text


def compare_transcription_normalization(raw_text: str) -> Dict[str, any]:
    """
    Compares raw and normalized transcription, reporting any changes or code-point differences.
    """
    normalized = normalize_tamil_unicode(raw_text)
    is_changed = (raw_text != normalized)
    
    raw_codepoints = [f"U+{ord(c):04X}" for c in raw_text] if raw_text else []
    norm_codepoints = [f"U+{ord(c):04X}" for c in normalized] if normalized else []
    
    return {
        "original": raw_text,
        "normalized": normalized,
        "is_changed": is_changed,
        "original_len": len(raw_text) if raw_text else 0,
        "normalized_len": len(normalized) if normalized else 0,
        "original_codepoints": raw_codepoints,
        "normalized_codepoints": norm_codepoints
    }


def validate_tamil_script(text: str) -> Dict[str, any]:
    """
    Analyzes Tamil script content percentage and character categories.
    Tamil Unicode block: U+0B80 to U+0BFF
    """
    if not text:
        return {"total_chars": 0, "tamil_chars": 0, "tamil_pct": 0.0, "contains_numerals": False}
    
    tamil_chars = 0
    tamil_numerals = 0
    other_chars = 0
    
    for c in text:
        cp = ord(c)
        if 0x0BE6 <= cp <= 0x0BF2:  # Tamil numerals ௦-௯, ௰, ௱, ௲
            tamil_numerals += 1
            tamil_chars += 1
        elif 0x0B80 <= cp <= 0x0BFA:
            tamil_chars += 1
        elif not c.isspace():
            other_chars += 1
            
    total = len(text.replace(" ", ""))
    pct = (tamil_chars / total * 100) if total > 0 else 0.0
    
    return {
        "total_nonspace_chars": total,
        "tamil_chars": tamil_chars,
        "tamil_numerals": tamil_numerals,
        "other_chars": other_chars,
        "tamil_pct": round(pct, 2),
        "contains_numerals": tamil_numerals > 0
    }
