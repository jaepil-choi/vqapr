"""A batch says how long it took, and how much of that was the bake (testbed report
`docs/issues/report-2026-09-15-batch-envelope-has-no-batch-elapsed-and-timing-total-is-undocumented.md`).

Each strategy's `timing.total` is its own event loop. A 516 s batch whose longest run reported
362.5 s left about 150 s in no record -- process start, the panels baked before the workers,
record writing -- and nothing said what `total` covered. The batch envelope now carries its own
wall clock (`elapsed`) and, under `--jobs`, the part spent baking before any worker started.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.cli.test_a_datamodel_run_through_the_cli import _declaration
from tests.cli.test_commands import _cli


def _registered(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> tuple[str, str]:
    project = ("--project-root", str(tmp_path))
    code, registered = _cli(capsys, *project, "register", str(_declaration(tmp_path)))
    assert code == 0, registered
    return project


def test_a_pooled_batch_states_its_wall_clock_and_its_bake(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = _registered(tmp_path, capsys)
    code, ran = _cli(capsys, *project, "run", "factors-reversal", "factors-momentum", "--jobs", "2")
    assert code == 0, ran
    assert isinstance(ran["elapsed"], float) and ran["elapsed"] > 0
    assert isinstance(ran["bake"], float) and 0 <= ran["bake"] <= ran["elapsed"]


def test_a_sequential_batch_states_its_wall_clock_and_bakes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = _registered(tmp_path, capsys)
    code, ran = _cli(capsys, *project, "run", "factors-reversal", "factors-momentum")
    assert code == 0, ran
    assert isinstance(ran["elapsed"], float) and ran["elapsed"] > 0
    assert "bake" not in ran, "only a pool bakes shared panels before its workers"


def test_one_run_keeps_the_envelope_it_always_had(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = _registered(tmp_path, capsys)
    code, ran = _cli(capsys, *project, "run", "factors-reversal")
    assert code == 0, ran
    assert "elapsed" not in ran and "bake" not in ran
