# Composing strategies, and what the budget means

## Contents

- A strategy can read another strategy's result
- Why the chain, rather than one calculation
- Budget: fixed or flexible, declared once
- Intended cash is not leftover cash

## A strategy can read another strategy's result

A stored result **is a dataset**, so a StrategyModel subscribes to another StrategyModel's output
the way it subscribes to prices. An ensemble is one instance of that pattern, not a separate
post-processing stage the framework imposes.

```
A   long-short alpha     -> executed -> stored result
B   ensemble             -> reads A and other members -> executed -> stored result
C   enhanced index       -> reads B and a benchmark   -> long-only allocation -> executed
```

**Every step passes through execution.** If A and B use the zero-friction academic profile the
fills cost nothing — but the account, the NAV and the feedback are real. That is what lets a
turnover-aware A see its own book, and an adaptive B see its members' realised outcomes rather
than their intentions.

Registering the upstream result as a dataset is a `run-backtest` step; that skill's
`feeding-the-next-run.md` has the declaration.

## Why the chain, rather than one calculation

Because a signed alpha must survive being turned into a long-only book.

Convert inside one calculation and the original becomes an intermediate value that disappears —
and then preserving it needs some extra apparatus. Chained, A's result stands on its own as a
result, and nothing had to be added to keep it.

## Budget: fixed or flexible, declared once

The strategy declares its budget in `budget()`, once for the run
([rebalance.md](rebalance.md) has the table):

| | each side | on a weak day |
|---|---|---|
| `Budget.fixed(long=, short=)` | exactly its value | still filled in full, concentrated on the names picked |
| `Budget.flexible(long_limit=, short_limit=)` | from 0 to its limit | may use less; the rest is cash |

Cash is never declared: it is `1 - net`.

## The rule that follows

**An operation that produces weights never decides the budget — the declaration does.** A result
that uses less than a flexible budget is **not topped up**, by the package or by a helper: that
would turn a flexible budget into a fixed one silently. A book outside the declaration is refused,
not clipped.

So: do not renormalise to reach the budget. Under `fixed`, `fill` reaches it; under `flexible`, a
side used in part is the signal's answer, not a bug to fix inside `decide()`.

## Intended cash is not leftover cash

Arithmetically, whatever is not allocated is cash. Economically these are two different things:

- **An intended cash position.** Strategies where the risk-free share is part of the alpha —
  betting-against-beta's leverage construction, risk parity's cash sleeve, market timing — hold
  cash *by choice*.
- **An unallocated residual.** Under a flexible budget, what a weak signal, high cost or a risk
  condition left behind.

The two can be the same number and must not be reported as the same thing. The source says which:
a flexible budget filled with a **constant** `use` — `fill(signal, use=0.9)` on every decision —
holds its cash by design; a `use` the signal sets, or a side left empty because no name
qualified, leaves a residual.

When you report a book's cash, say which of the two it is. Comparing a partly used budget with a
full one is the report's job, against the declaration the run recorded — not a reason to scale
the book up. If the source does not make it clear, ask the user rather than choosing the
flattering reading.

## More than NAV long: borrowed cash

A book that holds more than its NAV long needs cash below zero. Two declarations make it:

- **The run:** `initial_account.cash_mode: BORROWING`. Without it the account refuses negative
  cash and the planner cuts buys to the cash on hand, so the leverage silently does not happen.
- **The strategy:** a budget whose book nets above 1. `Budget.fixed(long=2, short=0)` with
  `Rebalance(self.budget().fill({"A": 1, "B": 1}))` is 200% long with cash at -1: one NAV
  borrowed, and never more. A 130/30 book (`fixed(long=1.3, short=-0.3)`) borrows nothing; the
  short pays for the extra long.

Borrowed cash is free: no interest, no margin, no forced sale. A borrowing backtest's return is
higher than a real one's by the financing cost, so say so when you report it. For a financing
cost, keep `FUNDED`, declare the account `SIGNED`, and short a registered derived unit-price asset
that grows at the borrowing rate instead: the short's growth is the interest.
