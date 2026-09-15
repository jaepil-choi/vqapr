"""A zero weight holds none of the name, through `fill` and through `Rebalance` alike.

Report 2026-09-11 (`docs/issues/report-2026-09-11-rebalance-of-refuses-a-zero-weight-that-
rebalance-signed-keeps.md`): an enhanced index that underweights a name by 0.5%p, floored at zero,
returned `Rebalance.of(long={..., "A000100": 0})` and the run stopped with a refusal about how
sides are chosen. The owner ruled (2026-09-11) that a zero is accepted as "hold none" (record
`260`). `Rebalance.of` and `Rebalance.signed` are gone since record `291`; the ruling holds at the
two doors that replaced them, `budget().fill(signal)` and `Rebalance(weights)`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from vqapr.portfolio.budget import DEFAULT_BUDGET, Budget, BudgetRefusal
from vqapr.public import Rebalance

LONG_ONLY = Budget.fixed(long=1, short=0)


def test_a_zero_is_kept_as_a_flat_position() -> None:
    book = Rebalance(LONG_ONLY.fill({"A": 1, "B": 0}))

    assert book.target_weights["A"] == Decimal(1)
    assert book.target_weights["B"] == Decimal(0)
    assert book.cash_weight == Decimal(0)


def test_a_zero_in_a_signed_signal_is_on_neither_side() -> None:
    book = DEFAULT_BUDGET.fill({"A": 3, "B": 0, "C": 1, "D": -1})

    assert book["B"] == 0
    assert sum(value for value in book.values() if value > 0) == Decimal(1)
    assert sum(value for value in book.values() if value < 0) == Decimal(-1)


def test_a_hand_written_zero_is_kept_by_rebalance() -> None:
    """Dropping it would make the decision disagree with the mapping the author passed -- and a
    name left out is sold anyway, so the zero says the same thing out loud."""
    book = Rebalance({"A": "0.5", "B": 0})

    assert set(book.target_weights) == {"A", "B"}
    assert book.target_weights["B"] == 0


def test_a_zero_is_no_short_so_a_long_only_budget_takes_it() -> None:
    """The old `a side of zeros is no side`: a zero neither makes the book signed nor is refused
    as a short by a long-only declaration."""
    LONG_ONLY.check({"A": Decimal(1), "B": Decimal(0)})
    Budget.flexible(long_limit=1, short_limit=0).check(
        Budget.flexible(long_limit=1, short_limit=0).fill({"A": 1, "B": 0}, use="0.5")
    )


def test_a_signal_of_only_zeros_fills_nothing() -> None:
    """A fixed side cannot be filled from zeros, so it is refused toward `Hold`; a flexible
    budget fills neither side and the book is all cash."""
    with pytest.raises(BudgetRefusal, match="Return Hold"):
        DEFAULT_BUDGET.fill({"A": 0, "B": 0})

    book = Rebalance(Budget.flexible(long_limit=1, short_limit=0).fill({"A": 0, "B": 0}))
    assert dict(book.target_weights) == {"A": Decimal(0), "B": Decimal(0)}
    assert book.cash_weight == Decimal(1)
