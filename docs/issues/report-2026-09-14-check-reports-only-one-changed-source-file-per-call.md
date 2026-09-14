# `check` reports only one changed source file per call; a second stale dataset surfaces only after the first is re-registered

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-stale-execution-dataset-reported-as-raw-traceback.md` (the traceback beside case 1), and closed `archive/095` (record `234`).

## What I was doing

After a data-preparation fix, several registered parquet files are rewritten at once. In the
testbed run these were the price table and the book-equity table. The next step is to ask `check`
what must be re-registered before the run can go.

## What I expected

`vqapr check --help`:

> Reports every INDEPENDENT problem at once rather than stopping at the first, so a declaration can
> be repaired in one pass instead of one round trip per defect.

`vqapr-run-backtest/references/check-before-run.md`:

> Runs every independent judgment it can and reports **all** of them in one call. A run with four
> defects costs one command, not four rounds of fix-and-retry.

`vqapr-introduce-vqapr/SKILL.md`: "A refusal says who must act, where it stopped and how to fix it —
before anything ran, and every problem at once."

Two rewritten files are two defects, each with its own fix (`vqapr register` for that dataset). I
expected both in one `check`.

## What happened

**Case 1: the execution dataset `px` and the input `fund` are both rewritten.** `check` names
only `px`. The `blocked` traceback beside it is filed separately as
`report-2026-09-14-stale-execution-dataset-reported-as-raw-traceback.md`.

    $ vqapr check r-fund
    {"blocked": [{"cause": {"message": "freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 189, in judgments\n    found.extend(judge())\n                 ^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 165, in <lambda>\n    lambda: _judge_execution_ordering(definition, at, read),\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 343, in _judge_execution_ordering\n    table = facts.execution_table()\n            ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 285, in execution_table\n    return self._once(  # type: ignore[return-value]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 276, in _once\n    raise error\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 271, in _once\n    self._settled[key] = (read(), None)\n                          ^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 286, in <lambda>\n    \"execution_table\", lambda: bound_execution_table(self._workspace, self._definition)\n                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 133, in bound_execution_table\n    registration = workspace.require_verified(binding.dataset)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registry.py\", line 405, in require_verified\n    require_verified(registration, source, digest=self.source_digest(source))\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\data\\verification.py\", line 706, in require_verified\n    raise VqaprError(\nvqapr.domain.errors.VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them\n", "type": "VqaprError", "where": null}, "code": "judgment.blocked", "example_total": 0, "examples": [], "fix": "run `vqapr check r-fund` to see the full report, then fix what stopped the judgment from answering; the exception is in `cause`", "observed": "execution_ordering could not answer: VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "requirement": "every judgment answers before a run is accepted", "source": {"file": null, "key_path": "runs.r-fund", "line": null}, "status": 412}], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'px' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'px': registered digest c95573120661…, file now d2ff4f2fa352…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "px.parquet", "key_path": "datasets.px", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

Restoring `px.parquet` to its registered bytes, and changing nothing else, makes `fund` appear. It
was stale the whole time:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fund' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fund': registered digest b51756de47d3…, file now 334f3e50d83e…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund.parquet", "key_path": "datasets.fund", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "judgments"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

**Case 2: two strategy inputs, `fund` and `fundb`, are rewritten, and the execution file is not.**
`check r-both` (a strategy that reads both) names only `fund`:

    $ vqapr check r-both
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fund' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fund': registered digest b51756de47d3…, file now 334f3e50d83e…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund.parquet", "key_path": "datasets.fund", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "judgments"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

`run` names only `fund` as well:

    $ vqapr run r-both
    {"correlation_id": "871815e024214d0ea36f3603ef42e2c3", "error": "VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fund' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fund': registered digest b51756de47d3…, file now 334f3e50d83e…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund.parquet", "key_path": "datasets.fund", "line": null}, "status": 412}], "mutation": false, "ok": false, "retry_precondition": "register dataset 'fund' again (`vqapr register <its declaration file>`), then retry", "stage": "freeze", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

Re-registering `fund`, and changing nothing else, makes `fundb` appear:

    $ vqapr register data.yaml
    {"ok": true, "registered": {"components": ["venue", "s-fund", "s-px"], "datasets": ["px", "fund"], "instruments": [{"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3}]}, "spoken": ["dataset 'px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'fund': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

    $ vqapr check r-both
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fundb' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fundb': registered digest b51756de47d3…, file now 334f3e50d83e…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund_b.parquet", "key_path": "datasets.fundb", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "judgments"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wss1"}

Three rewritten files took three `check` rounds to find.

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

`extra.yaml` adds a second input dataset `fundb` (file `fund_b.parquet`, a copy of `fund.parquet`
made at setup), a strategy `s-both` that reads `fund` and `fundb`, and its run `r-both`. It also
carries a raising strategy used by another report.

`extra.yaml`:

```yaml
datasets:
  fundb:
    source_id: fundb-source
    path: fund_b.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields:
      score: score
    field_types:
      score: DOUBLE
components:
  s-boom:
    kind: strategy
    path: s_boom.py
    object_name: SBoom
  s-both:
    kind: strategy
    path: s_both.py
    object_name: SBoth
runs:
  r-boom:
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
    writes: r-boom-weights
    strategy:
      component: s-boom
  r-both:
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
    writes: r-both-weights
    strategy:
      component: s-both
```

`s_both.py`:

```python
"""Weights every name by `score` from dataset `fund` times `score` from dataset `fundb` (two strategy inputs)."""

from __future__ import annotations

from decimal import Decimal

from vqapr import public as vq


class SBoth(vq.StrategyModel):
    def inputs(self):
        return {
            "a": vq.DatasetInput(dataset_id="fund", fields=("score",), lookback=vq.RowsLookback(rows=1)),
            "b": vq.DatasetInput(dataset_id="fundb", fields=("score",), lookback=vq.RowsLookback(rows=1)),
        }

    def decide(self, call):
        a = call.read("a", "score").current()
        b = call.read("b", "score").current()
        chosen = {n: Decimal(repr(float(a[n]) * float(b[n]))) for n in a if n in b}
        if not chosen:
            return vq.Hold(reason="no score")
        return vq.Rebalance.of(long=chosen, invested=1)
```

`s_boom.py`:

```python
"""Raises from its own decide(): what a genuine user-code failure looks like."""

from __future__ import annotations

from vqapr import public as vq


class SBoom(vq.StrategyModel):
    def inputs(self):
        return {"f": vq.DatasetInput(dataset_id="fund", fields=("score",), lookback=vq.RowsLookback(rows=1))}

    def decide(self, call):
        raise ValueError("deliberate failure in the user's own strategy")
```

1. `python gen.py .`, then `cp fund.parquet fund_b.parquet` and `cp px.parquet px.orig`
2. `vqapr register data.yaml`, `vqapr register runs.yaml`, `vqapr register extra.yaml`
3. `python gen.py . --variant 1 --only px` and `python gen.py . --variant 1 --only fund`
4. `vqapr check r-fund` names only `px`
5. `cp px.orig px.parquet`, then `vqapr check r-fund` names `fund`
6. `cp fund.parquet fund_b.parquet` (now `fund` and `fundb` are stale), then `vqapr check r-both` names only `fund`
7. `vqapr register data.yaml` (re-registers `fund`), then `vqapr check r-both` names `fundb`

Reproduced 2 of 2 attempts in fresh workspaces, with identical envelopes apart from paths.

## Impact

Not blocked: each round's `fix` works. The cost is one `check`-and-register round per rewritten
file. Each envelope's `fix` names one dataset, so a user who follows it believes the workspace is
repaired after one `register`. That round trip per defect is exactly what `check` is documented to
remove.

## What would have prevented it

`check` naming every registered dataset whose file no longer matches its digest, in one envelope,
as its help promises. Or, if one at a time is intended, the help and `check-before-run.md` saying
that stale sources are reported one per call.
