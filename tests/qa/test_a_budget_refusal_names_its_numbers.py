"""A budget refusal names the sums it saw and the declaration it held them to.

`docs/issues/archive/071`: `cash_weight is outside the declared budget` was the whole message for a
book whose quantised shorts summed to `-1.000000000001`, so cash was `2.000000000001` against a
`cash_upper` of `2`. The author reasoned both numbers out by hand.

Since record `291` the budget is declared once (`StrategyModel.budget()`) and `Budget.check`
judges each side's sum rather than cash. Cash is derived and cannot be wrong on its own, so the
cash, sum and empty-book refusals this file used to pin have no subject left. What carries over is
the rule: the refusal quotes the numbers, the declaration and the names, bounded like examples.
Each sentence is pinned whole, because it is the whole of what an agent reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal

import pytest

from vqapr.portfolio.budget import DEFAULT_BUDGET, Budget, BudgetRefusal


def _refusal(budget: Budget, weights: Mapping[str, Decimal]) -> str:
    with pytest.raises(BudgetRefusal) as refused:
        budget.check(weights)
    return str(refused.value)


def test_the_crumb_is_named_to_the_last_digit() -> None:
    """`071`'s book, judged by the side that missed rather than by cash."""
    message = _refusal(DEFAULT_BUDGET, {"A": Decimal(1), "B": Decimal("-1.000000000001")})

    assert message == (
        "Budget.fixed(long=1, short=-1) refuses this book: the short side sums to "
        "-1.000000000001, not -1. Size the book with self.budget().fill(signal), which lands "
        "each side exactly; or declare Budget.flexible if a side may be smaller"
    )


def test_a_flexible_refusal_names_each_side_and_its_limit() -> None:
    message = _refusal(
        Budget.flexible(long_limit=1, short_limit=-1),
        {"A": Decimal("1.5"), "B": Decimal("-1.5")},
    )

    assert message == (
        "Budget.flexible(long_limit=1, short_limit=-1) refuses this book: the long side sums to "
        "1.5, above its limit 1; the short side sums to -1.5, below its limit -1. Scale the book "
        "down, for example with self.budget().fill(signal, use=...)"
    )


def test_a_short_under_a_long_only_budget_is_named() -> None:
    message = _refusal(Budget.fixed(long=1, short=0), {"A": Decimal("0.6"), "B": Decimal("-0.1")})

    assert message == (
        "Budget.fixed(long=1, short=0) is long-only, but the book is short B. Drop those names, "
        "or declare a short side in budget()"
    )


def test_a_long_under_a_short_only_budget_is_named() -> None:
    message = _refusal(Budget.fixed(long=0, short=-1), {"A": Decimal("0.1"), "B": Decimal("-1.1")})

    assert message == (
        "Budget.fixed(long=0, short=-1) has no long side, but the book is long A. Drop those "
        "names, or declare a long side in budget()"
    )


def test_the_offenders_are_bounded_like_examples() -> None:
    weights = {f"N{i:02d}": Decimal("-0.1") for i in range(12)} | {"A": Decimal("2.2")}

    message = _refusal(Budget.fixed(long=1, short=0), weights)

    assert "the book is short N00, N01, N02, N03, N04, and 7 more." in message, message
