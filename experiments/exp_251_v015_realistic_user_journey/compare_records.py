"""Compare every economic table produced by two five-strategy user projects."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    baseline = args.baseline.resolve() / ".vqapr" / "runs"
    candidate = args.candidate.resolve() / ".vqapr" / "runs"
    compared = []
    ok = True
    for base_path in sorted(baseline.rglob("*.parquet")):
        relative = base_path.relative_to(baseline)
        candidate_path = candidate / relative
        base_table = pq.read_table(base_path)
        candidate_table = pq.read_table(candidate_path)
        equal = base_table.equals(candidate_table)
        ok &= equal
        compared.append(
            {
                "path": str(relative),
                "rows": base_table.num_rows,
                "columns": base_table.num_columns,
                "equal": equal,
                "byte_identical": digest(base_path) == digest(candidate_path),
            }
        )
    expected = sorted(str(path.relative_to(candidate)) for path in candidate.rglob("*.parquet"))
    actual = sorted(item["path"] for item in compared)
    same_files = actual == expected
    ok &= same_files
    result = {
        "ok": ok,
        "same_file_set": same_files,
        "tables": compared,
        "rows_total": sum(item["rows"] for item in compared),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
