"""A borrowing account holds more than its NAV long (records 288-289).

The owner's case (2026-09-15): on the academic venue, a book that buys 200% of NAV. The strategy's
budget is the limit -- `Rebalance.signed({...}, gross=2)` declares cash at -1 -- and the account
declared `initial_account.cash_mode: BORROWING` lets the fills take cash below zero. The same run
on a funded account is cut to its cash, and a funded run keeps the stored spelling, the record and
the identity it had before `cash_mode` existed: FUNDED is never written.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

SESSIONS = tuple(date(2024, 3, 4) + timedelta(days=offset) for offset in range(3))
PRICES = {"A005930": 100, "A000660": 50}

STRATEGIES = textwrap.dedent(
    '''
    from decimal import Decimal

    from vqapr.public import (
        AcademicExchange, DatasetInput, Hold, ListingAccess, Rebalance, RowsLookback,
        StrategyModel, TradeRule,
    )


    class TwiceLong(StrategyModel):
        """Buys 100% of NAV in each of two names once, then holds: 200% long, cash at -1."""

        def inputs(self):
            return {
                "prices": DatasetInput(
                    dataset_id="price_daily", fields=("close",), lookback=RowsLookback(rows=1)
                ),
            }

        def decide(self, call):
            state = self.memory if isinstance(self.memory, dict) else {}
            if state.get("formed") or not call.read("prices", "close").latest():
                return Hold(reason="formed")
            self.memory = {"formed": True}
            return Rebalance.signed({"A005930": 1, "A000660": 1}, gross=2)


    class LeverageExchange(AcademicExchange):
        """Whole shares, no cost, long-only listings: the leverage is cash, not a short."""

        def __init__(self):
            super().__init__(
                {
                    name: TradeRule(name, Decimal(1), Decimal(1), False, ListingAccess.LONG_ONLY)
                    for name in ("A005930", "A000660")
                },
                "leverage-academic",
            )
    '''
)

RUNNER = textwrap.dedent(
    '''
    import dataclasses
    import json
    import sys
    from datetime import date, datetime, time
    from decimal import Decimal
    from pathlib import Path
    from zoneinfo import ZoneInfo

    from vqapr.public import (
        AccountMode, AccountSnapshot, CashMode, DatasetRegistration, RunDefinition, RunExecution,
        RunFill, RunSchedule, SourceSpec, StrategyEntry, freeze, register_dataset,
        register_exchange, register_instruments, register_strategy_model, run,
    )
    from vqapr.run.recording import freeze_run_record

    import authored_strategies

    KST = ZoneInfo("Asia/Seoul")
    root, exec_path, price_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    sessions = tuple(date.fromisoformat(day) for day in sys.argv[4].split(","))

    register_dataset(
        root,
        DatasetRegistration.of(
            "price_daily", "leverage-observation",
            instrument_field="instrument", available_at="available_at",
            grain="instrument_instant", key_fields=("available_at", "instrument"),
            fields={"close": "close"}, field_types={"close": "DOUBLE"},
        ),
        SourceSpec.of("leverage-observation", price_path),
    )
    register_dataset(
        root,
        DatasetRegistration.of(
            "krx-daily", "leverage-execution",
            instrument_field="instrument", available_at="trade_at",
            grain="instrument_instant", key_fields=("trade_at", "instrument"),
            fields={"close": "close", "is_tradable": "is_tradable"},
            field_types={"close": "DOUBLE", "is_tradable": "BOOLEAN"},
            execution={"is_tradable": "is_tradable"},
        ),
        SourceSpec.of("leverage-execution", exec_path),
    )
    source = Path(authored_strategies.__file__).resolve()
    register_strategy_model(root, "leverage-strategy", source, "TwiceLong")
    register_exchange(root, "leverage-exchange", source, "LeverageExchange")
    register_instruments(root, {"A005930": "stock", "A000660": "stock"})

    for cash_mode in (CashMode.FUNDED, CashMode.BORROWING):
        run_id = f"leverage-{cash_mode.value}"
        definition = RunDefinition(
            run_id=run_id,
            strategy=StrategyEntry("leverage-strategy"),
            instruments=("A005930", "A000660"),
            timezone="Asia/Seoul",
            schedule=RunSchedule(every="1d", at=(time(8, 0),)),
            exchange="leverage-exchange",
            execution=RunExecution(
                dataset="krx-daily", trade_price="close", fill=RunFill(at=time(15, 30))
            ),
            start=datetime.combine(sessions[0], time(0, 0), tzinfo=KST),
            end=datetime.combine(sessions[-1], time(23, 0), tzinfo=KST),
            initial_account_snapshot=AccountSnapshot(0, Decimal("1000000"), {}),
            initial_account_mode=AccountMode.LONG_ONLY,
            initial_account_cash_mode=cash_mode,
            writes=f"{run_id}-weights",
        )
        stored = definition.model_dump(mode="json")
        reread = RunDefinition.model_validate({"run_id": run_id, **stored})
        frozen = freeze(root, definition)
        funded_twin = dataclasses.replace(frozen, initial_account_cash_mode=CashMode.FUNDED)
        snapshot = run(root, frozen).result().final_state.account.snapshot
        print("RESULT|" + json.dumps({
            "cash_mode": cash_mode.value,
            "cash": str(snapshot.cash),
            "positions": {name: str(quantity) for name, quantity in snapshot.positions.items()},
            "stored": stored["initial_account"],
            "reread": reread.initial_account_cash_mode.value,
            # `run` without a store writes no record; `run.json` is written by the one function
            # the CLI's run calls, so its block is read back from what that function wrote.
            "record": json.loads(
                freeze_run_record(root.parent / "records", frozen, source_digests={}).read_text(
                    encoding="utf-8"
                )
            )["initial_account"],
            "identity_moved": funded_twin.identity != frozen.identity,
        }, default=str))
    '''
)


@pytest.fixture(scope="module")
def leverage_runs(tmp_path_factory) -> dict[str, dict]:
    """The same 200%-long decision, run once on a funded account and once on a borrowing one."""
    tmp_path = tmp_path_factory.mktemp("leverage")
    (tmp_path / "authored_strategies.py").write_text(STRATEGIES, encoding="utf-8")
    (tmp_path / "runner.py").write_text(RUNNER, encoding="utf-8")

    execution = tmp_path / "exec.parquet"
    prices = tmp_path / "prices.parquet"
    executed = ",\n".join(
        f"('{name}', TIMESTAMPTZ '{session.isoformat()} 15:30:00+09', TRUE, {price}.0)"
        for session in SESSIONS
        for name, price in PRICES.items()
    )
    observed = ",\n".join(
        f"('{name}', TIMESTAMPTZ '{session.isoformat()} 07:00:00+09', {price}.0)"
        for session in SESSIONS
        for name, price in PRICES.items()
    )
    connection = duckdb.connect()
    connection.execute(
        f"""COPY (SELECT instrument, trade_at, is_tradable, CAST(close AS DOUBLE) AS close
        FROM (VALUES {executed}) AS t(instrument, trade_at, is_tradable, close))
        TO '{execution.as_posix()}' (FORMAT PARQUET)"""
    )
    connection.execute(
        f"""COPY (SELECT instrument, available_at, CAST(close AS DOUBLE) AS close
        FROM (VALUES {observed}) AS t(instrument, available_at, close))
        TO '{prices.as_posix()}' (FORMAT PARQUET)"""
    )
    connection.close()

    root = tmp_path / "project"
    root.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(tmp_path / "runner.py"),
            str(root),
            str(execution),
            str(prices),
            ",".join(session.isoformat() for session in SESSIONS),
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    runs = {}
    for line in result.stdout.splitlines():
        if line.startswith("RESULT|"):
            body = json.loads(line.removeprefix("RESULT|"))
            runs[body["cash_mode"]] = body
    assert set(runs) == {"funded", "borrowing"}, result.stdout
    return runs


def test_a_borrowing_account_buys_twice_its_nav(leverage_runs) -> None:
    """One NAV borrowed: 10,000 x 100 plus 20,000 x 50 bought with 1,000,000 of cash."""
    borrowing = leverage_runs["borrowing"]

    assert Decimal(borrowing["cash"]) == Decimal("-1000000")
    assert {name: Decimal(quantity) for name, quantity in borrowing["positions"].items()} == {
        "A005930": Decimal("10000"),
        "A000660": Decimal("20000"),
    }


def test_the_same_decision_on_a_funded_account_is_cut_to_its_cash(leverage_runs) -> None:
    funded = leverage_runs["funded"]

    assert Decimal(funded["cash"]) >= 0
    bought = sum(
        (Decimal(quantity) * PRICES[name] for name, quantity in funded["positions"].items()),
        Decimal(0),
    )
    assert Decimal("999000") <= bought <= Decimal("1000000"), "cut to the cash, not below it"


def test_funded_is_never_written_and_borrowing_is_said_everywhere(leverage_runs) -> None:
    """A funded run stores, records and identifies exactly as before `cash_mode` existed."""
    funded, borrowing = leverage_runs["funded"], leverage_runs["borrowing"]

    assert "cash_mode" not in funded["stored"]
    assert "cash_mode" not in funded["record"]
    assert not funded["identity_moved"]
    assert funded["reread"] == "funded"

    assert borrowing["stored"]["cash_mode"] == "BORROWING", "written by NAME, like `mode`"
    assert borrowing["record"]["cash_mode"] == "borrowing"
    assert borrowing["identity_moved"], "a borrowing run is a different run"
    assert borrowing["reread"] == "borrowing"
