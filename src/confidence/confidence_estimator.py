"""
CTC Output Confidence Estimator
Stage 9: Confidence Second Pass + Tamil Post-Correction

Extracts true token-level and sequence-level predictive confidence from
the TamilCRNN CTC log-probability outputs.
Never uses random or synthetic values.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F

from src.ocr.processor import TamilOCRProcessor


@dataclass
class TokenConfidence:
    char: str
    char_idx: int
    timestep: int
    probability: float
    entropy: float


@dataclass
class SequenceConfidenceResult:
    transcription: str
    sequence_confidence: float
    mean_token_confidence: float
    min_token_confidence: float
    geometric_mean_confidence: float
    mean_entropy: float
    token_confidences: List[TokenConfidence] = field(default_factory=list)
    raw_indices: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transcription": self.transcription,
            "sequence_confidence": round(self.sequence_confidence, 4),
            "mean_token_confidence": round(self.mean_token_confidence, 4),
            "min_token_confidence": round(self.min_token_confidence, 4),
            "geometric_mean_confidence": round(self.geometric_mean_confidence, 4),
            "mean_entropy": round(self.mean_entropy, 4),
            "num_emitted_tokens": len(self.token_confidences),
            "token_confidences": [
                {
                    "char": tc.char,
                    "char_idx": tc.char_idx,
                    "timestep": tc.timestep,
                    "probability": round(tc.probability, 4),
                    "entropy": round(tc.entropy, 4)
                }
                for tc in self.token_confidences
            ]
        }


class CTCConfidenceEstimator:
    def __init__(self, processor: Optional[TamilOCRProcessor] = None):
        self.processor = processor or TamilOCRProcessor()

    def estimate_confidence(
        self,
        log_probs: torch.Tensor,
        batch_index: int = 0
    ) -> SequenceConfidenceResult:
        """
        Calculates mathematically rigorous confidence metrics from CTC log_probs.
        log_probs shape: (T, B, num_class) or (T, num_class)
        """
        if log_probs.dim() == 3:
            # Shape (T, num_class) for batch_index
            lp = log_probs[:, batch_index, :]
        else:
            lp = log_probs

        # Move to CPU float numpy
        lp_cpu = lp.detach().cpu()
        probs = torch.exp(lp_cpu).numpy()  # (T, num_class)
        log_probs_np = lp_cpu.numpy()

        T, num_class = probs.shape

        # Greedy argmax per timestep
        argmax_indices = np.argmax(probs, axis=-1)  # (T,)
        max_probs = np.max(probs, axis=-1)  # (T,)

        # Compute Shannon entropy per timestep: H = -sum(p * log(p + eps))
        eps = 1e-12
        timestep_entropy = -np.sum(probs * np.log(np.clip(probs, eps, 1.0)), axis=-1)

        # Decode sequence and track non-blank emissions with CTC collapsing
        token_confidences: List[TokenConfidence] = []
        raw_indices: List[int] = argmax_indices.tolist()

        prev_idx = None
        decoded_chars = []

        for t in range(T):
            idx = int(argmax_indices[t])
            prob = float(max_probs[t])
            ent = float(timestep_entropy[t])

            if idx == 0:  # CTC Blank
                prev_idx = idx
                continue

            if idx == prev_idx:
                # CTC repeated index in consecutive frames -> collapsed
                continue

            # Valid new character emission
            char = self.processor.idx_to_char.get(idx, "")
            decoded_chars.append(char)
            token_confidences.append(TokenConfidence(
                char=char,
                char_idx=idx,
                timestep=t,
                probability=prob,
                entropy=ent
            ))
            prev_idx = idx

        transcription = "".join(decoded_chars)

        if not token_confidences:
            # Empty prediction or only blanks
            return SequenceConfidenceResult(
                transcription="",
                sequence_confidence=0.0,
                mean_token_confidence=0.0,
                min_token_confidence=0.0,
                geometric_mean_confidence=0.0,
                mean_entropy=float(np.mean(timestep_entropy)),
                token_confidences=[],
                raw_indices=raw_indices
            )

        token_probs = [tc.probability for tc in token_confidences]
        token_entropies = [tc.entropy for tc in token_confidences]

        mean_token_conf = float(np.mean(token_probs))
        min_token_conf = float(np.min(token_probs))
        
        # Geometric mean: exp(1/N * sum(log(p)))
        log_sum = sum(math.log(max(p, eps)) for p in token_probs)
        geom_mean_conf = float(math.exp(log_sum / len(token_probs)))
        mean_ent = float(np.mean(token_entropies))

        # Composite Sequence Confidence:
        # Weighted combination of harmonic/geometric mean and minimum token confidence
        # Penalizes sequences where even a single character has very low probability
        sequence_conf = (0.7 * mean_token_conf) + (0.3 * min_token_conf)

        return SequenceConfidenceResult(
            transcription=transcription,
            sequence_confidence=sequence_conf,
            mean_token_confidence=mean_token_conf,
            min_token_confidence=min_token_conf,
            geometric_mean_confidence=geom_mean_conf,
            mean_entropy=mean_ent,
            token_confidences=token_confidences,
            raw_indices=raw_indices
        )
