"""A declaration says what an edit replaced, as the three-argument form does (testbed report
`docs/issues/report-2026-09-15-yaml-re-register-of-a-changed-strategy-omits-the-replaced-fingerprint.md`).

`vqapr register <kind> <id> <file.py>` answered `replaced: {fingerprint: <old>}`, and
`vqapr register <declaration.yaml>` replaced the same component without a word. Both routes stage
the component through one merge, and the merge is the one place that knows what the id held
before, so both now answer from it: the three-argument form as before, a declaration per
component id.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from vqapr.cli.main import main


def _cli(capsys: pytest.CaptureFixture[str], root: Path, *argv: str) -> tuple[int, dict]:
    code = main(["--project-root", str(root), *argv])
    out = capsys.readouterr().out.strip()
    return code, json.loads(out.splitlines()[-1])


def _fingerprint(capsys: pytest.CaptureFixture[str], root: Path, component_id: str) -> str:
    code, listed = _cli(capsys, root, "list", "components")
    assert code == 0, listed
    return {row["component_id"]: row["fingerprint"] for row in listed["items"]}[component_id]


def _rule_and_its_declaration(
    capsys: pytest.CaptureFixture[str], root: Path
) -> tuple[Path, Path]:
    code, cap = _cli(capsys, root, "new", "compliance", "cap20")
    assert code == 0, cap
    path = Path(cap["path"])
    found = re.search(r"^class (\w+)\(", path.read_text(encoding="utf-8"), re.MULTILINE)
    assert found is not None, "the scaffold defines one class"
    declaration = path.parent / "rules.yaml"
    declaration.write_text(
        "components:\n"
        "  cap20:\n"
        "    kind: compliance\n"
        f"    path: {path.name}\n"
        f"    object_name: {found.group(1)}\n",
        encoding="utf-8",
    )
    return path, declaration


def _edit(path: Path, note: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + f"\n# {note}\n", encoding="utf-8")


def test_a_declaration_names_the_fingerprint_an_edit_replaced(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path, declaration = _rule_and_its_declaration(capsys, tmp_path)

    code, first = _cli(capsys, tmp_path, "register", str(declaration))
    assert code == 0 and "replaced" not in first, first
    before = _fingerprint(capsys, tmp_path, "cap20")

    code, same = _cli(capsys, tmp_path, "register", str(declaration))
    assert code == 0 and "replaced" not in same, "unchanged bytes replace nothing"

    _edit(path, "edited")
    code, edited = _cli(capsys, tmp_path, "register", str(declaration))
    assert code == 0, edited
    assert edited["replaced"] == {"cap20": {"fingerprint": before}}
    assert _fingerprint(capsys, tmp_path, "cap20") != before


def test_either_route_names_what_the_other_left(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One merge answers both routes, so it does not matter which one registered the id first."""
    path, declaration = _rule_and_its_declaration(capsys, tmp_path)
    code, first = _cli(capsys, tmp_path, "register", str(declaration))
    assert code == 0, first
    declared = _fingerprint(capsys, tmp_path, "cap20")

    _edit(path, "edited by hand")
    code, direct = _cli(capsys, tmp_path, "register", "compliance", "cap20", str(path))
    assert code == 0, direct
    assert direct["replaced"] == {"fingerprint": declared}
    direct_fingerprint = _fingerprint(capsys, tmp_path, "cap20")

    _edit(path, "edited again")
    code, again = _cli(capsys, tmp_path, "register", str(declaration))
    assert code == 0, again
    assert again["replaced"] == {"cap20": {"fingerprint": direct_fingerprint}}
