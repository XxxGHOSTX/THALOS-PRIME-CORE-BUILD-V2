"""
Pipeline orchestrator stitching encoder, Matrix Codex, and decoder.
"""

from __future__ import annotations

from typing import Any, Dict

from .matrix_codex import MatrixCodex
from interface.encoder import NeuralEncoder


class Orchestrator:
    """Full pipeline runner for mind/text inputs."""

    def __init__(self, codex: MatrixCodex | None = None):
        self.encoder = NeuralEncoder()
        self.codex = codex or MatrixCodex()

    def run_pipeline(self, text: str = "", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        latent = self.encoder.encode(text)
        payload = {"text": text, "context": context or {}, "latent": latent}
        return self.codex.forward(payload)
