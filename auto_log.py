"""Fallback shim for PaddleOCR optional dependency `auto_log`.

Some PaddleOCR code paths import `AutoLogger` conditionally. The GUI tool
does not rely on benchmark logging, so a no-op implementation is sufficient.
"""


class AutoLogger:
    def __init__(self, *args, **kwargs):
        pass

    def report(self, *args, **kwargs):
        return None
