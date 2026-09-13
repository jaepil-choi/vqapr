"""Create the fixed direct-computation variant from the same public project declarations."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DIRECT = {
    "direct-six-week-momentum": "DirectSixWeekMomentum",
    "direct-balanced-factors": "DirectBalancedFactors",
    "direct-value-quality": "DirectValueQuality",
    "direct-low-vol-momentum": "DirectLowVolMomentum",
    "direct-earnings-momentum": "DirectEarningsMomentum",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--vqapr", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists():
        shutil.rmtree(root)
    subprocess.run(
        [
            str(args.vqapr.resolve().parent / "python"),
            str(HERE / "build_project.py"),
            "--root",
            str(root),
            "--input",
            str(args.input.resolve()),
            "--vqapr",
            str(args.vqapr.resolve()),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # build_project's six public templates are retained as first-user scaffold evidence.
    direct_source = (HERE / "factor_model.py").read_text(encoding="utf-8")
    direct_source += (HERE / "direct_tail.py").read_text(encoding="utf-8")
    (root / "direct_strategies.py").write_text(direct_source, encoding="utf-8")
    producer = yaml.safe_load((root / "producer.yaml").read_text(encoding="utf-8"))
    instruments = producer["instruments"]
    datasets = producer["datasets"]
    exchange = producer["components"]["actual-research-exchange"]
    names = json.loads((args.input.resolve() / "universe.json").read_text(encoding="utf-8"))
    declaration = {
        "instruments": instruments,
        "datasets": datasets,
        "components": {
            "actual-research-exchange": exchange,
            **{
                run_id: {
                    "kind": "strategy",
                    "path": "direct_strategies.py",
                    "object_name": object_name,
                }
                for run_id, object_name in DIRECT.items()
            },
        },
        "runs": {
            run_id: {
                "instruments": names,
                "start": "2018-01-03T00:00:00+09:00",
                "end": "2026-07-20T23:59:59+09:00",
                "timezone": "Asia/Seoul",
                "agenda": {"every": "1w", "at": "07:30", "on": "last"},
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
            for run_id in DIRECT
        },
    }
    (root / "direct.yaml").write_text(
        yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
    )
    print(json.dumps({"runs": list(DIRECT), "instruments": len(names)}))


if __name__ == "__main__":
    main()
