"""exp_280's `trace_io.py`, with the values written in plain notation.

    uv run python experiments/exp_282_the_scenario_trace_registration_cleanup/trace_io.py OUT.json \
        --want WANT.json --name 01_register --project DIR \
        -- --project-root DIR register DIR/sample.yaml
    uv run python experiments/exp_282_the_scenario_trace_registration_cleanup/trace_io.py OUT.json \
        --want WANT.json --name 16_worker_factor --project DIR \
        --worker sample-factor-run --with sample-stoploss-run

Everything is exp_280's -- the same calls are counted, so `#idx` means the same thing -- except
how a list, tuple, set or mapping is described. exp_280 wrote `list[1] [x]`, which reads like
"item 1 of a list". Here a container is written the way it looks: `[x]`, `[a, b, c]`,
`[a, … 12개]`, `(a, b)`, `{k: v, … 5개}`; below the second level only the count, `[12개]`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Mapping, Set
from pathlib import Path

# exp_280's tracer, reused whole. Loaded from its file under its own name: this module is also
# called `trace_io`, so a plain import would find itself.
_spec = importlib.util.spec_from_file_location(
    "trace_io_280",
    Path(__file__).resolve().parents[1] / "exp_280_the_scenario_trace_0_16_0" / "trace_io.py",
)
assert _spec is not None and _spec.loader is not None
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

_original = base._describe
_BRACKETS = {list: ("[", "]"), tuple: ("(", ")")}


def _plain(value: object, depth: int) -> str:
    if isinstance(value, Mapping):
        n = len(value)
        if n == 0:
            return "{}"
        if depth >= 2:
            return f"{{{n}개}}"
        body = ", ".join(
            f"{_plain(k, depth + 1)}: {_plain(v, depth + 1)}" for k, v in list(value.items())[:3]
        )
        return "{" + body + (f", … {n}개" if n > 3 else "") + "}"
    if isinstance(value, list | tuple | Set):
        opening, closing = next(
            (pair for kind, pair in _BRACKETS.items() if isinstance(value, kind)), ("{", "}")
        )
        n = len(value)
        if n == 0:
            return "set()" if opening == "{" else opening + closing
        if depth >= 2:
            return f"{opening}{n}개{closing}"
        if n <= 3:
            return opening + ", ".join(_plain(item, depth + 1) for item in value) + closing
        return f"{opening}{_plain(next(iter(value)), depth + 1)}, … {n}개{closing}"
    return _original(value, depth)


# `describe` and the fallback inside `_original` look `_describe` up in base's globals, so nested
# values go through `_plain` as well.
base._describe = _plain


if __name__ == "__main__":
    arguments = sys.argv[1:]
    head, tail = (
        (arguments[: arguments.index("--")], arguments[arguments.index("--") + 1 :])
        if "--" in arguments
        else (arguments, [])
    )
    out_path = Path(head[0])
    name = head[head.index("--name") + 1]
    want_file = Path(head[head.index("--want") + 1])
    wanted_names = set(json.loads(want_file.read_text(encoding="utf-8")).get(name, []))
    project_dir = Path(head[head.index("--project") + 1]) if "--project" in head else None
    if "--worker" in head:
        run = head[head.index("--worker") + 1]
        with_runs = [head[i + 1] for i, a in enumerate(head) if a == "--with"]
        assert project_dir is not None
        base.trace_worker(out_path, project_dir, run, with_runs, wanted_names)
    else:
        raise SystemExit(base.trace_cli(tail, out_path, project_dir, wanted_names))
