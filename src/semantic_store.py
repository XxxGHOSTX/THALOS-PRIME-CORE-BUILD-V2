"""
Semantic memory layer with shard caching.
"""

from __future__ import annotations

from typing import Any, Dict

from cognition_store.persistence import CognitionVault


class SemanticMemory:
    """Caches shard vectors and persists snapshots via CognitionVault."""

    def __init__(self, vault: CognitionVault | None = None):
        self.vault = vault or CognitionVault("semantic_memory.db")
        self.memory: Dict[str, Any] = {}

    def store_shard(self, key: str, shard_vector: Any) -> None:
        vector_payload = shard_vector.tolist() if hasattr(shard_vector, "tolist") else shard_vector
        self.memory[key] = vector_payload
        self.vault.save_snapshot(f"lob::{key}", {"vector": vector_payload})

    def retrieve_shard(self, key: str):
        if key in self.memory:
            return self.memory[key]
        snap = self.vault.load_snapshot(f"lob::{key}")
        if snap:
            return snap.get("vector")
        return None
