"""
Library of Babel loader
Splits the corpus into deterministic shards for lightweight retrieval.
"""

import json
import os
from hashlib import sha256
from typing import Any, Dict, List


class LoBLoader:
    """Minimal shard loader for Library of Babel assets."""

    def __init__(self, path: str = None):
        base_path = path or os.path.join(os.path.dirname(__file__), "shards")
        self.path = base_path
        self.shards: List[str] = [
            os.path.join(base_path, f)
            for f in os.listdir(base_path)
            if f.endswith(".json")
        ]
        # Keep shards deterministic for a given key
        self.shards.sort()

    def get_shard(self, key: str) -> Dict[str, Any]:
        """Return shard payload based on a deterministic hash of the key."""
        if not self.shards:
            return {"entries": [], "meta": {}}

        shard_index = int(sha256(key.encode()).hexdigest(), 16) % len(self.shards)
        shard_path = self.shards[shard_index]

        with open(shard_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        payload["__shard_id"] = os.path.basename(shard_path)
        return payload


def load_default_loader() -> LoBLoader:
    """Helper to create a loader with the default shard path."""
    return LoBLoader()
