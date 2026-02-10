"""
Mind Interface Decoder
Maps latent vectors back into textual/UI friendly responses.
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict


class NeuralDecoder:
    """Decode latent vectors into human-readable output."""

    def __init__(self):
        self.temperature = 0.7

    def decode(self, vector: np.ndarray, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Convert latent vector back into a response payload.
        Generates a lightweight summary and surfaces supplied metadata.
        """
        energy = float(np.linalg.norm(vector)) if vector is not None else 0.0
        summary = f"Signal energy={energy:.3f}"

        return {
            "text": summary,
            "energy": energy,
            "meta": meta or {},
        }
