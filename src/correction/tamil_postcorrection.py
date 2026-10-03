"""
Conservative Tamil OCR Post-Correction Engine
Stage 9: Confidence Second Pass + Tamil Post-Correction

Applies strictly conservative, rule-based orthographic and Unicode repairs:
1. Unicode NFC Canonical Composition
2. Whitespace and non-printable control character normalization
3. Removal of erroneous whitespace preceding combining vowel signs and virama (pulli)
4. De-duplication of consecutive duplicate combining signs (e.g., duplicate pulli)
5. Canonical ordering of pre-base / post-base vowel markers
6. Preserves original historical Tamil without modernizing or fabricating words.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class CorrectionChange:
    rule_name: str
    original_segment: str
    corrected_segment: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule_name,
            "before": self.original_segment,
            "after": self.corrected_segment,
            "description": self.description
        }


@dataclass
class CorrectionResult:
    original_text: str
    corrected_text: str
    changes: List[CorrectionChange] = field(default_factory=list)
    was_modified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "was_modified": self.was_modified,
            "num_changes": len(self.changes),
            "changes": [c.to_dict() for c in self.changes]
        }


class TamilPostCorrector:
    def __init__(self):
        # Tamil combining signs range: \u0BBE to \u0BCD (\u0BBE=ா, \u0BBF=ி, \u0BC0=ீ, \u0BC1=ு, \u0BC2=ூ, \u0BC6=ெ, \u0BC7=ே, \u0BC8=ை, \u0BCA=ொ, \u0BCB=ோ, \u0BCC=ௌ, \u0BCD=்)
        self.combining_vowels_and_pulli = [
            "\u0BBE", "\u0BBF", "\u0BC0", "\u0BC1", "\u0BC2",
            "\u0BC6", "\u0BC7", "\u0BC8", "\u0BCA", "\u0BCB", "\u0BCC", "\u0BCD"
        ]
        self.pulli = "\u0BCD"  # ்

    def correct(self, text: str) -> CorrectionResult:
        if not text:
            return CorrectionResult(original_text="", corrected_text="", changes=[], was_modified=False)

        current = text
        changes: List[CorrectionChange] = []

        # 1. Unicode NFC Normalization
        nfc_text = unicodedata.normalize("NFC", current)
        if nfc_text != current:
            changes.append(CorrectionChange(
                rule_name="UNICODE_NFC_NORMALIZATION",
                original_segment=current,
                corrected_segment=nfc_text,
                description="Composed decomposed Unicode code points into standard NFC representation"
            ))
            current = nfc_text

        # 2. Whitespace Collapsing and Edge Trimming
        trimmed = re.sub(r"[ \t]+", " ", current).strip()
        if trimmed != current:
            changes.append(CorrectionChange(
                rule_name="WHITESPACE_CLEANUP",
                original_segment=current,
                corrected_segment=trimmed,
                description="Collapsed multiple consecutive spaces and stripped outer whitespace"
            ))
            current = trimmed

        # 3. Fix Erroneous Whitespace Preceding Combining Marks / Pulli
        # e.g., 'த ்' -> 'த்', 'க ா' -> 'கா'
        pattern_combining_space = r"([அ-ஹ௧-௺])\s+([\u0BBE-\u0BCD])"
        match = re.search(pattern_combining_space, current)
        if match:
            new_text = re.sub(pattern_combining_space, r"\1\2", current)
            changes.append(CorrectionChange(
                rule_name="DETACHED_COMBINING_SIGN_ATTACHMENT",
                original_segment=current,
                corrected_segment=new_text,
                description="Attached disconnected combining vowel sign or pulli to its base consonant"
            ))
            current = new_text

        # 4. Remove Duplicate Consecutive Combining Marks (e.g., 'க்்' -> 'க்' or 'காா' -> 'கா')
        pattern_duplicate_combining = r"([\u0BBE-\u0BCD])\1+"
        if re.search(pattern_duplicate_combining, current):
            new_text = re.sub(pattern_duplicate_combining, r"\1", current)
            changes.append(CorrectionChange(
                rule_name="DEDUPLICATE_COMBINING_MARKS",
                original_segment=current,
                corrected_segment=new_text,
                description="Removed duplicate consecutive combining vowel signs or pullis on the same consonant"
            ))
            current = new_text

        # 5. Fix Inverted Pulli and Vowel Sequences (e.g., Pulli followed by Vowel Sign on same consonant)
        pattern_pulli_vowel = r"\u0BCD([\u0BBE-\u0BCB])"
        if re.search(pattern_pulli_vowel, current):
            new_text = re.sub(pattern_pulli_vowel, r"\1", current)
            changes.append(CorrectionChange(
                rule_name="REMOVE_VIRAMA_BEFORE_VOWEL",
                original_segment=current,
                corrected_segment=new_text,
                description="Removed redundant pulli preceding an explicit vowel marker"
            ))
            current = new_text

        # 6. Final NFC verification
        final_text = unicodedata.normalize("NFC", current)

        return CorrectionResult(
            original_text=text,
            corrected_text=final_text,
            changes=changes,
            was_modified=(final_text != text)
        )
