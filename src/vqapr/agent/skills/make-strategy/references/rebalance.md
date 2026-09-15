# The budget, `Rebalance(weights)` and `fill`

A strategy says how large its book is **once**, in `budget()`. Each decision is weights only. The
run checks every `Rebalance` against the declaration and refuses one outside it — nothing is
clipped and nothing is topped up.

## Declare the budget

```python
def budget(self):
    return vq.Budget.fixed(long=1, short=0)   # long-only, fully invested
```

| declaration | long side | short side |
|---|---|---|
| `Budget.fixed(long=1, short=-1)` — the default | exactly 1 | exactly -1 |
| `Budget.fixed(long=0.5, short=-0.5)` | exactly 0.5 | exactly -0.5 |
| `Budget.fixed(long=1, short=0)` | exactly 1 | none (long-only) |
| `Budget.flexible(long_limit=1, short_limit=-1)` | 0 to 1 | -1 to 0 |
| `Budget.flexible(long_limit=1, short_limit=0)` | 0 to 1 | none |

- `fixed` is an equation, `flexible` a limit; the parameter names say which.
- The short side is written **negative**, the way a short weight is.
- **Undeclared means dollar neutral.** A long-only strategy must declare `short=0`.
- `fixed(long=0.5, short=-0.5)` has the gross of a fully invested long-only book.
- Cash is not declared. It is `1 - sum(weights)`.

`budget()` is evaluated before memory exists, like `inputs()`, and frozen with the run into its
record. `vqapr show model <id>` prints it.

## Size a signal with `fill`

```python
return vq.Rebalance(self.budget().fill({"A": 2, "B": 1, "C": -1}))
```

- The sign is the side; the size is **relative conviction within that side**. Under
  `fixed(long=1, short=-1)` this is A 2/3, B 1/3, C -1.
- Each side lands exactly on its declared size, on the canonical grid. A zero keeps the name at
  zero, so a held one is sold.
- `use=` takes that fraction of each limit, `0 < use <= 1`, and only a **flexible** budget accepts
  it. A fixed budget is filled in full.

`Rebalance(weights)` also takes weights built another way — an `optimize` result's `.weights`, a
hand-written book — and the run checks them the same way. `Rebalance({})` empties the book.

`Rebalance.of`, `Rebalance.signed` and the `cash_weight=` / `budget=` keywords are gone since
0.17.0.

## A fixed side must be filled every time

Under a fixed budget, a decision that leaves a declared side empty is refused: a signal with no
negative name under `short=-1`, or an empty book. If the strategy has such days, declare
`flexible`, or return `Hold` on them.

## Cash

The net residual. A dollar-neutral book therefore has cash 1 — that is not a bug and not idle
capital to reinvest.

## Declining

```python
return vq.Hold(reason="no name scored above zero")
```

Prose a human reads. Spaces are fine; only an empty string is refused. Warm-up callbacks — the
ones before the lookback has filled — are `Hold`, not failures.

## What is not yours to do

- **Do not normalise by hand.** `fill` lands each side exactly; a hand-made `1/3` each misses by a
  rounding step, and a fixed budget refuses it.
- **Do not top up an under-allocated result.** See
  [composition-and-budget.md](composition-and-budget.md).
