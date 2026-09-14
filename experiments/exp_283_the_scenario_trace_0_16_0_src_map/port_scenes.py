# ruff: noqa: E501, RUF001, RUF003 -- the usage line is one command; the scenes write counts with ×
"""Port a scenes file onto new traces and a moved tree: frame indices, every `name(#idx, ms)`.

    uv run python experiments/exp_283_the_scenario_trace_0_16_0_src_map/port_scenes.py OLD_SCENES.py TRACES_DIR OUT.py

The 0.16.0 concept tree moved files and renamed the door, so the 0.14.3 scenes point at call
indices, names and source anchors that no longer exist. What this does, mechanically:

- a frame `F("trace", idx, ...)` is re-found in the new trace by its function name (the name the
  frame's own prose gives that index, renamed through `RENAMES`), nearest by index -- the traces
  are the same commands on the same data, so the order of calls barely moves;
- every `<code>name</code>(#idx[, ms ms]` in the frame's prose gets the new index and the new
  milliseconds, and the displayed name follows the new qualname where its class changed;
- every `at("src/...", needle)` anchor is re-found by searching the needle in `src/vqapr/`.

What a frame *says* is not touched beyond identifiers: the prose is rewritten by hand after this.
Anything it could not place is printed and left as it was.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RENAMES = {
    "verify_run": "preflight",
    "preflight_run": "freeze",
    "RunFacts.agenda": "RunFacts.schedule",
    "derived_agenda": "derived_schedule",
    "_freeze_agenda": "_freeze_schedule",
}
# A needle found in more than one file: the file the old anchor's module became.
PREFERRED = {
    "inclusive_slice(": ["src/vqapr/run/preflight/checks.py"],
    "def require_verified": ["src/vqapr/data/verification.py"],
}
OLD_DECL ="experiments/exp_235_the_scenario_trace/declarations/"
NEW_DECL = "experiments/exp_283_the_scenario_trace_0_16_0_src_map/declarations/"

frame_re = re.compile(r'F\("(\w+)", (\d+), ')
mention_re = re.compile(
    r"<code>([\w.]+)((?:\(\))?)</code>((?:\s*×\d+)?\s*)\(#(\d+)(?:, ([\d,]+(?:\.\d+)?) ms)?"
)
at_re = re.compile(r"""at\("(src/[^"]+)", (?:"((?:[^"\\]|\\.)*)"|'([^']*)')""")


def renamed(name: str) -> str:
    if name in RENAMES:
        return RENAMES[name]
    head, _, last = name.rpartition(".")
    if last in RENAMES:
        return f"{head}.{RENAMES[last]}" if head else RENAMES[last]
    return name


def fmt_ms(ms: float) -> str:
    if ms >= 100:
        return f"{ms:,.1f}"
    if ms >= 1:
        return f"{ms:.1f}"
    if ms >= 0.01:
        return f"{ms:.2f}"
    return f"{ms:.3f}"


class Port:
    def __init__(self, traces: dict[str, dict]) -> None:
        self.traces = traces
        self.problems: list[str] = []

    def lookup(self, trace: str, name: str, old: int):
        calls = self.traces[trace]["calls"]
        name = renamed(name)
        last = name.split(".")[-1]
        # The tightest tier that has any call wins: the same qualname, then a qualname ending in
        # the name, then the same last segment (a class that was renamed around its method).
        pool = (
            [c for c in calls if c["qualname"] == name]
            or [c for c in calls if c["qualname"].endswith("." + name)]
            or [c for c in calls if c["qualname"].split(".")[-1] == last]
        )
        if not pool:
            return None
        return min(pool, key=lambda c: abs(c["idx"] - old))

    def display(self, old_name: str, qualname: str) -> str:
        new = renamed(old_name)
        parts, old_parts = qualname.split("."), new.split(".")
        if (
            len(parts) >= 2
            and len(old_parts) >= 2
            and "<locals>" not in parts[-2]
            and parts[-2] != old_parts[-2]
            and parts[-2][:1].isupper()
        ):
            return f"{parts[-2]}.{parts[-1]}"
        return new

    def frame_name(self, body: str, idx: int) -> str | None:
        for m in mention_re.finditer(body):
            if int(m.group(4)) == idx:
                return m.group(1)
        fn = re.search(r'fn="([^"(]+)', body)
        return fn.group(1).strip() if fn else None

    def port_body(self, trace: str, body: str) -> str:
        def one(m: re.Match) -> str:
            name, parens, gap, old, ms = m.groups()
            hit = self.lookup(trace, name, int(old))
            if hit is None:
                self.problems.append(f"{trace}: no call for <code>{name}</code>(#{old}")
                return m.group(0)
            shown = self.display(name, hit["qualname"])
            out = f"<code>{shown}{parens}</code>{gap}(#{hit['idx']}"
            if ms is not None:
                out += f", {fmt_ms(hit['ms'])} ms" if hit["ms"] is not None else ", ? ms"
            return out

        return mention_re.sub(one, body)

    def port_frames(self, text: str) -> str:
        frames = list(frame_re.finditer(text))
        out, cursor = [], 0
        for i, fm in enumerate(frames):
            trace, idx = fm.group(1), int(fm.group(2))
            end = frames[i + 1].start() if i + 1 < len(frames) else _frames_end(text)
            body = text[fm.end():end]
            name = self.frame_name(body, idx)
            hit = self.lookup(trace, name, idx) if name else None
            new_idx = hit["idx"] if hit else idx
            if hit is None:
                self.problems.append(f"FRAME {trace}#{idx} ({name}): not placed")
            out.append(text[cursor:fm.start()])
            out.append(f'F("{trace}", {new_idx}, ')
            out.append(self.port_body(trace, body))
            cursor = end
        out.append(text[cursor:])
        return "".join(out)


def _frames_end(text: str) -> int:
    return text.index("\nTABLE = ")


def port_anchors(text: str, problems: list[str]) -> str:
    sources = {
        str(p.relative_to(REPO)).replace("\\", "/"): p.read_text(encoding="utf-8")
        for p in (REPO / "src" / "vqapr").rglob("*.py")
    }

    def one(m: re.Match) -> str:
        path, needle = m.group(1), m.group(2) if m.group(2) is not None else m.group(3)
        plain = needle.encode().decode("unicode_escape") if "\\" in needle else needle
        for old, new in RENAMES.items():
            plain = plain.replace(old, new)
        homes = [file for file, body in sources.items() if plain in body]
        if len(homes) > 1 and path in homes:
            homes = [path]
        homes = [file for file in homes if file in PREFERRED.get(plain, homes)]
        if len(homes) == 1:
            return f'at("{homes[0]}", {json.dumps(plain, ensure_ascii=False)}'
        problems.append(f"anchor {path} :: {plain!r} -> {homes or 'nowhere'}")
        return m.group(0)

    return at_re.sub(one, text)


def main(old: Path, traces_dir: Path, out: Path) -> None:
    traces = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in traces_dir.glob("*.json")}
    text = old.read_text(encoding="utf-8")
    port = Port(traces)
    text = port.port_frames(text)
    text = port_anchors(text, port.problems)
    text = text.replace(f'DECL = "{OLD_DECL}"', f'DECL = "{NEW_DECL}"')
    text = text.replace('"return va.Hold("', '"return vq.Hold("')
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    for line in port.problems:
        print("  ! " + line)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: port_scenes.py OLD_SCENES.py TRACES_DIR OUT.py")
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
