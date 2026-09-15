"""The door: a report from a record on disk.

`strategy_report` opens one strategy's record and its four tables through `vqapr.record`
(the same reader `vqapr show strategy --table` uses) and hands the rows to `measure`.
`run_report` does that for every strategy of a run and adds what only the run can answer: the
headline table, the correlation of period returns, and each strategy against a benchmark
strategy of the same run.

`root` is the store -- the `store_root` `vqapr run` prints, `<project>/.vqapr` unless moved --
not the project directory, exactly as for `read_strategy_table`.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from vqapr.record import (
    read_run_record,
    read_strategy_record,
    read_table,
    record_address,
    resolve_strategy_ref,
    strategy_refs,
)
from vqapr.record.schema import ACCOUNT_TABLE, FILL_TABLE, MONITORING_TABLE, WEIGHT_TABLE
from vqapr.report import measure
from vqapr.report.document import BudgetUse, Compliance, RunReport, StrategyReport

__all__ = ["run_report", "strategy_report", "valuation_grid"]


def strategy_report(
    root: Path | str,
    run_id: str,
    strategy_ref: str | None = None,
    *,
    periods_per_year: int | None = None,
    risk_free_annual: Decimal = Decimal(0),
) -> StrategyReport:
    """One strategy's report from its record.

    `strategy_ref` resolves the way `read_strategy_table`'s does: `<strategy-id>@<fp8>`, the bare
    `<strategy-id>` when one record of it exists, or `None` when the run holds one strategy.
    `periods_per_year` defaults to what the valuation grid implies (`infer_periods_per_year`)
    and the report says which. `risk_free_annual` is a simple annual rate the record does not
    hold; zero unless given. `root` may be a `str`, and `run_id` may carry the ref the way the
    CLI writes it, `<run-id>/<strategy-id>@<fp8>` (`record_address`).
    """
    root, run_id, strategy_ref = record_address(root, run_id, strategy_ref)
    resolved = resolve_strategy_ref(root, run_id, strategy_ref)
    if resolved is None:
        raise ValueError(
            f"run {run_id!r} records tables of its own and no strategy; a report needs a "
            "strategy record"
        )
    record = read_strategy_record(root, run_id, resolved)
    grid, initial_nav = _opening_grid(root, run_id, resolved)
    if not grid:
        raise ValueError(f"{run_id!r}/{resolved!r} recorded no valuation; nothing to report")
    fill_rows = list(read_table(root, run_id, FILL_TABLE, resolved))
    placed = measure.fills(fill_rows)
    intended = measure.decisions(read_table(root, run_id, WEIGHT_TABLE, resolved))
    monitoring_rows = list(read_table(root, run_id, MONITORING_TABLE, resolved))

    # Positions are recorded unless the run was told not to (`--no-account-positions`). A book
    # with no position row and nothing ever dealt is simply empty; one with fills dealt and no
    # position row was recorded without them, and the sections that need them say so.
    dealt_anything = any(fill.dealt != 0 for fill in placed)
    positions_recorded = any(valuation.positions for valuation in grid) or not dealt_anything

    if periods_per_year is None:
        periods_per_year = measure.infer_periods_per_year([valuation.at for valuation in grid])
        source = "inferred"
    else:
        source = "given"

    # One door for every omission: a section's builder raises `SectionUndefined` with its reason,
    # and the section is `None` with that reason in `omitted`. A number undefined in one section
    # -- a return off a NAV that is not positive -- used to raise out of here and take all six
    # sections with it (testbed report 2026-09-15).
    omitted: dict[str, str] = {}

    def section[T](name: str, build: Callable[[], T]) -> T | None:
        try:
            return build()
        except measure.SectionUndefined as undefined:
            omitted[name] = str(undefined)
            return None

    unrecorded = (
        None
        if positions_recorded
        else (
            f"{ACCOUNT_TABLE} holds only the {measure.ACCOUNT_ROW} row (the run was recorded "
            "without positions), so the book cannot be read back"
        )
    )

    def from_positions[T](build: Callable[[], T]) -> Callable[[], T]:
        def built() -> T:
            if unrecorded is not None:
                raise measure.SectionUndefined(unrecorded)
            return build()

        return built

    def monitored() -> Compliance:
        if not monitoring_rows:
            raise measure.SectionUndefined(
                f"{MONITORING_TABLE} is empty: the run declared no compliance rule"
                if not record.get("compliance")
                else f"{MONITORING_TABLE} is empty although compliance rules were declared"
            )
        return measure.compliance(monitoring_rows)

    performance = section(
        "performance",
        lambda: measure.performance(
            grid,
            periods_per_year=periods_per_year,
            periods_per_year_source=source,
            risk_free_annual=risk_free_annual,
            initial_nav=initial_nav,
        ),
    )
    book = section("book", from_positions(lambda: measure.book(grid)))

    def budget_use() -> BudgetUse:
        # Use is measured against the declaration the run froze (record `292`): a share of the
        # book, against its returns. A record written before 0.17.0 has none -- the budget rode on
        # each decision and was dropped -- and a book or returns omitted above leave nothing to
        # measure use with.
        declared = record.get("budget")
        if not declared:
            raise measure.SectionUndefined(
                "the record states no budget: it was written before 0.17.0, when the budget "
                "rode on each decision and was not recorded"
            )
        if book is None or performance is None:
            raise measure.SectionUndefined(
                omitted.get("performance") or omitted.get("book") or "no book or no returns"
            )
        return measure.budget_use(book, performance, declared)

    budget = section("budget", from_positions(budget_use))
    attribution = section("attribution", from_positions(lambda: measure.attribution(grid, placed)))
    intent = section("intent", from_positions(lambda: measure.intent(grid, intended)))
    # `trading` is money and counts and always stands; its shares of NAV say `None` themselves.
    trading = measure.trading(
        grid,
        placed,
        fill_rows,
        intended,
        periods_per_year=periods_per_year,
        positions_recorded=positions_recorded,
    )
    if unrecorded is not None:
        omitted["trading.holding"] = unrecorded
    compliance = section("compliance", monitored)
    return StrategyReport(
        run_id=run_id,
        strategy_ref=resolved,
        strategy_id=str(record["strategy_id"]),
        period=dict(record.get("period") or {}),
        positions_recorded=positions_recorded,
        omitted=omitted,
        performance=performance,
        book=book,
        budget=budget,
        attribution=attribution,
        trading=trading,
        intent=intent,
        compliance=compliance,
    )


def run_report(
    root: Path | str,
    run_id: str,
    *,
    benchmark: str | None = None,
    periods_per_year: int | None = None,
    risk_free_annual: Decimal = Decimal(0),
) -> RunReport:
    """Every finished strategy of a run, side by side.

    `benchmark` names a strategy of the same run (a ref or a bare id); every other strategy is
    then also reported against it. A benchmark outside the run -- an index level, say -- is not
    something the record holds, and is not invented here. A strategy whose `performance` was
    omitted keeps its `headline` row with the return columns empty and is left out of
    `correlation` and `relative`; its own `omitted` says why.
    """
    root, run_id, named = record_address(root, run_id)
    if named is not None:
        raise ValueError(
            f"run_report reports every strategy of run {run_id!r}, and {named!r} names one; use "
            "strategy_report for that strategy, or benchmark= to measure the others against it"
        )
    refs = strategy_refs(root, run_id)
    if not refs:
        raise ValueError(f"run {run_id!r} has no finished strategy record under {root}")
    reports = {
        ref: strategy_report(
            root, run_id, ref, periods_per_year=periods_per_year, risk_free_annual=risk_free_annual
        )
        for ref in refs
    }
    ordered = list(reports.values())
    relative = []
    if benchmark is not None:
        resolved = resolve_strategy_ref(root, run_id, benchmark)
        if resolved not in reports:
            raise ValueError(
                f"benchmark {benchmark!r} is not a finished strategy of {run_id!r}; "
                f"finished: {', '.join(refs)}"
            )
        base = reports[resolved]
        against = (measure.relative(report, base) for report in ordered if report is not base)
        relative = [entry for entry in against if entry is not None]
    return RunReport(
        run_id=run_id,
        strategies=reports,
        headline=[measure.headline(report) for report in ordered],
        correlation=measure.correlation(ordered),
        relative=relative,
    )


def valuation_grid(
    root: Path | str, run_id: str, strategy_ref: str | None = None
) -> list[measure.Valuation]:
    """The valuation grid a strategy's report is computed on, in time order.

    One point per `vqapr.account` valuation -- its `_ACCOUNT` row's cash and NAV and the names
    held -- with the run's initial account in front when the first valuation already reflects a
    fill. `vqapr export` writes `nav.csv` and `holdings.csv` from this, so the files and the
    report's `performance.nav` are one series, not two computed alike (record `266`).
    """
    root, run_id, strategy_ref = record_address(root, run_id, strategy_ref)
    resolved = resolve_strategy_ref(root, run_id, strategy_ref)
    if resolved is None:
        raise ValueError(f"run {run_id!r} records tables of its own and no strategy")
    grid, _ = _opening_grid(root, run_id, resolved)
    return grid


def _opening_grid(
    root: Path, run_id: str, resolved: str
) -> tuple[list[measure.Valuation], Decimal | None]:
    """The grid and the initial NAV it opens from, when the run began with cash only."""
    run = read_run_record(root, run_id)
    initial = run.get("initial_account") or {}
    initial_nav = (
        Decimal(str(initial["cash"]))
        if initial.get("cash") is not None and not initial.get("positions")
        else None
    )
    grid = measure.opening(
        measure.valuations(read_table(root, run_id, ACCOUNT_TABLE, resolved)),
        initial_cash=initial_nav,
        period_start=_instant((run.get("period") or {}).get("start")),
    )
    return grid, initial_nav


def _instant(value: object) -> datetime | None:
    return datetime.fromisoformat(value) if isinstance(value, str) else None
