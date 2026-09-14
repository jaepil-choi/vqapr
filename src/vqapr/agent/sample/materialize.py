"""Write the sample journey into a directory the user owns.

Copies the strategy and the exchange as source files the user can read and edit, the synthetic
panel beside them, and two declaration documents: `instruments.yaml`, the roster -- what each of
the ten names IS -- and `sample.yaml`, which registers the dataset, the execution dataset, both
components and the run. They are two because the data and the instruments a venue may trade are
separate declarations (owner, 2026-09-14; record `284`): a dataset may carry names no strategy
trades, and only the roster's names can be ordered. Nothing is registered here: the next steps are
`vqapr register DIR/instruments.yaml` and `vqapr register DIR/sample.yaml`, the same verb every
user declaration takes, so the sample shows the real path rather than a shortcut through it.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import date
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from vqapr.domain.instrument import export_roster

VENUE = "Asia/Seoul"
OFFSET = "+09:00"
CALLBACK = "08:00"
"""The decision is made before the session opens, reading only closes already published."""
CLOSE = "15:30"
"""The fill happens at the close, after the decision, never at the same instant."""

DATASET_ID = "sample-prices"
EXECUTION_ID = "sample-execution"
STRATEGY_ID = "sample-reversal-5d"
EXCHANGE_ID = "sample-exchange"
RUN_ID = "sample-run"
OPENING_CASH = "100000000"
"""The book starts in cash, so the first rebalance is a plain set of purchases."""

DECLARATION = "sample.yaml"
ROSTER_DECLARATION = "instruments.yaml"
COMPONENT_FILES = ("reversal_5d.py", "exchange.py")
DATA_FILES = ("observations.parquet", "execution.parquet", "instruments.csv", "panel.json")

_HEADER = "# Written by `vqapr new sample`. Register with: vqapr register <this file>\n"


@dataclass(frozen=True, slots=True)
class Materialized:
    """Where the sample now lives, and what it declares."""

    directory: Path
    declaration: Path
    roster: Path
    run_id: str
    strategy_id: str
    exchange_id: str
    dataset_id: str
    panel: dict[str, Any]

    @property
    def instruments(self) -> tuple[str, ...]:
        return tuple(self.panel["instruments"])

    @property
    def late_listed(self) -> str:
        return str(self.panel["late_listed"])

    @property
    def delisted(self) -> str:
        return str(self.panel["delisted"])

    @property
    def session_count(self) -> int:
        return int(self.panel["sessions"])

    @property
    def observations(self) -> Path:
        return self.directory / "observations.parquet"

    @property
    def execution(self) -> Path:
        return self.directory / "execution.parquet"


def _package_file(name: str, *, data: bool = False) -> Path:
    anchor = "vqapr.agent.sample.data" if data else "vqapr.agent.sample"
    with resources.as_file(resources.files(anchor).joinpath(name)) as path:
        return Path(path)


def panel_metadata() -> dict[str, Any]:
    """`panel.json` as shipped: instruments, the late lister, the delisted name, the counts."""
    return json.loads(_package_file("panel.json", data=True).read_text(encoding="utf-8"))


def _iso(session: str, wall: str) -> str:
    day = date(int(session[:4]), int(session[4:6]), int(session[6:8]))
    return f"{day.isoformat()}T{wall}{OFFSET}"


def _next_session(sessions: int, observations_path: Path) -> str:
    """The second session of the panel, read from the data rather than assumed.

    The run's horizon opens on the second session (record `167`): the first close is published
    at 15:30, after the 08:00 decision, so a run that opened on the first session would ask its
    first decision to read history the dataset did not yet have, and `vqapr check` refuses that.
    """
    import pyarrow.parquet as pq

    stamps = pq.read_table(observations_path, columns=["available_at"]).column(0).to_pylist()
    days = sorted({stamp.astimezone(_zone()).date() for stamp in stamps})
    if len(days) != sessions:
        raise ValueError(f"panel.json says {sessions} sessions, the parquet has {len(days)}")
    return days[1].strftime("%Y%m%d")


def _zone():
    from zoneinfo import ZoneInfo

    return ZoneInfo(VENUE)


def roster_declaration(roster_tables: dict[str, str]) -> dict[str, Any]:
    """The `instruments.yaml` body: `{kind: file name}` for the roster `materialize` exported.

    Its own document (record `284`). A strategy run needs the project to have declared what each
    name IS before it can size or charge an order (design §6.2), so `vqapr check` refuses the
    sample's run until this is registered -- and the data registers without it.
    """
    return {"instruments": {"tables": roster_tables}}


def declaration(panel: dict[str, Any], second_session: str) -> dict[str, Any]:
    """The `sample.yaml` body: the datasets, the components and the run, paths relative to it."""
    return {
        "datasets": {
            DATASET_ID: {
                "source_id": f"{DATASET_ID}-source",
                "path": "observations.parquet",
                "instrument_field": "instrument",
                "available_at": "available_at",
                "grain": "instrument_instant",
                "key_fields": ["available_at", "instrument"],
                "fields": {name: name for name in ("open", "high", "low", "close", "volume")},
                # What each field IS (`docs/issues/archive/088`): prices are DOUBLE, the count is
                # INTEGER.
                "field_types": {
                    "open": "DOUBLE",
                    "high": "DOUBLE",
                    "low": "DOUBLE",
                    "close": "DOUBLE",
                    "volume": "INTEGER",
                },
            },
            # The venue table is a dataset too (record `185`): `trade_at` is the instant its
            # row is a fact about, and the execution role names the tradable flag. Which price
            # a run fills at is the run's choice, below.
            EXECUTION_ID: {
                "source_id": f"{EXECUTION_ID}-source",
                "path": "execution.parquet",
                "instrument_field": "instrument",
                "available_at": "trade_at",
                "grain": "instrument_instant",
                "key_fields": ["trade_at", "instrument"],
                "fields": {"close": "close", "is_tradable": "is_tradable"},
                "field_types": {"close": "DOUBLE", "is_tradable": "BOOLEAN"},
                "execution": {"is_tradable": "is_tradable"},
            },
        },
        "components": {
            STRATEGY_ID: {
                "kind": "strategy",
                "path": "reversal_5d.py",
                "object_name": "SampleReversal5d",
            },
            EXCHANGE_ID: {
                "kind": "exchange",
                "path": "exchange.py",
                "object_name": "SampleExchange",
                "config": {"instruments": list(panel["instruments"])},
            },
        },
        "runs": {
            RUN_ID: {
                "instruments": list(panel["instruments"]),
                "start": _iso(second_session, "00:00:00"),
                "end": _iso(panel["last_session"], "23:59:59"),
                "timezone": VENUE,
                # The schedule clock (design §3.4): decided once a day at CALLBACK, on every
                # day the execution table has rows for.
                "schedule": {"every": "1d", "at": CALLBACK},
                "exchange": EXCHANGE_ID,
                "execution": {
                    "dataset": EXECUTION_ID,
                    "trade_price": "close",
                    # The first execution instant after the 08:00 decision is that day's close;
                    # `at` says so explicitly (design §3.5).
                    "fill": {"at": CLOSE},
                },
                "initial_account": {"cash": OPENING_CASH, "mode": "LONG_ONLY", "positions": {}},
                "writes": f"{STRATEGY_ID}-weights",
                "strategy": {"component": STRATEGY_ID},
            }
        },
    }


_README = """\
# The vqapr sample journey

Everything here was written by `vqapr new sample`. The data is **synthetic** (see the note at the
end); the strategy and the venue are yours to read and change.

| file | what it is |
|---|---|
| `reversal_5d.py` | a five-day reversal `StrategyModel`: buys the weakest recent performers |
| `exchange.py` | a zero-friction academic venue listing exactly the sample's ten names |
| `observations.parquet` | daily OHLCV, one row per (close, instrument) |
| `execution.parquet` | the venue table a run fills against |
| `instruments.csv`, `panel.json` | the names and the panel's shape |
| `instruments_stock.parquet` | the roster table: what each of the ten names IS (all shares) |
| `instruments.yaml` | the roster declaration: the names a strategy may order |
| `sample.yaml` | registers the data, the strategy, the venue and the run `{run_id}` |

Four commands, from the directory that holds `.vqapr/` (or that will):

```bash
vqapr register {directory}/instruments.yaml
vqapr register {directory}/sample.yaml
vqapr check {run_id}
vqapr run {run_id}
```

The roster is its own declaration: a dataset may carry names no strategy trades, and only the
names in the roster can be ordered. Register `sample.yaml` alone and `vqapr check {run_id}` refuses
the run (`roster.absent`) until `instruments.yaml` is registered too.

Then `vqapr show run {run_id}` and `vqapr show strategy {run_id}` read the record back.

The panel is deliberately unbalanced: `{late_listed}` lists 200 sessions late and `{delisted}`
stops 250 sessions early, so the strategy meets a name with too little history and a name that
disappears from under a position -- the two things a balanced sample would let you assume away.

**The data is not market data.** It was cut from real KRX sessions and then transformed: codes
and names replaced, prices rescaled and jittered, volumes scaled. Use it to learn the shape of a
run, not to draw a conclusion about a market.
"""


def materialize(directory: str | Path) -> Materialized:
    """Write the sample into `directory`, which must not exist yet or must be empty."""
    target = Path(directory)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"{target} exists and is not empty")
    target.mkdir(parents=True, exist_ok=True)
    for name in COMPONENT_FILES:
        shutil.copyfile(_package_file(name), target / name)
    for name in DATA_FILES:
        shutil.copyfile(_package_file(name, data=True), target / name)
    panel = panel_metadata()
    second = _next_session(int(panel["sessions"]), target / "observations.parquet")
    # The ten names are synthetic shares. Exported here rather than shipped, so the parquet is
    # written by the same exporter `vqapr new instruments` uses and never drifts from it.
    roster = export_roster({name: "stock" for name in panel["instruments"]}, target)
    tables = {kind: path.name for kind, path in sorted(roster.items())}
    for name, body in (
        (ROSTER_DECLARATION, roster_declaration(tables)),
        (DECLARATION, declaration(panel, second)),
    ):
        (target / name).write_text(
            _HEADER + yaml.safe_dump(body, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    (target / "README.md").write_text(
        _README.format(
            run_id=RUN_ID,
            directory=target.name,
            late_listed=panel["late_listed"],
            delisted=panel["delisted"],
        ),
        encoding="utf-8",
    )
    return Materialized(
        directory=target,
        declaration=target / DECLARATION,
        roster=target / ROSTER_DECLARATION,
        run_id=RUN_ID,
        strategy_id=STRATEGY_ID,
        exchange_id=EXCHANGE_ID,
        dataset_id=DATASET_ID,
        panel=panel,
    )
