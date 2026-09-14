# Deliberate refusals carry `cause.origin: "user"` with `cause.where` pointing at the `vqapr.exe` launcher, the same label the skills teach as "your own code raised"; some refusals in `--jobs` workers carry all-null `cause` instead

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-stale-execution-dataset-reported-as-raw-traceback.md` and `report-2026-09-14-check-repeats-unregistered-input-as-raw-keyerror-traceback.md` (other `cause` fields that depart from `reading-the-envelope.md`).

## What I was doing

Reading refusal envelopes during the testbed run and while verifying its findings. Every
structured 4xx refusal from a CLI command run in one process names a file that is not the
user's, and labels it `origin: "user"`. The launcher's `__main__.py:10` appears as `where` on a
409 from `register`, a 409 from `run`, a 409 from `rm` and a 412 from `check` alike.

## What I expected

`vqapr-introduce-vqapr/references/reading-the-envelope.md`, the definition:

> `where` is always set: the innermost frame that is not the interpreter's, as
> `file:line (function)`. `origin` says whose frame that is: `"user"` for a file outside the vqapr
> package, `"framework"` for one inside it. … Two readings matter most: **`origin: "user"` with
> status 502 means your own code raised** — go to `where`, it is your line

The skills repeat the reading, always as "your own code". From `vqapr-inspect-workspace/SKILL.md`,
the same sentence closes `register-dataset`, `make-compliance`, `make-datamodel`,
`make-exchange` and `analyze-result`:

> **502 is your own code raising** — `cause.origin` is `"user"` and `cause.where` is your file and
> line; fix the component.

`vqapr-report-issue-dev/SKILL.md`: "`status` **502** | **No** — your own component raised.
`cause.origin` is `"user"` and `cause.where` names your file and line; fix it. Report only if
`cause.origin` is not `"user"`".

For a deliberate refusal, I expected the documented contract: `type`/`message`/`traceback` null and
`where` set. I expected `where` to name a frame that helps, and `origin` not to point the user at
their own code when no user code ran.

## What happened

A deliberate 409 from `register`. No user code is involved, yet `origin` is `"user"` and `where` is
the console-script launcher:

    $ vqapr register data-field-added.yaml
    {"correlation_id": "eb3fc9df917c41398dd3ca540c2c4e18", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'fund' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'fund' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'fund' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1"}

A deliberate 409 from `run`, the same labels:

    $ vqapr run r-fund
    {"correlation_id": "48e982bf299e49399c18985802396732", "error": "VqaprError: run: 1 failure(s)\n  [409 run.output_registered] a run publishes its output once unless told to replace it", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "run.output_registered", "example_total": 0, "examples": [], "fix": "vqapr run r-fund --force to replace it, or vqapr rm dataset r-fund-weights to withdraw it first", "observed": "'r-fund-weights' was published by an earlier run of 'r-fund'", "requirement": "a run publishes its output once unless told to replace it", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "pass --force, or withdraw the dataset, then retry", "stage": "run", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1"}

For comparison, a genuine raise from the user's own strategy (`s_boom.py`, line 13). This is what the
documentation describes, with `origin: "user"` and `where` the user's own file and line:

    $ vqapr run r-boom
    {"correlation_id": "61db01a8d4ce89291945937448ed19ec16b11ee2ec6a3911c5df72bb7bdc3ba0", "error": "1 of 1 strategies failed: s-boom; the other 0 completed and their records stand", "failures": [{"cause": {"message": "deliberate failure in the user's own strategy", "origin": "user", "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\engine\\stages\\decide.py\", line 231, in _callback_intent_boundary\n    yield\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\engine\\stages\\decide.py\", line 115, in dispatch\n    result = self._context.strategy.decide(\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py\", line 13, in decide\n    raise ValueError(\"deliberate failure in the user's own strategy\")\nValueError: deliberate failure in the user's own strategy\n", "type": "ValueError", "where": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py:13 (decide)"}, "code": "strategy.callback.intent", "example_total": 0, "examples": [], "fix": "your callback raised ValueError; read `observed` for the message it carried, fix the component, and re-run -- registration replaces in place, so no new id is needed", "observed": "deliberate failure in the user's own strategy", "requirement": "the strategy callback must return without raising", "source": {"file": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py", "key_path": "strategies.s-boom", "line": 13}, "status": 502, "strategy": "s-boom"}], "mutation": false, "ok": false, "retry_precondition": null, "roster": {"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "r-boom", "stage": "run.strategy_failed", "store_root": ".vqapr", "strategies": {"s-boom": {"at": {"account_version": 0, "clock": "2024-01-02T16:00:00+09:00", "cutoff": "2024-01-02T16:00:00+09:00", "frozen_run_identity": "61db01a8d4ce89291945937448ed19ec16b11ee2ec6a3911c5df72bb7bdc3ba0", "model_version": 0, "pending_id": null, "root_version": 1}, "component_id": "s-boom", "correlation_id": "61db01a8d4ce89291945937448ed19ec16b11ee2ec6a3911c5df72bb7bdc3ba0", "failures": [{"cause": {"message": "deliberate failure in the user's own strategy", "origin": "user", "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\engine\\stages\\decide.py\", line 231, in _callback_intent_boundary\n    yield\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\engine\\stages\\decide.py\", line 115, in dispatch\n    result = self._context.strategy.decide(\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py\", line 13, in decide\n    raise ValueError(\"deliberate failure in the user's own strategy\")\nValueError: deliberate failure in the user's own strategy\n", "type": "ValueError", "where": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py:13 (decide)"}, "code": "strategy.callback.intent", "example_total": 0, "examples": [], "fix": "your callback raised ValueError; read `observed` for the message it carried, fix the component, and re-run -- registration replaces in place, so no new id is needed", "observed": "deliberate failure in the user's own strategy", "requirement": "the strategy callback must return without raising", "source": {"file": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1\\s_boom.py", "key_path": "strategies.s-boom", "line": 13}, "status": 502}], "kind": "PRE_COMMIT", "mutation": false, "retry_precondition": {"required_pending_id": null, "requires_replay_from_root": true}, "stage": "simulation.callback.intent", "status": "failed"}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1"}

The two differ only in `status` and `type`. The `origin` label does not tell them apart, and the
skills' reading "`origin: "user"` … go to `where`, it is your line" sends the reader of the first two
to `...\Scripts\vqapr.exe\__main__.py`.

Inside `--jobs` workers the fields are not consistent. A worker's `409 record.exists` carries the
same `origin: "user"` and launcher `where`:

    $ vqapr run r-fund r-px --jobs 2
    {"jobs": 2, "ok": false, "runs": {"r-fund": {"correlation_id": "2064ea28e1974edcaca40f09f05292eb", "error": "VqaprError: record: 1 failure(s)\n  [409 record.exists] a strategy record is written once per run and fingerprint", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "record.exists", "example_total": 0, "examples": [], "fix": "edit the strategy (a new fingerprint records beside the old one), or replace this record and the dataset it published deliberately: vqapr run r-fund --force", "observed": "'r-fund/s-fund@4bb784ce' already has a record at .vqapr\\runs\\r-fund\\strategies\\s-fund@4bb784ce", "requirement": "a strategy record is written once per run and fingerprint", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "change the strategy so its fingerprint differs, or pass --force to replace the standing record, then retry", "stage": "record"}, "r-px": {"correlation_id": "cf65d40c2a2441e8992c6b7ce9caa87c", "error": "VqaprError: record: 1 failure(s)\n  [409 record.exists] a strategy record is written once per run and fingerprint", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "record.exists", "example_total": 0, "examples": [], "fix": "edit the strategy (a new fingerprint records beside the old one), or replace this record and the dataset it published deliberately: vqapr run r-px --force", "observed": "'r-px/s-px@10b2c6f5' already has a record at .vqapr\\runs\\r-px\\strategies\\s-px@10b2c6f5", "requirement": "a strategy record is written once per run and fingerprint", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "change the strategy so its fingerprint differs, or pass --force to replace the standing record, then retry", "stage": "record"}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1"}

A worker's `409 dataset.registered` in a `--force` batch carries an all-null `cause`, `where`
included, although `where` is documented as always set:

    $ vqapr run r-fund r-px --jobs 2 --force
    {"jobs": 2, "ok": false, "runs": {"r-fund": {"correlation_id": "560abd89761240e191faf5a06237df5c", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-fund-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-fund-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}, "r-px": {"correlation_id": "c358969805d24a25a29cd204e10d2c76", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'r-px-weights' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": null, "traceback": null, "type": null, "where": null}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'r-px-weights' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'r-px-weights' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register"}}, "stage": "run.complete", "store_root": ".vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws16b"}

By the letter of the definition, the launcher is "a file outside the vqapr package", so `"user"`
may be a literal reading of it. The point of this report is what the label then tells a reader:
the documented reading points at a file the user did not write, for a refusal no user code caused.

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

`data-field-added.yaml` is `data.yaml` with `score2: score2` added under `datasets.fund.fields` and
`score2: DOUBLE` under `datasets.fund.field_types`. `extra.yaml` registers a raising strategy and
its run, plus a second input dataset (`fund_b.parquet` is a copy of `fund.parquet`, used by other
reports):

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

1. `python gen.py .`, copy `fund.parquet` to `fund_b.parquet`
2. `vqapr register data.yaml`, `vqapr register runs.yaml`, `vqapr register extra.yaml`
3. `vqapr register data-field-added.yaml` returns 409 with `origin: "user"`, `where: ...\vqapr.exe\__main__.py:10 (<module>)`
4. `vqapr run r-fund r-px`, then `vqapr run r-fund` returns 409 with the same labels
5. `vqapr run r-fund r-px --jobs 2` returns worker `record.exists` entries with the same labels
6. `vqapr run r-boom` returns 502 with `origin: "user"` and `where` the user's `s_boom.py:13`, for contrast

The all-null worker `cause` needs an edited strategy with a published output: edit `s_fund.py`
(`INVESTED = Decimal("0.9")`) and `s_px.py` likewise, then `vqapr register strategy s-fund s_fund.py`,
`vqapr register strategy s-px s_px.py`, `vqapr run r-fund r-px --jobs 2 --force`.

Reproduced 2 of 2 attempts in fresh workspaces for steps 3–6. The all-null worker `cause`
reproduced 2 of 2 as well, in the workspaces of
`report-2026-09-14-run-force-in-a-jobs-batch-refused-with-409-dataset-registered.md`. The launcher
`where` appears on every single-process structured refusal in this verification: `register`, `run`,
`rm` and `check`.

## Impact

Not blocked. `status` disambiguates for a reader who branches on it first, as the documentation
advises. The cost is that the one field documented as deciding "correctly" who must act gives the
same answer for a package refusal and for a raise in the user's strategy. `where` names a frame that
carries no information. An agent following `report-issue-dev` ("Report only if `cause.origin` is not
`"user"`") is steered away from reporting, and in the testbed run an agent was shown package-side
paths in a field it was told means "your line".

## What would have prevented it

Deliberate refusals carrying the contract the envelope documentation states (`where` set to a frame
that locates the refusal, or a documented value meaning "no frame"), with an `origin` that does not
read as the user's code. The same fields in one process and inside `--jobs` workers.
