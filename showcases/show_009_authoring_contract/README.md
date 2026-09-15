# show_009 — the same book, filled by the budget or built by hand

One cross-sectional momentum view, expressed twice: once as `Rebalance(self.budget().fill(scores))`,
and once as a book assembled by hand and passed as `Rebalance(weights)`. Both produce **the same
book**, which is the whole point — `fill` was never carrying information. It carries the arithmetic
an author can get wrong.

Reproduce:

```
uv run python showcases/show_009_authoring_contract/run.py
```

## What it shows

**Identical output, four fewer lines of arithmetic.** The strategy declares
`Budget.flexible(long_limit=1, short_limit=0)` once, on the class. By hand, an author normalises the
scores, scales by the invested fraction, quantises onto the canonical grid, and settles the rounding
crumb on the largest name so the long side lands on 0.9. `self.budget().fill(scores, use=0.9)` does
exactly that. Cash is `1 - sum(weights)` in both books — nobody writes it — so both show
`0.100000000000`.

**The signed book is where hand-arithmetic reliably broke.** Cash is *net*, while the size an author
thinks in is *gross*. The showcase declares `Budget.fixed(long=0.4, short=-0.4)` and prints:

```
sides : 0.400000000000 / -0.400000000000   (gross 0.800000000000, declared once in budget())
cash  : 1.000000000000                     (1 - gross would have said 0.200000000000)
```

An author computing `cash = 1 - invested` is wrong for every signed book, and wrong by the entire
portfolio for a dollar-neutral one, which is fully invested and nets to zero. That mistake was in the
package's own first implementation of the old `Rebalance.of`. Now there is no cash to write.

**The budget is declared once, and a hand-built book is held to it.** The run checks every
`Rebalance` against the strategy's `budget()` and fails on a violation, so `Rebalance(weights)` is
no way around it. The showcase drops one name from the signed book by hand, and the declaration
refuses it:

```
Budget.fixed(long=0.4, short=-0.4) refuses this book: the long side sums to 0.266666666667, not 0.4
```
