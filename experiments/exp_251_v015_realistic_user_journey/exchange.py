"""Zero-friction signed venue for the frozen research universe."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from vqapr.public import AcademicExchange, ListingAccess, TradeRule


class ResearchExchange(AcademicExchange):
    def __init__(self, instruments: Sequence[str]) -> None:
        super().__init__(
            {
                str(name): TradeRule(
                    instrument_id=str(name),
                    quantity_step=Decimal("1"),
                    minimum_quantity=Decimal("1"),
                    fractional_allowed=False,
                    access=ListingAccess.SIGNED,
                )
                for name in instruments
            },
            exchange_id="research",
        )
