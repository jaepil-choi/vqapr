# `AcademicExchange` is documented as "full-fill" and records `partial_fills: "never"`, yet it cuts buys to zero when cash runs short; the sizing and funding rule is written only for `krx`

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-money-in-a-delisted-or-halted-holding-cannot-fund-the-next-book.md` (the stuck capital that produces the cut buys).

## What I was doing

Run 4 runs six Fama-French leg strategies on an academic venue with divisible listings,
rebalancing once a year. After the June fills, leg `ff-s1`'s run envelope reported `"reasons":
{"absent": 209, "no_trade": 1121, "nontradable": 266}`. Its `fills.csv` held `no_trade` rows with
`requested_quantity 0` and `sized_quantity > 0`. The agent needed to know whether a frictionless,
"full-fill" venue was refusing orders or running out of cash, and which buys get cut.

## What I expected

- **`vqapr.public.AcademicExchange.__doc__`:** "Zero-friction, full-fill execution for declared
  academic listings."
- **The academic scaffold's `Venue` docstring** (`vqapr new exchange … --profile academic`):
  "Fills every order completely at the venue price, with no cost or slippage."
- **The record's `exchange.settings`** for an academic run: `{"costs": "none", "partial_fills":
  "never", "profile": "academic"}`. A krx run records `"partial_fills": "cash-limited"`.
- **`vqapr-make-exchange/references/execution-profiles.md`:**
  - The academic section (lines 11–28) covers the lifecycle and the whole-rebalance refusal
    conditions. It says nothing about sizing or funding.
  - The sizing, funding and settling steps (lines 44–59) sit under "## `krx` — costed, and
    long-only" as "**What a KRX rebalance does, in order**". Step 2 reads: "Buys are then funded
    **largest money delta first** … a buy that no longer fits is cut to the whole shares the
    remaining cash pays for … possibly nothing."
- **`vqapr-analyze-result/references/panels-from-tables.md:193`:** "On KRX the order is already
  cut to the cash …".

From these I expected an academic buy either to fill at its weight or to be refused whole.

Two skill lines do describe the effect, without naming a profile or the rule:

- `vqapr-introduce-vqapr/SKILL.md:70-73`: "money held in a name that cannot be sold — halted or
  delisted — cannot pay for the next book, so the smallest new buys go unfilled".
- `vqapr-make-strategy/references/factor-portfolios.md:116-119`: "(recorded `no_trade`)".

## What happened

The original run (`FINDINGS.md`, F-012): "I wanted to open the academic execution code to confirm
the funding and cut rule. I did not. I reasoned from the `krx` description and from the
stuck-capital numbers … I still have not verified whether academic funds largest-first."

I checked this on 0.16.0 with the sample data. Half the book is in K000001, which becomes
nontradable from 2022-01-20. The strategy then asks for K000002, K000003 and K000004 at 5:3:2 with
the whole book. The same strategy and data run on an academic venue and on the `--profile krx`
scaffold venue:

    $ uv run vqapr --project-root . run acad-halt krx-halt
    {"jobs": 1, "ok": true, "runs": {"acad-halt": {"ok": true, "roster": {"by_kind": {"stock": 10}, "digest": "875b5fe1129438c3ce3641cf11b2b4d56a2b716a58484779584715d801b75e37", "instruments": 10, "known": true, "tables": ["stock"]}, "run_id": "acad-halt", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\repro-f012\\.vqapr", "strategies": {"switch-half": {"account_version": 16, "contract": {"accepted_intents": 16}, "events": 32, "fills": {"dealt": 10, "never_filled": [{"dealt": 0, "instrument": "K000003", "orders": 4, "reason": "no_trade"}, {"dealt": 0, "instrument": "K000004", "orders": 4, "reason": "no_trade"}], "orders": 28, "partial": 0, "reasons": {"no_trade": 14, "nontradable": 4}, "zero_dealt": 18}, "fingerprint": "7e1e249df9fc82944d0709715d12d2348811e8e2313445e6fd95d11e6b0a2faf", "record": "switch-half@7e1e249d", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.005203, "due": 0.022206, "simulation.due.account_commit": 0.003043, "simulation.due.account_mark": 0.003564, "simulation.due.account_preparation": 0.001278, "simulation.due.exchange_execution": 0.000447, "simulation.due.feedback_candidate": 6.1e-05, "simulation.due.feedback_publication": 0.000174, "simulation.due.instrument_declaration": 8.5e-05, "simulation.due.order_planning": 0.000767, "simulation.due.snapshot": 0.011307, "simulation.due.valuation_mark": 5.3e-05, "simulation.due.valuation_selection": 8.5e-05, "total": 0.033517}}}, "writes": "acad-halt-weights"}, "krx-halt": {"ok": true, "roster": {"by_kind": {"stock": 10}, "digest": "875b5fe1129438c3ce3641cf11b2b4d56a2b716a58484779584715d801b75e37", "instruments": 10, "known": true, "tables": ["stock"]}, "run_id": "krx-halt", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\repro-f012\\.vqapr", "strategies": {"switch-half": {"account_version": 16, "contract": {"accepted_intents": 16}, "events": 32, "fills": {"dealt": 10, "never_filled": [{"dealt": 0, "instrument": "K000003", "orders": 4, "reason": "no_trade"}, {"dealt": 0, "instrument": "K000004", "orders": 4, "reason": "no_trade"}], "orders": 28, "partial": 0, "reasons": {"no_trade": 14, "nontradable": 4}, "zero_dealt": 18}, "fingerprint": "7e1e249df9fc82944d0709715d12d2348811e8e2313445e6fd95d11e6b0a2faf", "record": "switch-half@7e1e249d", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.004922, "due": 0.02228, "simulation.due.account_commit": 0.003063, "simulation.due.account_mark": 0.003461, "simulation.due.account_preparation": 0.001263, "simulation.due.exchange_execution": 0.000556, "simulation.due.feedback_candidate": 5.8e-05, "simulation.due.feedback_publication": 0.000173, "simulation.due.instrument_declaration": 3.3e-05, "simulation.due.order_planning": 0.000947, "simulation.due.snapshot": 0.011327, "simulation.due.valuation_mark": 4.5e-05, "simulation.due.valuation_selection": 8.3e-05, "total": 0.033663}}}, "writes": "krx-halt-weights"}}, "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\repro-f012\\.vqapr", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\repro-f012"}

`fills.csv` rows at the 2022-01-20 fill, identical on both venues:

| instrument | reason | sized | requested | dealt | price |
|---|---|---|---|---|---|
| K000001 | nontradable | -347 | -347 | 0 | |
| K000002 | | 229 | 229 | 229 | 214774.5541 |
| K000003 | no_trade | 43 | 0 | 0 | |
| K000004 | no_trade | 69 | 0 | 0 | |

What this shows:

- **The venue documented as full-fill cut two buys to zero.** On the academic venue, K000003 and
  K000004 were sized at 43 and 69 shares and requested at 0, with reason `no_trade`. The
  envelope's `partial: 0` and the record's `partial_fills: "never"` hold only for dealt against
  requested; the requested quantity was already cut.
- **The largest buy was funded first.** The one buy filled was the largest by money: K000002,
  229 × 214774.5541 = 49,183,372.89 out of 49,338,325.52 cash. That matches step 2 of the `krx`
  text, and the academic venue did exactly the same.

Not reproduced from the original entry: "On this academic venue the cut buys come out as
`no_trade` (requested 0), not `unfunded`, so the same shortfall carries a different reason code
per profile". On 0.16.0 both profiles recorded the same cut buys as `no_trade`, and neither
produced `unfunded` in these runs. This report does not claim a difference between profiles.

## Reproduction

This uses only the `vqapr new sample` data.

1. `uv run vqapr --project-root . new sample --out ./sample`
2. `uv run vqapr --project-root . new exchange krx-venue --profile krx --instruments K000001 K000002 K000003 K000004 --out ./krx_venue.py`
3. `make_halt.py`, run with `uv run python make_halt.py`:

   ```python
   import duckdb
   duckdb.sql("""
   copy (select trade_at, instrument,
                case when instrument = 'K000001' and trade_at >= timestamptz '2022-01-20 00:00:00+09'
                     then false else is_tradable end as is_tradable,
                close
         from read_parquet('sample/execution.parquet'))
   to 'sample/exec_halt.parquet' (format parquet)
   """)
   ```

4. `switch_half.py`:

   ```python
   from datetime import date

   from vqapr.public import DatasetInput, Rebalance, RowsLookback, StrategyModel

   SWITCH = date(2022, 1, 20)


   class SwitchHalf(StrategyModel):
       def inputs(self):
           return {"prices": DatasetInput(dataset_id="sample-prices", fields=("close",),
                                          lookback=RowsLookback(rows=1))}

       def decide(self, call):
           if call.at.date() < SWITCH:
               return Rebalance.of(long={"K000001": 1}, invested="0.5")
           return Rebalance.of(long={"K000002": 5, "K000003": 3, "K000004": 2}, invested=1)
   ```

5. `repro.yaml`:

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
     exec-halt:
       source_id: exec-halt-source
       path: sample/exec_halt.parquet
       instrument_field: instrument
       available_at: trade_at
       grain: instrument_instant
       key_fields: [trade_at, instrument]
       fields: {close: close, is_tradable: is_tradable}
       field_types: {close: DOUBLE, is_tradable: BOOLEAN}
       execution: {is_tradable: is_tradable}
   components:
     switch-half: {kind: strategy, path: switch_half.py, object_name: SwitchHalf}
     acad-venue:
       kind: exchange
       path: sample/exchange.py
       object_name: SampleExchange
       config: {instruments: [K000001, K000002, K000003, K000004]}
     krx-venue: {kind: exchange, path: krx_venue.py, object_name: Venue}
   runs:
     acad-halt: &base
       instruments: [K000001, K000002, K000003, K000004]
       start: '2022-01-04T00:00:00+09:00'
       end: '2022-01-25T23:59:59+09:00'
       timezone: Asia/Seoul
       schedule: {every: 1d, at: '08:00'}
       exchange: acad-venue
       execution: {dataset: exec-halt, trade_price: close, fill: {at: '15:30'}}
       initial_account: {cash: '100000000', mode: LONG_ONLY, positions: {}}
       writes: acad-halt-weights
       strategy: {component: switch-half}
     krx-halt:
       <<: *base
       exchange: krx-venue
       writes: krx-halt-weights
   ```

6. `uv run vqapr register repro.yaml`, then `uv run vqapr run acad-halt krx-halt`.
7. `uv run vqapr export acad-halt/switch-half --out out/acad-halt` and the same for `krx-halt`.
   Read the 2022-01-20 rows of `fills.csv`.
8. `uv run vqapr show strategy acad-halt/switch-half` shows `"settings": {"costs": "none",
   "partial_fills": "never", "profile": "academic"}`.

Reproduced 2 of 2 attempts: in a scratch workspace, and on a fresh one. The results were
identical.

## Impact

Worked around by guess. The agent inferred the rule from the `krx` text and from its own
weight-gap arithmetic, and recorded an `urge` entry because it wanted to open the academic
execution code.

The effect on the results is the stuck-capital drag measured in the same run (F-008): up to 5.8%
of a leg's NAV stuck after a fill, and legs trailing a full-reinvestment rebuild by 0.04–0.66% a
year. That drag is documented. What is not documented is the academic profile's own behaviour. Its
docstring, its scaffold and its recorded setting all say full fill, so a user cannot predict or
explain the `no_trade` rows from the profile's description.

## What would have prevented it

The sizing and funding steps written once for both profiles in `execution-profiles.md`, or stated
under `academic` as well:

- sells first;
- largest money delta first;
- a buy that does not fit is cut, possibly to zero, and recorded as `no_trade`.

Plus `AcademicExchange.__doc__` and the scaffold's `Venue` docstring saying that "full-fill" means
filling the cut order.
