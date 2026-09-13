"""Build the fixed final-20-session producer through the public project path."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
START = "2026-06-22T00:00:00+09:00"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--vqapr", type=Path, required=True)
    args = parser.parse_args()
    subprocess.run(
        [
            str(args.vqapr.resolve().parent / "python"),
            str(HERE / "build_project.py"),
            "--root",
            str(args.root),
            "--input",
            str(args.input),
            "--vqapr",
            str(args.vqapr),
        ],
        check=True,
    )
    producer_path = args.root / "producer.yaml"
    producer = yaml.safe_load(producer_path.read_text(encoding="utf-8"))
    producer["runs"]["materialize-actual-factors"]["start"] = START
    producer_path.write_text(yaml.safe_dump(producer, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
