"""The strategy's budget: how large each side of the book is, declared once for the run.

Design `docs/design/strategy-budget.md` (record `291`). A budget used to ride on every `Rebalance`,
so a strategy could widen its own limits on any day and the run record never learned what they
were. It is a declaration now -- `StrategyModel.budget()` -- frozen with the run, checked against
every decision, and written to the record so the report has a denominator.

Two shapes, and the parameter names say which relation holds:

    Budget.fixed(long=1, short=-1)                 the long side sums to exactly 1, the short to -1
    Budget.flexible(long_limit=1, short_limit=-1)  the long side is 0 to 1, the short side -1 to 0

The short side is written negative, the same as `rescale`. A side of zero is a side the book does
not have: `short=0` is long-only. Cash is not declared -- it is `1 - net`, whatever the weights
leave.

`check` judges a book; `fill` makes one. Filling is `rescale` on the canonical grid with the
declared sides as targets, so a fixed budget is met to the last digit and a strategy never
normalises by hand. The rule `weights.py` states still holds: sizing never decides the budget.
Here the declaration decides it, in the strategy's own source.
"""

from __future__ import annotations

import numbers
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from vqapr.portfolio.optimize import QUANTIZATION_EXPONENT, QUANTUM, finite_exponent
from vqapr.portfolio.weights import Weights, rescale

__all__ = ["DEFAULT_BUDGET", "Budget", "BudgetRefusal"]


class BudgetRefusal(ValueError):
    """A declaration, a signal or a book the budget cannot accept, with the numbers that failed."""


_SHOWN = 5
"""How many offending names a refusal quotes; the rest are counted."""


def _shown(names: Iterable[str]) -> str:
    ordered = sorted(names)
    shown = ", ".join(ordered[:_SHOWN])
    rest = len(ordered) - _SHOWN
    return shown + (f", and {rest} more" if rest > 0 else "")


def _number(value: object, *, name: str) -> Decimal:
    """One author-written number as an exact Decimal; a float through `str`, never its binary."""
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, bool) or not isinstance(value, numbers.Real | str):
        raise BudgetRefusal(f"{name} must be a number; got {type(value).__name__}")
    else:
        try:
            number = Decimal(str(value))
        except ArithmeticError as invalid:
            raise BudgetRefusal(f"{name} must be a number; got {value!r}") from invalid
    if not number.is_finite():
        raise BudgetRefusal(f"{name} must be finite; got {number}")
    return number


def _spelled(value: Decimal) -> str:
    """`1`, `0.5`, `-1`: one spelling per value, so `1.0` and `1` fold to the same identity."""
    text = format(value.normalize(), "f")
    return "0" if text in ("-0", "0") else text


def _sides(weights: Mapping[str, Decimal]) -> tuple[Decimal, Decimal]:
    long = sum((value for value in weights.values() if value > 0), Decimal(0))
    short = sum((value for value in weights.values() if value < 0), Decimal(0))
    return long, short


@dataclass(frozen=True, slots=True)
class Budget:
    """How large each side of the book is: exactly (`fixed`) or at most (`flexible`).

    Build it with `Budget.fixed(long=, short=)` or `Budget.flexible(long_limit=, short_limit=)`.
    `long` and `short` hold the declared values either way; `kind` says which relation they carry.
    """

    kind: Literal["fixed", "flexible"]
    long: Decimal
    short: Decimal

    def __post_init__(self) -> None:
        if self.kind not in ("fixed", "flexible"):
            raise BudgetRefusal(f"kind must be 'fixed' or 'flexible'; got {self.kind!r}")
        long_name, short_name = self._names()
        for name, value in ((long_name, self.long), (short_name, self.short)):
            if not isinstance(value, Decimal) or not value.is_finite():
                raise BudgetRefusal(f"{name} must be a finite Decimal; got {value!r}")
            if finite_exponent(value) < QUANTIZATION_EXPONENT:
                raise BudgetRefusal(
                    f"{name} {value} is finer than the canonical grid {QUANTUM}; weights on that "
                    "grid cannot sum to it"
                )
        if self.long < 0:
            raise BudgetRefusal(
                f"{long_name} is the size of the long side and cannot be negative; got {self.long}"
            )
        if self.short > 0:
            raise BudgetRefusal(
                f"{short_name} is written negative, the way a short weight is "
                f"({short_name}=-1); got {self.short}"
            )
        if self.long == 0 and self.short == 0:
            raise BudgetRefusal(
                f"{self} has no side at all, so it can hold nothing; declare the side the book has"
            )

    @classmethod
    def fixed(cls, *, long: object, short: object) -> Budget:
        """Each side sums to exactly its value: `fixed(long=1, short=-1)` is dollar neutral,
        `fixed(long=0.5, short=-0.5)` has the gross of a fully invested long-only book, and
        `fixed(long=1, short=0)` is that long-only book."""
        return cls("fixed", _number(long, name="long"), _number(short, name="short"))

    @classmethod
    def flexible(cls, *, long_limit: object, short_limit: object) -> Budget:
        """Each side may go as far as its limit and no further: the long side from 0 to
        `long_limit`, the short side from `short_limit` to 0. Using less is allowed; how much was
        used is what the report measures."""
        return cls(
            "flexible",
            _number(long_limit, name="long_limit"),
            _number(short_limit, name="short_limit"),
        )

    def _names(self) -> tuple[str, str]:
        return ("long", "short") if self.kind == "fixed" else ("long_limit", "short_limit")

    @property
    def long_only(self) -> bool:
        """No short side: every weight must be zero or positive."""
        return self.short == 0

    def encoded(self) -> dict[str, str]:
        """The declaration in its constructor's own spelling -- what the identity folds and the
        record states."""
        long_name, short_name = self._names()
        return {
            "kind": self.kind,
            long_name: _spelled(self.long),
            short_name: _spelled(self.short),
        }

    def __str__(self) -> str:
        long_name, short_name = self._names()
        return (
            f"Budget.{self.kind}({long_name}={_spelled(self.long)}, "
            f"{short_name}={_spelled(self.short)})"
        )

    def check(self, weights: Mapping[str, Decimal]) -> None:
        """Refuse a book this budget does not admit, naming each side's sum and the declaration.

        Nothing is clipped and nothing is topped up: a book the declaration does not admit is the
        strategy's to fix, and fixing it here would run a book nobody wrote.
        """
        if self.long_only:
            negative = [name for name, value in weights.items() if value < 0]
            if negative:
                raise BudgetRefusal(
                    f"{self} is long-only, but the book is short {_shown(negative)}. Drop those "
                    "names, or declare a short side in budget()"
                )
        if self.long == 0:
            positive = [name for name, value in weights.items() if value > 0]
            if positive:
                raise BudgetRefusal(
                    f"{self} has no long side, but the book is long {_shown(positive)}. Drop "
                    "those names, or declare a long side in budget()"
                )
        long, short = _sides(weights)
        problems: list[str] = []
        if self.kind == "fixed":
            if long != self.long:
                problems.append(f"the long side sums to {long}, not {_spelled(self.long)}")
            if short != self.short:
                problems.append(f"the short side sums to {short}, not {_spelled(self.short)}")
            fix = (
                "Size the book with self.budget().fill(signal), which lands each side exactly; "
                "or declare Budget.flexible if a side may be smaller"
            )
        else:
            if long > self.long:
                problems.append(
                    f"the long side sums to {long}, above its limit {_spelled(self.long)}"
                )
            if short < self.short:
                problems.append(
                    f"the short side sums to {short}, below its limit {_spelled(self.short)}"
                )
            fix = "Scale the book down, for example with self.budget().fill(signal, use=...)"
        if problems:
            raise BudgetRefusal(f"{self} refuses this book: {'; '.join(problems)}. {fix}")

    def fill(self, signal: Mapping[str, object], *, use: object = 1) -> Weights:
        """Size a signed signal to this budget: each side scaled to its declared value.

        The signal's numbers are relative conviction within a side -- `{"A": 2, "B": 1, "C": -1}`
        under `fixed(long=1, short=-1)` is A 2/3, B 1/3, C -1 -- and a zero keeps the name at
        zero. Every weight lands on the canonical grid and each side on its target exactly, the
        rounding crumb settled on that side's largest name (`rescale`).

        `use` takes that fraction of each side, `0 < use <= 1`, and only a flexible budget
        accepts anything but 1: a fixed budget is filled in full, which is what fixed means.
        """
        if not isinstance(signal, Mapping) or not signal:
            raise BudgetRefusal("signal must be a non-empty mapping of instrument to signed score")
        scores: dict[str, Decimal] = {}
        for name, raw in signal.items():
            if not isinstance(name, str) or not name:
                raise BudgetRefusal(f"signal has a non-string instrument identifier: {name!r}")
            scores[name] = _number(raw, name=f"signal[{name!r}]")
        share = _number(use, name="use")
        if not 0 < share <= 1:
            raise BudgetRefusal(
                f"use is the fraction of each side to fill, greater than 0 and at most 1; "
                f"got {share}"
            )
        if self.kind == "fixed" and share != 1:
            raise BudgetRefusal(
                f"{self} is filled in full, so use must be 1; got {share}. A budget a strategy "
                "may use part of is Budget.flexible"
            )
        longs = [name for name, value in scores.items() if value > 0]
        shorts = [name for name, value in scores.items() if value < 0]
        if longs and self.long == 0:
            raise BudgetRefusal(
                f"{self} has no long side, but the signal is positive for {_shown(longs)}. "
                "Drop those names, or declare a long side in budget()"
            )
        if shorts and self.short == 0:
            raise BudgetRefusal(
                f"{self} is long-only, but the signal is negative for {_shown(shorts)}. Drop "
                "those names, or declare a short side in budget()"
            )
        if self.kind == "fixed":
            for side, names, size in (("long", longs, self.long), ("short", shorts, self.short)):
                if size != 0 and not names:
                    sign = "positive" if side == "long" else "negative"
                    raise BudgetRefusal(
                        f"{self} fills a {side} side of {_spelled(size)}, but the signal has no "
                        f"{sign} name. Return Hold for this event, or declare Budget.flexible "
                        "if a side may be empty"
                    )
        long_target = (self.long * share).quantize(QUANTUM) if longs else Decimal(0)
        short_target = (self.short * share).quantize(QUANTUM) if shorts else Decimal(0)
        for side, names, target in (("long", longs, long_target), ("short", shorts, short_target)):
            if names and target == 0:
                raise BudgetRefusal(
                    f"use {share} of the {side} side rounds below the canonical grid {QUANTUM}; "
                    "ask for at least one grid step"
                )
        return rescale(
            dict(sorted(scores.items())), long=long_target, short=short_target, grid=QUANTUM
        )


DEFAULT_BUDGET = Budget.fixed(long=1, short=-1)
"""What `StrategyModel.budget()` declares unless overridden: dollar neutral, each side in full."""
