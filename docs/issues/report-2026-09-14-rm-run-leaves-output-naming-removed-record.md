# `vqapr rm run` removes the record but leaves the run's `writes` dataset registered, still naming the removed record as its producer, and says nothing about it

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** closed `archive/080`/`081` (record `157`), which made `rm` enumerate what it leaves and added `--cascade`. The run side's `writes` dataset is not in what `rm run` reports.

## What I was doing

Throwing away a run's provisional records, so that the next run would leave one clean record per
leg. In the testbed run this was `vqapr rm run ff-s1` after the leg's strategy had been
re-registered. The next `vqapr check ff-s1` was refused with `run.output_stale`, and the refusal
named `ff-s1@c9855fa5`, the record just removed.

## What I expected

`vqapr rm --help`: "run: a run id (its records)". `vqapr-run-backtest/references/records-and-tweaks.md`
lists `vqapr rm run <run-id> [--keep-latest]` as removing "a run's records".
`vqapr-inspect-workspace/references/deleting.md` sets the standard for a partial removal:
"`rm run-definition` reports the records it left behind and names the verb that removes them, so a
half-cleanup says what is left rather than looking finished."

I expected `rm run` either to withdraw the dataset that the removed record published, or to say it
left that dataset behind.

## What happened

Before `rm run`, the run's output names its producing record:

    $ vqapr list datasets --id r-fund-weights
    {"count": 1, "items": [{"dataset_id": "r-fund-weights", "produced_by": "r-fund", "produced_by_record": "s-fund@4bb784ce"}], "kind": "datasets", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a"}

`rm run` removes the record and reports nothing about the output:

    $ vqapr rm run r-fund
    {"kind": "run", "ok": true, "removed": ["s-fund@4bb784ce", "record.json"], "run_id": "r-fund", "stage": "record.removed", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a"}

Afterwards the output still names the removed record, while the run holds no record at all:

    $ vqapr list datasets --id r-fund-weights
    {"count": 1, "items": [{"dataset_id": "r-fund-weights", "produced_by": "r-fund", "produced_by_record": "s-fund@4bb784ce"}], "kind": "datasets", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a"}

    $ vqapr list strategies --run r-fund
    {"count": 0, "items": [], "kind": "strategies", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a"}

`check` passes a registered output whose producing record no longer exists. The next `run` is
refused, with a working fix:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "ok": true, "passed": ["workspace", "run", "judgments", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a"}

    $ vqapr run r-fund
    {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-fund", "stage": "run.complete", "store_root": ".vqapr", "strategies": {"s-fund": {"account_version": 9, "contract": {"accepted_intents": 9}, "events": 51, "fills": {"dealt": 27, "never_filled": [], "orders": 27, "partial": 0, "reasons": {}, "zero_dealt": 0}, "fingerprint": "4bb784ce862dc0cfff3a6d2b46173ebbe2a6138e72cba50d6e63359eea68d80c", "record": "s-fund@4bb784ce", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.008907, "due": 0.027876, "simulation.due.account_commit": 0.001684, "simulation.due.account_mark": 0.009735, "simulation.due.account_preparation": 0.000926, "simulation.due.exchange_execution": 0.000341, "simulation.due.feedback_candidate": 3.7e-05, "simulation.due.feedback_publication": 0.000105, "simulation.due.instrument_declaration": 5.6e-05, "simulation.due.order_planning": 0.00058, "simulation.due.snapshot": 0.012141, "simulation.due.valuation_mark": 0.000126, "simulation.due.valuation_selection": 0.000247, "total": 0.042935}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws15a", "writes": "r-fund-weights"}

When the strategy was re-registered with an edit before `rm run`, as in the testbed run, `check`
names the removed record as the output's writer:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "run.output_stale", "example_total": 0, "examples": [], "fix": "vqapr run r-fund --force to rewrite it from the current component, or re-register the component version that wrote it", "observed": "'r-fund-weights' was written by record 's-fund@4bb784ce'; the registered component is 's-fund@f5f091ad'", "requirement": "a run's registered output was written by the component version registered now", "source": {"file": null, "key_path": "runs.r-fund.writes", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16"}

**This correction matters for triage.** The `run.output_stale` refusal is caused by the component
re-registration, not by `rm run`. The identical refusal comes back *before* `rm run` in the same
workspace:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "run.output_stale", "example_total": 0, "examples": [], "fix": "vqapr run r-fund --force to rewrite it from the current component, or re-register the component version that wrote it", "observed": "'r-fund-weights' was written by record 's-fund@4bb784ce'; the registered component is 's-fund@f5f091ad'", "requirement": "a run's registered output was written by the component version registered now", "source": {"file": null, "key_path": "runs.r-fund.writes", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16"}

With no component change, `check` passes after `rm run` (above). What `rm run` contributes is the
dangling provenance: a registered dataset whose `produced_by_record` is gone. `rm run` is also silent
about it.

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
2. `vqapr register data.yaml`, `vqapr register runs.yaml`, `vqapr run r-fund`
3. `vqapr rm run r-fund` reports `removed: ["s-fund@4bb784ce", "record.json"]`, with nothing about `r-fund-weights`
4. `vqapr list datasets --id r-fund-weights` still shows `produced_by_record: "s-fund@4bb784ce"`, and
   `vqapr list strategies --run r-fund` shows 0 items

Variant with the testbed's ordering: after step 2, edit `s_fund.py` (`INVESTED = Decimal("0.9")`),
then `vqapr register strategy s-fund s_fund.py`, `vqapr rm run r-fund`, `vqapr check r-fund`. The
check returns `run.output_stale` naming `s-fund@4bb784ce`.

Reproduced 2 of 2 attempts in fresh workspaces, one with and one without the component edit.

## Impact

A papercut: nothing was blocked. The next run is refused (`run.output_registered` or
`run.output_stale`), and both refusals carry a fix that works. The cost is provenance. After
`rm run`, `list datasets` reports a producer record that `list strategies` no longer has, `check`
accepts it, and a later run that reads the dataset cannot trace its rows to a record. The testbed
agent also read the stale refusal as a consequence of the removal, which cost it a round.

## What would have prevented it

`rm run` naming the `writes` dataset it leaves, for example "r-fund-weights still carries rows from
s-fund@4bb784ce; withdraw it with `vqapr rm dataset r-fund-weights`, or the next run needs `--force`",
the way `rm run-definition` names the records it leaves.
