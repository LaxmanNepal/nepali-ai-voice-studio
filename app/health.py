from __future__ import annotations

import os
import time

from .config import BACKENDS
from .runtime import runtime_summary


_STARTED_AT = time.time()


def health_payload() -> dict:
    runtime = runtime_summary()
    return {
        "status": "ok",
        "service": "nepali-ai-voice-studio",
        "backends": len(BACKENDS),
        "uptime_seconds": round(time.time() - _STARTED_AT, 1),
        "runtime": runtime,
        "environment": os.getenv("SPACE_ID") and "huggingface-space" or "generic",
    }
