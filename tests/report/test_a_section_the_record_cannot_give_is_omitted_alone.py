"""A section the record cannot give is `None` with its reason, and the others are still computed
(testbed report 2026-09-15, `docs/issues/` `report-2026-09-15-strategy-report-raises-bare-...`).

A signed book short one name that more than doubles: the NAV goes 100, 100, 10, -40, -10. A return
or a share of NAV off a NAV that is not positive is undefined, so `performance`, `book` and `intent`
are omitted with one reason naming where and how low. `attribution` is money and is computed, to
the last digit. `trading` keeps its money and counts and leaves the turnover of the period that
opens below zero as `None`. `strategy_report` used to raise a bare `ValueError` and lose all six.

Worked by hand: short 1 A at 60 from cash 100, so cash is 160; A is then marked 150, 200, 170.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from vqapr.cli.main import main
from vqapr.public import run_report, strategy_report
from vqapr.record import (
    RUN_KIND,
    STRATEGY_KIND,
    RunRecordWriter,
    record_fields,
    write_run_record,
)

SEOUL = timezone(timedelta(hours=9))
T0 = datetime(2024, 1, 1, 0, 0, tzinfo=SEOUL)
T1 = datetime(2024, 1, 2, 15, 30, tzinfo=SEOUL)
T2 = datetime(2024, 1, 3, 15, 30, tzinfo=SEOUL)
T3 = datetime(2024, 1, 4, 15, 30, tzinfo=SEOUL)
T4 = datetime(2024, 1, 5, 15, 30, tzinfo=SEOUL)
RUN = "r"
SHORT = "short@00000001"
CASH = "cash@00000002"


def _head(at: datetime, version: int, cash: str, nav: str) -> dict[str, object]:
    return {
        "event_time": at,
        "observed_at": at,
        "instrument": "_ACCOUNT",
        "account_version": version,
        "cash": Decimal(cash),
        "nav": Decimal(nav),
        "quantity": None,
        "price": None,
    }


def _held(at: datetime, price: str) -> dict[str, object]:
    return {
        "event_time": at,
        "observed_at": at,
        "instrument": "A",
        "account_version": 1,
        "cash": None,
        "nav": None,
        "quantity": Decimal(-1),
        "price": Decimal(price),
    }


def _strategy_record(strategy_ref: str) -> dict[str, object]:
    values: dict[str, object] = dict.fromkeys(record_fields(STRATEGY_KIND))
    values.update(
        {
            "run_id": RUN,
            "writes": f"{RUN}-weights",
            "strategy_ref": strategy_ref,
            "strategy_id": strategy_ref.split("@")[0],
            "fingerprint": strategy_ref.split("@")[1] * 8,
            "component": {"component_id": strategy_ref.split("@")[0]},
            "schedule": {},
            "compliance": [],
            "account": {},
            "tables": {},
            "contract": {},
            "source_digest": {},
            "declared_digest": "d",
            "roster": None,
            "period": {"start": T0.isoformat(), "end": T4.isoformat(), "events": 4},
            "timing": {},
        }
    )
    return values


@pytest.fixture
def store(tmp_path: Path) -> Path:
    root = tmp_path / ".vqapr"
    run: dict[str, object] = dict.fromkeys(record_fields(RUN_KIND))
    run.update(
        {
            "declared_digest": "d",
            "instruments": ["A"],
            "period": {"start": T0.isoformat(), "end": T4.isoformat()},
            "initial_account": {"cash": "100", "mode": "signed", "positions": {}, "version": 0},
            "datasets": [],
            "strategies": [
                {"component_id": "short", "record": SHORT},
                {"component_id": "cash", "record": CASH},
            ],
            "datamodels": [],
        }
    )
    write_run_record(root, RUN, run)

    short = RunRecordWriter(root, RUN, SHORT)
    short.open()
    short.append(
        "vqapr.weight", [{"event_time": T1.replace(hour=8), "instrument": "A", "weight": "-0.6"}]
    )
    short.append(
        "vqapr.fill",
        [
            {
                "event_time": T1,
                "instrument": "A",
                "kind": "stock",
                "account_version": 1,
                "requested_quantity": "-1",
                "dealt_quantity": "-1",
                "price": "60",
                "cash_delta": "60",
                "commission": "0",
                "tax": "0",
                "reason": None,
            }
        ],
    )
    marks = ((T1, "60", "100"), (T2, "150", "10"), (T3, "200", "-40"), (T4, "170", "-10"))
    for at, price, nav in marks:
        short.append("vqapr.account", [_head(at, 1, "160", nav), _held(at, price)])
    short.finish(_strategy_record(SHORT), kind=STRATEGY_KIND)
    short.release()

    cash = RunRecordWriter(root, RUN, CASH)
    cash.open()
    for at, nav in ((T0, "100"), (T1, "100"), (T2, "101"), (T3, "100"), (T4, "102")):
        cash.append("vqapr.account", [_head(at, 0, nav, nav)])
    cash.finish(_strategy_record(CASH), kind=STRATEGY_KIND)
    cash.release()
    return root


def test_the_nav_shares_are_omitted_with_one_reason_and_the_money_is_not(store: Path) -> None:
    report = strategy_report(store, RUN, SHORT)

    assert report.performance is None and report.book is None and report.intent is None
    reason = report.omitted["performance"]
    assert report.omitted["book"] == reason and report.omitted["intent"] == reason
    assert "not positive" in reason
    assert "2 of 5" in reason, "T3 and T4, of T0 (the initial account) to T4"
    assert T3.isoformat() in reason and "-40" in reason

    attribution = report.attribution
    assert attribution is not None
    assert attribution.total == [Decimal(0), Decimal(-90), Decimal(-50), Decimal(30)]
    assert attribution.residual == [Decimal(0)] * 4
    assert attribution.total_pnl == Decimal(-110) == Decimal(-10) - Decimal(100)

    trading = report.trading
    assert trading.realized_turnover.values == [Decimal("0.3"), Decimal(0), Decimal(0), None]
    assert trading.annualized_realized_turnover is None
    assert trading.costs.traded_notional == Decimal(60)
    assert trading.costs.share_of_mean_nav_per_year is None
    assert trading.holding is not None

    report.as_record()  # the whole document still serialises: `vqapr export` writes it


def test_a_run_report_lines_up_the_strategies_that_have_returns(store: Path) -> None:
    ran = run_report(store, RUN, benchmark="cash")

    rows = {row.strategy_ref: row for row in ran.headline}
    assert rows[SHORT].total_return is None and rows[SHORT].sharpe is None
    assert rows[SHORT].annualized_realized_turnover is None
    assert rows[CASH].total_return == Decimal("0.02")
    assert ran.correlation is None, "one strategy has returns; a correlation needs two"
    assert ran.relative == [], "the short book has no returns to set against the benchmark"


def test_export_writes_the_report_and_its_omissions_travel_inside_it(
    store: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "exported"
    code = main(["--project-root", str(store.parent), "export", f"{RUN}/short", "--out", str(out)])
    exported = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert code == 0, exported
    assert exported["omitted"] == {}, "report.json is written; the sections say what they omit"
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["performance"] is None and "not positive" in report["omitted"]["performance"]
    assert report["attribution"]["total_pnl"] == "-110"
