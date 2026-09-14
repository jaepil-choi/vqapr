# Money in a held name that is delisted, or halted at a rebalance, cannot fund the next book, and no declaration can settle it

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** the behaviour is documented in `introduce-vqapr/SKILL.md` ("What it does not do") and `factor-portfolios.md`. This report asks for a declarable treatment and a stated number. The zero-dealt reason code on the academic profile is filed separately from the same run (testbed F-012).

## What I was doing

Six Fama-French 2x3 legs on Korean data (KOSPI and KOSDAQ, June 2018 to July 2026). Each leg is a
value-weighted StrategyModel on a divisible `academic` venue. It decides once a year after June's
last close and fills at the next session's close.

The definition being reproduced is the Fama-French buy-and-hold one: buy the leg at value weights
every June with all of the leg's money. A name that stopped trading during the year is worth its
last price, and that value goes into the new book. The comparison series is a pandas rebuild of the
same membership that does exactly this. The evaluator reproduced the mechanism on a four-name
synthetic panel, below.

## What I expected

The behaviour itself is documented:

- `vqapr-introduce-vqapr/SKILL.md`, "What it does not do": "A delisted holding is never sold. It
  stays in the book at its last price until the run ends, and money held in a name that cannot be
  sold — halted or delisted — cannot pay for the next book, so the smallest new buys go unfilled.
  A leg held a year at a time carries a few percent of such dead capital; the record shows exactly
  how much."
- `vqapr-make-strategy/references/factor-portfolios.md`, "What it cannot express exactly":
  "Delisted holdings ... the smallest new buys go unfilled (recorded `no_trade`) ... Read
  `vqapr.fill` to see it per rebalance."

What I expected, and did not find, was one of two things:

1. **A way to declare the treatment.** For example, "a held name with no row in the execution
   table at a fill is settled at its last price". I looked in every declaration surface I could
   reach:
   - the `vqapr new run` template
   - the `execution:` block of the `vqapr new dataset` template, whose only key is `is_tradable`
   - the `vqapr new instruments` template
   - the `vqapr new exchange --profile academic` scaffold
   - `RunFill` / `FillRule`: `trade_price`, `timezone`, `at`, `after`, `within`
   - `TradeRule`: `instrument_id`, `quantity_step`, `minimum_quantity`, `fractional_allowed`,
     `access`, `buy`, `sell`
   - `AcademicExchange(listings, exchange_id)`
   - `ZeroDealtReason`: `ABSENT`, `NONTRADABLE`, `NO_TRADE`, `UNFUNDED`

   None offers a delisting or halt treatment.
2. **"The record shows exactly how much" as a number.** That is, the money held in names the
   target did not ask for, as a share of NAV, at each rebalance.

## What happened

A synthetic panel of four names, A to D, on an academic, divisible, long-only venue. The strategy
decides after the close on each month's last session. It holds, in equal weight, every name with a
tradable close in the newest cross-section. A delists after 2024-02-15, meaning it has no row after
that date. B is halted (`is_tradable` false) from 2024-03-28 to 2024-04-02. D lists on 2024-02-01.
The targets were therefore January {A, B, C}, February {B, C, D} and March {C, D}.

    $ vqapr --project-root <dir> register <dir>/data.yaml
    {"ok": true, "registered": {"components": ["stuck-venue", "eqw"], "datasets": ["stuck-px"], "instruments": [{"by_kind": {"stock": 4}, "digest": "fd4ed2b07323fdaa679857e5c6c60a8c952f324c2a26613814a95cf0b7cd70f5", "instruments": 4}]}, "spoken": ["dataset 'stuck-px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008"}

    $ vqapr --project-root <dir> register <dir>/runs.yaml
    {"ok": true, "registered": {"runs": ["stuck"]}, "spoken": ["run 'stuck' fills against dataset 'stuck-px': the first execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'close' price", "run 'stuck': the model is called every 1M on the last trading day at 16:00:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008"}

    $ vqapr --project-root <dir> check stuck
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "ok": true, "passed": ["workspace", "run", "judgments", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008"}

    $ vqapr --project-root <dir> run stuck
    {"ok": true, "roster": {"by_kind": {"stock": 4}, "digest": "fd4ed2b07323fdaa679857e5c6c60a8c952f324c2a26613814a95cf0b7cd70f5", "instruments": 4, "known": true, "tables": ["stock"]}, "run_id": "stuck", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\.vqapr", "strategies": {"eqw": {"account_version": 3, "contract": {"accepted_intents": 3}, "events": 89, "fills": {"dealt": 6, "never_filled": [], "orders": 11, "partial": 0, "reasons": {"absent": 2, "no_trade": 2, "nontradable": 1}, "zero_dealt": 5}, "fingerprint": "628e3a11c043ef34f4b6212b52b4c2ee9227cc192b555994dce2bac3f0958cab", "record": "eqw@628e3a11", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.018018, "due": 0.063407, "simulation.due.account_commit": 0.000737, "simulation.due.account_mark": 0.022942, "simulation.due.account_preparation": 0.000409, "simulation.due.exchange_execution": 0.000184, "simulation.due.feedback_candidate": 2.4e-05, "simulation.due.feedback_publication": 5.1e-05, "simulation.due.instrument_declaration": 3.4e-05, "simulation.due.order_planning": 0.000287, "simulation.due.snapshot": 0.034316, "simulation.due.valuation_mark": 0.000268, "simulation.due.valuation_selection": 0.00057, "total": 0.088101}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008", "writes": "stuck-weights"}

    $ vqapr --project-root <dir> export stuck/eqw --out <dir>/export
    {"files": [{"path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export\\nav.csv", "rows": 86}, {"path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export\\holdings.csv", "rows": 235}, {"path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export\\fills.csv", "rows": 11}, {"path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export\\weights.csv", "rows": 8}, {"path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export\\report.json", "rows": null}], "ok": true, "omitted": {}, "out": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008\\export", "run_id": "stuck", "stage": "strategy.export", "strategy_ref": "eqw@628e3a11", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008"}

    $ vqapr --project-root <dir> show strategy stuck/eqw --table vqapr.fill --limit 20
    {"items": [{"account_version": 1, "cash_delta": "-333333.3333330000000000000000", "commission": "0E-22", "dealt_quantity": "4350.150580457992553412236365", "event_time": "2024-02-01 15:30:00+09:00", "instrument": "A", "kind": "stock", "price": "76.6257", "producer_id": "eqw", "reason": null, "requested_quantity": "4350.150580457992553412236365", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 25, "sized_quantity": "4350.150580457992553412236365", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 1, "cash_delta": "-333333.3333330000000000000000", "commission": "0E-22", "dealt_quantity": "3689.944311356763003732747665", "event_time": "2024-02-01 15:30:00+09:00", "instrument": "B", "kind": "stock", "price": "90.3356", "producer_id": "eqw", "reason": null, "requested_quantity": "3689.944311356763003732747665", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 26, "sized_quantity": "3689.944311356763003732747665", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 1, "cash_delta": "-333333.3333340000000000000000", "commission": "0E-22", "dealt_quantity": "3327.935422085377517666345188", "event_time": "2024-02-01 15:30:00+09:00", "instrument": "C", "kind": "stock", "price": "100.1622", "producer_id": "eqw", "reason": null, "requested_quantity": "3327.935422085377517666345188", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 27, "sized_quantity": "3327.935422085377517666345188", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 2, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-03-01 15:30:00+09:00", "instrument": "A", "kind": null, "price": null, "producer_id": "eqw", "reason": "absent", "requested_quantity": "0E-24", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 115, "sized_quantity": null, "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 2, "cash_delta": "59401.97537598904269116869864", "commission": "0E-23", "dealt_quantity": "-773.150135504880740887071754", "event_time": "2024-03-01 15:30:00+09:00", "instrument": "B", "kind": "stock", "price": "76.8311", "producer_id": "eqw", "reason": null, "requested_quantity": "-773.150135504880740887071754", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 116, "sized_quantity": "-773.150135504880740887071754", "stage": "STRATEGY_CALLBACK", "tax": "0E-23"}, {"account_version": 2, "cash_delta": "164698.5296289768101487672648", "commission": "0E-22", "dealt_quantity": "-1409.741336509860232774315814", "event_time": "2024-03-01 15:30:00+09:00", "instrument": "C", "kind": "stock", "price": "116.8289", "producer_id": "eqw", "reason": null, "requested_quantity": "-1409.741336509860232774315814", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 117, "sized_quantity": "-1409.741336509860232774315814", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 2, "cash_delta": "-224100.5050049658528399359634", "commission": "0E-22", "dealt_quantity": "2457.468725244055952959877482", "event_time": "2024-03-01 15:30:00+09:00", "instrument": "D", "kind": "stock", "price": "91.1916", "producer_id": "eqw", "reason": null, "requested_quantity": "2457.468725244055952959877482", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 118, "sized_quantity": "2457.468725244055952959877482", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 3, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-04-01 15:30:00+09:00", "instrument": "A", "kind": null, "price": null, "producer_id": "eqw", "reason": "absent", "requested_quantity": "0E-24", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 226, "sized_quantity": null, "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 3, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-04-01 15:30:00+09:00", "instrument": "B", "kind": null, "price": null, "producer_id": "eqw", "reason": "nontradable", "requested_quantity": "-2916.794175851882262845675911", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 227, "sized_quantity": "-2916.794175851882262845675911", "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 3, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-04-01 15:30:00+09:00", "instrument": "C", "kind": null, "price": null, "producer_id": "eqw", "reason": "no_trade", "requested_quantity": "0", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 228, "sized_quantity": "951.246668154471352376939094", "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 3, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-04-01 15:30:00+09:00", "instrument": "D", "kind": null, "price": null, "producer_id": "eqw", "reason": "no_trade", "requested_quantity": "0", "run_id": "0a40df1ac61b7418eb808c416a26443f6536a49afe90e6ff8a9a0178239e2bf5", "sequence": 229, "sized_quantity": "1177.629232348260182113061613", "stage": "STRATEGY_CALLBACK", "tax": "0"}], "matched": 11, "ok": true, "returned": 11, "rows_total": 11, "run_id": "stuck", "stage": "strategy.table", "strategy_ref": "eqw@628e3a11", "table": "vqapr.fill", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f008"}

From `export/holdings.csv`, `nav.csv` and `weights.csv`, at the valuation of each fill instant:

| fill | NAV | cash | held in names the target left out | target vs held |
|---|---|---|---|---|
| 2024-02-01 | 1,000,000.00 | 0 | 0 | A, B, C: 0.3333 each / 0.3333 each |
| 2024-03-01 | 991,143.63 | 0 | A (delisted, `absent`): 318,842.11 = **32.17%** | B, C, D: 0.3333 each / **0.2261** each |
| 2024-04-01 | 995,400.00 | 0 | A (`absent`) 32.03% + B (halted, `nontradable`) 22.28% = **54.31%** | C, D: 0.5000 each / **0.2272**, **0.2297** |

- **2024-03-01:** A could not be sold. B and C were sold down, and D bought exactly the proceeds
  (cash_delta −224,100.505 = 59,401.975 + 164,698.530). On B, C and D, `requested_quantity` equals
  `sized_quantity` equals `dealt_quantity`. Each of the three ended at 0.2261 of NAV against a
  0.3333 target, and **no row carries a reason for that shortfall.** Only A's `absent` row appears.
- **2024-04-01:** there was nothing to sell, so both buys dealt zero, recorded
  `reason: "no_trade"`, `requested_quantity "0"`, `sized_quantity` 951.25 (C) and 1177.63 (D).
- **To the end of the run:** A stays in the book at 2024-02-15's close (73.2945) through
  2024-04-30, 31.96% of the final NAV.
- **`report.json`:** at every fill, `book.cash_share` is 0, `book.unmarked` is 0 and
  `book.net_exposure` is 1.000000. No field names money held outside the target. `intent.gap`
  (0, 0.6434, 1.0861; `mean_gap` 0.5765) equals twice the stuck share at each fill here, because
  cash is zero. It is a total of absolute weight gaps, not the stuck amount, and the stuck share had
  to be rebuilt from `holdings.csv` and `weights.csv`.

## Reproduction

This needs only the wheel, plus pandas, pyarrow and numpy, which the testbed's environment already
has. It reproduced 2 of 2 times, each from an empty directory. `fills.csv`, `holdings.csv` and
`nav.csv` were identical between the two runs apart from the `run_id` hash column.

1. Save the generator below as `make_f008.py` and run `uv run python make_f008.py <dir>`.
2. `uv run vqapr --project-root <dir> register <dir>/data.yaml`, then `... register <dir>/runs.yaml`.
3. `uv run vqapr --project-root <dir> check stuck`, then `... run stuck`.
4. `uv run vqapr --project-root <dir> export stuck/eqw --out <dir>/export`.
5. `uv run vqapr --project-root <dir> show strategy stuck/eqw --table vqapr.fill --limit 20`:
   `absent` on A at both later fills, `nontradable` on B and `no_trade` on C and D at 2024-04-01.
6. `uv run python analyze_f008.py <dir>` prints the table above.

```python
"""F-008 repro: money in a delisted or halted holding cannot fund the next book.

Writes, into the directory given as argv[1] (default: this file's directory):
  px.parquet   execution table, A B C D, one row per business day stamped 15:30 Asia/Seoul,
               2024-01-02 .. 2024-04-30, seeded random-walk closes:
                 A  last row 2024-02-15 (delisted: no row after that)
                 B  is_tradable = False 2024-03-28 .. 2024-04-02 (halted; rows present, close flat)
                 C  every day
                 D  first row 2024-02-01 (lists late)
  instruments_stock.parquet, venue.py (academic, divisible, long-only), eqw.py, data.yaml, runs.yaml

The strategy decides after the close (16:00) on each month's last session and holds, in equal
weight, every name that has a tradable close in the newest cross-section. It fills at the next
session's 15:30 close. Expected targets: Jan {A,B,C}, Feb {B,C,D}, Mar {C,D}.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
TZ = "Asia/Seoul"
DAYS = pd.bdate_range("2024-01-02", "2024-04-30")
rng = np.random.default_rng(20260914)

rows = []
for name in ["A", "B", "C", "D"]:
    close = 100.0
    for d in DAYS:
        if name == "A" and d > pd.Timestamp("2024-02-15"):
            continue  # delisted
        if name == "D" and d < pd.Timestamp("2024-02-01"):
            continue  # not yet listed
        halted = name == "B" and pd.Timestamp("2024-03-28") <= d <= pd.Timestamp("2024-04-02")
        if not halted:
            close *= 1.0 + rng.normal(0.001, 0.02)
        rows.append(
            {
                "instrument": name,
                "available_at": pd.Timestamp(f"{d:%Y-%m-%d} 15:30:00", tz=TZ),
                "close": round(close, 4),
                "is_tradable": not halted,
            }
        )
pd.DataFrame(rows).to_parquet(OUT / "px.parquet", index=False)
pd.DataFrame({"instrument_id": ["A", "B", "C", "D"], "kind": "stock"}).to_parquet(
    OUT / "instruments_stock.parquet", index=False
)

(OUT / "venue.py").write_text(
    '''from decimal import Decimal
from vqapr.public import AcademicExchange, ListingAccess, TradeRule

STEP = Decimal("0.00000001")


class Venue(AcademicExchange):
    """Divisible, long-only, cost-free listings."""

    def __init__(self, instruments):
        super().__init__(
            {
                str(n): TradeRule(instrument_id=str(n), quantity_step=STEP, minimum_quantity=STEP,
                                  fractional_allowed=True, access=ListingAccess.LONG_ONLY)
                for n in instruments
            },
            exchange_id="stuck-venue",
        )
''',
    encoding="utf-8",
)

(OUT / "eqw.py").write_text(
    '''import math

from vqapr import public as vq


class Eqw(vq.StrategyModel):
    """Equal weight over every name with a tradable close in the newest cross-section."""

    def inputs(self):
        return {"px": vq.DatasetInput(dataset_id="stuck-px", fields=("close", "is_tradable"),
                                      lookback=vq.CalendarLookback(days=7, timezone="Asia/Seoul"))}

    def decide(self, call):
        close = call.read("px", "close").current()
        ok = call.read("px", "is_tradable").current()
        names = sorted(n for n in close if close.get(n) is not None and math.isfinite(close.get(n))
                       and ok.get(n) is True)
        if not names:
            return vq.Hold(reason="nothing tradable")
        return vq.Rebalance.of(long={n: 1 for n in names}, invested=1)
''',
    encoding="utf-8",
)

(OUT / "data.yaml").write_text(
    """instruments:
  tables:
    stock: instruments_stock.parquet
datasets:
  stuck-px:
    source_id: stuck-px-source
    path: px.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields: {close: close, is_tradable: is_tradable}
    field_types: {close: DOUBLE, is_tradable: BOOLEAN}
    execution:
      is_tradable: is_tradable
components:
  stuck-venue:
    kind: exchange
    path: venue.py
    object_name: Venue
    config:
      instruments: [A, B, C, D]
  eqw:
    kind: strategy
    path: eqw.py
    object_name: Eqw
""",
    encoding="utf-8",
)

(OUT / "runs.yaml").write_text(
    """runs:
  stuck:
    instruments: [A, B, C, D]
    start: '2024-01-01T00:00:00+09:00'
    end: '2024-04-30T15:30:01+09:00'
    timezone: Asia/Seoul
    schedule:
      every: 1M
      'on': last
      at: '16:00'
    exchange: stuck-venue
    execution:
      dataset: stuck-px
      trade_price: close
      fill:
        at: '15:30'
    initial_account:
      cash: '1000000'
      mode: LONG_ONLY
      positions: {}
    writes: stuck-weights
    strategy:
      component: eqw
""",
    encoding="utf-8",
)
print(f"wrote {OUT}")
```

`analyze_f008.py` reads only the export, `report.json` and `px.parquet`. The script that produced
the numbers above ended with one more line, a raw-string search of `report.json`, which is omitted
here.

```python
"""F-008 analysis: stuck share after each fill, and a liquidate-at-last-price rebuild.

Usage: python analyze_f008.py <dir>   (the directory make_f008.py wrote, after
       `vqapr export stuck/eqw --out <dir>/export`)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
EX = D / "export"


def utc(s):
    return pd.to_datetime(s, utc=True)


nav = pd.read_csv(EX / "nav.csv")
nav["t"] = utc(nav["event_time"])
nav = nav.set_index("t")[["cash", "nav"]].astype(float)
hold = pd.read_csv(EX / "holdings.csv")
hold["t"] = utc(hold["event_time"])
fills = pd.read_csv(EX / "fills.csv")
fills["t"] = utc(fills["event_time"])
w = pd.read_csv(EX / "weights.csv")
w["t"] = utc(w["event_time"])
px = pd.read_parquet(D / "px.parquet")
px["t"] = utc(px["available_at"])

decisions = sorted(w["t"].unique())
fill_instants = sorted(fills["t"].unique())
pd.set_option("display.width", 200)

print("== After each fill: target vs held (vqapr account)")
rows = []
for d, f in zip(decisions, fill_instants):
    target = w[w.t == d].set_index("instrument")["weight"].astype(float)
    h = hold[hold.t == f].set_index("instrument")["value"].astype(float)
    n, cash = nav.loc[f, "nav"], nav.loc[f, "cash"]
    stuck = h[~h.index.isin(target.index)].sum()
    for name in sorted(set(target.index) | set(h.index)):
        rows.append({"decision": d.tz_convert("Asia/Seoul").date(), "fill": f.tz_convert("Asia/Seoul").date(),
                     "instrument": name, "target_w": target.get(name, 0.0),
                     "held_w": h.get(name, 0.0) / n, "in_target": name in target.index})
    print(f"fill {f.tz_convert('Asia/Seoul')}: NAV {n:,.2f}  cash {cash:,.2f} ({cash / n:.4%})  "
          f"held outside target {stuck:,.2f} = {stuck / n:.4%} of NAV  "
          f"target names hold {(h[h.index.isin(target.index)].sum()) / n:.4%} of NAV")
print(pd.DataFrame(rows).to_string(index=False))

print("\n== Held names not in the latest target, at the last valuation")
last = nav.index[-1]
h_last = hold[hold.t == last].set_index("instrument")[["quantity", "price", "value"]].astype(float)
print(h_last.assign(share=h_last["value"] / nav.loc[last, "nav"]).to_string())
a_last = px[px.instrument == "A"].sort_values("t").iloc[-1]
print(f"A's last row in px.parquet: {a_last['available_at']} close {a_last['close']}")

print("\n== Rebuild: at each fill, liquidate every held name at its last price, reinvest all of NAV")
cal = sorted(px["t"].unique())
wide = px.pivot(index="t", columns="instrument", values="close").reindex(cal).ffill()
q = pd.Series(0.0, index=wide.columns)
cash = 1_000_000.0
reb = {}
dec_for_fill = dict(zip(fill_instants, decisions))
for t in cal:
    price = wide.loc[t]
    if t in dec_for_fill:
        value = cash + float((q * price.fillna(0.0)).sum())
        target = w[w.t == dec_for_fill[t]].set_index("instrument")["weight"].astype(float)
        q = pd.Series(0.0, index=wide.columns)
        for name, wt in target.items():
            q[name] = wt * value / price[name]
        cash = value - float((q * price.fillna(0.0)).sum())
    reb[t] = cash + float((q * price.fillna(0.0)).sum())
reb = pd.Series(reb)
v = nav["nav"].reindex(reb.index)
both = pd.DataFrame({"vqapr": v, "rebuild": reb}).dropna()
r = both.pct_change().dropna()
print(f"final NAV  vqapr {both['vqapr'].iloc[-1]:,.2f}  rebuild {both['rebuild'].iloc[-1]:,.2f}")
tv, tr = both.iloc[-1] / both.iloc[0] - 1
print(f"total return  vqapr {tv:.4%}  rebuild {tr:.4%}  gap (vqapr - rebuild) {tv - tr:.4%}")
print(f"daily returns: corr {r['vqapr'].corr(r['rebuild']):.6f}  "
      f"MSE {((r['vqapr'] - r['rebuild']) ** 2).mean() * 1e8:.2f} bp^2  "
      f"first divergence {r.index[(r['vqapr'] - r['rebuild']).abs() > 1e-12][0].tz_convert('Asia/Seoul')}")

print("\n== report.json: book.cash_share and book.unmarked at each fill and at the end")
rep = json.loads((EX / "report.json").read_text(encoding="utf-8"))
book = rep["book"]
bi = utc(pd.Series(book["instants"]))
for f in [*fill_instants, last]:
    k = int(np.nonzero((bi == f).to_numpy())[0][0])
    print(f"{f.tz_convert('Asia/Seoul')}: held {book['held'][k]}  unmarked {book['unmarked'][k]}  "
          f"cash_share {float(book['cash_share'][k]):.6f}  net_exposure {float(book['net_exposure'][k]):.6f}")
```

## Impact

Worked around, not blocked, and it changes the result. The scenario's answer was to keep vqapr's
series as the main one and report beside it a pandas rebuild that liquidates at the last price and
reinvests fully. Each leg's stuck share had to be reconstructed from `holdings.csv` and
`weights.csv`. Measured on the Korean FF3 run:

- **Provisional runs** (formation decided after June's last close, filled at July's first close):
  - Most NAV stuck in names the new target did not ask for, right after a fill: S1 5.8% (2025),
    S2 4.6% (2026), S3 3.6%, B1 3.5%, B3 1.7%, B2 0.7%.
  - Legs, vqapr − rebuild: daily correlation 0.9998 or higher, but vqapr earns less. S1 −0.66%/yr,
    S2 −0.45%/yr, B1 −0.36%/yr, S3 −0.23%/yr, B3 −0.17%/yr, B2 −0.04%/yr; daily MSE 0.4 to 33 bp².
  - The stuck capital accumulates from year to year, because a delisted name is never removed.
- **Final runs** (the user's answers applied), most NAV stuck right after a fill:
  - Scenario 1: S1 5.4%, S2 4.7%, S3 3.8%, B1 3.4%, B3 1.9%, B2 0.6%.
  - Scenario 2: S1 5.6%, S2 5.3%, S3 3.4%, B1 2.8%, B2 1.6%, B3 1.0%.
- **Factor level, final runs, vqapr − rebuild:**
  - Scenario 1: SMB −0.23%/yr, HML +0.30%/yr (correlation 0.9996 / 0.9995, tracking error
    0.45% / 0.49%).
  - Scenario 2: SMB −0.28%/yr, HML +0.38%/yr (tracking error 0.47% / 0.50%).

On the synthetic panel the stuck share is 32.2% and then 54.3% of NAV. A three-name book makes that
large by construction. Over the four months, vqapr returned −0.23% and the rebuild −6.14%; daily
correlation was 0.936, first divergence on 2024-03-04. The sign of that gap comes from the seeded
price paths and means nothing on its own.

**Update from a third scenario in the same testbed run.** Book equity gained a fallback to separate
statements, and one small stock, A052670, entered S1 through it. It was halted at 2,080 KRW through
both the 2024 and the 2025 rebalances, so it stayed in the vqapr book each time. On 2026-02-09 it
resumed at 625,000 KRW in the vendor price file, a `return` of +29,948%. That is an unadjusted
capital reduction, a defect in the data, not in vqapr. That day the vqapr S1 leg returned +26.4%. The
benchmark S1 and the pandas rebuild both returned +3.4%; the rebuild settles unsellable names at
their last price at each formation.

Money stuck in unsellable names reached 17.0% of S1's NAV after the 2026-07-01 rebalance, 13.0% in
that one name. Over the full period, vqapr against the rebuild at factor level fell to SMB
correlation 0.982 (tracking error 2.95%/yr) and HML 0.959 (4.39%/yr), from 0.9996 without the
fallback. This decided a pre-registered comparison against the benchmark. The data defect started
it; the account's inability to settle a halted holding carried the defect into a factor return
two years after the name stopped trading.

## What would have prevented it

- A declarable treatment for a held name that cannot be sold at a fill. For example, "a name absent
  from the execution table is settled at its last price at the next fill", and the same for a name
  halted at a fill.
- Failing that, the number the skill promises: money held in names outside the target, as a share
  of NAV at each rebalance, in the run envelope or the report. Today every book figure at a fill
  says fully invested (`cash_share` 0, `net_exposure` 1.0).
- A reason on the rows whose buy came up short: at 2024-03-01 no row has one, and at 2024-04-01 it
  is `no_trade`. The zero-dealt reason code is also filed separately (testbed F-012).
