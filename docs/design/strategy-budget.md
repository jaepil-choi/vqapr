# The strategy budget: declared once, filled or bounded

Status: decided by the owner 2026-09-15; campaign branch `redesign/strategy-budget`.

## The problem

A budget was attached to every `Rebalance`. A strategy could therefore widen its own limits on any
day, and the budget never reached the run record, so the report had no denominator. Two strategies
-- one at long 0.5 / short -0.3, one at 1 / -1 -- could not be compared, which is the problem a
flexible budget made visible in practice.

Analogy: a fund's limits are written once in its prospectus, not on every trade ticket. Trades
happen inside the prospectus, and performance is judged against it.

## The decision

**The budget is declared once, on the strategy class. A decision is weights only.**

```python
class Alpha(vq.StrategyModel):
    def budget(self):
        return vq.Budget.flexible(long_limit=1, short_limit=-1)   # default: Budget.fixed(long=1, short=-1)

    def decide(self, call):
        return vq.Rebalance(self.budget().fill(signal))
```

| declaration | long side | short side |
|---|---|---|
| `Budget.fixed(long=1, short=-1)` (default) | = 1 | = -1 |
| `Budget.fixed(long=0.5, short=-0.5)` | = 0.5 | = -0.5 (gross 1, like long-only 1) |
| `Budget.fixed(long=1, short=0)` | = 1 | none |
| `Budget.flexible(long_limit=1, short_limit=-1)` | 0 to 1 | -1 to 0 |
| `Budget.flexible(long_limit=1, short_limit=0)` | 0 to 1 | none |

- Fixed takes `long` / `short` (an equation); flexible takes `long_limit` / `short_limit` (how far a
  side may go). The short side is written negative everywhere, the same as `rescale`.
- Cash is not declared: it is `1 - net`, derived.
- Per-name limits stay where they were: the `bounds` kit and Compliance.

## Who does what

| piece | where | does |
|---|---|---|
| `Budget` | `portfolio/budget.py` | the value: `fixed`, `flexible`, `check(weights)`, `fill(signal, use=1)` |
| `StrategyModel.budget()` | `component/strategy/base.py` | the declaration; evaluated before memory, like `inputs()` |
| registration | `component/conformance.py` | calls `budget()` once and refuses a non-`Budget` |
| freeze | `run/preflight` | `FrozenStrategy.budget`, folded into the strategy's identity |
| decide stage | `run/engine/stages/decide.py` | `check`s every `Rebalance`; refuses, never clips or tops up |
| record | `strategy.json` `budget` | the declaration in its constructor's spelling |
| report | `report/measure.py` | utilization against the declared sides; the timing decomposition |

`fill(signal)` scales each side of a signed signal to its declared size on the canonical grid
(`rescale(..., grid=QUANTUM)`). Relative conviction is what the signal already is:
`{"A": 2, "B": 1, "C": -1}` under `fixed(1, -1)` gives A 2/3, B 1/3, C -1. Under a flexible budget
`use` (0 < use <= 1) takes that fraction of each limit; a fixed budget is filled in full.

## What goes away

- `Rebalance.of`, `Rebalance.signed`, and `Rebalance`'s `cash_weight` / `budget` arguments. One door:
  `Rebalance(weights)`, cash derived.
- `PortfolioDirection`: long-only is `short=0`.
- The budget on `EconomicPortfolioIntent`, on `plan_orders`, and on `AccountCommitEvidence`. The
  decision is checked once, at the decide stage, against the frozen declaration.

## Consequences

- A long-only strategy must declare its budget; the default is dollar neutral.
- Under a fixed budget a day that cannot fill a side is refused -- a signal with no short name, or
  an empty book. A strategy that has such days declares a flexible budget or returns `Hold`.
- Breaking: 0.17.0.

## Comparison is the report's job

Return on NAV alone cannot compare a partly used budget with a full one. The report reads the
declared sides and shows, per period, how much of each side was used, and splits the mean return
into `mean(use) x mean(return per full budget) + cov(use, return per full budget)` -- the last term
is the skill of using more when it pays. Sharpe and IR against a benchmark stay the scale-free
comparison.
