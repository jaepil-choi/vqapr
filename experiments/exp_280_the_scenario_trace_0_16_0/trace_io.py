"""Trace one command as `exp_230/trace.py` does, and also record what went in and what came out.

    uv run python experiments/exp_280_the_scenario_trace_0_16_0/trace_io.py OUT.json \
        --want WANT.json --name 01_register --project DIR \
        -- --project-root DIR register DIR/sample.yaml
    uv run python experiments/exp_280_the_scenario_trace_0_16_0/trace_io.py OUT.json \
        --want WANT.json --name 16_worker_factor --project DIR \
        --worker sample-factor-run --with sample-stoploss-run

Every call is recorded exactly as exp_230 records it, so `#idx` counts the same calls. For a call
whose qualname is listed under WANT[name], two more fields: `args` -- each parameter at call time --
and `ret` -- the value returned -- as a short description of the value's shape (type, size, a few
fields, the first item), never a full repr. The descriptions are taken inside the profile function,
where CPython does not profile, so they add nothing to the count.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import decimal
import enum
import io
import json
import shutil
import sys
import tempfile
import time
import types
from collections.abc import Callable, Mapping, Set
from contextlib import redirect_stdout
from pathlib import Path, PurePath

REPO = Path(__file__).resolve().parents[2]
SRC = str(REPO / "src" / "vqapr")
sys.path.insert(0, str(REPO / "experiments" / "exp_230_the_spine_trace"))
from trace import INTERESTING_LOCALS, _short  # noqa: E402 - the shared profiler's pieces

LIMIT = 220
_project = ""


def _path(value: object) -> str:
    text = str(value).replace("\\", "/")
    if _project and text.startswith(_project):
        return "sample" + text[len(_project) :]
    at = text.find("/src/vqapr/")
    if at >= 0:
        return text[at + 1 :]
    return text if len(text) <= 60 else "…" + text[-57:]


def _fields(value: object) -> list[str]:
    if dataclasses.is_dataclass(value):
        return [f.name for f in dataclasses.fields(value)]
    model = getattr(type(value), "model_fields", None)
    if isinstance(model, dict):
        return list(model)
    slots: list[str] = []
    for klass in type(value).__mro__:
        own = getattr(klass, "__slots__", ())
        slots += [own] if isinstance(own, str) else [s for s in own if not s.startswith("__")]
    if slots:
        return slots
    attrs = getattr(value, "__dict__", None)
    return [k for k in attrs if not k.startswith("__")] if isinstance(attrs, dict) else []


def _describe(value: object, depth: int) -> str:
    if value is None or isinstance(value, bool | int | float):
        text = repr(value)
        return text if len(text) <= 40 else text[:39] + "…"
    if isinstance(value, decimal.Decimal):
        return str(value)
    if isinstance(value, str):
        text = value.replace("\\", "/")
        if _project:
            text = text.replace(_project, "sample")
        return repr(text if len(text) <= 70 else text[:67] + "…")
    if isinstance(value, bytes | bytearray):
        return f"bytes[{len(value)}]"
    if isinstance(value, dt.datetime):
        return value.isoformat(sep=" ", timespec="minutes")
    if isinstance(value, dt.date | dt.time):
        return value.isoformat()
    if isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    if isinstance(value, PurePath):
        return f"Path({_path(value)})"
    if isinstance(value, type):
        return f"class {value.__name__}"
    if isinstance(value, types.FunctionType | types.MethodType | types.BuiltinFunctionType):
        return f"fn {getattr(value, '__qualname__', '?')}"
    if isinstance(value, types.GeneratorType):
        return "generator"
    kind = type(value)
    module = kind.__module__ or ""
    if (
        module.startswith("pyarrow")
        and hasattr(value, "num_rows")
        and hasattr(value, "column_names")
    ):
        columns = list(value.column_names)
        more = ", …" if len(columns) > 6 else ""
        return f"pa.Table {value.num_rows}행 [{', '.join(columns[:6])}{more}]"
    if module.startswith("numpy"):
        if getattr(value, "ndim", 0):
            return f"ndarray{tuple(value.shape)} {value.dtype}"
        return repr(value.item()) if hasattr(value, "item") else kind.__name__
    if module.startswith(("duckdb", "threading", "_thread", "io")):
        return kind.__name__
    if isinstance(value, Mapping):
        n = len(value)
        if n == 0:
            return "{}"
        if depth >= 2:
            return f"{{{n}개}}"
        items = list(value.items())[:3]
        body = ", ".join(f"{_describe(k, depth + 1)}: {_describe(v, depth + 1)}" for k, v in items)
        return "{" + body + (f", … {n}개" if n > 3 else "") + "}"
    if isinstance(value, list | tuple | Set):
        n = len(value)
        name = "list" if isinstance(value, list) else "tuple" if isinstance(value, tuple) else "set"
        if n == 0:
            return f"{name}[]"
        if depth >= 2:
            return f"{name}[{n}]"
        if n <= 3:
            return f"{name}[" + ", ".join(_describe(v, depth + 1) for v in value) + "]"
        return f"{name}[{n}] [{_describe(next(iter(value)), depth + 1)}, …]"
    name = kind.__name__
    if depth >= 2:
        return name
    parts: list[str] = []
    for field in _fields(value)[:4]:
        try:
            item = getattr(value, field)
        except Exception:
            continue
        if callable(item) and not isinstance(item, type):
            continue
        parts.append(f"{field.lstrip('_')}={_describe(item, depth + 1)}")
    return f"{name}({', '.join(parts)})" if parts else name


def describe(value: object) -> str:
    try:
        text = _describe(value, 0)
    except Exception:
        text = f"<{type(value).__name__}>"
    return text if len(text) <= LIMIT else text[: LIMIT - 1] + "…"


def _parameters(code: types.CodeType) -> tuple[str, ...]:
    count = code.co_argcount + code.co_kwonlyargcount
    count += bool(code.co_flags & 0x04) + bool(code.co_flags & 0x08)  # *args, **kwargs
    return code.co_varnames[:count]


def profiled(
    run: Callable[[], object], project: Path | None, wanted: set[str]
) -> tuple[list, object, float]:
    global _project
    calls: list[dict[str, object]] = []
    open_frames: dict[int, tuple[int, float]] = {}
    counter = 0
    depth = 0
    project_str = str(project.resolve()) if project else None
    _project = project_str.replace("\\", "/") if project_str else ""

    def profiler(frame, event, arg):
        nonlocal counter, depth
        code = frame.f_code
        filename = code.co_filename
        ours = filename.startswith(SRC) or (
            project_str is not None and filename.startswith(project_str)
        )
        if event == "call":
            depth += 1
            if not ours:
                return
            idx = counter
            counter += 1
            qualname = getattr(code, "co_qualname", code.co_name)
            entry: dict[str, object] = {
                "idx": idx,
                "depth": depth,
                "file": str(Path(filename).relative_to(REPO)).replace("\\", "/")
                if filename.startswith(str(REPO))
                else filename,
                "line": code.co_firstlineno,
                "qualname": qualname,
                "ms": None,
                "locals": {
                    name: _short(frame.f_locals[name])
                    for name in INTERESTING_LOCALS
                    if name in frame.f_locals
                },
                "author": project_str is not None and filename.startswith(project_str),
            }
            if qualname in wanted:
                entry["args"] = {
                    name: (
                        type(frame.f_locals[name]).__name__
                        if name in ("self", "cls")
                        else describe(frame.f_locals[name])
                    )
                    for name in _parameters(code)
                    if name in frame.f_locals
                }
            calls.append(entry)
            open_frames[id(frame)] = (len(calls) - 1, time.perf_counter())
        elif event == "return":
            depth -= 1
            started = open_frames.pop(id(frame), None)
            if started is not None:
                position, t0 = started
                calls[position]["ms"] = round((time.perf_counter() - t0) * 1000, 3)
                if "args" in calls[position]:
                    calls[position]["ret"] = describe(arg)
        return None

    started = time.perf_counter()
    sys.setprofile(profiler)
    try:
        result = run()
    finally:
        sys.setprofile(None)
    return calls, result, time.perf_counter() - started


def trace_cli(argv: list[str], out: Path, project: Path | None, wanted: set[str]) -> int:
    from vqapr.cli.main import main

    buffer = io.StringIO()

    def run() -> object:
        with redirect_stdout(buffer):
            return main(argv)

    calls, code, elapsed = profiled(run, project, wanted)
    printed = buffer.getvalue().strip().splitlines()
    envelope: object = None
    if printed:
        try:
            envelope = json.loads(printed[-1])
        except json.JSONDecodeError:
            envelope = printed[-1]
    files: list[str] = []
    if project is not None and project.exists():
        for path in sorted(project.rglob("*")):
            if path.is_file() and ".venv" not in path.parts and "__pycache__" not in path.parts:
                files.append(str(path.relative_to(project)).replace("\\", "/"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "argv": argv,
                "exit": code,
                "elapsed_ms": round(elapsed * 1000, 1),
                "calls": calls,
                "envelope": envelope,
                "files_after": files,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    captured = sum(1 for c in calls if "args" in c)
    print(
        f"{out.name}: exit {code}, {len(calls)} calls, {captured} with io, {elapsed * 1000:.0f} ms",
        file=sys.stderr,
    )
    return int(code) if isinstance(code, int) else 0


def trace_worker(
    out: Path, project: Path, run_id: str, others: list[str], wanted: set[str]
) -> None:
    from vqapr.run.assemble import run_registered_strategy
    from vqapr.run.batch import _bake_for_batch, batch_reads
    from vqapr.workspace.registry import Workspace

    cubes = Path(tempfile.mkdtemp(prefix="cubes-", dir=project / ".vqapr"))
    workspace = Workspace.open(project)
    _bake_for_batch(workspace, batch_reads(workspace, [run_id, *others]), cubes)
    baked = sorted(
        str(p.relative_to(cubes)).replace("\\", "/") for p in cubes.rglob("*") if p.is_file()
    )
    try:
        calls, outcome, elapsed = profiled(
            lambda: run_registered_strategy(
                str(project), run_id, str(project / ".vqapr"), True, True, str(cubes)
            ),
            project,
            wanted,
        )
    finally:
        shutil.rmtree(cubes, ignore_errors=True)
    out.write_text(
        json.dumps(
            {
                "argv": ["<worker>", "run_registered_strategy", run_id, "cubes=<baked>"],
                "exit": 0 if outcome.status == "completed" else 1,
                "elapsed_ms": round(elapsed * 1000, 1),
                "calls": calls,
                "envelope": {
                    "ok": outcome.status == "completed",
                    "stage": "worker",
                    "status": outcome.status,
                    "cubes_baked": baked,
                },
                "files_after": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"{out.name}: {outcome.status}, {len(calls)} calls, {elapsed * 1000:.0f} ms",
        file=sys.stderr,
    )


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
        trace_worker(out_path, project_dir, run, with_runs, wanted_names)
    else:
        raise SystemExit(trace_cli(tail, out_path, project_dir, wanted_names))
