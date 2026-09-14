"""Read a few real rows out of the traced project, for the tables the page shows beside a frame.

    uv run python experiments/exp_280_the_scenario_trace_0_16_0/probe_data.py PROJECT RUNS OUT.json

PROJECT is the traced sample project; RUNS is the copy of its `.vqapr/runs/` taken before the
`--jobs` batch rewrote two of them. Every preview is the file's own rows, cut to a few; nothing is
made up. Times are shown in the venue's zone (Asia/Seoul).
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow.parquet as pq

SEOUL = ZoneInfo("Asia/Seoul")


def cell(value: object) -> str:
    if isinstance(value, datetime):
        return value.astimezone(SEOUL).strftime("%Y-%m-%d %H:%M")
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return str(value)


def table(
    path: Path, *, where=None, limit: int = 4, title: str, columns: list[str] | None = None
) -> dict:
    data = pq.read_table(path)
    names = columns or list(data.column_names)
    rows = data.to_pylist()
    total = len(rows)
    if where is not None:
        rows = [row for row in rows if where(row)]
    shown = rows[:limit]
    return {
        "title": title,
        "columns": names,
        "types": {f.name: str(f.type) for f in data.schema if f.name in names},
        "rows": [[cell(row[name]) for name in names] for row in shown],
        "note": f"{len(rows)}행 중 {len(shown)}행"
        + ("" if where is None else f" (전체 {total}행)"),
    }


def at(prefix: str):
    return lambda row: cell(row.get("event_time") or row.get("available_at")).startswith(prefix)


def ledger_block(workspace: Path, dataset: str) -> dict:
    lines = workspace.read_text(encoding="utf-8").splitlines()
    start = lines.index(f"  {dataset}:")
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if (line.startswith("  ") and not line.startswith("    ")) or not line.startswith(" "):
            break
        block.append(line)
    return {"title": f".vqapr/workspace.yaml — datasets.{dataset}", "text": "\n".join(block)}


def json_excerpt(path: Path, keys: list[str], title: str) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {
        "title": title,
        "text": json.dumps({k: doc[k] for k in keys if k in doc}, ensure_ascii=False, indent=1)[
            :900
        ],
    }


if __name__ == "__main__":
    project, runs, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    vq = project / ".vqapr"
    factor = runs / "sample-factor-run" / "strategies" / "sample-factor@0696c8f4"
    stop = next((runs / "sample-stoploss-run" / "strategies").iterdir())
    enhanced = next((runs / "sample-enhanced-run" / "strategies").iterdir())
    previews = {
        "roster": table(
            project / "instruments_stock.parquet",
            limit=5,
            title="sample/instruments_stock.parquet — 종목 명단",
        ),
        "prices": table(
            project / "observations.parquet",
            limit=3,
            title="sample/observations.parquet — 일봉 가격",
        ),
        "execution": table(
            project / "execution.parquet", limit=3, title="sample/execution.parquet — 체결표"
        ),
        "ledger_prices": ledger_block(vq / "workspace.yaml", "sample-prices"),
        "ledger_execution": ledger_block(vq / "workspace.yaml", "sample-execution"),
        "features": table(
            vq / "materialized" / "sample-features" / "all.parquet",
            limit=4,
            title=".vqapr/materialized/sample-features/all.parquet — DataModel 출력",
        ),
        "run_json": json_excerpt(
            runs / "sample-factor-run" / "run.json",
            ["run_id", "period", "datasets", "writes"],
            "runs/sample-factor-run/run.json — 표지",
        ),
        "factor_weight": table(
            factor / "tables" / "vqapr.weight" / "all.parquet",
            where=at("2022-01-12 08:00"),
            limit=6,
            columns=["event_time", "instrument", "weight"],
            title="vqapr.weight — 01-12 08:00 결정",
        ),
        "factor_fill": table(
            factor / "tables" / "vqapr.fill" / "all.parquet",
            where=at("2022-01-12 15:30"),
            limit=6,
            columns=["event_time", "instrument", "requested_quantity", "dealt_quantity", "price"],
            title="vqapr.fill — 01-12 15:30 체결",
        ),
        "factor_account": table(
            factor / "tables" / "vqapr.account" / "all.parquet",
            where=at("2022-01-12 15:30"),
            limit=7,
            columns=["event_time", "instrument", "quantity", "price", "cash", "nav"],
            title="vqapr.account — 01-12 15:30 평가",
        ),
        "stop_last": table(
            stop / "tables" / "vqapr.fill" / "all.parquet",
            where=at("2022-02-23"),
            limit=3,
            columns=["event_time", "instrument", "requested_quantity", "dealt_quantity", "price"],
            title="vqapr.fill — 02-23 마지막 매도",
        ),
        "stop_weight": table(
            stop / "tables" / "vqapr.weight" / "all.parquet",
            where=at("2022-01-05 08:00"),
            limit=8,
            columns=["event_time", "instrument", "weight"],
            title="vqapr.weight — 01-05 08:00 (K000005 빠짐)",
        ),
        "enhanced_weight": table(
            vq / "materialized" / "sample-enhanced-weights" / "all.parquet",
            where=at("2022-01-13 09:00"),
            limit=9,
            title="sample-enhanced-weights — 01-13 09:00",
        ),
        "factor_alpha": table(
            vq / "materialized" / "sample-factor-weights" / "all.parquet",
            where=at("2022-01-13 08:00"),
            limit=6,
            title="sample-factor-weights — 01-13 08:00 (alpha)",
        ),
    }

    from vqapr.run.batch import _bake_for_batch, batch_reads
    from vqapr.workspace.registry import Workspace

    baked = Path(tempfile.mkdtemp(prefix="cubes-"))
    try:
        workspace = Workspace.open(project)
        _bake_for_batch(
            workspace, batch_reads(workspace, ["sample-factor-run", "sample-stoploss-run"]), baked
        )
        rows = []
        for path in sorted(baked.rglob("*")):
            if path.is_file():
                shape = str(np.load(path, mmap_mode="r").shape) if path.suffix == ".npy" else ""
                rows.append(
                    [
                        str(path.relative_to(baked)).replace("\\", "/"),
                        f"{path.stat().st_size:,} B",
                        shape,
                    ]
                )
        previews["cube"] = {
            "title": ".vqapr/cubes/<batch>/ — 구운 파일 (probe로 다시 구움)",
            "columns": ["file", "size", "shape"],
            "rows": rows,
            "note": f"{len(rows)}개",
        }
    finally:
        shutil.rmtree(baked, ignore_errors=True)

    out.write_text(json.dumps(previews, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v.get("note", "text") for k, v in previews.items()})
