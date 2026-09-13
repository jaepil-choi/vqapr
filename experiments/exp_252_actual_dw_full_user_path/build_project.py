"""Create the fixed first-time-user project and preserve the public scaffold evidence."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml

HERE = Path(__file__).resolve().parent
SCORES = {
    "six-week-momentum": ("SixWeekMomentum", "momentum_score"),
    "balanced-factors": ("BalancedFactors", "balanced_score"),
    "value-quality": ("ValueQuality", "value_quality_score"),
    "low-vol-momentum": ("LowVolMomentum", "low_vol_momentum_score"),
    "earnings-momentum": ("EarningsMomentum", "earnings_momentum_score"),
}
SCORE_FIELDS = [field for _, field in SCORES.values()]
START = "2018-01-02T00:00:00+09:00"
END = "2026-07-20T23:59:59+09:00"


def dataset(input_dir: Path, name: str, fields: tuple[str, ...]) -> dict:
    return {
        "source_id": f"actual-{name}-source",
        "path": str((input_dir / f"{name}.parquet").resolve()),
        "instrument_field": "instrument",
        "available_at": "available_at",
        "grain": "instrument_instant",
        "key_fields": ["available_at", "instrument"],
        "fields": {field: field for field in fields},
        "field_types": {field: "DOUBLE" for field in fields},
    }


def scaffold(vqapr: Path, root: Path) -> list[dict]:
    target = root / "scaffolds"
    target.mkdir(parents=True, exist_ok=True)
    commands = [
        [
            str(vqapr),
            "--project-root",
            str(root),
            "new",
            "dataset",
            "--out",
            str(target / "dataset.yaml"),
        ],
        [
            str(vqapr),
            "--project-root",
            str(root),
            "new",
            "datamodel",
            "example-factor",
            "--dataset",
            "prices",
            "--out",
            str(target / "datamodel.py"),
        ],
        [
            str(vqapr),
            "--project-root",
            str(root),
            "new",
            "strategy",
            "example-strategy",
            "--dataset",
            "actual_daily_factors",
            "--out",
            str(target / "strategy.py"),
        ],
        [
            str(vqapr),
            "--project-root",
            str(root),
            "new",
            "instruments",
            "--out",
            str(target / "instruments.yaml"),
        ],
        [
            str(vqapr),
            "--project-root",
            str(root),
            "new",
            "exchange",
            "--profile",
            "academic",
            "--out",
            str(target / "exchange.py"),
        ],
        [str(vqapr), "--project-root", str(root), "new", "run", "--out", str(target / "run.yaml")],
    ]
    evidence = []
    for command in commands:
        started = time.perf_counter()
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        evidence.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "wall_s": round(time.perf_counter() - started, 6),
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        if completed.returncode:
            raise RuntimeError(json.dumps(evidence[-1]))
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--vqapr", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    input_dir = args.input.resolve()
    start = "2026-01-02T00:00:00+09:00" if args.smoke else START
    end = "2026-04-30T23:59:59+09:00" if args.smoke else END
    consumer_start = "2026-01-03T00:00:00+09:00" if args.smoke else "2018-01-03T00:00:00+09:00"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    scaffolds = scaffold(args.vqapr.resolve(), root)
    for name in ("factor_model.py", "strategies.py", "exchange.py"):
        shutil.copy2(HERE / name, root / name)

    instruments = json.loads((input_dir / "universe.json").read_text(encoding="utf-8"))
    if len(instruments) != 309:
        raise AssertionError(f"fixed universe is 309, got {len(instruments)}")
    pq.write_table(
        pa.table({"instrument_id": instruments, "kind": ["stock"] * len(instruments)}),
        root / "instruments_stock.parquet",
        compression="zstd",
    )

    datasets = {
        "prices": dataset(input_dir, "prices", ("close", "volume", "turnover")),
        "shares": dataset(input_dir, "shares", ("listed_shares", "investable_shares")),
        "valuation": dataset(
            input_dir,
            "valuation",
            ("beta", "forward_eps", "forward_per", "pbr", "ev_ebitda", "profit_12m"),
        ),
        "consensus": dataset(
            input_dir, "consensus", ("sales", "operating_profit", "net_debt", "owner_profit")
        ),
        "membership": dataset(input_dir, "membership", ("member", "index_weight")),
    }
    datasets["execution"] = {
        **dataset(input_dir, "prices", ("close",)),
        "source_id": "actual-execution-source",
        "fields": {"close": "close", "is_tradable": "is_tradable"},
        "field_types": {"close": "DOUBLE", "is_tradable": "BOOLEAN"},
        "execution": {"is_tradable": "is_tradable"},
    }
    producer = {
        "instruments": {"tables": {"stock": "instruments_stock.parquet"}},
        "datasets": datasets,
        "components": {
            "actual-daily-factors": {
                "kind": "datamodel",
                "path": "factor_model.py",
                "object_name": "ActualDailyFactors",
            },
            "actual-research-exchange": {
                "kind": "exchange",
                "path": "exchange.py",
                "object_name": "ActualResearchExchange",
                "config": {"instruments": instruments},
            },
        },
        "runs": {
            "materialize-actual-factors": {
                "instruments": instruments,
                "start": start,
                "end": end,
                "timezone": "Asia/Seoul",
                "agenda": {"every": "1d", "at": "18:30", "days_from": "prices"},
                "datamodels": {
                    "actual-daily-factors": {
                        "dataset_id": "actual_daily_factors",
                        "value_fields": [*SCORE_FIELDS, "eligible"],
                    }
                },
            }
        },
    }
    consumers = {
        "components": {
            run_id: {"kind": "strategy", "path": "strategies.py", "object_name": object_name}
            for run_id, (object_name, _) in SCORES.items()
        },
        "runs": {
            run_id: {
                "instruments": instruments,
                "start": consumer_start,
                "end": end,
                "timezone": "Asia/Seoul",
                "agenda": {"every": "1w", "at": "08:30", "on": "last"},
                "exchange": "actual-research-exchange",
                "execution": {
                    "dataset": "execution",
                    "trade_price": "close",
                    "fill": {"at": "15:30"},
                },
                "initial_account": {"cash": "100000000000", "mode": "SIGNED", "positions": {}},
                "writes": f"{run_id}-weights",
                "strategy": {"component": run_id},
            }
            for run_id in SCORES
        },
    }
    (root / "producer.yaml").write_text(yaml.safe_dump(producer, sort_keys=False), encoding="utf-8")
    (root / "consumers.yaml").write_text(
        yaml.safe_dump(consumers, sort_keys=False), encoding="utf-8"
    )
    manifest = {
        "input": str(input_dir),
        "instruments": len(instruments),
        "period": {"start": start, "end": end},
        "producer": "materialize-actual-factors",
        "consumers": list(SCORES),
        "scaffolds": scaffolds,
    }
    (root / "project-build.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in manifest.items() if key != "scaffolds"}))


if __name__ == "__main__":
    main()
