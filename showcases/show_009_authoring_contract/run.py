"""show_009 — the same book, filled by the budget or built by hand.

Runs one cross-sectional momentum view twice: once as `Rebalance(self.budget().fill(scores))`,
and once as a book assembled by hand and passed as `Rebalance(weights)`. Both produce the same book,
which is the point -- `fill` was never carrying information, it was carrying the arithmetic an
author can get wrong. And a hand-built book is not trusted for being hand-built: the run checks
every `Rebalance` against the budget the strategy declared once.

Reproduce:

```
uv run python showcases/show_009_authoring_contract/run.py
```
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path

from vqapr.public import QUANTUM, Budget, Rebalance, StrategyModel

OUTPUTS = Path(__file__).parent / "outputs"

SCORES = {
    "A005930": Decimal("0.081"),
    "A000660": Decimal("0.047"),
    "A035420": Decimal("0.019"),
}
INVESTED = Decimal("0.9")
SIGNED_SCORES = {"A005930": 2, "A000660": 1, "A035420": -1}


class Momentum(StrategyModel):
    """Long-only and allowed to hold cash; the book uses INVESTED of the long side."""

    def budget(self) -> Budget:
        return Budget.flexible(long_limit=1, short_limit=0)

    def decide(self, call) -> Rebalance:
        # The scores are fixed for this showcase, so there is nothing in the call to read.
        return self.filled(SCORES)

    def filled(self, scores: Mapping[str, Decimal]) -> Rebalance:
        """What an author writes: which names, how much they like them, how much to use."""
        return Rebalance(self.budget().fill(scores, use=INVESTED))

    def by_hand(self, scores: Mapping[str, Decimal]) -> Rebalance:
        """What an author writes without `fill`: normalise, scale, round, and settle the crumb.

        Every line is arithmetic with one right answer, and every line is a place to be wrong. The
        last one is the trap -- three names rarely divide evenly, so the rounded weights can miss
        `INVESTED` by a grid step, and the crumb has to be put somewhere on purpose.
        """
        total = sum(scores.values(), Decimal(0))
        weights = {
            name: (score / total * INVESTED).quantize(QUANTUM)
            for name, score in sorted(scores.items())
        }
        largest = max(weights, key=lambda name: (weights[name], name))
        weights[largest] += INVESTED - sum(weights.values(), Decimal(0))
        return Rebalance(weights)


class LongShort(StrategyModel):
    """Dollar neutral at 0.4 a side: 0.8 gross, zero net."""

    def budget(self) -> Budget:
        return Budget.fixed(long="0.4", short="-0.4")

    def decide(self, call) -> Rebalance:
        return Rebalance(self.budget().fill(SIGNED_SCORES))


def _described(book: Rebalance, budget: Budget) -> dict[str, object]:
    """The book as the record would show it, after the check the decide stage runs on it."""
    budget.check(book.target_weights)
    return {
        "weights": {name: str(value) for name, value in sorted(book.target_weights.items())},
        "cash": str(book.cash_weight),
        "admitted_by": str(budget),
    }


def with_the_budget() -> dict[str, object]:
    strategy = Momentum()
    return {**_described(strategy.decide(None), strategy.budget()), "lines_of_arithmetic": 0}


def by_hand() -> dict[str, object]:
    strategy = Momentum()
    return {**_described(strategy.by_hand(SCORES), strategy.budget()), "lines_of_arithmetic": 4}


def a_signed_book() -> dict[str, object]:
    """The case hand arithmetic got wrong more often than not: the cash of a long/short book.

    Cash is `1 - sum(weights)`, the NET residual, while the size an author thinks in is GROSS. A
    dollar-neutral book at 0.4 a side is 0.8 gross and nets to zero, so its cash is 1 -- not the
    `1 - 0.8` an author reaching for "invested" would write. Nobody writes cash now: the budget
    names each side, and cash is derived.
    """
    strategy = LongShort()
    budget = strategy.budget()
    book = strategy.decide(None)
    weights = book.target_weights
    long_side = sum((value for value in weights.values() if value > 0), Decimal(0))
    short_side = sum((value for value in weights.values() if value < 0), Decimal(0))
    # A hand-built book with one name dropped by mistake: the declaration refuses it rather than
    # letting a book nobody meant reach the account.
    try:
        budget.check({**weights, "A000660": Decimal(0)})
    except ValueError as refusal:
        refused = str(refusal)
    else:
        raise AssertionError("a book off its declared budget was admitted")
    return {
        **_described(book, budget),
        "long_side": str(long_side),
        "short_side": str(short_side),
        "gross_exposure": str(long_side - short_side),
        "naive_cash_would_have_been": str(Decimal(1) - (long_side - short_side)),
        "off_budget_book_refused": refused,
    }


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    filled = with_the_budget()
    manual = by_hand()
    signed = a_signed_book()

    report = {
        "with_the_budget": filled,
        "by_hand": manual,
        "same_book": (filled["weights"] == manual["weights"] and filled["cash"] == manual["cash"]),
        "signed_book": signed,
    }
    (OUTPUTS / "authoring_contract.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not report["same_book"]:
        raise AssertionError(f"fill and the hand-built book differ: {filled} vs {manual}")

    print("with budget  :", filled["weights"], "cash", filled["cash"])
    print("by hand      :", manual["weights"], "cash", manual["cash"])
    print("same book    :", report["same_book"])
    print()
    print("signed book  :", signed["weights"])
    print(
        "  sides      :",
        signed["long_side"],
        "/",
        signed["short_side"],
        f"(gross {signed['gross_exposure']}, declared once in budget())",
    )
    print(
        "  cash       :",
        signed["cash"],
        f"(1 - gross would have said {signed['naive_cash_would_have_been']})",
    )
    print("  off budget :", signed["off_budget_book_refused"].split(". ")[0])
    print()
    print(f"wrote {OUTPUTS / 'authoring_contract.json'}")


if __name__ == "__main__":
    main()
