#!/usr/bin/env bash
# The sixteen commands of exp_246/exp_280, one per process, under this directory's trace_io.py.
# Fresh project under $1. Run from the repository root:
#   bash experiments/exp_282_the_scenario_trace_registration_cleanup/run_traces.sh SCRATCH WANT.json
set -u
export PYTHONUTF8=1
S="$1"; W="$2"
P="$S/sample"; T="$S/traces"; mkdir -p "$T"
E=experiments/exp_282_the_scenario_trace_registration_cleanup
D=experiments/exp_280_the_scenario_trace_0_16_0/declarations
uv run vqapr --project-root "$P" new sample --out "$P" > /dev/null
cp "$D"/* "$P"/
X() { name="$1"; shift; uv run python "$E/trace_io.py" "$T/$name.json" --want "$W" --name "$name" --project "$P" -- --project-root "$P" "$@"; }
git rev-parse HEAD > "$T/TREE"; git status --short -- src >> "$T/TREE"

X 01_register register "$P/sample.yaml"
X 02_register_bad register "$P/bad.yaml"
cp "$P/execution.parquet" "$S/execution.orig.parquet"
# execution.parquet without its last day, so the check sees a changed file
uv run python - "$P/execution.parquet" <<'PY'
import sys, os, duckdb
path = sys.argv[1].replace(os.sep, "/")
con = duckdb.connect()
con.execute(f"COPY (SELECT * FROM read_parquet('{path}') WHERE trade_at < (SELECT max(trade_at) FROM read_parquet('{path}')) ORDER BY trade_at, instrument) TO '{path}.tmp' (FORMAT parquet)")
con.close()
os.replace(path + ".tmp", path)
PY
X 03_check_changed check sample-run
X 04_register_again register "$P/sample.yaml"
cp "$S/execution.orig.parquet" "$P/execution.parquet"
uv run vqapr --project-root "$P" register "$P/sample.yaml" > /dev/null
X 05_register_features register "$P/features.yaml"
X 06_run_features run sample-features-run
X 07_register_factor register "$P/factor.yaml"
X 08_run_factor run sample-factor-run
X 09_register_stoploss register "$P/stoploss.yaml"
X 10_run_stoploss run sample-stoploss-run
X 11_register_enhanced register "$P/enhanced.yaml"
X 12_run_enhanced run sample-enhanced-run
X 13_list_datasets list datasets
X 14_show_run_enhanced show run sample-enhanced-run
cp -r "$P/.vqapr/runs" "$S/runs_after_traces"
X 15_run_batch run sample-factor-run sample-stoploss-run --jobs 2 --force
uv run python "$E/trace_io.py" "$T/16_worker_factor.json" --want "$W" --name 16_worker_factor --project "$P" --worker sample-factor-run --with sample-stoploss-run
echo "traces done"
