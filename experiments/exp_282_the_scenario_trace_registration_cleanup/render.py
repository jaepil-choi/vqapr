# ruff: noqa: E501 -- the CSS and the JS anchors below are one line each on purpose
"""Render the stepper for f862c147: exp_280's renderer, plus a command badge on every frame.

    uv run python experiments/exp_282_the_scenario_trace_registration_cleanup/render.py \
        experiments/exp_282_the_scenario_trace_registration_cleanup/scenes.py TRACES_DIR OUT.html

exp_280's `render_0_16_0.py` does the work unchanged. This module points it at this directory's
src/ map and plain-words lines, and adds one thing: each frame shows which of the sixteen commands
it was traced from (`02 · vqapr register bad.yaml`), read from the trace's own argv.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "exp_280_the_scenario_trace_0_16_0"))
import render_0_16_0 as page  # noqa: E402 - exp_280's renderer, reused whole

page.SRC_MAP = HERE / "src_map.json"
_namespace: dict = {"__file__": str(HERE / "explain.py")}
exec((HERE / "explain.py").read_text(encoding="utf-8"), _namespace)
page._EXPLAIN.update(_namespace["EXPLAIN"])

_resolve = page.base.resolve_frame
_traces: dict[str, dict] = {}


def resolve_frame(spec: dict, traces: dict[str, dict]) -> dict:
    frame = _resolve(spec, traces)
    frame["cmd"] = f"{spec['trace'][:2]} · {page.command_words(traces[spec['trace']])}"
    return frame


page.base.resolve_frame = resolve_frame

BADGE_CSS = """
/* the command a frame was traced from */
.cmdb{display:block;width:fit-content;max-width:100%;margin:0 0 8px;padding:2px 10px;border:1px solid var(--accent);border-radius:999px;background:var(--accent-bg);color:var(--accent);font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;font-size:12px;word-break:break-all}
"""
ANCHOR = "$('frame').innerHTML = `"


def render(scenes: Path, traces_dir: Path, out: Path) -> None:
    page.render(scenes, traces_dir, out)
    text = out.read_text(encoding="utf-8")
    for old in (ANCHOR, "</style>"):
        if text.count(old) != 1:
            raise ValueError(f"expected one {old!r}, found {text.count(old)}")
    text = text.replace(
        ANCHOR, ANCHOR + "${fr.cmd?`<div class=\"cmdb\">${esc(fr.cmd)}</div>`:''}", 1
    )
    text = text.replace("</style>", BADGE_CSS + "</style>", 1)
    out.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: render.py SCENES.py TRACES_DIR OUT.html")
    render(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
