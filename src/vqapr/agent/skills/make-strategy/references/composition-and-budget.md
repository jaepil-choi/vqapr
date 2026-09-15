# Composing strategies, and what the budget means

## Contents

- A strategy can read another strategy's result
- Why the chain, rather than one calculation
- Budget: fixed, flexible, and intended cash
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

## Budget: three shapes of one declaration

Budget semantics are a **declared range for cash**, not a separate concept:

| | cash range |
|---|---|
| fixed budget | lower = upper = 0 — allocate everything |
| flexible budget | lower 0, upper free — leaving some is allowed |
| intended cash holding | a narrow range at the value you want |

## The rule that follows

**An operation that produces weights never decides the budget.** A result that allocated less than
the declared budget is **not topped up**, by the package or by a helper.

Automatically filling it turns a flexible budget into a fixed one silently, and the two mean
different things about the same book.

So: do not renormalise to reach the budget, and do not treat "the weights do not sum to the
target" as a bug to fix inside `decide()`.

## Intended cash is not leftover cash

Arithmetically, whatever is not allocated is cash. Economically these are two different things:

- **An intended cash position.** Strategies where the risk-free share is part of the alpha —
  betting-against-beta's leverage construction, risk parity's cash sleeve, market timing — hold
  cash *by choice*.
- **An unallocated residual.** Under a flexible budget, what a weak signal, high cost or a risk
  condition left behind.

The two can be the same number and must not be reported as the same thing. Declaring a narrow
range says "intended"; leaving it wide says "residual" — and the result then shows which it was,
because **cash is a decided value rather than a derived one** and stays in the record as such.

When you report a book's cash, say which of the two it is. If the declaration does not make it
clear, ask the user rather than choosing the flattering reading.

## More than NAV long: borrowed cash

A book that holds more than its NAV long needs cash below zero. Two declarations make it:

- **The run:** `initial_account.cash_mode: BORROWING`. Without it the account refuses negative
  cash and the planner cuts buys to the cash on hand, so the leverage silently does not happen.
- **The strategy:** a budget whose `cash_lower` is below zero. `Rebalance.signed({"A": 1, "B": 1},
  gross=2)` is 200% long with cash at -1, and `cash_lower=-1` means at most one NAV borrowed.
  `Rebalance.of` caps `invested` at 1 and cannot express this.

Borrowed cash is free: no interest, no margin, no forced sale. A borrowing backtest's return is
higher than a real one's by the financing cost, so say so when you report it. For a financing
cost, keep `FUNDED`, declare the account `SIGNED`, and short a registered derived unit-price asset
that grows at the borrowing rate instead: the short's growth is the interest.
