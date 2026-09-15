"""Which vqapr wrote a record (testbed report 2026-09-15, `docs/issues/`
`report-2026-09-15-no-record-or-public-surface-names-the-vqapr-version-that-wrote-a-run.md`).

The package is part of the code that produced a number, and nothing named it: no
`vqapr.__version__`, `vqapr --version` was a usage refusal, and no record field said which
version wrote it. The version is a receipt, not part of a run's identity (owner, 2026-09-15, as
for a data digest), so the same strategy file run again after an upgrade is still the same record
-- and the refusal of that second run now names the version that wrote the standing one.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

import pytest

import vqapr
from tests.cli.test_commands import _cli, _workspace_for_run
from vqapr.cli.envelope import failure
from vqapr.cli.run import _standing_record
from vqapr.domain.errors import Stage
from vqapr.record import record_directory
from vqapr.record.writer import RunRecordExists

VERSION = metadata.version("vqapr")


def test_the_package_and_the_cli_name_the_installed_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert vqapr.__version__ == VERSION
    code, said = _cli(capsys, "--version")
    assert code == 0, said
    assert said["ok"] is True and said["package_version"] == VERSION


def test_a_strategy_record_names_the_version_and_the_refusal_to_rewrite_it_repeats_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _workspace_for_run(tmp_path, capsys)
    code, ran = _cli(capsys, "--project-root", str(tmp_path), "run", "r1")
    assert code == 0, ran

    code, shown = _cli(capsys, "--project-root", str(tmp_path), "show", "strategy", "r1/my-alpha")
    assert code == 0, shown
    assert shown["package_version"] == VERSION

    # A second `vqapr run r1` is refused sooner, by the dataset the first published
    # (`run.output_registered`); the standing record's own refusal is asked of directly.
    directory = record_directory(tmp_path / ".vqapr", "r1", shown["strategy_ref"])
    standing = RunRecordExists("r1", directory)
    assert standing.written_by == VERSION
    rendered = failure(_standing_record(standing, object(), "r1"), stage=Stage.RECORD)
    refused = rendered["failures"][0]
    assert refused["code"] == "record.exists"
    assert f"written by vqapr {VERSION}" in refused["observed"]


def test_a_record_written_before_the_field_existed_says_nothing(tmp_path: Path) -> None:
    directory = tmp_path / "old"
    directory.mkdir()
    (directory / "strategy.json").write_text('{"run_id": "r1"}', encoding="utf-8")
    standing = RunRecordExists("r1", directory)
    assert standing.written_by is None
    rendered = failure(_standing_record(standing, object(), "r1"), stage=Stage.RECORD)
    assert "written by" not in rendered["failures"][0]["observed"]
