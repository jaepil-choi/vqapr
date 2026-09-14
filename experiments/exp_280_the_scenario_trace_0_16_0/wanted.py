"""Which calls the page shows: run the scenes against the traces and note every call they touch.

    uv run python experiments/exp_280_the_scenario_trace_0_16_0/wanted.py TRACES_DIR WANT.json

The scenes read a call through `TRACES[trace]["calls"][idx]` (a frame, a chain step, a quoted
millisecond). Executing them against traces whose `calls` lists record each index read gives the
exact set; WANT.json maps each trace name to the qualnames at those indices, which is what
`trace_io.py` records inputs and outputs for.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from render_0_16_0 import load_scenes, load_traces  # noqa: E402

touched: dict[str, set[int]] = {}


class Calls(list):
    def __init__(self, name: str, items: list) -> None:
        super().__init__(items)
        self.name = name

    def __getitem__(self, index):  # type: ignore[override]
        if isinstance(index, int):
            touched.setdefault(self.name, set()).add(index)
        return super().__getitem__(index)


if __name__ == "__main__":
    traces = load_traces(Path(sys.argv[1]))
    for name, trace in traces.items():
        trace["calls"] = Calls(name, trace["calls"])
    spec = load_scenes(HERE / "scenes_0_16_0.py", traces)
    for scene in spec["SCENES"]:
        for frame in scene["frames"]:
            touched.setdefault(frame["trace"], set()).add(frame["idx"])
    wanted = {
        name: sorted({list.__getitem__(traces[name]["calls"], i)["qualname"] for i in indices})
        for name, indices in sorted(touched.items())
    }
    Path(sys.argv[2]).write_text(json.dumps(wanted, ensure_ascii=False, indent=1), encoding="utf-8")
    print({name: len(q) for name, q in wanted.items()})
