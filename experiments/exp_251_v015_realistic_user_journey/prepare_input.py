"""Split the frozen DW-derived panel into the tables a realistic user registers.

All writes stay under this experiment's outputs directory. The source is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

GROUPS = {
    "prices": ("close", "volume", "turnover_value"),
    "valuation": ("beta", "forward_per", "pbr", "ev_ebitda"),
    "consensus": (
        "forward_net_income",
        "consensus_sales",
        "consensus_operating_income",
        "consensus_net_income",
    ),
    "shares": ("shares",),
    "membership": ("k200_weight",),
}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--instrument-limit", type=int, default=1800)
    parser.add_argument("--session-limit", type=int, default=0)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parquet = pq.ParquetFile(source)
    instruments = sorted(
        value.as_py() for value in pc.unique(parquet.read(columns=["instrument"])["instrument"])
    )[: args.instrument_limit]
    sessions = sorted(
        value.as_py() for value in pc.unique(parquet.read(columns=["session"])["session"])
    )
    if args.session_limit:
        sessions = sessions[: args.session_limit]
    chosen = pa.array(instruments)
    last_session = sessions[-1]
    writers: dict[str, pq.ParquetWriter] = {}
    rows = 0
    try:
        for index in range(parquet.num_row_groups):
            table = parquet.read_row_group(index)
            keep = pc.and_(
                pc.is_in(table["instrument"], value_set=chosen),
                pc.less_equal(table["session"], pa.scalar(last_session)),
            )
            table = table.filter(keep)
            if not len(table):
                continue
            midnight = pc.cast(table["session"], pa.timestamp("us"))
            available_at = pc.cast(
                pc.add(midnight, pa.scalar(23_400_000_000, type=pa.duration("us"))),
                pa.timestamp("us", tz="UTC"),
            )
            base = pa.table(
                {
                    "available_at": available_at,
                    "instrument": table["instrument"],
                }
            )
            for group, fields in GROUPS.items():
                part = base
                for field in fields:
                    part = part.append_column(field, table[field])
                path = output / f"{group}.parquet"
                if group not in writers:
                    writers[group] = pq.ParquetWriter(path, part.schema, compression="zstd")
                writers[group].write_table(part)
            tradable = pc.and_(pc.is_valid(table["close"]), pc.greater(table["close"], 0.0))
            execution = base.append_column("close", table["close"]).append_column(
                "is_tradable", tradable
            )
            if "execution" not in writers:
                writers["execution"] = pq.ParquetWriter(
                    output / "execution.parquet", execution.schema, compression="zstd"
                )
            writers["execution"].write_table(execution)
            rows += len(table)
    finally:
        for writer in writers.values():
            writer.close()

    manifest = {
        "source": str(source),
        "source_sha256": digest(source),
        "rows": rows,
        "sessions": len(sessions),
        "instruments": len(instruments),
        "first_session": str(sessions[0]),
        "last_session": str(sessions[-1]),
        "tables": {
            path.name: {"bytes": path.stat().st_size, "sha256": digest(path)}
            for path in sorted(output.glob("*.parquet"))
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
