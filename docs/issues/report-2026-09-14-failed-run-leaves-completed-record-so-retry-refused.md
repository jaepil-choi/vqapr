# A run that returned `ok: false` at `stage: register` had already written a `completed` strategy record, so the plain retry is refused with `record.exists`

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-run-force-in-a-jobs-batch-refused-with-409-dataset-registered.md` (the refusal that produces this state).

## What I was doing

Re-running six edited factor legs. A `vqapr run … --jobs 4 --force` batch refused every edited leg
at `stage: register` with `409 dataset.registered` on its output dataset (filed separately as
`report-2026-09-14-run-force-in-a-jobs-batch-refused-with-409-dataset-registered.md`). The agent
read the failed runs as having done nothing. It withdrew the six output datasets with
`vqapr rm dataset` and ran the legs again without `--force`. Every one was refused with
`409 record.exists`.

## What I expected

`vqapr-run-backtest/references/watching-and-failures.md`: "A record is written last". The same file,
under "`unfinished` is not `running`", says a strategy "killed, or its flow ended in a refusal" shows
as `status: unfinished`. `records-and-tweaks.md`: "a run killed or refused inside a callback leaves a
directory with rows and no record, which `list` shows as `status: unfinished`". The run-backtest
skill: "A run whose envelope is `ok: false` has not finished". I expected a run whose entry is
`ok: false` to leave no `completed` record. If it did leave one, I expected the failing entry to say
so.

## What happened

The failing batch entry for `r-fund` says only that the output dataset was not registered. It says
nothing about a record:

    $ vqapr run r-fund r-px --jobs 2 --force
    {"jobs": 2, "ok": false, "runs": {"r-fund": {"correlation_id": "f2f93f35ad9c497e870236e8a1991796", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-fund-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}, "r-px": {"ok": true, "run_id": "r-px", "strategies": {"s-px": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "10b2c6f5ad1c9b3ea11ae7230e090bbeb93f17b6aa86f844bf4ef05f9eb5ea2e", "record": "s-px@10b2c6f5", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.014162, "due": 0.029154, "simulation.due.account_commit": 0.001892, "simulation.due.account_mark": 0.01037, "simulation.due.account_preparation": 0.001012, "simulation.due.exchange_execution": 0.000377, "simulation.due.feedback_candidate": 4e-05, "simulation.due.feedback_publication": 0.000118, "simulation.due.instrument_declaration": 5.9e-05, "simulation.due.order_planning": 0.000613, "simulation.due.snapshot": 0.012167, "simulation.due.valuation_mark": 0.00014, "simulation.due.valuation_selection": 0.00027, "total": 0.048949}}}}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

Immediately afterwards, the store holds a new **`completed`** record for the refused run
(`s-fund@f5f091ad`, beside the earlier `s-fund@4bb784ce`). Meanwhile the output dataset still names
the old record:

    $ vqapr list strategies --run r-fund
    {"count": 2, "items": [{"account_version": 9, "contract_failed": [], "fingerprint": "4bb784ce862dc0cfff3a6d2b46173ebbe2a6138e72cba50d6e63359eea68d80c", "period": {"end": "2024-02-28T15:30:00+09:00", "events": 51, "start": "2024-01-02T00:00:00+09:00"}, "run_id": "r-fund", "status": "completed", "strategy_id": "s-fund", "strategy_ref": "s-fund@4bb784ce", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"]}, {"account_version": 9, "contract_failed": [], "fingerprint": "f5f091ad63b0c89eef2a96f161fc8bdec46926b8353cca7c484eef0536c254e2", "period": {"end": "2024-02-28T15:30:00+09:00", "events": 51, "start": "2024-01-02T00:00:00+09:00"}, "run_id": "r-fund", "status": "completed", "strategy_id": "s-fund", "strategy_ref": "s-fund@f5f091ad", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"]}], "kind": "strategies", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

    $ vqapr list datasets --id r-fund-weights
    {"count": 1, "items": [{"dataset_id": "r-fund-weights", "produced_by": "r-fund", "produced_by_record": "s-fund@4bb784ce"}], "kind": "datasets", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

The route the agent took was to withdraw the output and run again. The plain run is refused because of
the record the failed run wrote:

    $ vqapr rm dataset r-fund-weights
    {"deleted": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e\\.vqapr\\materialized\\r-fund-weights", "identifier": "r-fund-weights", "kind": "dataset", "ok": true, "removed": true, "stage": "workspace.removed", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

    $ vqapr run r-fund
    {"correlation_id": "1e8602ca6f28430e877e407018d94033", "error": "VqaprError: record: 1 failure(s)\n  [409 record.exists] a strategy record is written once per run and fingerprint", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "record.exists", "example_total": 0, "examples": [], "fix": "edit the strategy (a new fingerprint records beside the old one), or replace this record and the dataset it published deliberately: vqapr run r-fund --force", "observed": "'r-fund/s-fund@f5f091ad' already has a record at .vqapr\\runs\\r-fund\\strategies\\s-fund@f5f091ad", "requirement": "a strategy record is written once per run and fingerprint", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "change the strategy so its fingerprint differs, or pass --force to replace the standing record, then retry", "stage": "record", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e"}

`--force`, as that refusal says, then works:

    $ vqapr run r-fund --force
    {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-fund", "stage": "run.complete", "store_root": ".vqapr", "strategies": {"s-fund": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "f5f091ad63b0c89eef2a96f161fc8bdec46926b8353cca7c484eef0536c254e2", "record": "s-fund@f5f091ad", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.008755, "due": 0.028113, "simulation.due.account_commit": 0.00173, "simulation.due.account_mark": 0.009557, "simulation.due.account_preparation": 0.001501, "simulation.due.exchange_execution": 0.000335, "simulation.due.feedback_candidate": 4.2e-05, "simulation.due.feedback_publication": 0.000104, "simulation.due.instrument_declaration": 5.7e-05, "simulation.due.order_planning": 0.000519, "simulation.due.snapshot": 0.012003, "simulation.due.valuation_mark": 0.00013, "simulation.due.valuation_selection": 0.000253, "total": 0.04324}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16e", "writes": "r-fund-weights"}

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
4. `vqapr run r-fund r-px --jobs 2 --force` gives `r-fund`: `ok: false`, `stage: register`, `409 dataset.registered`
5. `vqapr list strategies --run r-fund` shows `s-fund@f5f091ad`, `status: completed`, `account_version: 9`. **This is the defect.**
6. `vqapr list datasets --id r-fund-weights` shows `produced_by_record: "s-fund@4bb784ce"`, the old record
7. `vqapr rm dataset r-fund-weights`, then `vqapr run r-fund` gives `409 record.exists` on `s-fund@f5f091ad`

Reproduced 2 of 2 attempts in fresh workspaces. The testbed run showed the same state on 6 of 6
refused legs: `vqapr list strategies --run ff-s1` gave `ff-s1@3e05e371`, `status: completed`,
`account_version: 9`, after the refused batch.

## Impact

Worked around with `vqapr run <id> --force`, which the `record.exists` refusal names. In the testbed
run this was the third round for six legs. The larger cost is in what the store says. After the
failure, a `completed` record exists whose output was never published, and the registered output
names a different record. A reader who counts `completed` records to count tweaks, as
`records-and-tweaks.md` recommends, counts a run whose envelope said it failed.

## What would have prevented it

The failing entry saying what it left behind, for example "the record s-fund@f5f091ad was written;
its output dataset was not published; retry with `--force`". Or the run recording and publishing
all or nothing.
