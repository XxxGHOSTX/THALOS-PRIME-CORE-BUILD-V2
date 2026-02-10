"""
Predictive adjustment engine for SBI responses.
"""

from __future__ import annotations

from typing import Dict


class PredictiveEngine:
    """Applies lightweight self-tuning to certainty scores."""

    def adjust(self, certainty: float, semantic_coverage: float = 0.0) -> Dict[str, float]:
        base = certainty
        # Encourage outputs when semantic coverage is strong
        tuned = base + (semantic_coverage * 0.1)
        tuned = max(0.05, min(0.99, tuned))
        return {
            "certainty": tuned,
            "coverage": semantic_coverage,
        }
