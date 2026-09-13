"""Low-overhead stage totals for benchmark components, flushed once at process exit."""

from __future__ import annotations

import atexit
import json
import os
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

TOTALS: dict[str, float] = defaultdict(float)
CALLS: dict[str, int] = defaultdict(int)


@contextmanager
def stage(name: str):
    started = time.perf_counter()
    try:
        yield
    finally:
        TOTALS[name] += time.perf_counter() - started
        CALLS[name] += 1


def flush() -> None:
    root = os.environ.get("VQAPR_BENCH_TIMINGS")
    if not root or not TOTALS:
        return
    destination = Path(root)
    destination.mkdir(parents=True, exist_ok=True)
    payload = {
        "pid": os.getpid(),
        "seconds": {key: round(value, 6) for key, value in sorted(TOTALS.items())},
        "calls": dict(sorted(CALLS.items())),
    }
    (destination / f"component-{os.getpid()}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


atexit.register(flush)
