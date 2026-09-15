# `strategy_report` raises a bare `ValueError` when a record's NAV goes non-positive, losing every section instead of omitting `performance`

**Status: CLOSED 2026-09-15 by record 297 (`redesign/sections-and-one-register`) — sections are built one at a time; a NAV that is not positive omits `performance`, `book` and `intent` with one reason, and `vqapr export` writes `report.json`.**

| | |
|---|---|
| vqapr version | `0.16.1` |
| installed from | `../../vqapr/dist/vqapr-0.16.1-py3-none-any.whl` (files match a `v0.16.1@9c54f211` tag build except line endings) |
| reported | 2026-09-15 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 5 (scenario 4, SMB book rebalancing), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

## What I was doing

Book A was an SMB long-short book on a SIGNED academic venue (long = short = NAV at each June
formation, then no trades for a year). In 2025-07..2026-06 its short big-cap buckets returned +64% to
+235%. Its NAV crossed zero on 2026-05-06 and stayed at or below zero for 38 sessions, reaching
−0.648 × the formation NAV. The run completed. The agent then asked for the book's report: turnover,
exposure and attribution, plus returns where they are defined.

## What I expected

`vqapr-analyze-result/SKILL.md:51`: "A `StrategyReport` has six sections; each is `None` with a reason
in `omitted` when the record cannot give it". `references/report-sections.md:13` says the same. A
return off a non-positive NAV is undefined, so I expected `performance: None` with a reason in
`omitted`, and the other sections intact. `book`, `trading` and `attribution` are sums over positions
and fills.

## What happened

    $ uv run --no-sync python -c "from pathlib import Path; from vqapr.public import strategy_report; strategy_report(Path('.vqapr'), 'bd-a')"
    builtins.ValueError: nav[1943] must be positive to define a return

The exception is not a `VqaprError` and carries no `fix`. `vqapr export bd-a/bd-book` returns
`ok: true` and writes `nav.csv`, `holdings.csv`, `fills.csv`, `weights.csv` and `tables/`. It writes
no `report.json`, with `omitted: {"report.json": "nav[1943] must be positive to define a return"}`.
The export names the omission, but it still drops the whole report for one undefined section.

## Reproduction

Needs a record whose NAV goes to or below zero. The testbed's `bd-a` record is one. It uses private
Korean data that is not in this repository. A synthetic version, not attempted here, would be a SIGNED
academic book short one asset that more than doubles, with no rebalance scheduled while the NAV is
negative.

Reproduced 2 of 2 on the `bd-a` record (the agent, then the evaluator on the same record).

## Impact

The agent had to compute turnover, exposure and every other number for book A in pandas from the
exported CSVs. The Python call gives no hint that only one section is undefined.

## What would have prevented it

`performance: None` with a reason such as `"nav ≤ 0 from 2026-05-06 for 38 sessions: returns
undefined"` in `omitted`, and the other sections computed. Failing that, a `VqaprError` naming the
instant and the section. Note: develop's record 288 (`85e03ec5`) makes an order plan at NAV ≤ 0 stop
with a reason. Book A made no decision in that window, so a record like this one can still be
written. That was not checked on develop.
