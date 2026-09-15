# The strategy that `vqapr new sample` emits imports `Budget` and `PortfolioDirection` from the private module `vqapr.domain.intent`

**Status: RECEIVED 2026-09-15 (접수) — confirmed against `develop` (`src/vqapr/agent/sample/reversal_5d.py:16`). Being fixed on `redesign/strategy-budget`: the budget becomes a declaration on the strategy class (`vq.Budget`, `vqapr.portfolio.budget`) and `PortfolioDirection` goes away, so the sample imports from `vqapr.public` only.** **CLOSED 2026-09-15 by record `291` — the budget is the strategy's declaration (`vq.Budget`, exported from `vqapr.public`), `PortfolioDirection` is gone, and the sample declares `budget()` and imports from `vqapr.public` only.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** the sample's docstring citation of an unshipped document is in `report-2026-09-14-public-docstrings-cite-internal-documents-the-wheel-does-not-ship.md`.

## What I was doing

Run 4 needed six long-only Fama-French leg strategies. The agent copied the shape of the sample
strategy and meant to use only the public surface.

## What I expected

- `vqapr-introduce-vqapr/SKILL.md:79-84` ("See one run happen first") starts users on
  `vqapr new sample`.
- The emitted `sample/README.md` says "the strategy and the venue are yours to read and change".
- `vqapr-make-strategy/SKILL.md:25-27` says scaffolds are "generated from the contracts the
  package enforces, so it cannot drift from them".
- `vqapr-make-strategy/SKILL.md:125` names `vqapr.public` as the module whose names a strategy
  uses.

I expected the emitted file to import only from `vqapr.public`, as every other scaffold does.

## What happened

The original run (`FINDINGS.md`, F-004): "`from vqapr.domain.intent import Budget,
PortfolioDirection`; the module docstring cites
`docs/implementations/013-halted-names-do-not-stop-a-rebalance.md`."

I checked this again on 0.16.0. `vqapr new sample --out ./sample` emits `reversal_5d.py`, whose
lines 16–23 read:

```python
from vqapr.domain.intent import Budget, PortfolioDirection
from vqapr.public import (
    DatasetInput,
    Hold,
    Rebalance,
    RowsLookback,
    StrategyModel,
)
```

Both names are public:

- They are in `vqapr.public.__all__`.
- `vqapr.public.Budget is vqapr.domain.intent.Budget` is `True`, and so is the same check for
  `PortfolioDirection`.

Every other scaffold imports from `vqapr.public` only:

- `new strategy` (with and without `--calendar-lookback`), `new datamodel` and `new compliance`
  use `from vqapr import public as vq`.
- `new exchange` (academic and krx) and the sample's own `exchange.py` use
  `from vqapr.public import …`.

The sample strategy is the only emitted file that reaches outside `vqapr.public`.

Scope notes:

- The sample's docstring citation of an unshipped document is included in the separate report on
  internal citations.
- The original entry's point about the direct `Rebalance(...)` constructor did not reproduce as
  stated. `Rebalance.__doc__` ranks it ("Three ways in, and the direct constructor is the last of
  them"). `Budget.__doc__` spells out the budgets for direct construction. And
  `vqapr-make-compliance/SKILL.md:35` itself uses `Rebalance(target_weights=result.weights,
  cash_weight=result.cash, budget=BUDGET)`. That point is not part of this report.

## Reproduction

1. `uv run vqapr --project-root . new sample --out ./sample`
2. Read `sample/reversal_5d.py`, line 16.
3. `uv run python -c "import vqapr.public as p, vqapr.domain.intent as d; print('Budget' in p.__all__, p.Budget is d.Budget, p.PortfolioDirection is d.PortfolioDirection)"`
   prints `True True True`.

Reproduced 1 of 1 attempts. Deterministic.

## Impact

A papercut. The agent imported both names from `vqapr.public` instead. A user who copies the
sample, which is what the skills lead them to do, inherits a dependency on an internal module
path. The rest of the surface never asks them to know that path.

## What would have prevented it

The sample importing `Budget` and `PortfolioDirection` from `vqapr.public`, as its other imports
already do.
