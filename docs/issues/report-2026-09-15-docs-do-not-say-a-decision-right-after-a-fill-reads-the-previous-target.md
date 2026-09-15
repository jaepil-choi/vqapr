# Nothing says that a decision taken right after a fill reads the book that fill just set, so "scale the current holdings" silently becomes "restore the previous target" on a daily schedule

**Status: RECEIVED 2026-09-15 (접수) — reproduced by the evaluator on the 0.16.1 wheel (triage: `docs/handoff/2026-09-15-scenario-testbed-run-5-findings.md`); fix plan with the owner.**

| | |
|---|---|
| vqapr version | `0.16.1` |
| installed from | `../../vqapr/dist/vqapr-0.16.1-py3-none-any.whl` (files match a `v0.16.1@9c54f211` tag build except line endings) |
| reported | 2026-09-15 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 5 (scenario 4, SMB book rebalancing), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Evaluator's classification.** The agent filed this as F-025, a `code` gap ("a relative-quantity order
cannot be expressed"). On review, the weight-only target is not a defect. On an academic venue with
fractional listings, a weight is a money amount at the fill, and a scaled-quantity order would differ
from it only by one session of within-group price drift. What cost real time was a fixed point that no
document warns about. That makes this a **docs** report of low severity.

## What I was doing

Scenario 4 asked for an SMB long-short book that is reset to long = short = NAV (1/3 per size bucket)
at every rebalance, without changing names or within-bucket proportions. That means scaling each
bucket's existing share counts by one factor. One strategy served three runs: annual, daily (`every:
1d`) and month end. It decided at 16:00 and filled at the next session's 15:30 close. The first
version of the rule read each name's share of its bucket from `call.account.values` and returned
those shares as weights.

## What I expected

`PortfolioTarget.__doc__` says a target is "a fraction of execution-time NAV". `EconomicAccountView`
says the strategy sees "the previous valuation's marks". Reading holdings from the account and
returning their proportions looked like "keep the bucket as it is, resize it".

## What happened

On the daily schedule, the 16:00 decision reads the book that the 15:30 fill has just set. That book's
value proportions at the fill's close are the previous target's weights, exactly. So the rule returns
the previous target, which returned the one before it, and the within-bucket weights stay at June's
formation weights all year.

- Half-L1 against the formation weights stayed at or below 0.6% at year end. For the annual and month-end
  books it was 6–17%.
- At return level, the daily book tracked a "June weights restored daily" series (corr 0.9993) and
  not buy-and-hold (+2.7%/yr, tracking error 1.8%).
- Nothing in the record or the envelope pointed at this. The agent found it from a persistent
  +2.7%/yr gap.

The fix is to derive the proportions from prices rather than from the account:
`me_june × P(t) / P(first fill after formation)`. That leaves a one-session lag. Within-bucket half-L1
against buy-and-hold was 0.8–1.2% per rebalance and did not accumulate. The daily book then tracked
the daily SMB at corr 0.9992, −0.63%/yr, TE 0.53%.

## Reproduction

Any daily-scheduled strategy that decides after the fill and returns
`account.values[n] / sum(account.values[group])` as its weights keeps its first target's proportions
indefinitely. Measured on the testbed's `bd-b` runs (private data). A synthetic reproduction was not
attempted.

## Impact

Slowed. It cost one full batch rerun (three books, about eight minutes) and the diagnosis. It would
have gone unnoticed without an outside benchmark.

## What would have prevented it

One sentence in `vqapr-make-strategy/references/rebalance.md` (or `access-and-account.md`): "A
decision taken after a fill reads marks whose proportions equal the previous target's. To let a
group drift and only resize it, derive the proportions from prices, not from `call.account`." A
quantity-scaling rebalance form ("scale these names' current quantities so their value at the fill is
w × NAV") would remove the one-session lag, but that is the owner's call and not needed for
correctness.
