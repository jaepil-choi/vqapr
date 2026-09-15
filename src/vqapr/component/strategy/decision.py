"""What a strategy returns: `Hold` or `Rebalance`.

`Hold` is no decision: the book and any intent already pending stay as they are. `Rebalance` names
one complete desired portfolio -- a signed weight per name, cash being whatever they leave -- which
is the decision the framework exists to take; to empty the book is `Rebalance({})`, not a `Hold`.

How large each side may be is not the decision's to say. The strategy declares it once, in
`StrategyModel.budget()`, and the run checks every `Rebalance` against that frozen declaration
(record `291`). A budget carried on each decision let a strategy change its own limits on any day,
and `Rebalance.of` / `Rebalance.signed` each stated a size (`invested`, `gross`) that could disagree
with it; both constructors are gone, and `budget().fill(signal)` does their arithmetic.

Both values are strict and frozen, so a wrong shape is refused at the boundary the author can see.
"""

from __future__ import annotations

import numbers
from collections.abc import Mapping
from decimal import Decimal

from pydantic import BaseModel, field_validator

from vqapr.component._validation import _VALUE_CONFIG, _copy_weights
from vqapr.data.panel import CrossSection

__all__ = [
    "Hold",
    "Rebalance",
    "_as_decimal",
]


class Hold(BaseModel):
    """A Strategy decision that intentionally emits no order.

    **This is the engine's decline type as well as the author's.** It absorbed
    `models.strategy_model.NoDecision` in record `125`: the two were the same frozen one-field
    dataclass with two names, and the adapter's whole contribution was `NoDecision(hold.reason)`.

    `reason` is prose, not an identifier. It was validated with `_identifier` here, which rejects
    whitespace -- so `Hold(reason="no name scored above zero")` was refused while the engine's
    `NoDecision` accepted the identical string. Merging two types means merging two validations,
    and the looser one is the correct one: a reason a human reads should be allowed spaces.
    """

    model_config = _VALUE_CONFIG

    reason: str

    @field_validator("reason")
    @classmethod
    def _prose(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reason must be a non-empty string")
        return value


def _as_decimal(value: object, *, name: str) -> Decimal:
    """One weight as an exact Decimal.

    `Decimal(str(v))` for a float rather than `Decimal(v)`: a float64 `0.1` is not one tenth, and
    binding the binary expansion here would put the error into every weight downstream. Any real
    number is taken this way, so a numpy scalar out of a signal is a weight too.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool) or not isinstance(value, numbers.Real | str):
        raise TypeError(f"{name} must be a Decimal, int, float, or string")
    try:
        return Decimal(str(value))
    except ArithmeticError as invalid:
        raise ValueError(f"{name} must be a finite number; got {value!r}") from invalid


class Rebalance(BaseModel):
    """A Strategy decision naming one complete desired portfolio: a signed weight per name.

    `Rebalance(self.budget().fill(signal))` is the usual way in: the declared budget sizes each
    side exactly, on the canonical grid. `Rebalance(weights)` takes weights built any other way --
    an `optimize` result, a hand-written book -- and the run checks them against the same budget.

    A negative weight is a short. A zero holds none of the name, so the next fill sells whatever is
    held of it (record `260`). Cash is not stated: it is `1 - sum(weights)`, the net residual, so a
    dollar-neutral book's cash is 1 and a short-only book holds more than its NAV in cash.

    `target_weights` is held as the read-only `CrossSection` it validates into.
    """

    model_config = _VALUE_CONFIG

    target_weights: CrossSection[Decimal]

    def __init__(
        self,
        weights: Mapping[str, Decimal | int | float | str] | None = None,
        /,
        **retired: object,
    ) -> None:
        # The old keywords get a sentence rather than Python's "unexpected keyword": an author
        # (or an agent) reaching for the pre-0.17 spelling is told the road that exists.
        if retired:
            raise TypeError(
                "Rebalance takes the weights alone since 0.17.0; got "
                f"{', '.join(sorted(retired))}. Write Rebalance(weights): cash is "
                "1 - sum(weights), and the budget is declared once by StrategyModel.budget()"
            )
        if weights is None:
            raise TypeError(
                "Rebalance needs the weights: Rebalance(self.budget().fill(signal)), or "
                "Rebalance({}) to empty the book"
            )
        super().__init__(target_weights=weights)

    @field_validator("target_weights", mode="before")
    @classmethod
    def _weights(cls, value: object) -> CrossSection[Decimal]:
        if not isinstance(value, Mapping):
            raise TypeError(
                "Rebalance takes a mapping of instrument to signed weight; got "
                f"{type(value).__name__}"
            )
        exact = {name: _as_decimal(raw, name=f"weights[{name!r}]") for name, raw in value.items()}
        return _copy_weights(exact, name="target_weights")

    @property
    def cash_weight(self) -> Decimal:
        """What the weights leave: `1 - sum(weights)`, the net residual."""
        return Decimal(1) - sum(self.target_weights.values(), Decimal(0))
