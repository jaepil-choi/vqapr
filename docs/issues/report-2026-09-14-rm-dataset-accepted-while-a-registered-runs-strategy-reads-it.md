# `vqapr rm dataset` withdraws a dataset that a registered run's strategy reads; only a dataset the run names directly is protected

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-register-refuses-changed-dataset-declaration-skill-says-replaces.md` (the refusal the testbed agent was working around), and closed `archive/080`/`081` (record `157`).

## What I was doing

In the testbed run, the agent ran `vqapr rm dataset ff-book-equity` to get past a refused
re-registration (filed separately as
`report-2026-09-14-register-refuses-changed-dataset-declaration-skill-says-replaces.md`). Registered
runs had strategies that read `ff-book-equity`, and the agent wrote that it "had half expected the
rm to be refused". The rm was accepted. The reproduction below isolates that acceptance.

## What I expected

`vqapr-register-dataset/references/correcting-a-registration.md`, "Withdrawing":

> Refused while a registered run still names it — and the refusal names which run.

`vqapr-inspect-workspace/SKILL.md`, "Removing things":

> Removing something a registered run still names is refused, **and the refusal names the run**,
> which makes `rm` a dependency report as well as a verb.

`vqapr-inspect-workspace/references/deleting.md` presents the refusal as the same query as
`list components --reads`:

> `rm` refuses while a registered run still names the thing — **and the refusal names which run.**
> That makes a refused `rm` a useful answer rather than an obstacle: it is the dependency query you
> would otherwise have to construct.
>
> The deliberate version of the same query, before deleting anything:
>
>     vqapr list components --reads <dataset-id>    # what would lose its input

`vqapr rm --help`: "run-definition and the other declaration kinds … a registration nothing live
still names". I expected `rm dataset fund` to be refused, because the registered runs `r-fund` and
`r-px` run strategies that `list components --reads fund` names.

## What happened

The survey the skill recommends shows two components that read `fund`, and both are run by
registered runs:

    $ vqapr list components --reads fund
    {"count": 2, "items": [{"component_id": "s-fund", "fingerprint": "4bb784ce862dc0cfff3a6d2b46173ebbe2a6138e72cba50d6e63359eea68d80c", "kind": "strategy", "object_name": "SFund", "reads": {"fund": ["score"]}}, {"component_id": "s-px", "fingerprint": "10b2c6f5ad1c9b3ea11ae7230e090bbeb93f17b6aa86f844bf4ef05f9eb5ea2e", "kind": "strategy", "object_name": "SPx", "reads": {"fund": ["score"]}}], "kind": "components", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

    $ vqapr list runs
    {"count": 2, "items": [{"end": "2024-02-28T15:30:00+09:00", "exchange": "venue", "execution": {"dataset": "px", "fill": {"at": "15:30:00"}, "trade_price": "close"}, "kind": "strategy", "model": "s-fund", "recorded": [], "run_id": "r-fund", "start": "2024-01-02T00:00:00+09:00", "status": "registered", "timezone": "Asia/Seoul", "writes": "r-fund-weights"}, {"end": "2024-02-28T15:30:00+09:00", "exchange": "venue", "execution": {"dataset": "px", "fill": {"at": "15:30:00"}, "trade_price": "close"}, "kind": "strategy", "model": "s-px", "recorded": [], "run_id": "r-px", "start": "2024-01-02T00:00:00+09:00", "status": "registered", "timezone": "Asia/Seoul", "writes": "r-px-weights"}], "kind": "runs", "ok": true, "stage": "workspace.list", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

The dataset both runs name directly, as their execution table, is protected, and the refusal names
the runs:

    $ vqapr rm dataset px
    {"correlation_id": "57895abaacc241e89d9f8bfd8debde9c", "error": "VqaprError: remove: 1 failure(s)\n  [409 remove.referenced] a dataset may be removed only when nothing live still names it", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "remove.referenced", "example_total": 0, "examples": [], "fix": "remove run 'r-fund' (execution), run 'r-px' (execution) first, or keep 'px' registered", "observed": "'px' is referenced by run 'r-fund' (execution), run 'r-px' (execution)", "requirement": "a dataset may be removed only when nothing live still names it", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "withdraw the referencing declarations, then retry", "stage": "remove", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

The dataset their strategies read is withdrawn without a word:

    $ vqapr rm dataset fund
    {"identifier": "fund", "kind": "dataset", "ok": true, "removed": true, "stage": "workspace.removed", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

Both registered runs are now unrunnable. The next `run` is refused:

    $ vqapr run r-fund
    {"correlation_id": "71c4eadb464b40f6a3a0c32990d8100d", "error": "VqaprError: check: 1 failure(s)\n  [404 dataset.unregistered] dataset 'fund' must be registered before a run can read it", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.unregistered", "example_total": 1, "examples": ["score"], "fix": "register 'fund' with `vqapr register <declaration>`", "observed": "'s-fund' reads 1 field(s) from it; registered: px", "requirement": "dataset 'fund' must be registered before a run can read it", "source": {"file": null, "key_path": "runs.r-fund.strategies.s-fund", "line": null}, "status": 404}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\wsr1"}

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
2. `vqapr register data.yaml`, `vqapr register runs.yaml`
3. `vqapr list components --reads fund` lists `s-fund` and `s-px`
4. `vqapr rm dataset px` gives `409 remove.referenced`, naming `r-fund` and `r-px`
5. `vqapr rm dataset fund` gives `ok: true`, `removed: true`. **This is the report.**
6. `vqapr run r-fund` gives `404 dataset.unregistered`

Reproduced 2 of 2 attempts in fresh workspaces. The testbed run saw the same acceptance on
`ff-book-equity`.

## Impact

Nothing was blocked, and in the testbed the acceptance happened to be the workaround the agent
wanted. The removal is reversible: registering the declaration again restores it, and the user's
file is untouched. The cost is that `rm` does not work as the dependency report the skills
describe for the most common dependency, a strategy's input. A registered run becomes unrunnable,
and that is found only at the next `check` or `run`. Whether acceptance is the intended behaviour is
not visible from the surface: the rm and the skills disagree.

## What would have prevented it

`rm dataset` refusing while a registered run's strategy reads the dataset, naming the run and the
component, as it already does for `execution`. Or the skills saying that the refusal covers only
datasets a run names directly (for example `execution`), with `list components --reads` as the
survey for the rest.
