"""
Intent resolver wrapper for cognitive inference.
"""

from __future__ import annotations

from inference_network.cognitive_net import CognitiveInferenceNet


class IntentResolver:
    """Lightweight wrapper around CognitiveInferenceNet."""

    def __init__(self):
        self.net = CognitiveInferenceNet()

    def resolve(self, text: str, context=None):
        return self.net.infer(text, ctx_data=context or {})
