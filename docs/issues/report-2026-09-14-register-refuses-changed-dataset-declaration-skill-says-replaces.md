# `register` refuses a changed dataset declaration with 409, while the register-dataset skill says registering the same id again replaces it in place

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** closed `archive/067` (the skill required `register --force` for an edited component; a plain re-register now replaces) and `archive/084` (a run definition refuses re-registration). The skill's replace-in-place rule names `runs:` as its only exception; this is the dataset case it does not cover.

## What I was doing

Correcting a dataset that was already registered. In the testbed run, the user redefined book equity, so the
agent added two fields (`nci`, `book_equity`) to the registered dataset `ff-book-equity` and
registered the same YAML document again. In the reproduction below, the same step is adding one field,
`score2`, to the registered dataset `fund`. The column is already in the parquet, so only the
declaration changes.

## What I expected

`vqapr-register-dataset/SKILL.md`, section "Correcting a registration":

> Registering the same id again replaces it in place, with no flag; there is no `register --force`.
> A `runs:` declaration is the exception.

`vqapr-register-dataset/references/correcting-a-registration.md`, "The ordinary loop":

> `vqapr register prices.yaml   # a declaration: the same file again` … It replaces the
> registration in place, with no flag … The success payload then carries
> `replaced: {fingerprint: <the old one>}`

Both name `runs:` as the only kind that is refused in place. The package's own dataset template
(`vqapr new dataset`) says the opposite: "Registrations are immutable. During disposable first-run
setup, correct this YAML and rebuild the project-local workspace; after a run matters, preserve
provenance by registering a new id." The package's surfaces disagree. The skill is the one an agent
follows, and it is wrong for datasets.

## What happened

The changed declaration is refused. The whole document is refused (`mutation: false`), so no other
dataset or component in the same file is registered or re-measured either:

    $ vqapr register data-field-added.yaml
    {"correlation_id": "9b0c44c71b424ac4850483a395304bcf", "error": "VqaprError: register: 1 failure(s)\n  [409 dataset.registered] dataset_id 'fund' must keep its existing declaration or use a new identity", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "dataset.registered", "example_total": 0, "examples": [], "fix": "keep the registered declaration for 'fund' unchanged, or choose a new dataset_id", "observed": "a different declaration is already registered", "requirement": "dataset_id 'fund' must keep its existing declaration or use a new identity", "source": {"file": null, "key_path": null, "line": null}, "status": 409}], "mutation": false, "ok": false, "retry_precondition": "use the existing declaration or choose a new dataset_id", "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws13"}

For contrast, in the same workspace a component re-registered under the same id is replaced in place,
as the skill describes, and an unchanged dataset declaration registered again is accepted:

    $ vqapr register strategy s-fund s_fund.py
    {"component": {"id": "s-fund", "kind": "strategy", "object": "SFund", "source": "s_fund.py"}, "ok": true, "registered": {"components": ["s-fund"]}, "replaced": {"fingerprint": "4bb784ce862dc0cfff3a6d2b46173ebbe2a6138e72cba50d6e63359eea68d80c"}, "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws13"}

    $ vqapr register data.yaml
    {"ok": true, "registered": {"components": ["venue", "s-fund", "s-px"], "datasets": ["px", "fund"], "instruments": [{"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3}]}, "spoken": ["dataset 'px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'fund': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws13"}

The route that worked was withdrawing the dataset first, then registering the document:

    $ vqapr rm dataset fund
    {"identifier": "fund", "kind": "dataset", "ok": true, "removed": true, "stage": "workspace.removed", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws13"}

    $ vqapr register data-field-added.yaml
    {"ok": true, "registered": {"components": ["venue", "s-fund", "s-px"], "datasets": ["px", "fund"], "instruments": [{"by_kind": {"stock": 3}, "digest": "ec447dd5cf8223b626b22a0e8c8dcf74fb722497f32bd28c17230e9741be982f", "instruments": 3}]}, "spoken": ["dataset 'px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'fund': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v2\\ws13"}

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

`data-field-added.yaml` is `data.yaml` with two lines added under `datasets.fund`: `score2: score2`
under `fields`, and `score2: DOUBLE` under `field_types`. No other difference.

1. `python gen.py .`
2. `vqapr register data.yaml` succeeds
3. `vqapr register data-field-added.yaml` fails here with `409 dataset.registered`

Reproduced 2 of 2 attempts, in one fresh workspace with the same command twice. The testbed run hit the
identical refusal on `ff-book-equity`.

## Impact

Worked around with `vqapr rm dataset <id>` followed by the same `register`. In the testbed run this
cost a check cycle. Because the document was refused whole, a second dataset in it (`ff-prices`) was
not re-measured either, although its declaration was unchanged and only its file had changed. The
result is unaffected.

## What would have prevented it

The skill and `correcting-a-registration.md` naming datasets as a second exception beside `runs:`,
with the route (a new id, or `vqapr rm dataset <id>` first), in agreement with the dataset
template. Or the 409's `fix` naming `vqapr rm dataset fund` as a route, beside "choose a new
dataset_id".
