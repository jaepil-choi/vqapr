"""Trace one `--jobs` worker in this process: the strategy worker, given a directory of baked cubes.

`exp_238/trace_worker.py` on the 0.16.0 tree: `flow/orchestration.py` is `run/batch.py` (the bake)
and `run/assemble.py` (the worker function), `project/store.py` is `workspace/registry.py`
(records 273-274). What it does is unchanged. `exp_230/trace.py` traces a CLI command, and under
`--jobs` the driver spawns its workers, so the driver's trace ends at `in_workers` and never sees a
worker map a cube. This bakes the batch's cubes the way `batch_cubes` does (untraced, into a scratch
directory removed afterwards), then runs the function the pool would run --
`run_registered_strategy` -- under the same profiler:

    uv run python experiments/exp_280_the_scenario_trace_0_16_0/trace_worker.py OUT.json \
        --project DIR --run sample-factor-run --with sample-stoploss-run

`--with` names the other runs of the batch, so the bake covers what the batch would have read.
The record is replaced (`--force` semantics), as a batch run over a standing record would be.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "exp_230_the_spine_trace"))
from trace import INTERESTING_LOCALS, SRC, _short  # noqa: E402 - the shared profiler's pieces


def trace_worker(out: Path, project: Path, run_id: str, others: list[str]) -> None:
    from vqapr.run.assemble import run_registered_strategy
    from vqapr.run.batch import _bake_for_batch, batch_reads
    from vqapr.workspace.registry import Workspace

    # The store root is passed as the CLI passes it (unresolved); the profiler matches the
    # author's files by the resolved path the interpreter records.
    resolved = project.resolve()
    cubes = Path(tempfile.mkdtemp(prefix="cubes-", dir=project / ".vqapr"))
    workspace = Workspace.open(project)
    _bake_for_batch(workspace, batch_reads(workspace, [run_id, *others]), cubes)
    baked = sorted(
        str(p.relative_to(cubes)).replace("\\", "/") for p in cubes.rglob("*") if p.is_file()
    )

    calls: list[dict[str, object]] = []
    open_frames: dict[int, tuple[int, float]] = {}
    counter = 0
    depth = 0
    project_str = str(resolved)

    def profiler(frame, event, arg):
        nonlocal counter, depth
        code = frame.f_code
        filename = code.co_filename
        ours = filename.startswith(SRC) or filename.startswith(project_str)
        if event == "call":
            depth += 1
            if not ours:
                return
            idx = counter
            counter += 1
            entry: dict[str, object] = {
                "idx": idx,
                "depth": depth,
                "file": str(Path(filename).relative_to(REPO)).replace("\\", "/")
                if filename.startswith(str(REPO))
                else filename,
                "line": code.co_firstlineno,
                "qualname": getattr(code, "co_qualname", code.co_name),
                "ms": None,
                "locals": {
                    name: _short(frame.f_locals[name])
                    for name in INTERESTING_LOCALS
                    if name in frame.f_locals
                },
                "author": filename.startswith(project_str),
            }
            calls.append(entry)
            open_frames[id(frame)] = (len(calls) - 1, time.perf_counter())
        elif event == "return":
            depth -= 1
            started = open_frames.pop(id(frame), None)
            if started is not None:
                position, t0 = started
                calls[position]["ms"] = round((time.perf_counter() - t0) * 1000, 3)
        return None

    started = time.perf_counter()
    sys.setprofile(profiler)
    try:
        outcome = run_registered_strategy(
            str(project), run_id, str(project / ".vqapr"), True, True, str(cubes)
        )
    finally:
        sys.setprofile(None)
        shutil.rmtree(cubes, ignore_errors=True)
    elapsed = time.perf_counter() - started
    out.parent.mkdir(parents=True, exist_ok=True)
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
        f"{out.name}: {outcome.status}, {len(calls)} calls, {elapsed * 1000:.0f} ms, "
        f"cubes {len(baked)} files",
        file=sys.stderr,
    )


if __name__ == "__main__":
    arguments = sys.argv[1:]
    out_path = Path(arguments[0])
    project_dir = Path(arguments[arguments.index("--project") + 1])
    run = arguments[arguments.index("--run") + 1]
    with_runs = [arguments[i + 1] for i, a in enumerate(arguments) if a == "--with"]
    trace_worker(out_path, project_dir, run, with_runs)
