"""The report measures a book against the budget its strategy declared (record `292`).

The owner's question (2026-09-15): a strategy allowed to use long 0.5 / short 0.3 of a 1 / -1
budget cannot be compared with one that uses all of it on NAV return alone. The budget section
answers with a denominator -- use per side and per book -- and splits the mean period return into
what a whole budget earned and what using more when it paid added.

The grid is small enough to work by hand: 100 in cash; half of NAV long A; then A up to 60 beside a
short of 20 in B, NAV 110; then flat at 99. Under `flexible(1, -1)` the declared gross is 2.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from vqapr.public import Budget
from vqapr.report import measure

SEOUL = timezone(timedelta(hours=9))
T = [datetime(2024, 1, day, 15, 30, tzinfo=SEOUL) for day in (1, 2, 3, 4)]
D = Decimal

GRID = [
    measure.Valuation(T[0], 0, D(100), D(100), {}),
    measure.Valuation(T[1], 1, D(50), D(100), {"A": measure.Position(D(50), D(1))}),
    measure.Valuation(
        T[2],
        2,
        D(70),
        D(110),
        {"A": measure.Position(D(50), D("1.2")), "B": measure.Position(D(-20), D(1))},
    ),
    measure.Valuation(T[3], 3, D(99), D(99), {}),
]


def _split(budget: Budget):
    book = measure.book(GRID)
    performance = measure.performance(
        GRID,
        periods_per_year=252,
        periods_per_year_source="given",
        risk_free_annual=D(0),
        initial_nav=None,
    )
    return measure.budget_use(book, performance, budget.encoded())


def test_use_is_exposure_over_the_declared_size_per_side_and_per_book() -> None:
    split = _split(Budget.flexible(long_limit=1, short_limit=-1))

    assert split.declared == {"kind": "flexible", "long_limit": "1", "short_limit": "-1"}
    assert split.long_use == [D(0), D("0.5"), D(60) / D(110), D(0)]
    assert split.short_use == [D(0), D(0), D(20) / D(110), D(0)]
    assert split.use == [D(0), D("0.25"), D(80) / D(110) / 2, D(0)]


def test_the_mean_return_splits_into_a_whole_budgets_return_and_timing() -> None:
    """Two periods held something (the first opened flat). Their returns, +10% then -10%, average
    to zero; the book used more of its budget going into the loss, so timing is negative."""
    split = _split(Budget.flexible(long_limit=1, short_limit=-1))

    assert split.periods == 2
    assert split.mean_return == 0
    assert split.mean_use_held == (D("0.25") + D(80) / D(220)) / 2
    assert (
        split.mean_return_at_full_use == (D("0.1") / D("0.25") + D("-0.1") / (D(80) / D(220))) / 2
    )
    assert split.timing is not None and split.timing < 0, "more was used before the loss"
    assert split.mean_use_held * split.mean_return_at_full_use + split.timing == split.mean_return


def test_a_side_the_budget_does_not_have_has_no_use() -> None:
    split = _split(Budget.fixed(long=1, short=0))

    assert split.short_use is None
    assert split.use == [D(0), D("0.5"), D(80) / D(110), D(0)], "declared gross is 1"
