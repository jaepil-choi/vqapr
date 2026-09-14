# `register` of a run says a model "sees only rows knowable before each instant", but a row stamped exactly at the decision instant is read by that decision

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** closed `archive/027` (record `160`), which introduced the `spoken` sentences. The dataset sentence and the run sentence it added state the boundary differently.

## What I was doing

Building daily Fama-French legs on Korean data. Market cap is registered with `available_at` at
each session's 15:30 close, and the formation decision is on June's last session. Before choosing
the decision's wall time, the agent needed to know one fact: does a decision at 15:30 see the
market cap stamped 15:30 that same session? The two `register` envelopes answer that question in
opposite ways. The agent avoided the question by deciding at 16:00. The evaluator then tested which
statement is true on a synthetic workspace, reproduced below.

## What I expected

One inequality, stated the same way wherever the package states it. The two `spoken` lines from
the same wheel:

- `vqapr register <datasets>.yaml`, for every dataset: "a model reading it at instant t sees rows
  with available_at <= t"
- `vqapr register <runs>.yaml`, for every run: "the model is called ... and sees only rows knowable
  before each instant"

For a row with `available_at == t`, the first says visible and the second says not visible. The
skills lean towards the first:
- `vqapr-introduce-vqapr/SKILL.md`: "Every read after that sees only what was available at that
  instant".
- `vqapr-make-exchange/references/fill-timing.md`: "The close is knowable only *at* the close, so a
  decision taken at that instant using that value could not have been acted on". This describes a
  decision at the close instant seeing the close.

## What happened

The package reads `available_at <= t`. A row stamped exactly at the decision instant is visible to
that decision. That is the dataset sentence, and it contradicts the run sentence.

Two datasets. `probe-px` is the execution table: rows at 15:30 and 16:00 each session, with `tag` =
yyyymmdd for the 15:30 row and yyyymmdd + 0.5 for the 16:00 row. `probe-sig` has a baseline row on
2024-01-05 (`tag` 0), then three rows on 2024-01-10: X1 at 15:29:59 (`tag` 1), X2 at exactly
15:30:00 (`tag` 2) and X3 at 15:30:01 (`tag` 3). The run decides every session at 15:30 and fills at
16:00. Its strategy writes what it read into a declared table, `seen`.

    $ vqapr --project-root <dir> register <dir>/data.yaml
    {"ok": true, "registered": {"components": ["probe-venue", "probe"], "datasets": ["probe-px", "probe-sig"], "instruments": [{"by_kind": {"stock": 3}, "digest": "7905c5d3bbb50d8894aaa122b1b0fc71df7d67592be72179dbd70a2c79259b83", "instruments": 3}]}, "spoken": ["dataset 'probe-px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'probe-sig': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006"}

    $ vqapr --project-root <dir> register <dir>/runs.yaml
    {"ok": true, "registered": {"runs": ["probe-run"]}, "spoken": ["run 'probe-run' fills against dataset 'probe-px': the first execution instant after the decision, at 16:00:00 Asia/Seoul, at its 'close' price", "run 'probe-run': the model is called every 1d at 15:30:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006"}

    $ vqapr --project-root <dir> check probe-run
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "ok": true, "passed": ["workspace", "run", "judgments", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006"}

    $ vqapr --project-root <dir> run probe-run
    {"ok": true, "roster": {"by_kind": {"stock": 3}, "digest": "7905c5d3bbb50d8894aaa122b1b0fc71df7d67592be72179dbd70a2c79259b83", "instruments": 3, "known": true, "tables": ["stock"]}, "run_id": "probe-run", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006\\.vqapr", "strategies": {"probe": {"account_version": 10, "contract": {"accepted_intents": 10}, "events": 30, "fills": {"dealt": 1, "never_filled": [], "orders": 10, "partial": 0, "reasons": {"no_trade": 9}, "zero_dealt": 9}, "fingerprint": "6b30d2850a7be749864247616530b70b1f380d652d2fc18b516ab2d356d62825", "record": "probe@6b30d285", "status": "completed", "tables": ["seen", "vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.078165, "due": 0.168224, "simulation.due.account_commit": 0.001845, "simulation.due.account_mark": 0.028908, "simulation.due.account_preparation": 0.000769, "simulation.due.exchange_execution": 0.000247, "simulation.due.feedback_candidate": 4.4e-05, "simulation.due.feedback_publication": 0.000122, "simulation.due.instrument_declaration": 5.9e-05, "simulation.due.order_planning": 0.000355, "simulation.due.snapshot": 0.134413, "simulation.due.valuation_mark": 5.6e-05, "simulation.due.valuation_selection": 9.6e-05, "total": 0.251263}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006", "writes": "probe-weights"}

    $ vqapr --project-root <dir> show strategy probe-run/probe --table seen --limit 20
    {"items": [{"decision_at": "2024-01-08T15:30:00+09:00", "event_time": "2024-01-08 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-08T15:30:00+09:00", "px_current_tag_X1": 20240108.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 1, "sig_latest_X1": 0.0, "sig_latest_X2": 0.0, "sig_latest_X3": 0.0, "sig_newest_instant": "2024-01-05T15:30:00+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-09T15:30:00+09:00", "event_time": "2024-01-09 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-09T15:30:00+09:00", "px_current_tag_X1": 20240109.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 8, "sig_latest_X1": 0.0, "sig_latest_X2": 0.0, "sig_latest_X3": 0.0, "sig_newest_instant": "2024-01-05T15:30:00+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-10T15:30:00+09:00", "event_time": "2024-01-10 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-10T15:30:00+09:00", "px_current_tag_X1": 20240110.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 15, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 0.0, "sig_newest_instant": "2024-01-10T15:30:00+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-11T15:30:00+09:00", "event_time": "2024-01-11 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-11T15:30:00+09:00", "px_current_tag_X1": 20240111.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 22, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-12T15:30:00+09:00", "event_time": "2024-01-12 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-12T15:30:00+09:00", "px_current_tag_X1": 20240112.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 29, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-15T15:30:00+09:00", "event_time": "2024-01-15 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-15T15:30:00+09:00", "px_current_tag_X1": 20240115.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 36, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-16T15:30:00+09:00", "event_time": "2024-01-16 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-16T15:30:00+09:00", "px_current_tag_X1": 20240116.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 43, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-17T15:30:00+09:00", "event_time": "2024-01-17 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-17T15:30:00+09:00", "px_current_tag_X1": 20240117.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 50, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-18T15:30:00+09:00", "event_time": "2024-01-18 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-18T15:30:00+09:00", "px_current_tag_X1": 20240118.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 57, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}, {"decision_at": "2024-01-19T15:30:00+09:00", "event_time": "2024-01-19 15:30:00+09:00", "producer_id": "probe", "px_current_at": "2024-01-19T15:30:00+09:00", "px_current_tag_X1": 20240119.0, "run_id": "1da731ed2b4ea8ffd0b7db904877af575dbcaece333840ddd7166eed66e6d245", "sequence": 64, "sig_latest_X1": 1.0, "sig_latest_X2": 2.0, "sig_latest_X3": 3.0, "sig_newest_instant": "2024-01-10T15:30:01+09:00", "stage": "STRATEGY_CALLBACK"}], "matched": 10, "ok": true, "returned": 10, "rows_total": 10, "run_id": "probe-run", "stage": "strategy.table", "strategy_ref": "probe@6b30d285", "table": "seen", "tables": ["seen", "vqapr.account", "vqapr.fill", "vqapr.weight"], "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\f006"}

What the 2024-01-10 15:30:00 decision read:

| row | `available_at` | read by the 15:30:00 decision? |
|---|---|---|
| `probe-sig` X1 | 2024-01-10 15:29:59 | yes (`sig_latest_X1` 1.0) |
| `probe-sig` X2 | 2024-01-10 **15:30:00** | **yes** (`sig_latest_X2` 2.0; `sig_newest_instant` 15:30:00) |
| `probe-sig` X3 | 2024-01-10 15:30:01 | no (0.0, the baseline; read from the next session) |
| `probe-px` X1, the 15:30 row | 2024-01-10 **15:30:00** | **yes** (`current().at` 15:30:00, `tag` 20240110.0, not the previous 16:00 row's 20240109.5) |

Every 15:30 decision in the run read that session's 15:30 execution row: 10 of 10 decisions.

## Reproduction

This needs only the wheel, plus pandas and pyarrow, which the testbed's environment already has.
It reproduced 2 of 2 times, each from an empty directory, with identical `spoken` text and an
identical `seen` table. An earlier attempt declared the fill at 15:30, the same wall time as the
decision. `check` refused it with `execution.not_after_decision` for the last decision, and its
`spoken` lines were the same as above. That was a mistake in my declaration, not part of this
report.

1. Save the generator below as `make_f006.py` and run `uv run python make_f006.py <dir>`.
2. `uv run vqapr --project-root <dir> register <dir>/data.yaml`: dataset `spoken` says `available_at <= t`.
3. `uv run vqapr --project-root <dir> register <dir>/runs.yaml`: run `spoken` says "before each instant".
4. `uv run vqapr --project-root <dir> check probe-run`, then `uv run vqapr --project-root <dir> run probe-run`.
5. `uv run vqapr --project-root <dir> show strategy probe-run/probe --table seen --limit 20`. The
   2024-01-10 row has `sig_latest_X2` 2.0 and `px_current_at` 15:30:00. **Each is a row stamped at
   the decision instant, read by that decision.**

```python
"""F-006 repro: is a row stamped exactly at the decision instant visible to that decision?

Writes, into the directory given as argv[1] (default: this file's directory):
  px.parquet        execution table, X1..X3, two rows per business day, stamped 15:30 and 16:00
                    Asia/Seoul; `tag` = yyyymmdd (+0.5 for the 16:00 row), so a strategy can say
                    which row it saw. The run decides at 15:30 and fills at 16:00.
  sig.parquet       signal table, X1..X3: a baseline row on 2024-01-05 15:30 (tag 0), then on
                    2024-01-10 X1 at 15:29:59 (tag 1), X2 at 15:30:00 (tag 2), X3 at 15:30:01 (tag 3)
  instruments_stock.parquet, venue.py, probe.py, data.yaml, runs.yaml

The run decides every session at 15:30 and records, per decision, what it saw, in a table `seen`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
TZ = "Asia/Seoul"
NAMES = ["X1", "X2", "X3"]
DAYS = pd.bdate_range("2024-01-02", "2024-01-19")

px = pd.DataFrame(
    [
        {
            "instrument": n,
            "available_at": pd.Timestamp(f"{d:%Y-%m-%d} {clock}", tz=TZ),
            "close": 100.0 + i,
            "tag": float(d.strftime("%Y%m%d")) + frac,  # .0 = the 15:30 row, .5 = the 16:00 row
            "is_tradable": True,
        }
        for i, d in enumerate(DAYS)
        for clock, frac in (("15:30:00", 0.0), ("16:00:00", 0.5))
        for n in NAMES
    ]
)
px.to_parquet(OUT / "px.parquet", index=False)

sig = pd.DataFrame(
    [{"instrument": n, "available_at": pd.Timestamp("2024-01-05 15:30:00", tz=TZ), "tag": 0.0} for n in NAMES]
    + [
        {"instrument": "X1", "available_at": pd.Timestamp("2024-01-10 15:29:59", tz=TZ), "tag": 1.0},
        {"instrument": "X2", "available_at": pd.Timestamp("2024-01-10 15:30:00", tz=TZ), "tag": 2.0},
        {"instrument": "X3", "available_at": pd.Timestamp("2024-01-10 15:30:01", tz=TZ), "tag": 3.0},
    ]
)
sig.to_parquet(OUT / "sig.parquet", index=False)

pd.DataFrame({"instrument_id": NAMES, "kind": "stock"}).to_parquet(
    OUT / "instruments_stock.parquet", index=False
)

(OUT / "venue.py").write_text(
    '''from decimal import Decimal
from vqapr.public import AcademicExchange, ListingAccess, TradeRule

STEP = Decimal("0.00000001")


class Venue(AcademicExchange):
    def __init__(self, instruments):
        super().__init__(
            {
                str(n): TradeRule(instrument_id=str(n), quantity_step=STEP, minimum_quantity=STEP,
                                  fractional_allowed=True, access=ListingAccess.LONG_ONLY)
                for n in instruments
            },
            exchange_id="probe-venue",
        )
''',
    encoding="utf-8",
)

(OUT / "probe.py").write_text(
    '''from vqapr import public as vq


class Probe(vq.StrategyModel):
    """Buys X1 and records what each decision could read."""

    def inputs(self):
        return {
            "px": vq.DatasetInput(dataset_id="probe-px", fields=("tag",),
                                  lookback=vq.CalendarLookback(days=10, timezone="Asia/Seoul")),
            "sig": vq.DatasetInput(dataset_id="probe-sig", fields=("tag",),
                                   lookback=vq.CalendarLookback(days=10, timezone="Asia/Seoul")),
        }

    def tables(self):
        return (vq.TableSpec("seen", ("decision_at", "px_current_at", "px_current_tag_X1",
                                      "sig_newest_instant", "sig_latest_X1", "sig_latest_X2",
                                      "sig_latest_X3")),)

    def decide(self, call):
        px = call.read("px", "tag").current()
        sig_w = call.read("sig", "tag")
        latest = sig_w.latest()
        self.recorder.append("seen", {
            "decision_at": call.at.isoformat(),
            "px_current_at": px.at.isoformat(),
            "px_current_tag_X1": px.get("X1"),
            "sig_newest_instant": sig_w.instants[-1].isoformat() if sig_w.instants else None,
            "sig_latest_X1": latest.get("X1"),
            "sig_latest_X2": latest.get("X2"),
            "sig_latest_X3": latest.get("X3"),
        })
        return vq.Rebalance.of(long={"X1": 1}, invested=1)
''',
    encoding="utf-8",
)

(OUT / "data.yaml").write_text(
    """instruments:
  tables:
    stock: instruments_stock.parquet
datasets:
  probe-px:
    source_id: probe-px-source
    path: px.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields: {close: close, tag: tag, is_tradable: is_tradable}
    field_types: {close: DOUBLE, tag: DOUBLE, is_tradable: BOOLEAN}
    execution:
      is_tradable: is_tradable
  probe-sig:
    source_id: probe-sig-source
    path: sig.parquet
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields: {tag: tag}
    field_types: {tag: DOUBLE}
components:
  probe-venue:
    kind: exchange
    path: venue.py
    object_name: Venue
    config:
      instruments: [X1, X2, X3]
  probe:
    kind: strategy
    path: probe.py
    object_name: Probe
""",
    encoding="utf-8",
)

(OUT / "runs.yaml").write_text(
    """runs:
  probe-run:
    instruments: [X1, X2, X3]
    start: '2024-01-08T00:00:00+09:00'
    end: '2024-01-19T16:00:00+09:00'
    timezone: Asia/Seoul
    schedule:
      every: 1d
      at: '15:30'
    exchange: probe-venue
    execution:
      dataset: probe-px
      trade_price: close
      fill:
        at: '16:00'
    initial_account:
      cash: '1000000'
      mode: LONG_ONLY
      positions: {}
    writes: probe-weights
    strategy:
      component: probe
""",
    encoding="utf-8",
)
print(f"wrote {OUT}")
```

## Impact

Worked around, not blocked. In the scenario run, the agent could not tell from the envelopes
whether a 15:30 decision sees the market cap stamped at that session's 15:30 close. It moved the
decision to 16:00 so that both readings gave the same answer, and recorded the ambiguity as
unresolved. No number in that run is wrong because of this.

The cost is that the two sentences disagree on exactly the case a close-stamped row meets. A user
who trusts the run sentence and decides at the close instant would expect the close to be hidden,
but it is read. The fill still comes strictly after the decision, so this report claims no
look-ahead. The claim is only that one of the two sentences describes a boundary the package does
not use.

## What would have prevented it

The run's `spoken` line stating the same inequality as the dataset's, for example "sees rows with
available_at <= each instant". One sentence in the run-backtest skill could say the same thing: a
row stamped at the decision instant is visible to that decision.
