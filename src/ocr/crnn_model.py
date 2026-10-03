"""
ResNet-VGG + BiLSTM + CTC Sequence Recognizer for Tamil Palm-Leaf OCR
Stage 8 Model Domain Adaptation

Architecture:
- 53.79M Parameter ResNet / VGG Feature Extractor
- 2-layer Bidirectional LSTM Sequence Encoder (hidden_size=512)
- 143-class Linear CTC Projection Head
- Token-level probability & confidence estimation
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, List, Optional
import easyocr.model.model as easymodel


class TamilCRNN(nn.Module):
    def __init__(
        self,
        in_channels: int = 1,
        output_channel: int = 512,
        hidden_size: int = 512,
        num_class: int = 143
    ):
        super().__init__()
        self.num_class = num_class
        self.net = easymodel.Model(
            input_channel=in_channels,
            output_channel=output_channel,
            hidden_size=hidden_size,
            num_class=num_class
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input: (B, 1, 32, W)
        Output: Log-softmax logits of shape (T, B, num_class) for PyTorch CTCLoss.
        """
        raw_logits = self.net(x, text=None)  # Shape: (B, T, num_class)
        log_probs = F.log_softmax(raw_logits, dim=2)
        # Permute to (T, B, num_class) for CTCLoss
        return log_probs.permute(1, 0, 2)

    def decode_predictions(
        self,
        log_probs: torch.Tensor,
        processor
    ) -> List[Dict[str, Any]]:
        """
        Greedy CTC decoding with token probabilities and overall confidence score.
        log_probs shape: (T, B, num_class)
        """
        probs = torch.exp(log_probs)  # (T, B, num_class)
        max_probs, argmax_indices = torch.max(probs, dim=2)  # (T, B)

        # Transpose to (B, T)
        argmax_indices = argmax_indices.permute(1, 0).cpu().numpy()
        max_probs = max_probs.permute(1, 0).cpu().numpy()

        results = []
        for b in range(len(argmax_indices)):
            indices_seq = argmax_indices[b].tolist()
            probs_seq = max_probs[b]

            # Decode text
            text = processor.decode_indices(indices_seq, merge_repeated=True)

            # Compute mean confidence of non-blank predictions
            non_blank_probs = [probs_seq[t] for t, idx in enumerate(indices_seq) if idx != 0]
            mean_conf = float(np.mean(non_blank_probs)) if non_blank_probs else 0.0

            results.append({
                "transcription": text,
                "confidence": round(mean_conf, 4),
                "raw_indices": indices_seq
            })

        return results
