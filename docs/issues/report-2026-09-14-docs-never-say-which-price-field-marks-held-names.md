# No documentation says which price field marks held names when an execution table carries more than one numeric price field

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** closed `archive/034` (record `139`), which put the fill declaration in the run record. The record still names no valuation field.

## What I was doing

Run 4 has two scenarios over the same price parquet:

- Scenario 1 fills and values its factor legs at the adjusted close.
- Scenario 2 fills and values its legs at a return-compounded price (`ret_close`).

The dataset template says an execution table's numeric fields are "the prices a run may choose
from". So the natural route was one execution table with both price fields, and each run choosing
one with `execution.fill.trade_price`. That route is only safe if the book is also marked at the
chosen field.

## What I expected

I expected a statement of which field held names are valued at. I checked every place that
describes the execution table or valuation:

- **The `vqapr new dataset` template**, `execution:` comment: "Its numeric fields are the prices a
  run may choose from; the run names one as `execution.fill.trade_price`." This covers the fill
  only.
- **The `vqapr new run` template:**
  - "`trade_price: close` — which numeric field of the dataset this run fills at; another run may
    fill the same table at `open`".
  - The header: "The book is valued at every instant of the market clock … there is no separate
    valuation or monitoring time to declare."
- **`vqapr-run-backtest/references/run-declaration.md:57`** (the same sentence is in
  `vqapr-run-backtest/SKILL.md:30-31`): "The book is valued at every instant of the market clock,
  and the run's declared Compliance rules observe it right after. There is nothing to schedule."
- **`vqapr.public.ExecutionRole.__doc__`:** "its numeric fields are the prices it published …
  Which price a run fills at is the RUN's choice (`runs.<id>.execution.fill.trade_price`)".
- **`vqapr export --help`:** "holdings.csv event_time, date, instrument, quantity, price, value".
  It does not say which price.

None of them names the field that marks held names.

## What happened

The original run (`FINDINGS.md`, F-019): "the docs describe the fill price (`trade_price`) and say
"the book is valued at every instant of the market clock", but not at which field. With two
numeric price fields in one table, a leg could fill at one and be marked at the other without any
message." The agent avoided the question by registering the scenario 2 series as its own dataset
(`km-prices`, with `ret_close` as its only price).

I checked this again on 0.16.0. The documentation gap is as quoted above. I then checked the
behaviour: one table with `close` and `alt = 2 × close`, one run filling at each, and a strategy
that buys K000002 once and holds it.

    $ uv run vqapr --project-root . show run mark-alt
    ... "execution": {"dataset_id": "exec-two", "fill": {"after": null, "at": "15:30:00", "declaration_identity": ["alt", "Asia/Seoul", "15:30:00", "", ""], "timezone": "Asia/Seoul", "trade_price": "alt", "within": null}, "price_fields": {"alt": "alt", "close": "close"} ...

The record lists both price fields and the fill field, and names no valuation field. The
registration's `spoken` line says only "run 'mark-alt' fills against dataset 'exec-two': the first
execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'alt' price".

The exported holdings:

    mark-close holdings.csv
    2022-01-04T15:30:00+09:00,2022-01-04,K000002,454,219816.8862,99796866.3348
    2022-01-05T15:30:00+09:00,2022-01-05,K000002,454,215021.3134,97619676.2836
    2022-01-06T15:30:00+09:00,2022-01-06,K000002,454,214266.4292,97276958.8568

    mark-alt holdings.csv
    2022-01-04T15:30:00+09:00,2022-01-04,K000002,227,439633.7724,99796866.3348
    2022-01-05T15:30:00+09:00,2022-01-05,K000002,227,430042.6268,97619676.2836
    2022-01-06T15:30:00+09:00,2022-01-06,K000002,227,428532.8584,97276958.8568

Every valuation marked K000002 at the run's own `trade_price` field, and the two `nav.csv` files
are identical (100000000.0000, 97822809.9488, …). So on 0.16.0 the book was observed to be marked
at the `trade_price` field. Nothing I could reach states it, so a user cannot rely on it without
testing.

## Reproduction

This uses only the `vqapr new sample` data.

1. `uv run vqapr --project-root . new sample --out ./sample`
2. `make_two.py`, run with `uv run python make_two.py`:

   ```python
   import duckdb
   duckdb.sql("""
   copy (select trade_at, instrument, is_tradable, close, close * 2 as alt
         from read_parquet('sample/execution.parquet'))
   to 'sample/exec_two.parquet' (format parquet)
   """)
   ```

3. `hold_one.py`:

   ```python
   from datetime import date

   from vqapr.public import DatasetInput, Hold, Rebalance, RowsLookback, StrategyModel


   class HoldOne(StrategyModel):
       def inputs(self):
           return {"prices": DatasetInput(dataset_id="sample-prices", fields=("close",),
                                          lookback=RowsLookback(rows=1))}

       def decide(self, call):
           if call.at.date() > date(2022, 1, 4):
               return Hold(reason="bought on the first session")
           return Rebalance.of(long={"K000002": 1}, invested=1)
   ```

4. `repro.yaml`:

   ```yaml
   instruments:
     tables:
       stock: sample/instruments_stock.parquet
   datasets:
     sample-prices:
       source_id: sample-prices-source
       path: sample/observations.parquet
       instrument_field: instrument
       available_at: available_at
       grain: instrument_instant
       key_fields: [available_at, instrument]
       fields: {close: close}
       field_types: {close: DOUBLE}
     exec-two:
       source_id: exec-two-source
       path: sample/exec_two.parquet
       instrument_field: instrument
       available_at: trade_at
       grain: instrument_instant
       key_fields: [trade_at, instrument]
       fields: {close: close, alt: alt, is_tradable: is_tradable}
       field_types: {close: DOUBLE, alt: DOUBLE, is_tradable: BOOLEAN}
       execution: {is_tradable: is_tradable}
   components:
     hold-one: {kind: strategy, path: hold_one.py, object_name: HoldOne}
     acad-venue:
       kind: exchange
       path: sample/exchange.py
       object_name: SampleExchange
       config: {instruments: [K000001, K000002, K000003, K000004]}
   runs:
     mark-close: &base
       instruments: [K000001, K000002, K000003, K000004]
       start: '2022-01-04T00:00:00+09:00'
       end: '2022-01-12T23:59:59+09:00'
       timezone: Asia/Seoul
       schedule: {every: 1d, at: '08:00'}
       exchange: acad-venue
       execution: {dataset: exec-two, trade_price: close, fill: {at: '15:30'}}
       initial_account: {cash: '100000000', mode: LONG_ONLY, positions: {}}
       writes: mark-close-weights
       strategy: {component: hold-one}
     mark-alt:
       <<: *base
       execution: {dataset: exec-two, trade_price: alt, fill: {at: '15:30'}}
       writes: mark-alt-weights
   ```

5. `uv run vqapr register repro.yaml`, then `uv run vqapr run mark-close mark-alt`.
6. `uv run vqapr export mark-close/hold-one --out out/mark-close` and the same for `mark-alt`.
   Compare the `price` column of `holdings.csv` against the docs above.

Reproduced 2 of 2 attempts: in a scratch workspace, and on a fresh one.

## Impact

Worked around in run 4 by registering the second price series as a separate dataset. That cost an
extra registration and a second copy of the price declaration. No number changed.

For a user who does not test, putting two price fields in one table carries an unstated
assumption: that NAV is computed from the field they filled at.

## What would have prevented it

One line beside `trade_price` in the run template and in `run-declaration.md`: "held names are
marked at this same field", or whichever rule is intended. Naming the valuation field in the
`execution` block of `show run` would put the same fact in the record.
