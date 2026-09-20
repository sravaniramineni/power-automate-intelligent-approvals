"""Idempotency + retry helpers for approval workflows."""
import time
import uuid

_seen: dict[str, dict] = {}

def dedupe(key: str | None, result: dict) -> tuple[bool, dict]:
    """Return (is_duplicate, result). Generates a key when missing."""
    key = key or str(uuid.uuid4())
    if key in _seen:
        return True, {"status": "duplicate", "original": _seen[key]}
    _seen[key] = result
    return False, result

def with_retry(fn, attempts: int = 3, base_delay: float = 0.5):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - retry transient failures
            last = e
            time.sleep(base_delay * (2 ** i))
    raise last
