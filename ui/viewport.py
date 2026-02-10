"""
Floating viewport wrapper that reuses the existing DynamicViewport implementation.
"""

try:
    from viewport_canvas.dynamic_viewport import DynamicViewport
except Exception:  # pragma: no cover - optional GUI dependency
    DynamicViewport = None


class FloatingViewport:
    """Thin abstraction around the interactive viewport."""

    def __init__(self, query_fn):
        self.query_fn = query_fn
        self._impl = DynamicViewport(query_fn) if DynamicViewport else None

    def start(self):
        if self._impl:
            self._impl.start()

    def stop(self):
        if self._impl:
            self._impl.stop()
