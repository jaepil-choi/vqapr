"""Create one clean installed-user project from the frozen experiment inputs."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

STRATEGIES = {
    "six-week-momentum": "SixWeekMomentum",
    "balanced-factors": "BalancedFactors",
    "value-quality": "ValueQuality",
    "low-vol-momentum": "LowVolMomentum",
    "earnings-momentum": "EarningsMomentum",
}

FIELDS = {
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


def dataset(input_dir: Path, name: str, fields: tuple[str, ...]) -> dict:
    return {
        "source_id": f"{name}-source",
        "path": str((input_dir / f"{name}.parquet").resolve()),
        "instrument_field": "instrument",
        "available_at": "available_at",
        "grain": "instrument_instant",
        "key_fields": ["available_at", "instrument"],
        "fields": {field: field for field in fields},
        "field_types": {field: "DOUBLE" for field in fields},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--instrument-limit", type=int, default=0)
    parser.add_argument("--session-limit", type=int, default=0)
    args = parser.parse_args()

    root = args.root.resolve()
    input_dir = args.input.resolve()
    templates = args.templates.resolve()
    root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(templates / "strategy.py", root / "strategy.py")
    shutil.copy2(templates / "exchange.py", root / "exchange.py")

    prices = pq.read_table(input_dir / "prices.parquet", columns=["available_at", "instrument"])
    instruments = sorted(value.as_py() for value in pc.unique(prices["instrument"]))
    sessions = sorted(value.as_py() for value in pc.unique(prices["available_at"]))
    if args.instrument_limit:
        instruments = instruments[: args.instrument_limit]
    if args.session_limit:
        sessions = sessions[: args.session_limit]
    start_index = min(40, len(sessions) - 1)
    start = sessions[start_index].isoformat()
    end = sessions[-1].isoformat()

    roster = pa.table(
        {
            "instrument_id": instruments,
            "kind": ["stock"] * len(instruments),
        }
    )
    pq.write_table(roster, root / "instruments_stock.parquet", compression="zstd")

    datasets = {
        name: dataset(input_dir, name, fields) for name, fields in FIELDS.items()
    }
    datasets["execution"] = {
        **dataset(input_dir, "execution", ("close",)),
        "fields": {"close": "close", "is_tradable": "is_tradable"},
        "field_types": {"close": "DOUBLE", "is_tradable": "BOOLEAN"},
        "execution": {"is_tradable": "is_tradable"},
    }
    components = {
        strategy_id: {
            "kind": "strategy",
            "path": "strategy.py",
            "object_name": object_name,
        }
        for strategy_id, object_name in STRATEGIES.items()
    }
    components["research-exchange"] = {
        "kind": "exchange",
        "path": "exchange.py",
        "object_name": "ResearchExchange",
        "config": {"instruments": instruments},
    }
    runs = {}
    for strategy_id in STRATEGIES:
        runs[strategy_id] = {
            "instruments": instruments,
            "start": start,
            "end": end,
            "timezone": "Asia/Seoul",
            "agenda": {"every": "1w", "at": "08:30"},
            "exchange": "research-exchange",
            "execution": {
                "dataset": "execution",
                "trade_price": "close",
                "fill": {"at": "15:30"},
            },
            "initial_account": {
                "cash": "100000000000",
                "mode": "SIGNED",
                "positions": {},
            },
            "writes": f"{strategy_id}-weights",
            "strategy": {"component": strategy_id},
        }
    declaration = {
        "instruments": {"tables": {"stock": "instruments_stock.parquet"}},
        "datasets": datasets,
        "components": components,
        "runs": runs,
    }
    (root / "project.yaml").write_text(
        yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
    )
    manifest = {
        "input": str(input_dir),
        "instruments": len(instruments),
        "sessions": len(sessions),
        "start": start,
        "end": end,
        "runs": list(runs),
    }
    (root / "fixture.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
