"""The installed vqapr's version, in one place.

The skills' install manifest, `vqapr.__version__`, `vqapr --version` and every record's
`package_version` read the same answer (testbed report 2026-09-15: nothing but the skill manifest
named the version, so records from two versions of the same strategy file could not be told
apart). It lives below every layer because the run layer stamps records with it and must not
import the agent layer to do so.
"""

from __future__ import annotations

from functools import cache
from importlib import metadata


@cache
def package_version() -> str:
    """The installed distribution's version, or `"unknown"` when it cannot be read.

    An editable install reports its version too. It is a receipt of what wrote a record, never a
    judgment: skill content is judged by hash, and a run's identity does not fold it.
    """
    try:
        return metadata.version("vqapr")
    except metadata.PackageNotFoundError:
        return "unknown"
