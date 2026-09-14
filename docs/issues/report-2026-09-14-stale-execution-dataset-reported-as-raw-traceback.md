# A rewritten source file under a run's execution dataset is reported as `judgment.blocked` carrying a raw Python traceback; `vqapr run` gives only that

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** closed `archive/095` (record `234`), which made `dataset.source_changed` the one answer for a stale source. A stale **execution** dataset does not reach that answer.

## What I was doing

The agent had corrected its data preparation and rewritten two registered parquet files: the price
table, which is also the runs' execution dataset, and a fundamentals table that the strategies read.
It then checked two runs before re-running them. `vqapr check km-s1`, whose execution dataset had
been registered on the new bytes and which read the stale fundamentals, came back with a structured
`dataset.source_changed` and a `fix`. `vqapr check ff-s1`, whose execution dataset `ff-prices` was
stale, came back with a blocked judgment whose cause is a Python traceback.

## What I expected

`vqapr-run-backtest/references/check-before-run.md`: "A judgment that could not run because an
earlier one failed is reported as **blocked**, naming what blocked it". The run-backtest skill
closes with: "A refusal carries its own status, stage and cause, plus `fix`, `requirement`,
`observed` and `source` — read it rather than looking for it here."

For a stale dataset that a strategy reads, the package answers with exactly that. The refusal is
`412 dataset.source_changed`, with both digests and a `fix` naming the register command. I expected
the same answer when the stale dataset is the run's `execution.dataset`.

## What happened

Which dataset was rewritten decides the answer. Whether the run has records, whether the strategy
also reads the execution dataset as an input, and whether the rewrite changed values or added a
column make no difference.

| rewritten file | `vqapr check <run>` | `vqapr run <run>` |
|---|---|---|
| a strategy input only (`fund`) | structured `412 dataset.source_changed` in `failures`, with `fix` and both digests; `judgments` passed | `stage: freeze`, the same structured 412, `retry_precondition` naming the register command |
| the run's execution dataset (`px`) | `blocked`: `412 judgment.blocked` whose `cause.traceback` is a full Python traceback through files under `site-packages\vqapr\`; its `fix` is "run `vqapr check r-fund` to see the full report", the command just run. The structured 412 for `px` is also in `failures` | `stage: check`, **only** the `judgment.blocked` entry with the traceback: no `dataset.source_changed` failure, no digests, and a `fix` pointing back at `check` |

Execution dataset rewritten, `check`:

    $ vqapr check r-fund
    {"blocked": [{"cause": {"message": "freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 189, in judgments\n    found.extend(judge())\n                 ^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 165, in <lambda>\n    lambda: _judge_execution_ordering(definition, at, read),\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 343, in _judge_execution_ordering\n    table = facts.execution_table()\n            ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 285, in execution_table\n    return self._once(  # type: ignore[return-value]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 276, in _once\n    raise error\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 271, in _once\n    self._settled[key] = (read(), None)\n                          ^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 286, in <lambda>\n    \"execution_table\", lambda: bound_execution_table(self._workspace, self._definition)\n                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 133, in bound_execution_table\n    registration = workspace.require_verified(binding.dataset)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registry.py\", line 405, in require_verified\n    require_verified(registration, source, digest=self.source_digest(source))\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\data\\verification.py\", line 706, in require_verified\n    raise VqaprError(\nvqapr.domain.errors.VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them\n", "type": "VqaprError", "where": null}, "code": "judgment.blocked", "example_total": 0, "examples": [], "fix": "run `vqapr check r-fund` to see the full report, then fix what stopped the judgment from answering; the exception is in `cause`", "observed": "execution_ordering could not answer: VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "requirement": "every judgment answers before a run is accepted", "source": {"file": null, "key_path": "runs.r-fund", "line": null}, "status": 412}], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'px' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'px': registered digest c95573120661…, file now d2ff4f2fa352…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "px.parquet", "key_path": "datasets.px", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws14a"}

Execution dataset rewritten, `run` (the run had an earlier record; the answer is the same on a run
with none):

    $ vqapr run r-fund
    {"correlation_id": "d390ba5b18114b0a82313c3c1829af18", "error": "VqaprError: check: 1 failure(s)\n  [412 judgment.blocked] every judgment answers before a run is accepted", "failures": [{"cause": {"message": "freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 189, in judgments\n    found.extend(judge())\n                 ^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 165, in <lambda>\n    lambda: _judge_execution_ordering(definition, at, read),\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 343, in _judge_execution_ordering\n    table = facts.execution_table()\n            ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 285, in execution_table\n    return self._once(  # type: ignore[return-value]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 276, in _once\n    raise error\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 271, in _once\n    self._settled[key] = (read(), None)\n                          ^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 286, in <lambda>\n    \"execution_table\", lambda: bound_execution_table(self._workspace, self._definition)\n                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 133, in bound_execution_table\n    registration = workspace.require_verified(binding.dataset)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registry.py\", line 405, in require_verified\n    require_verified(registration, source, digest=self.source_digest(source))\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\data\\verification.py\", line 706, in require_verified\n    raise VqaprError(\nvqapr.domain.errors.VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them\n", "type": "VqaprError", "where": null}, "code": "judgment.blocked", "example_total": 0, "examples": [], "fix": "run `vqapr check r-fund` to see the full report, then fix what stopped the judgment from answering; the exception is in `cause`", "observed": "execution_ordering could not answer: VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "requirement": "every judgment answers before a run is accepted", "source": {"file": null, "key_path": "runs.r-fund", "line": null}, "status": 412}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws14b"}

For contrast, the strategy-input file rewritten, `check` and `run`:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fund' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fund': registered digest b51756de47d3…, file now 334f3e50d83e…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund.parquet", "key_path": "datasets.fund", "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run", "judgments"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws14a"}

    $ vqapr run r-fund
    {"correlation_id": "d4f8564f860142c4b4b47f0c4157beab", "error": "VqaprError: freeze: 1 failure(s)\n  [412 dataset.source_changed] the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.source_changed", "example_total": 0, "examples": [], "fix": "register dataset 'fund' again so its facts are measured on the file as it is now -- the command is `vqapr register <its declaration file>`", "observed": "dataset 'fund': registered digest b51756de47d3…, file now 21390619180d…", "requirement": "the bytes a run reads must be the bytes registration measured; every fact the registration carries (span, key, prices) was measured on them", "source": {"file": "fund.parquet", "key_path": "datasets.fund", "line": null}, "status": 412}], "mutation": false, "ok": false, "retry_precondition": "register dataset 'fund' again (`vqapr register <its declaration file>`), then retry", "stage": "freeze", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws14c"}

On the testbed run's own envelope: the `check ff-s1` envelope was not saved. The testbed recorded
that it carried no `fix` naming the register command and no digests. In this reproduction, `check`
carries the structured failure beside the traceback, and `run` does not. So the part that reproduces
without condition is the traceback, and a `run` that names no route.

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
2. `vqapr register data.yaml`, then `vqapr register runs.yaml`
3. `python gen.py . --variant 1 --only px` rewrites the execution dataset's file
4. `vqapr check r-fund` returns a `blocked` entry with a traceback (plus the structured failure)
5. `vqapr run r-fund` returns only the `blocked` entry with the traceback

Contrast: step 3 with `--only fund` gives the structured 412 in both commands.

Reproduced in 3 of 3 fresh workspaces, with runs `r-fund` and `r-px` checked each time:
- never run before;
- run once before the rewrite;
- a rewrite that only added a column (`ret_close`), as in the testbed run, with `run` under `--jobs 2`.

The input-only case gave the structured 412 in all three.

## Impact

Not blocked. The agent recovered because a second run's envelope named the fix. A user with only
the one run, or only the `run` envelope, is told to run `check`, and gets a traceback. The envelope
also puts package file paths and line numbers in front of a user whose instructions forbid opening
package source.

## What would have prevented it

A stale execution dataset answered with the same structured `dataset.source_changed` (fix and both
digests) that a stale input gets, in `run` as well as in `check`, and no traceback in the envelope
for a condition the package already names.
