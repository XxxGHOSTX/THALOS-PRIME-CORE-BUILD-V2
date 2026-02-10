"""
Symbolic-Behavioral Interface (SBI) reasoning wrapper.
"""

from __future__ import annotations

import numpy as np
from typing import Dict


class SBIEngine:
    """Combines input and shard vectors to generate a reasoning vector."""

    def resolve(self, input_vec: np.ndarray, shard_vec: np.ndarray) -> Dict[str, np.ndarray]:
        if input_vec is None:
            input_vec = np.zeros_like(shard_vec)
        if shard_vec is None:
            shard_vec = np.zeros_like(input_vec)

        limit = min(input_vec.shape[0], shard_vec.shape[0])
        combined = np.zeros(limit)
        combined[:limit] = (input_vec[:limit] + shard_vec[:limit]) * 0.5

        coherence = float(np.mean(np.abs(combined))) if combined.size else 0.0

        return {
            "combined_vector": combined,
            "coherence": coherence,
        }
