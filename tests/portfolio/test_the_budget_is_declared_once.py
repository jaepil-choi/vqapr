"""The strategy's budget is declared once, on the class, and every decision is judged by it.

Design `docs/design/strategy-budget.md` (record `291`). A budget used to ride on each `Rebalance`,
so a strategy could widen its own limits on any day and the run record never learned them; and
`Rebalance.of` / `Rebalance.signed` each stated a size (`invested`, `gross`) that could disagree
with the budget beside it. Now `StrategyModel.budget()` declares it once, the run freezes it into
the strategy's identity, and the decide stage checks every `Rebalance` against it -- refused,
never clipped and never topped up.

Pinned here, from the value outwards: what a declaration may say, what `check` admits, what
`fill` makes, how the declaration is spelled for the identity, what `Rebalance` became, and the
two doors that read `budget()` -- registration and the run.

The retired constructors' invariants that still have a subject are ported here rather than lost:
each side lands exactly on its target with the rounding crumb on its own side (`075`), a side
finer than the grid is refused rather than rounded away, a zero stays at zero (`260`), cash is the
net residual, and the textbook +1/-1 book is reachable (`018`) -- it is now the default.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date, time
from decimal import Decimal
from pathlib import Path

import pytest

import tests.sample.journey as journey
from vqapr import public as vq
from vqapr.component.reference import ComponentRef
from vqapr.domain.errors import VqaprError
from vqapr.domain.instants import LocalInstantDeclaration
from vqapr.domain.schedule import ScheduledEvent
from vqapr.domain.wiring import Role
from vqapr.portfolio.budget import DEFAULT_BUDGET, Budget, BudgetRefusal
from vqapr.portfolio.optimize import QUANTUM
from vqapr.run.engine.failure import SimulationFailure
from vqapr.run.preflight.frozen import FrozenSchedule, FrozenStrategy
from vqapr.workspace.run_definition import ComplianceSet, StrategyConfig


def _sides(weights: Mapping[str, Decimal]) -> tuple[Decimal, Decimal]:
    values = list(weights.values())
    return (
        sum((value for value in values if value > 0), Decimal(0)),
        sum((value for value in values if value < 0), Decimal(0)),
    )


# ---------------------------------------------------------------------------------------------
# The declaration
# ---------------------------------------------------------------------------------------------


def test_a_strategy_that_declares_nothing_is_dollar_neutral() -> None:
    class Undeclared(vq.StrategyModel):
        def decide(self, call: vq.StrategyCall) -> vq.Hold:
            return vq.Hold(reason="declaration only")

    assert Undeclared().budget() == Budget.fixed(long=1, short=-1)
    assert Undeclared().budget() is DEFAULT_BUDGET
    assert not DEFAULT_BUDGET.long_only


def test_the_textbook_book_is_the_default_fill() -> None:
    """`docs/issues/archive/018`: `Rebalance.of` topped out at half of a $1-long/$1-short book, so
    a factor arm could not be compared with a published series. The default budget IS that book."""
    book = DEFAULT_BUDGET.fill({"A": 1, "B": -1})

    assert dict(book) == {"A": Decimal(1), "B": Decimal(-1)}
    assert vq.Rebalance(book).cash_weight == Decimal(1), "dollar neutral: cash is all of NAV"


def test_a_half_sized_fixed_budget_fills_to_exactly_half() -> None:
    """`fixed(long=0.5, short=-0.5)` has the gross of a fully invested long-only book, and each
    side lands on it to the last digit even when the names do not divide it."""
    budget = Budget.fixed(long=0.5, short=-0.5)

    book = budget.fill({"A": 1, "B": 1, "C": -1, "D": -1, "E": -1})

    assert _sides(book) == (Decimal("0.5"), Decimal("-0.5"))


@pytest.mark.parametrize(
    ("label", "build", "says"),
    [
        ("a positive short", lambda: Budget.fixed(long=1, short=1), "short is written negative"),
        (
            "a negative long",
            lambda: Budget.flexible(long_limit=-1, short_limit=-1),
            "long_limit is the size of the long side and cannot be negative",
        ),
        ("no side at all", lambda: Budget.fixed(long=0, short=0), "has no side at all"),
        ("a bool", lambda: Budget.fixed(long=True, short=-1), "long must be a number; got bool"),
        (
            "finer than the grid",
            lambda: Budget.fixed(long="0.0000000000001", short=0),
            "finer than the canonical grid",
        ),
        (
            "not finite",
            lambda: Budget.flexible(long_limit="Infinity", short_limit=0),
            "long_limit must be finite",
        ),
    ],
)
def test_a_declaration_no_book_can_meet_is_refused(label: str, build, says: str) -> None:
    with pytest.raises(BudgetRefusal) as refused:
        build()

    assert says in str(refused.value), (label, str(refused.value))
    assert isinstance(refused.value, ValueError), "a refusal is still a ValueError to a caller"


# ---------------------------------------------------------------------------------------------
# `check`: judging a book
# ---------------------------------------------------------------------------------------------


def test_a_fixed_budget_refuses_a_side_that_misses_naming_both_sums_and_the_declaration() -> None:
    DEFAULT_BUDGET.check({"A": Decimal("0.6"), "B": Decimal("0.4"), "C": Decimal("-1")})

    with pytest.raises(BudgetRefusal) as refused:
        DEFAULT_BUDGET.check({"A": Decimal("0.5"), "B": Decimal("-0.7")})

    message = str(refused.value)
    assert message.startswith("Budget.fixed(long=1, short=-1) refuses this book"), message
    assert "the long side sums to 0.5, not 1" in message
    assert "the short side sums to -0.7, not -1" in message
    assert "self.budget().fill(signal)" in message, "the refusal names the road that lands exactly"


def test_a_flexible_budget_admits_less_and_refuses_more() -> None:
    budget = Budget.flexible(long_limit=1, short_limit=-1)

    budget.check({"A": Decimal("0.4"), "B": Decimal("-0.2")})
    budget.check({"A": Decimal(1), "B": Decimal(-1)})
    budget.check({})

    with pytest.raises(
        BudgetRefusal, match=re.escape("the long side sums to 1.000000000001, above its limit 1")
    ):
        budget.check({"A": Decimal("1.000000000001"), "B": Decimal("-0.5")})
    with pytest.raises(
        BudgetRefusal, match=re.escape("the short side sums to -1.5, below its limit -1")
    ):
        budget.check({"A": Decimal("0.5"), "B": Decimal("-1.5")})


@pytest.mark.parametrize(
    "budget",
    [Budget.fixed(long=1, short=0), Budget.flexible(long_limit=1, short_limit=0)],
    ids=str,
)
def test_a_long_only_budget_refuses_a_short_in_check_and_in_fill(budget: Budget) -> None:
    """`short=0` is long-only; `PortfolioDirection` is gone and this is what replaced it."""
    assert budget.long_only

    with pytest.raises(BudgetRefusal, match="is long-only, but the book is short B"):
        budget.check({"A": Decimal("0.5"), "B": Decimal("-0.1")})
    with pytest.raises(BudgetRefusal, match="is long-only, but the signal is negative for B"):
        budget.fill({"A": 1, "B": -1})


# ---------------------------------------------------------------------------------------------
# `fill`: making a book
# ---------------------------------------------------------------------------------------------


def test_fill_keeps_the_signals_conviction_within_each_side() -> None:
    """The design's example, and a signal that divides exactly so the ratios can be exact."""
    assert dict(DEFAULT_BUDGET.fill({"A": 2, "B": 1, "C": -1})) == {
        "A": Decimal("0.666666666667"),
        "B": Decimal("0.333333333333"),
        "C": Decimal(-1),
    }

    book = DEFAULT_BUDGET.fill({"A": 3, "B": 1, "C": -1, "D": -3})
    assert book["A"] == book["B"] * 3
    assert book["D"] == book["C"] * 3


@pytest.mark.parametrize(
    ("label", "budget", "signal", "use"),
    [
        # `075`'s measured regression: the three shorts' crumb landed on the LONG name.
        ("one long against three shorts", DEFAULT_BUDGET, {"A": 1, "B": -1, "C": -1, "D": -1}, 1),
        (
            "seven against eleven",
            Budget.fixed(long="0.5", short="-0.5"),
            {**{f"L{i}": 1 for i in range(7)}, **{f"S{i}": -1 for i in range(11)}},
            1,
        ),
        ("uneven conviction", DEFAULT_BUDGET, {"A": 3, "B": 2, "C": 1, "D": -5, "E": -2}, 1),
        (
            "part used",
            Budget.flexible(long_limit=1, short_limit=-1),
            {"A": 2, "B": 1, "C": -1, "D": -1, "E": -1},
            "0.9",
        ),
        (
            "awkward use, long-only",
            Budget.flexible(long_limit=1, short_limit=0),
            {"A": 1, "B": 1, "C": 1},
            "0.333",
        ),
    ],
)
def test_each_side_lands_exactly_on_its_target_on_the_grid(
    label: str, budget: Budget, signal: dict, use: object
) -> None:
    book = budget.fill(signal, use=use)
    share = Decimal(str(use))

    assert _sides(book) == (
        (budget.long * share).quantize(QUANTUM),
        (budget.short * share).quantize(QUANTUM),
    ), label
    assert all(value == value.quantize(QUANTUM) for value in book.values()), label
    if label == "one long against three shorts":
        assert book["A"] == Decimal(1), "the short side's crumb stays on the short side"


def test_a_zero_score_is_kept_at_zero() -> None:
    book = DEFAULT_BUDGET.fill({"A": 1, "B": 0, "C": -1})

    assert set(book) == {"A", "B", "C"}
    assert book["B"] == 0


def test_use_takes_a_fraction_of_each_flexible_side_and_is_refused_on_a_fixed_one() -> None:
    flexible = Budget.flexible(long_limit=1, short_limit=-1)

    assert _sides(flexible.fill({"A": 2, "B": 1, "C": -1}, use="0.8")) == (
        Decimal("0.8"),
        Decimal("-0.8"),
    )
    in_full = re.escape("is filled in full, so use must be 1; got 0.5")
    with pytest.raises(BudgetRefusal, match=in_full):
        DEFAULT_BUDGET.fill({"A": 1, "B": -1}, use="0.5")
    for outside in (0, -1, "1.5"):
        with pytest.raises(BudgetRefusal, match="greater than 0 and at most 1"):
            flexible.fill({"A": 1}, use=outside)


def test_a_side_finer_than_the_grid_is_refused_rather_than_rounded_away() -> None:
    """It used to come back as a book of zeros with cash 1: a decision that says nothing."""
    with pytest.raises(BudgetRefusal, match="rounds below the canonical grid"):
        Budget.flexible(long_limit=1, short_limit=-1).fill({"A": 1}, use="1E-13")


def test_a_fixed_budget_refuses_a_signal_missing_a_side_it_must_fill() -> None:
    """A fixed side cannot be filled from nothing; the refusal says to Hold, or to declare
    flexible. A flexible budget fills the side the signal has and leaves the other empty."""
    with pytest.raises(BudgetRefusal) as refused:
        DEFAULT_BUDGET.fill({"A": 1, "B": 2})

    message = str(refused.value)
    assert "fills a short side of -1, but the signal has no negative name" in message
    assert "Return Hold" in message
    assert _sides(Budget.flexible(long_limit=1, short_limit=-1).fill({"A": 1, "B": 2})) == (
        Decimal(1),
        Decimal(0),
    )
    with pytest.raises(BudgetRefusal, match="non-empty mapping"):
        DEFAULT_BUDGET.fill({})


# ---------------------------------------------------------------------------------------------
# The spelling the identity folds
# ---------------------------------------------------------------------------------------------


def test_the_declaration_is_spelled_in_its_constructors_words() -> None:
    assert DEFAULT_BUDGET.encoded() == {"kind": "fixed", "long": "1", "short": "-1"}
    assert str(DEFAULT_BUDGET) == "Budget.fixed(long=1, short=-1)"

    flexible = Budget.flexible(long_limit="0.50", short_limit=0)
    assert flexible.encoded() == {"kind": "flexible", "long_limit": "0.5", "short_limit": "0"}
    assert str(flexible) == "Budget.flexible(long_limit=0.5, short_limit=0)"

    assert Budget.fixed(long=1.0, short=-1.0).encoded() == DEFAULT_BUDGET.encoded(), (
        "`1.0` and `1` are one declaration, so they must fold to one identity"
    )


def _layer(**budget: Budget) -> FrozenStrategy:
    """One strategy layer, built directly: nothing but the budget varies between calls."""
    event = ScheduledEvent(
        "alpha-1",
        LocalInstantDeclaration(date(2024, 1, 2), time(4, 0), "Asia/Seoul", 0, "+09:00"),
    )
    component = ComponentRef.of(
        "alpha", Role.STRATEGY_MODEL, Path("alpha.py"), "Alpha", fingerprint="0" * 64
    )
    return FrozenStrategy(
        config=StrategyConfig(component, "alpha"),
        compliance=ComplianceSet(()),
        schedule=FrozenSchedule("alpha", (event,)),
        **budget,
    )


def test_two_strategies_differing_only_in_their_budget_are_two_identities() -> None:
    """The report compares runs by what they declared, so the declaration is part of what a run
    IS: the same code under another budget is another strategy layer."""
    neutral = _layer(budget=DEFAULT_BUDGET)

    assert _layer().identity == neutral.identity, "an undeclared layer holds the default"
    assert _layer(budget=Budget.fixed(long=1.0, short=-1)).identity == neutral.identity
    assert _layer(budget=Budget.fixed(long=1, short=0)).identity != neutral.identity
    assert _layer(budget=Budget.flexible(long_limit=1, short_limit=-1)).identity != (
        neutral.identity
    ), "fixed and flexible with the same numbers are different declarations"
    with pytest.raises(TypeError, match="budget must be a Budget"):
        _layer(budget={"long": 1, "short": -1})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------------------------
# `Rebalance`: the weights alone
# ---------------------------------------------------------------------------------------------


def test_rebalance_is_the_weights_alone_and_cash_is_what_they_leave() -> None:
    """Cash is the net residual, never `1 - gross`: three books, three cashes."""
    assert vq.Rebalance({"A": 1, "B": -1}).cash_weight == Decimal(1)
    assert vq.Rebalance({"A": "0.6"}).cash_weight == Decimal("0.4")
    assert vq.Rebalance({"A": "0.5", "B": -2}).cash_weight == Decimal("2.5"), "shorting raises cash"

    exact = vq.Rebalance({"A": 1, "B": 0.1, "C": "0.2"}).target_weights
    assert dict(exact) == {"A": Decimal(1), "B": Decimal("0.1"), "C": Decimal("0.2")}
    assert not hasattr(vq.Rebalance, "of") and not hasattr(vq.Rebalance, "signed")


def test_the_retired_keywords_name_the_spelling_that_exists() -> None:
    with pytest.raises(TypeError) as refused:
        vq.Rebalance(target_weights={"A": 1}, cash_weight=0, budget=None)  # type: ignore[call-arg]

    message = str(refused.value)
    assert "got budget, cash_weight, target_weights" in message
    assert "Write Rebalance(weights)" in message
    assert "StrategyModel.budget()" in message
    with pytest.raises(TypeError, match=r"or Rebalance\(\{\}\) to empty the book"):
        vq.Rebalance()


def test_an_empty_rebalance_empties_the_book() -> None:
    """All cash. A flexible budget admits it; a fixed one does not, because a fixed side left
    empty is exactly what fixed forbids -- the design's consequence, not an accident."""
    empty = vq.Rebalance({})

    assert dict(empty.target_weights) == {}
    assert empty.cash_weight == Decimal(1)
    Budget.flexible(long_limit=1, short_limit=0).check(empty.target_weights)
    with pytest.raises(BudgetRefusal, match="the long side sums to 0, not 1"):
        DEFAULT_BUDGET.check(empty.target_weights)


# ---------------------------------------------------------------------------------------------
# The two doors that read `budget()`
# ---------------------------------------------------------------------------------------------

_DECLARING = """
from vqapr.public import Budget, Hold, StrategyModel


class Declaring(StrategyModel):
    def inputs(self):
        return {{}}

    def budget(self):
        {body}

    def decide(self, call):
        return Hold(reason="registration only")
"""


@pytest.mark.parametrize(
    ("label", "body", "observed"),
    [
        ("not a Budget", 'return {"long": 1, "short": -1}', "budget() returned dict"),
        (
            "a refused declaration",
            "return Budget.fixed(long=1, short=1)",
            "BudgetRefusal: short is written negative",
        ),
    ],
)
def test_registration_refuses_a_budget_it_cannot_read(
    label: str, body: str, observed: str, tmp_path: Path
) -> None:
    """`budget()` takes nothing from the run, so registration can call it -- and a strategy whose
    declaration cannot be read should not register only to fail at its first decision."""
    source = tmp_path / "declaring.py"
    source.write_text(_DECLARING.format(body=body), encoding="utf-8")

    with pytest.raises(VqaprError) as refused:
        vq.register_strategy_model(tmp_path, "declaring", source, "Declaring")

    (failure,) = refused.value.as_dict()["failures"]
    assert failure["code"] == "component.budget_invalid", label
    assert observed in (failure["observed"] or ""), failure
    assert "vq.Budget.flexible(long_limit=, short_limit=)" in failure["fix"]


_HALF_LONG = '''"""Buys one name with half of NAV and declares no budget: it is dollar neutral."""

from vqapr.public import DatasetInput, Rebalance, RowsLookback, StrategyModel


class HalfLong(StrategyModel):
    def inputs(self):
        return {
            "prices": DatasetInput(
                dataset_id="sample-prices", fields=("close",), lookback=RowsLookback(rows=1)
            )
        }

    def decide(self, call):
        window = call.read("prices", "close")
        return Rebalance({window.instruments[0]: "0.5"})
'''


def test_a_rebalance_that_breaks_the_declared_budget_fails_the_run(tmp_path: Path) -> None:
    """End to end, on the shipped sample: a strategy that forgot to declare its long-only budget
    is judged by the default one at its first decision, and the run fails with the sentence.

    Nothing is clipped to fit and nothing is topped up: the book the strategy wrote is not a book
    its declaration admits, so no fill happens and no record is left."""
    project = tmp_path / "project"
    project.mkdir()
    panel = journey.install(project)
    source = tmp_path / "half_long.py"
    source.write_text(_HALF_LONG, encoding="utf-8")
    vq.register_strategy_model(project, "half-long", source, "HalfLong")
    vq.register_run(
        project,
        journey.definition(panel, run_id="half-long").replace(
            strategy=vq.StrategyEntry("half-long"), writes="half-long-weights"
        ),
    )
    frozen = vq.freeze(project, vq.Workspace.open(project).run_definition("half-long"))
    assert frozen.strategy.budget == DEFAULT_BUDGET
    store = tmp_path / "store"

    outcome = vq.run(project, frozen, store_root=store)

    assert not outcome.ok
    failed = outcome.errors["half-long"]
    assert isinstance(failed, SimulationFailure)
    (entry,) = failed.as_dict()["failures"]
    # The author's contract failure, not the framework's crash: 422, pointing at their file.
    assert entry["code"] == "rebalance.outside_budget"
    assert entry["status"] == 422
    assert entry["source"]["key_path"] == "strategies.half-long"
    assert entry["cause"]["type"] == "BudgetRefusal"
    assert entry["observed"].startswith(
        "Budget.fixed(long=1, short=-1) refuses this book: the long side sums to 0.5, not 1; "
        "the short side sums to 0, not -1."
    ), entry["observed"]
    assert vq.strategy_refs(store, "half-long") == (), "the refused run left no record"
