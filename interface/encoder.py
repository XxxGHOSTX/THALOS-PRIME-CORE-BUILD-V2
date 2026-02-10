"""
Mind Interface Encoder
Transforms neural or textual signals into latent vectors for Matrix Codex.
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, Iterable, Union


class NeuralEncoder:
    """Capture and encode neural or textual signals."""

    def __init__(self, latent_dim: int = 512):
        self.latent_dim = latent_dim

    def capture(self) -> np.ndarray:
        """
        Simulate capture from a mind-interface device.
        Returns a low-amplitude random signal that can be passed through encode().
        """
        return np.random.uniform(-0.05, 0.05, size=self.latent_dim)

    def encode(self, signal: Union[str, Iterable[Any], Dict[str, Any]]) -> np.ndarray:
        """
        Normalize signal input into a fixed-length latent vector.
        - Strings: character-normalized embedding.
        - Iterables: numeric normalization.
        - Dict: hashes keys/values into a vector.
        """
        if isinstance(signal, str):
            return self._encode_text(signal)
        if isinstance(signal, dict):
            return self._encode_dict(signal)
        if isinstance(signal, Iterable):
            return self._encode_iterable(signal)
        return np.zeros(self.latent_dim)

    def _encode_text(self, txt: str) -> np.ndarray:
        vec = np.zeros(self.latent_dim)
        for idx, ch in enumerate(txt[: self.latent_dim]):
            vec[idx] = (ord(ch) % 255) / 255.0
        return vec

    def _encode_iterable(self, data: Iterable[Any]) -> np.ndarray:
        seq = list(data)
        try:
            arr = np.array(seq, dtype=float)
        except (ValueError, TypeError):
            joined = " ".join(str(item) for item in seq)
            return self._encode_text(joined)

        if arr.size == 0:
            return np.zeros(self.latent_dim)
        scaled = np.interp(arr, (arr.min(), arr.max()), (-1, 1)) if arr.max() != arr.min() else arr
        vec = np.zeros(self.latent_dim)
        limit = min(self.latent_dim, scaled.size)
        vec[:limit] = scaled[:limit]
        return vec

    def _encode_dict(self, data: Dict[str, Any]) -> np.ndarray:
        pairs = [f"{k}:{v}" for k, v in sorted(data.items())]
        joined = "|".join(pairs)
        return self._encode_text(joined)
