# `check` reports an unregistered strategy input twice, the second copy carrying a raw `KeyError` traceback with `where: null`; `check <unknown run id>` has the same shape

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-rm-dataset-accepted-while-a-registered-runs-strategy-reads-it.md` (how the testbed reached this state).

## What I was doing

Checking a run whose strategy reads a dataset that is not registered. The first time, this came
from `vqapr rm dataset fund` being accepted while registered runs' strategies read `fund` (filed
separately as `report-2026-09-14-rm-dataset-accepted-while-a-registered-runs-strategy-reads-it.md`).
The same answer comes back without any `rm`, when the dataset was simply never registered, so this
is a separate problem.

## What I expected

`vqapr-introduce-vqapr/references/reading-the-envelope.md`, on `cause`:

> When an exception was involved, `type`/`message`/`traceback` are the exception as Python would
> print it … when the framework refused deliberately without one, those three are `null`. `where`
> is always set: the innermost frame that is not the interpreter's, as `file:line (function)`.

The same file: "**`origin: "framework"` with status 500 means the framework failed**". `vqapr check --help`:
"Reports every INDEPENDENT problem at once". One missing dataset is one problem, and a missing
registration is a deliberate refusal. I expected one entry, like the first one below, with no
exception attached.

## What happened

`check` returns the same 404 code twice for the one missing dataset. The first entry is the
structured refusal, with the reading component and a `fix`. The second has:
- `cause.type: "KeyError"` and a full Python traceback through files under `site-packages\vqapr\`;
- `cause.origin: null` and `cause.where: null`, although `where` is documented as always set;
- an all-null `source`;
- a `fix` telling the user to look up "one of the registered datasets listed above".

Here the dataset was never registered:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.unregistered", "example_total": 1, "examples": ["score"], "fix": "register 'fund' with `vqapr register <declaration>`", "observed": "'s-fund' reads 1 field(s) from it; registered: px", "requirement": "dataset 'fund' must be registered before a run can read it", "source": {"file": null, "key_path": "runs.r-fund.strategies.s-fund", "line": null}, "status": 404}, {"cause": {"message": "'fund'", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registry.py\", line 289, in dataset\n    registration = self._datasets[key]\n                   ~~~~~~~~~~~~~~^^^^^\nKeyError: 'fund'\n", "type": "KeyError", "where": null}, "code": "dataset.unregistered", "example_total": 0, "examples": [], "fix": "register dataset 'fund', or look up one of the registered datasets listed above", "observed": "registered datasets: px", "requirement": "dataset 'fund' must be registered in this workspace", "source": {"file": null, "key_path": null, "line": null}, "status": 404}], "ok": false, "passed": ["workspace", "run"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsk1"}

`run` on the same state returns only the first, structured entry:

    $ vqapr run r-fund
    {"correlation_id": "bfdd41c03c4f43c6a5246f44b6f7fb78", "error": "VqaprError: check: 1 failure(s)\n  [404 dataset.unregistered] dataset 'fund' must be registered before a run can read it", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.unregistered", "example_total": 1, "examples": ["score"], "fix": "register 'fund' with `vqapr register <declaration>`", "observed": "'s-fund' reads 1 field(s) from it; registered: px", "requirement": "dataset 'fund' must be registered before a run can read it", "source": {"file": null, "key_path": "runs.r-fund.strategies.s-fund", "line": null}, "status": 404}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsk1"}

It is identical after the dataset is withdrawn with `rm`:

    $ vqapr check r-fund
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.unregistered", "example_total": 1, "examples": ["score"], "fix": "register 'fund' with `vqapr register <declaration>`", "observed": "'s-fund' reads 1 field(s) from it; registered: px", "requirement": "dataset 'fund' must be registered before a run can read it", "source": {"file": null, "key_path": "runs.r-fund.strategies.s-fund", "line": null}, "status": 404}, {"cause": {"message": "'fund'", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registry.py\", line 289, in dataset\n    registration = self._datasets[key]\n                   ~~~~~~~~~~~~~~^^^^^\nKeyError: 'fund'\n", "type": "KeyError", "where": null}, "code": "dataset.unregistered", "example_total": 0, "examples": [], "fix": "register dataset 'fund', or look up one of the registered datasets listed above", "observed": "registered datasets: px", "requirement": "dataset 'fund' must be registered in this workspace", "source": {"file": null, "key_path": null, "line": null}, "status": 404}], "ok": false, "passed": ["workspace", "run"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

The same shape answers `check` on a run id that does not exist: `404 run.unregistered` whose
`cause` is a `KeyError` traceback with `where: null`:

    $ vqapr check no-such-run
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": "'no-such-run'", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\references.py\", line 91, in _config_lookup\n    return declarations[key]\n           ~~~~~~~~~~~~^^^^^\nKeyError: 'no-such-run'\n", "type": "KeyError", "where": null}, "code": "run.unregistered", "example_total": 0, "examples": [], "fix": "register a run for run 'no-such-run', or use one of the ids listed above", "observed": "registered runs: r-boom, r-both, r-fund, r-px", "requirement": "run for run 'no-such-run' must be registered", "source": {"file": null, "key_path": null, "line": null}, "status": 404}], "ok": false, "passed": ["workspace"], "skipped": [{"blocked_by": "run", "check": "judgments"}, {"blocked_by": "run", "check": "preflight"}], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wso1"}

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

`data-no-fund.yaml` is `data.yaml` with the whole `datasets.fund` block deleted. It keeps
`instruments`, `px`, and the three components, `s-fund` among them, which reads `fund`.

1. `python gen.py .`
2. `vqapr register data-no-fund.yaml`, `vqapr register runs.yaml` (both accepted)
3. `vqapr check r-fund` returns two `404 dataset.unregistered` entries, the second with a `KeyError` traceback

Also: `vqapr check no-such-run` in any workspace.

Reproduced 2 of 2 attempts with the dataset never registered, 2 of 2 after `rm dataset fund`, and
2 of 2 for `check no-such-run`, all in fresh workspaces.

## Impact

A papercut. The first entry carries the right fix. The cost is noise, in the command whose purpose
is a clean list of problems: a user counting problems sees two where there is one. A traceback with
package file paths and line numbers arrives for a lookup miss, with no `where` to go to. A mistyped
run id gives only the traceback form.

## What would have prevented it

One entry per missing dataset, and a lookup miss (dataset or run id) answered as the first entry
is: a deliberate refusal with `type`, `message` and `traceback` null and `where` set, as the
envelope documentation describes.
