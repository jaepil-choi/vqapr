"""A `vqapr new` kind that writes a .py and its declaration takes `--out` as the .py (record `283`).

The declaration lands beside the script as `<name>.yaml`. An `--out` ending in `.yaml` made the
two one path, and the declaration overwrote the script: `vqapr new instruments --out
instruments.yaml` left a declaration pointing at tables no script would ever export.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from test_commands import _cli


@pytest.mark.parametrize(
    "kind",
    [
        ("instruments", "--instruments", "A", "B"),
        ("exchange",),
        ("compliance", "position-cap"),
    ],
)
def test_an_out_that_is_not_a_py_is_refused_before_anything_is_written(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], kind: tuple[str, ...]
) -> None:
    out = tmp_path / "written.yaml"

    code, payload = _cli(capsys, "--project-root", str(tmp_path), "new", *kind, "--out", str(out))

    assert code == 1, payload
    (failure,) = payload["failures"]
    assert failure["status"] == 400
    assert "--out names the script" in failure["requirement"]
    assert failure["fix"] == "pass --out written.py, then retry"
    assert not list(tmp_path.glob("written.*")), "nothing may be written"


def test_the_named_ids_reach_the_roster_script(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "roster.py"

    code, payload = _cli(
        capsys, "--project-root", str(tmp_path), "new", "instruments", "--instruments", "A", "B",
        "--out", str(out),
    )

    assert code == 0, payload
    assert Path(payload["declaration"]) == tmp_path / "roster.yaml"
    script = out.read_text(encoding="utf-8")
    assert "'A': 'stock'" in script and "'B': 'stock'" in script
    assert "stock: roster_stock.parquet" in (tmp_path / "roster.yaml").read_text(encoding="utf-8")
