"""
Matrix Codex SBI engine with Library of Babel integration.
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict

from interface.encoder import NeuralEncoder
from interface.decoder import NeuralDecoder
from lob_db.loader import LoBLoader, load_default_loader
from src.intent_resolver import IntentResolver
from src.predictive_engine import PredictiveEngine
from src.semantic_store import SemanticMemory
from src.sbi_engine import SBIEngine
from synapse_matrix.bio_synthesizer import BioSynthesizer


class MatrixCodex:
    """Core SBI model with LoB-aware reasoning."""
    DEFAULT_QUERY_KEY = "mind_signal"

    def __init__(
        self,
        lob_loader: LoBLoader | None = None,
        semantic_memory: SemanticMemory | None = None,
    ):
        self.encoder = NeuralEncoder()
        self.decoder = NeuralDecoder()
        self.intent_resolver = IntentResolver()
        self.predictive = PredictiveEngine()
        self.semantic_store = semantic_memory or SemanticMemory()
        self.lob = lob_loader or load_default_loader()
        self.sbi_engine = SBIEngine(latent_dim=self.encoder.latent_dim)
        self.bio = BioSynthesizer(2_000_000)

    def forward(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main forward path:
        - Encode text and LoB shard
        - Run SBI resolution
        - Decode and assemble response
        """
        key = input_dict.get("text", "")
        shard = self.lob.get_shard(key or "default")
        shard_vec = self.encoder.encode(shard.get("entries", []))
        self.semantic_store.store_shard(key or "default", shard_vec)

        latent_vector = input_dict.get("latent") or self.encoder.encode(key)
        sbi_result = self.sbi_engine.resolve(latent_vector, shard_vec)

        # Intent + predictive tuning
        intent = self.intent_resolver.resolve(key, input_dict.get("context"))
        predictive = self.predictive.adjust(intent.get("certainty", 0.5), sbi_result["coherence"])

        # Feed through BioSynthesizer for contextual certainty
        biosynth_resp = self.bio.infer_query(key or self.DEFAULT_QUERY_KEY, {"intent": intent})

        decoded = self.decoder.decode(
            sbi_result["combined_vector"],
            {
                "intent": intent,
                "shard": shard.get("__shard_id"),
                "predictive": predictive,
            },
        )

        return {
            "text": decoded["text"],
            "certainty": predictive["certainty"],
            "sbi_vector": sbi_result["combined_vector"],
            "coherence": sbi_result["coherence"],
            "biosynth": biosynth_resp,
            "meta": decoded["meta"],
        }


class MatrixCodexLoB(MatrixCodex):
    """Explicit LoB-specialized subclass for clarity."""

    def __init__(self, lob_loader: LoBLoader):
        super().__init__(lob_loader=lob_loader)
        self.lob_mode = True

    def forward(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = super().forward(input_dict)
        meta = result.get("meta", {})
        meta["lob_mode"] = True
        result["meta"] = meta
        return result
