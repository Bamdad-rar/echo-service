from datetime import datetime, timezone
from typing import Callable

# Default implementation
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Pointer to the currently active clock function
_now_fn: Callable[[], datetime] = _utc_now

def now() -> datetime:
    """Current UTC time. Use this everywhere."""
    return _now_fn()

# Testing helper
class freeze_time:     # context-manager
    def __init__(self, fixed: datetime):
        self.fixed = fixed
        self._saved = None
    def __enter__(self):
        global _now_fn
        self._saved = _now_fn
        _now_fn = lambda: self.fixed
    def __exit__(self, *exc):
        global _now_fn
        _now_fn = self._saved
