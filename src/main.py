"""
Entry point for Matrix Codex + Mind Interface pipeline.
"""

from __future__ import annotations

from src.orchestrator import Orchestrator


def demo():
    orchestrator = Orchestrator()
    return orchestrator.run_pipeline("hello, who are you?")


if __name__ == "__main__":
    result = demo()
    print(result["text"])
    print(f"Certainty: {result['certainty']:.2f}")
