# `vqapr run --force` in a `--jobs` batch refuses a run whose strategy changed since its output was published (409 `dataset.registered`); the same `--force` outside a batch replaces it

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-11-a-jobs-batch-writes-no-run-record-so-show-run-refuses-runs-it-reported-completed.md` (another way a `--jobs` batch differs from a single-process run), and `report-2026-09-14-failed-run-leaves-completed-record-so-retry-refused.md` (the state this refusal leaves behind).

## What I was doing

Six factor-leg strategies had been edited and re-registered, and each leg's run had already
published its `writes` dataset. `vqapr check ff-s1` answered `run.output_stale` with
`fix: "vqapr run ff-s1 --force"`. The agent ran the fix for all the legs at once:
`vqapr run ff-s1 … ff-b3 km-s1 … km-b3 --jobs 4 --force`. The six new `km-*` runs completed. Every
`ff-*` run was refused at `stage: register` with `409 dataset.registered` on its own output
dataset, `ff-<leg>-weights`.

## What I expected

`vqapr run --help`, `--force`: "replace this run's record (its strategy's or its datamodel's) that
already exists under this run and fingerprint, and the dataset it published, instead of refusing."
The `check` refusal's own `fix` is `vqapr run r-fund --force to rewrite it from the current component`.
`vqapr-run-backtest/references/check-before-run.md`: "each worker passes the one door `check` and
`run` pass". Nothing in `run --help` or the run-backtest skill says that `--force` behaves
differently under `--jobs`.

## What happened

`check` names `--force` as the fix:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "run.output_stale", "example_total": 0, "examples": [], "fix": "vqapr run r-fund --force to rewrite it from the current component, or re-register the component version that wrote it", "observed": "'r-fund-weights' was written by record 's-fund@4bb784ce'; the registered component is 's-fund@f5f091ad'", "requirement": "a run's registered output was written by the component version registered now", "source": {"file": null, "key_path": "runs.r-fund.writes", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16b"}

In a `--jobs 2` batch, `--force` is refused for the edited run. The failure has `stage: register`,
and its `cause` is all null:

    $ vqapr run r-fund r-px --jobs 2 --force
    {"jobs": 2, "ok": false, "runs": {"r-fund": {"correlation_id": "560abd89761240e191faf5a06237df5c", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-fund-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}, "r-px": {"correlation_id": "c358969805d24a25a29cd204e10d2c76", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-px-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-px-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-px-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16b"}

When only one of the two strategies was edited, only that run was refused. The unedited run
completed in the same batch:

    $ vqapr run r-fund r-px --jobs 2 --force
    {"jobs": 2, "ok": false, "runs": {"r-fund": {"correlation_id": "f2f93f35ad9c497e870236e8a1991796", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-fund-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}, "r-px": {"ok": true, "run_id": "r-px", "strategies": {"s-px": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "10b2c6f5ad1c9b3ea11ae7230e090bbeb93f17b6aa86f844bf4ef05f9eb5ea2e", "record": "s-px@10b2c6f5", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.014162, "due": 0.029154, "simulation.due.account_commit": 0.001892, "simulation.due.account_mark": 0.01037, "simulation.due.account_preparation": 0.001012, "simulation.due.exchange_execution": 0.000377, "simulation.due.feedback_candidate": 4e-05, "simulation.due.feedback_publication": 0.000118, "simulation.due.instrument_declaration": 5.9e-05, "simulation.due.order_planning": 0.000613, "simulation.due.snapshot": 0.012167, "simulation.due.valuation_mark": 0.00014, "simulation.due.valuation_selection": 0.00027, "total": 0.048949}}}}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

The same state, the same flag, outside a `--jobs` batch replaces the record and the dataset. Here
are two ids in one process, after both strategies were edited:

    $ vqapr run r-fund r-px --force
    {"jobs": 1, "ok": true, "runs": {"r-fund": {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-fund", "stage": "run.complete", "store_root": ".vqapr", "strategies": {"s-fund": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "f5f091ad63b0c89eef2a96f161fc8bdec46926b8353cca7c484eef0536c254e2", "record": "s-fund@f5f091ad", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.00964, "due": 0.030062, "simulation.due.account_commit": 0.001882, "simulation.due.account_mark": 0.010189, "simulation.due.account_preparation": 0.001466, "simulation.due.exchange_execution": 0.000373, "simulation.due.feedback_candidate": 4e-05, "simulation.due.feedback_publication": 0.000115, "simulation.due.instrument_declaration": 5.7e-05, "simulation.due.order_planning": 0.000587, "simulation.due.snapshot": 0.012806, "simulation.due.valuation_mark": 0.000138, "simulation.due.valuation_selection": 0.000278, "total": 0.046095}}}, "writes": "r-fund-weights"}, "r-px": {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-px", "stage": "run.complete", "store_root": ".vqapr", "strategies": {"s-px": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "d384c75b5f9acf7f41dd864c9047b04d30008c405c1061a4569ae493385c12f2", "record": "s-px@d384c75b", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.013668, "due": 0.028808, "simulation.due.account_commit": 0.001928, "simulation.due.account_mark": 0.010154, "simulation.due.account_preparation": 0.000872, "simulation.due.exchange_execution": 0.000361, "simulation.due.feedback_candidate": 3.8e-05, "simulation.due.feedback_publication": 0.000119, "simulation.due.instrument_declaration": 5.9e-05, "simulation.due.order_planning": 0.000545, "simulation.due.snapshot": 0.012294, "simulation.due.valuation_mark": 0.000137, "simulation.due.valuation_selection": 0.000269, "total": 0.048713}}}, "writes": "r-px-weights"}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16c"}

A `--jobs 2 --force` batch in which no strategy changed succeeds:

    $ vqapr run r-fund r-px --jobs 2 --force
    {"jobs": 2, "ok": true, "runs": {"r-fund": {"ok": true, "run_id": "r-fund", "strategies": {"s-fund": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "4bb784ce862dc0cfff3a6d2b46173ebbe2a6138e72cba50d6e63359eea68d80c", "record": "s-fund@4bb784ce", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.010262, "due": 0.030399, "simulation.due.account_commit": 0.001939, "simulation.due.account_mark": 0.01087, "simulation.due.account_preparation": 0.000986, "simulation.due.exchange_execution": 0.000438, "simulation.due.feedback_candidate": 4e-05, "simulation.due.feedback_publication": 0.000116, "simulation.due.instrument_declaration": 6.4e-05, "simulation.due.order_planning": 0.000648, "simulation.due.snapshot": 0.012738, "simulation.due.valuation_mark": 0.000139, "simulation.due.valuation_selection": 0.000281, "total": 0.048305}}}}, "r-px": {"ok": true, "run_id": "r-px", "strategies": {"s-px": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "10b2c6f5ad1c9b3ea11ae7230e090bbeb93f17b6aa86f844bf4ef05f9eb5ea2e", "record": "s-px@10b2c6f5", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.015302, "due": 0.029209, "simulation.due.account_commit": 0.001897, "simulation.due.account_mark": 0.010277, "simulation.due.account_preparation": 0.001021, "simulation.due.exchange_execution": 0.000385, "simulation.due.feedback_candidate": 4.1e-05, "simulation.due.feedback_publication": 0.000123, "simulation.due.instrument_declaration": 6.3e-05, "simulation.due.order_planning": 0.000608, "simulation.due.snapshot": 0.01229, "simulation.due.valuation_mark": 0.000139, "simulation.due.valuation_selection": 0.000268, "total": 0.052194}}}}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16d"}

A single id with `--jobs 2 --force` after an edit also succeeds. Its envelope has the single-run
shape, with no `jobs` key:

    $ vqapr run r-fund --jobs 2 --force
    {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-fund", "stage": "run.complete", "store_root": ".vqapr", "strategies": {"s-fund": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "dddcac476c374c51813be9ca3fe5aa98adf08e76a2b27e861c9a480edd12eba8", "record": "s-fund@dddcac47", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.009554, "due": 0.030071, "simulation.due.account_commit": 0.001899, "simulation.due.account_mark": 0.010069, "simulation.due.account_preparation": 0.001475, "simulation.due.exchange_execution": 0.000356, "simulation.due.feedback_candidate": 4.2e-05, "simulation.due.feedback_publication": 0.000119, "simulation.due.instrument_declaration": 5.9e-05, "simulation.due.order_planning": 0.00056, "simulation.due.snapshot": 0.012939, "simulation.due.valuation_mark": 0.000136, "simulation.due.valuation_selection": 0.000269, "total": 0.045621}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16c", "writes": "r-fund-weights"}

The testbed run's own envelope matches the refusal above. Its `ff-s1` entry, from the
`--jobs 4 --force` batch of 12 runs, `"jobs": 4, "ok": false`:

    {"correlation_id": "d725801dd82247f98126730052e159db", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'ff-s1-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'ff-s1-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'ff-s1-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}

## Reproduction

Everything below runs on synthetic data, no project data needed. Invocation: every `vqapr` below is
`uv run --no-sync --project <env with the 0.16.0 wheel> vqapr --project-root .`, run from a fresh,
empty directory holding these files; every `python` is the same environment's interpreter.

Data: 3 instruments (`S01`–`S03`), weekdays 2024-01-02 .. 2024-02-29, every row stamped
15:30 Asia/Seoul. `python gen.py .` writes `px.parquet` (the venue table), `fund.parquet` (a
strategy input) and `instruments_stock.parquet` (the roster). `--variant N --only px|fund`
rewrites one file with the same schema and different values.

`gen.py`:

```python
"""Write a tiny synthetic workspace data set for the vqapr lifecycle reproductions.

    uv run python gen.py <out_dir> [--variant N] [--only px|fund|all]

Files (3 instruments S01..S03, KRX business days 2024-01-02 .. 2024-02-29, stamped 15:30 Asia/Seoul):
  px.parquet                 available_at, instrument, close (DOUBLE), is_tradable (BOOL)   -- the venue table
  fund.parquet               available_at, instrument, score (DOUBLE), score2 (DOUBLE)       -- a strategy input
  instruments_stock.parquet  instrument_id, kind="stock"                                     -- the roster
--variant N (N > 0) rewrites the chosen file(s) with the same schema and different values, which is
"the registered source file was rewritten". Deterministic: seed = 7 + variant.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

NAMES = ["S01", "S02", "S03"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--variant", type=int, default=0)
    ap.add_argument("--only", choices=["px", "fund", "all"], default="all")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7 + a.variant)

    days = pd.bdate_range("2024-01-02", "2024-02-29")
    stamps = [pd.Timestamp(f"{d.date()} 15:30").tz_localize("Asia/Seoul") for d in days]
    rows = [(t, n) for t in stamps for n in NAMES]
    base = pd.DataFrame(rows, columns=["available_at", "instrument"])

    if a.only in ("px", "all"):
        px = base.copy()
        px["close"] = 100.0 + rng.normal(0, 1, len(px)).cumsum().round(4)
        px["is_tradable"] = True
        px.to_parquet(out / "px.parquet", index=False)
    if a.only in ("fund", "all"):
        fund = base.copy()
        fund["score"] = rng.uniform(1, 2, len(fund)).round(6)
        fund["score2"] = rng.uniform(1, 2, len(fund)).round(6)
        fund.to_parquet(out / "fund.parquet", index=False)
    if a.variant == 0 and a.only == "all":
        pd.DataFrame({"instrument_id": NAMES, "kind": "stock"}).to_parquet(
            out / "instruments_stock.parquet", index=False
        )


if __name__ == "__main__":
    main()
```

`data.yaml`:

```yaml
instruments:
  tables:
    stock: instruments_stock.parquet
datasets:
  px:
    source_id: px-source
    path: px.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields:
      close: close
      is_tradable: is_tradable
    field_types:
      close: DOUBLE
      is_tradable: BOOLEAN
    execution:
      is_tradable: is_tradable
  fund:
    source_id: fund-source
    path: fund.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields:
      score: score
    field_types:
      score: DOUBLE
components:
  venue:
    kind: exchange
    path: venue.py
    object_name: Venue
    config:
      instruments: [S01, S02, S03]
  s-fund:
    kind: strategy
    path: s_fund.py
    object_name: SFund
  s-px:
    kind: strategy
    path: s_px.py
    object_name: SPx
```

`runs.yaml`:

```yaml
runs:
  r-fund:
    instruments: [S01, S02, S03]
    start: "2024-01-02T00:00:00+09:00"
    end: "2024-02-28T15:30:00+09:00"
    timezone: Asia/Seoul
    schedule:
      every: 1w
      at: "16:00"
    exchange: venue
    execution:
      dataset: px
      trade_price: close
      fill:
        at: "15:30"
    initial_account:
      cash: "1000000"
      mode: LONG_ONLY
      positions: {}
    writes: r-fund-weights
    strategy:
      component: s-fund
  r-px:
    instruments: [S01, S02, S03]
    start: "2024-01-02T00:00:00+09:00"
    end: "2024-02-28T15:30:00+09:00"
    timezone: Asia/Seoul
    schedule:
      every: 1w
      at: "16:00"
    exchange: venue
    execution:
      dataset: px
      trade_price: close
      fill:
        at: "15:30"
    initial_account:
      cash: "1000000"
      mode: LONG_ONLY
      positions: {}
    writes: r-px-weights
    strategy:
      component: s-px
```

`venue.py`:

```python
"""Zero-friction, divisible, long-only academic venue listing the names given under `config:`."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from vqapr.public import AcademicExchange, ListingAccess, TradeRule

STEP = Decimal("0.00000001")


class Venue(AcademicExchange):
    def __init__(self, instruments: Sequence[str]) -> None:
        super().__init__(
            {
                str(n): TradeRule(
                    instrument_id=str(n),
                    quantity_step=STEP,
                    minimum_quantity=STEP,
                    fractional_allowed=True,
                    access=ListingAccess.LONG_ONLY,
                )
                for n in instruments
            },
            exchange_id="venue",
        )
```

`s_fund.py`:

```python
"""Weights every name in proportion to its latest `score` from the `fund` dataset (not the venue table)."""

from __future__ import annotations

from decimal import Decimal

from vqapr import public as vq

INVESTED = 1


class SFund(vq.StrategyModel):
    def inputs(self):
        return {"f": vq.DatasetInput(dataset_id="fund", fields=("score",), lookback=vq.RowsLookback(rows=1))}

    def decide(self, call):
        cur = call.read("f", "score").current()
        chosen = {n: Decimal(repr(float(v))) for n, v in cur.items() if v is not None and v == v}
        if not chosen:
            return vq.Hold(reason="no score")
        return vq.Rebalance.of(long=chosen, invested=INVESTED)
```

`s_px.py`:

```python
"""Weights every name by `score` (dataset `fund`) times its latest close (dataset `px`, also the venue table)."""

from __future__ import annotations

from decimal import Decimal

from vqapr import public as vq

INVESTED = 1


class SPx(vq.StrategyModel):
    def inputs(self):
        return {
            "f": vq.DatasetInput(dataset_id="fund", fields=("score",), lookback=vq.RowsLookback(rows=1)),
            "p": vq.DatasetInput(dataset_id="px", fields=("close",), lookback=vq.RowsLookback(rows=1)),
        }

    def decide(self, call):
        score = call.read("f", "score").current()
        close = call.read("p", "close").current()
        chosen = {
            n: Decimal(repr(float(score[n]) * float(close[n])))
            for n in score
            if n in close and score[n] == score[n] and close[n] == close[n]
        }
        if not chosen:
            return vq.Hold(reason="no score")
        return vq.Rebalance.of(long=chosen, invested=INVESTED)
```

1. `python gen.py .`
2. `vqapr register data.yaml`, `vqapr register runs.yaml`, `vqapr run r-fund r-px`
3. Edit `s_fund.py`: `INVESTED = 1` becomes `INVESTED = Decimal("0.9")`. Then `vqapr register strategy s-fund s_fund.py`
4. `vqapr check r-fund` gives `412 run.output_stale`, `fix: "vqapr run r-fund --force …"`
5. `vqapr run r-fund r-px --jobs 2 --force` gives `r-fund`: `409 dataset.registered`, `stage: register`

The same state with `vqapr run r-fund --force`, or with `vqapr run r-fund r-px --force` (no `--jobs`),
succeeds.

Reproduced 2 of 2 attempts in fresh workspaces (both strategies edited, and only `s-fund` edited).
The testbed run showed the same refusal on 6 of 6 edited legs in a `--jobs 4` batch.

## Impact

Worked around, at a cost of about three rounds in the testbed run. The agent went through
`vqapr rm dataset ff-<leg>-weights` six times, then a plain run (refused with `record.exists`, filed
separately), then `--force` again. The workaround does not change a result. The cost is that the
batch form the skill recommends for several legs ("`vqapr run a b c --jobs 3`") cannot carry out the
fix that `check` gives, and nothing says so.

## What would have prevented it

`--force` doing under `--jobs` what it does in one process, as its help says. Or, until then, the
409's `fix` and `run --help` saying that `--force` under `--jobs` does not replace a published
dataset whose producing record changed, and naming the per-run command.
