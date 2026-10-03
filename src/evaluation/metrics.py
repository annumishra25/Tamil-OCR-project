"""
String Normalization and Error Metric Calculations (CER & WER)
Stage 3 Evaluation Engine
"""

import sys
import unicodedata
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def normalize_tamil_text(text: str) -> str:
    """
    Conservative Tamil text normalization:
    1. Unicode NFC Canonical Composition (combining pulli and vowel markers).
    2. Normalize consecutive whitespace to a single space.
    3. Strip leading and trailing whitespace.
    Does NOT remove historical Tamil numerals or grantha characters.
    """
    if not text:
        return ""
    # NFC Unicode Normalization
    norm = unicodedata.normalize("NFC", text)
    # Collapse multiple whitespace characters into single space
    norm = re.sub(r"\s+", " ", norm).strip()
    return norm

def levenshtein_distance(seq1, seq2):
    """Compute character-level or token-level Levenshtein distance."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # Deletion
                    dp[i][j - 1],     # Insertion
                    dp[i - 1][j - 1]  # Substitution
                )
    return dp[m][n]

def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Compute Character Error Rate (CER).
    CER = LevenshteinDistance(ref, hyp) / len(ref)
    """
    ref_norm = normalize_tamil_text(reference)
    hyp_norm = normalize_tamil_text(hypothesis)
    
    if len(ref_norm) == 0:
        return 0.0 if len(hyp_norm) == 0 else 1.0
        
    dist = levenshtein_distance(list(ref_norm), list(hyp_norm))
    return dist / len(ref_norm)

def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Compute Word Error Rate (WER).
    WER = WordLevenshteinDistance(ref_words, hyp_words) / len(ref_words)
    """
    ref_norm = normalize_tamil_text(reference)
    hyp_norm = normalize_tamil_text(hypothesis)
    
    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()
    
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
        
    dist = levenshtein_distance(ref_words, hyp_words)
    return dist / len(ref_words)

if __name__ == "__main__":
    ref = "இல்லைத் தவற் வாக்காயினு மூடுதல்"
    hyp = "இல்லை தவற் வாக்காயினு மூடுதல்"
    print(f"Ref: '{ref}'")
    print(f"Hyp: '{hyp}'")
    print(f"CER: {calculate_cer(ref, hyp):.4f}")
    print(f"WER: {calculate_wer(ref, hyp):.4f}")
