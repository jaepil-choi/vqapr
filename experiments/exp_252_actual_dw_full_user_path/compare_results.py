"""Compare baseline, optimized, and direct experiment outputs without tolerance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

RUNS = (
    "six-week-momentum",
    "balanced-factors",
    "value-quality",
    "low-vol-momentum",
    "earnings-momentum",
)
TABLES = ("vqapr.account", "vqapr.fill", "vqapr.weight")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def store(root: Path) -> Path:
    nested = root / ".vqapr"
    return nested if nested.exists() else root


def strategy_table(root: Path, run: str, table: str) -> Path:
    matches = list(
        (store(root) / "runs" / run / "strategies").glob(f"*/tables/{table}/all.parquet")
    )
    if len(matches) != 1:
        raise RuntimeError(f"expected one {run}/{table}, found {len(matches)}")
    return matches[0]


def sorted_table(path: Path) -> pa.Table:
    table = pq.read_table(path)
    keys = [
        (name, "ascending")
        for name in ("available_at", "instrument", "trade_at", "event_id")
        if name in table.column_names
    ]
    if not keys:
        return table
    return pc.take(table, pc.sort_indices(table, sort_keys=keys))


def compare_exact(left: Path, right: Path) -> dict[str, object]:
    left_table = sorted_table(left)
    right_table = sorted_table(right)
    return {
        "left_rows": left_table.num_rows,
        "right_rows": right_table.num_rows,
        "schema_equal": left_table.schema.equals(right_table.schema),
        "values_equal": left_table.equals(right_table),
        "left_sha256": digest(left),
        "right_sha256": digest(right),
        "file_hash_equal": digest(left) == digest(right),
    }


def compare_economic(left: Path, right: Path) -> dict[str, object]:
    left_table = sorted_table(left)
    right_table = sorted_table(right)
    identity = {"producer_id", "run_id"}
    columns = [name for name in left_table.column_names if name not in identity]
    return {
        **compare_exact(left, right),
        "economic_values_equal": left_table.select(columns).equals(right_table.select(columns)),
        "ignored_identity_columns": sorted(identity),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--direct", type=Path, required=True)
    parser.add_argument("--sql", type=Path, required=True)
    parser.add_argument("--incremental", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result: dict[str, object] = {}
    result["datamodel"] = compare_exact(
        store(args.baseline) / "materialized/actual_daily_factors/all.parquet",
        store(args.candidate) / "materialized/actual_daily_factors/all.parquet",
    )
    strategy_results: dict[str, object] = {}
    direct_results: dict[str, object] = {}
    for run in RUNS:
        strategy_results[run] = {
            table: compare_exact(
                strategy_table(args.baseline, run, table),
                strategy_table(args.candidate, run, table),
            )
            for table in TABLES
        }
        direct_run = f"direct-{run}"
        direct_results[run] = {
            table: compare_economic(
                strategy_table(args.candidate, run, table),
                strategy_table(args.direct, direct_run, table),
            )
            for table in ("vqapr.account", "vqapr.fill")
        }
    result["strategies"] = strategy_results
    result["direct"] = direct_results
    candidate_factor = sorted_table(
        store(args.candidate) / "materialized/actual_daily_factors/all.parquet"
    )
    sql_factor = sorted_table(args.sql)
    result["sql"] = {
        "candidate_rows": candidate_factor.num_rows,
        "sql_rows": sql_factor.num_rows,
        "schema_equal": candidate_factor.schema.equals(sql_factor.schema),
        "values_equal": candidate_factor.equals(sql_factor),
    }
    incremental = sorted_table(args.incremental)
    first_instant = pc.min(incremental["available_at"]).as_py()
    candidate_tail = candidate_factor.filter(
        pc.greater_equal(candidate_factor["available_at"], first_instant)
    )
    result["incremental"] = {
        "candidate_tail_rows": candidate_tail.num_rows,
        "incremental_rows": incremental.num_rows,
        "schema_equal": candidate_tail.schema.equals(incremental.schema),
        "values_equal": candidate_tail.equals(incremental),
        "first_instant": first_instant.isoformat(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
