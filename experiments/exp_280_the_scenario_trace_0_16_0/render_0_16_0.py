# ruff: noqa: E501 -- the CSS, JS and HTML templates below are one line each on purpose
"""Render the 0.16.0 scenario stepper: `exp_230/render.py`, plus three things that page did not have.

    uv run python experiments/exp_280_the_scenario_trace_0_16_0/render_0_16_0.py \
        experiments/exp_280_the_scenario_trace_0_16_0/scenes_0_16_0.py TRACES_DIR OUT.html

What `exp_230/render.py` does is unchanged and reused: a frame names a trace and a call index, and
the renderer fills in the definition line, the qualified name, the milliseconds and the code window.
What this adds:

- **the shelf** -- under each scene's story, what the scene's commands left on disk. Computed from
  the traces' own `files_after` (the project's file list after each command) and from the write
  calls the trace recorded (`Workspace._write`, `Workspace._write_roster`), never typed by hand;
- **the chronicle** -- the same, for all sixteen commands in one table, above the map;
- **the file card and the src/ map** -- the 2026-09-12 page's description of every file under
  `src/vqapr/`, carried as data in `src_map.json` and checked against the traced tree (every path
  exists; every line count matches `26726b1f`), rendered as a card under each frame and a
  searchable map at the end.

The scenes module is executed with `REPO` and `TRACES` bound, so its prose can quote a call's
milliseconds and a count of calls straight from a trace (`c()`, `ms()`, `count()` in the scenes).
"""

from __future__ import annotations

import html as html_module
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments" / "exp_230_the_spine_trace"))
import render as base  # noqa: E402 - exp_230's renderer, reused whole

SRC_MAP = HERE / "src_map.json"


def esc_attr(text: str) -> str:
    return html_module.escape(text, quote=True)


def strip(text: str) -> str:
    return html_module.unescape(re.sub(r"<[^>]+>", "", text or ""))


def load_traces(directory: Path) -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
        if ".envelope" not in path.name
    }


def load_scenes(path: Path, traces: dict[str, dict]) -> dict:
    namespace: dict = {"__file__": str(path), "REPO": REPO, "TRACES": traces}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    return namespace


# ---------------------------------------------------------------- the shelf and the chronicle

WRITERS = {
    # qualname the trace records -> the file that call writes (read off the code:
    # workspace/registry.py `_write` and `_write_roster`)
    "Workspace._write": ".vqapr/workspace.yaml",
    "Workspace._write_roster": ".vqapr/instruments.json",
}


def command_words(trace: dict) -> str:
    """The traced command as a user would type it, the project path taken out."""
    argv = [str(a) for a in trace["argv"]]
    if argv and argv[0] == "<worker>":
        return "worker: run_registered_strategy(" + ", ".join(argv[2:]) + ")"
    words: list[str] = []
    skip = False
    for i, word in enumerate(argv):
        if skip:
            skip = False
            continue
        if word == "--project-root":
            skip = True
            continue
        if ("\\" in word or "/" in word) and i > 0:
            word = Path(word.replace("\\", "/")).name
        words.append(word)
    return "vqapr " + " ".join(words)


def disk_changes(traces: dict[str, dict]) -> dict[str, dict]:
    """Per trace: files that appeared, files that went, files a recorded write call rewrote."""
    out: dict[str, dict] = {}
    previous: set[str] | None = None
    for name in sorted(traces):
        trace = traces[name]
        files = set(trace.get("files_after") or [])
        if not files:
            out[name] = {"added": [], "removed": [], "rewritten": [], "listed": False}
            continue
        if previous is None:
            previous = {f for f in files if not f.startswith(".vqapr/")}
            out["_initial"] = {"files": sorted(previous)}
        written = {
            WRITERS[c["qualname"]] for c in trace["calls"] if c["qualname"] in WRITERS
        }
        out[name] = {
            "added": sorted(files - previous),
            "removed": sorted(previous - files),
            "rewritten": sorted(f for f in written if f in previous),
            "listed": True,
        }
        previous = files
    return out


def shelf_html(names: list[str], traces: dict[str, dict], changes: dict[str, dict], note: str = "") -> str:
    rows: list[str] = []
    for name in names:
        change = changes[name]
        items: list[str] = []
        for f in change["added"]:
            items.append(f'<li class="new"><span class="tag">새로 생김</span><code>{html_module.escape(f)}</code></li>')
        for f in change["rewritten"]:
            items.append(f'<li class="rew"><span class="tag">고쳐 씀</span><code>{html_module.escape(f)}</code></li>')
        for f in change["removed"]:
            items.append(f'<li class="gone"><span class="tag">없어짐</span><code>{html_module.escape(f)}</code></li>')
        if not items:
            items.append(
                '<li class="none">디스크에 새로 생기거나 고쳐 쓴 파일 없음</li>'
                if change["listed"]
                else '<li class="none">이 트레이스는 파일 목록을 남기지 않는다(다른 프로세스의 일꾼)</li>'
            )
        rows.append(f'<div class="cmd"><code>{html_module.escape(command_words(traces[name]))}</code></div><ul>{"".join(items)}</ul>')
    initial = changes["_initial"]["files"]
    same = f'<div class="same">원본 {len(initial)}개는 그대로.</div>'
    extra = f'<div class="same">{note}</div>' if note else ""
    return f'<div class="shelf"><div class="sh">디스크에 남은 것</div>{"".join(rows)}{same}{extra}</div>'


def chronicle_html(traces: dict[str, dict], changes: dict[str, dict], notes: dict[str, str]) -> str:
    rows = []
    for name in sorted(traces):
        change = changes[name]
        added = "<br>".join(f"<code>{html_module.escape(f)}</code>" for f in change["added"]) or "—"
        rewritten = "<br>".join(f"<code>{html_module.escape(f)}</code>" for f in change["rewritten"]) or "—"
        note = notes.get(name, "")
        rows.append(
            f'<tr><td class="num">{name[:2]}</td><td><code>{html_module.escape(command_words(traces[name]))}</code>{"<br><span class=muted>" + note + "</span>" if note else ""}</td>'
            f'<td class="num">{len(traces[name]["calls"]):,}</td><td>{added}</td><td>{rewritten}</td></tr>'
        )
    initial = changes["_initial"]["files"]
    return (
        "<h2>명령별 파일 변화</h2>\n"
        f'<p class="lede">시작할 때는 원본 {len(initial)}개뿐. 트레이스의 파일 목록을 앞 명령과 비교했습니다.</p>\n'
        '<div class="tablewrap chron"><table>\n<tr><th class="num">#</th><th>명령</th><th class="num">호출</th><th>새로 생긴 파일</th><th>고쳐 쓴 파일</th></tr>\n'
        + "".join(rows)
        + "\n</table></div>\n"
    )


# ---------------------------------------------------------------- the file card and the src/ map


def slug(path: str) -> str:
    return "f-" + re.sub(r"[^A-Za-z0-9]+", "-", path)


def files_const(data: dict) -> dict[str, dict]:
    files: dict[str, dict] = {}
    for fold in data["folds"]:
        for entry in fold["entries"]:
            if "path" in entry:
                files[entry["path"]] = {"role": entry["role"], "explain": entry["explain"], "lines": entry["lines"]}
    for path, card in data["authors"].items():
        files[path] = {"role": card["role"], "explain": card["explain"], "author": True}
    return files


def srcmap_html(data: dict, lede: str) -> str:
    count = sum(1 for fold in data["folds"] for e in fold["entries"] if "path" in e)
    table = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in data["looptbl"])
    seq = "".join(
        f'<div><h4>{head}</h4><ol>{"".join(f"<li>{item}</li>" for item in items)}</ol></div>'
        for head, items in data["seq"]
    )
    folds: list[str] = []
    for fold in data["folds"]:
        body: list[str] = []
        for e in fold["entries"]:
            if "sub" in e:
                body.append(f'<div class="sub">{e["sub"]}</div>')
                continue
            search = " ".join(
                [e["path"], strip(e["role"]), strip(e["explain"]), *(strip(b) for b in e["bullets"])]
            ).lower()
            lines = f'<span class="ln">{e["lines"]}줄</span>' if e["lines"] else ""
            bullets = f'<ul>{"".join(f"<li>{b}</li>" for b in e["bullets"])}</ul>' if e["bullets"] else ""
            used = f'<div class="ub">{e["used"]}</div>' if e["used"] else ""
            body.append(
                f'<details class="fe" id="{slug(e["path"])}" data-search="{esc_attr(search)}"><summary><code>{e["name"]}</code>{lines}'
                f'<span class="role">{e["role"]}</span><span class="hits" data-hits="{e["path"]}"></span></summary>'
                f'<div class="fb"><p>{e["explain"]}</p>{bullets}{used}<div class="fr" data-frames="{e["path"]}"></div></div></details>'
            )
        folds.append(
            f'<details class="fold"><summary><code>{fold["name"]}</code><span class="an">{fold["analogy"]}</span>'
            f'<span class="cnt">{fold["count"]}</span></summary><p class="fs">{fold["summary"]}</p>{"".join(body)}</details>'
        )
    return (
        f'<section class="srcmap" id="srcmap">\n<h2>src/ 지도 — 폴더 {len(data["folds"])}묶음, 파일 {count}개를 하나하나</h2>\n'
        f'<p class="lede">{lede}</p>\n<div class="tablewrap looptbl"><table><tr><th>폴더</th><th>고리에서 맡는 것</th></tr>{table}</table></div>\n'
        f'<div class="seq">{seq}</div>\n'
        '<div class="q"><input id="mapq" type="search" placeholder="파일 이름 · 역할 · 함수 이름으로 찾기 (예: freeze, 계좌, cube)" aria-label="src 지도 검색"><span id="mapn"></span></div>\n'
        + "\n".join(folds)
        + "\n</section>\n"
    )


HELPERS_JS = r"""
function fileKey(loc){ return String(loc||'').replace(/:\d+$/,''); }
function slug(p){ return 'f-'+p.replace(/[^A-Za-z0-9]+/g,'-'); }
function fileCard(loc){ const p=fileKey(loc), f=FILES[p]; if(!f) return ''; const link=f.author?'':`<a href="#${slug(p)}" data-open="${p}">src 지도에서 보기 ↓</a>`; return `<div class="fcard${f.author?' author':''}"><div class="fh"><span class="fk">${f.author?'당신의 코드':'이 파일'}</span><code>${esc(p)}</code>${f.lines?`<span class="ln">${f.lines}줄</span>`:''}${link}</div><div class="fr">${f.role}</div></div>`; }
function openFile(p){ const el=document.getElementById(slug(p)); if(!el) return; el.open=true; const fold=el.closest('details.fold'); if(fold) fold.open=true; }
function buildFrameIndex(){
  const idx={}; S.forEach((sc,s)=>sc.frames.forEach((fr,f)=>{ const p=fileKey(fr.loc); (idx[p]=idx[p]||[]).push([s,f]); }));
  document.querySelectorAll('[data-frames]').forEach(el=>{ const hits=idx[el.dataset.frames]||[]; if(!hits.length) return; el.innerHTML='<span>이 파일에 선 프레임</span>'+hits.map(([s,f])=>`<button class="jump" data-s="${s}" data-f="${f}">${S[s].key} ${String(f+1).padStart(2,'0')}</button>`).join(''); });
  document.querySelectorAll('[data-hits]').forEach(el=>{ const n=(idx[el.dataset.hits]||[]).length; if(n) el.textContent='프레임 '+n; });
  document.addEventListener('click',e=>{
    const b=e.target.closest('.jump'); if(b){ go(+b.dataset.s,+b.dataset.f); $('tabs').scrollIntoView({behavior:'smooth',block:'start'}); return; }
    const a=e.target.closest('[data-open]'); if(a){ openFile(a.dataset.open); }
  });
}
function buildMapSearch(){
  const box=$('mapq'), out=$('mapn'); if(!box) return;
  const all=[...document.querySelectorAll('.srcmap details.fe')];
  const apply=()=>{ const q=box.value.trim().toLowerCase(); let n=0;
    all.forEach(el=>{ const hit=!q||el.dataset.search.includes(q); el.hidden=!hit; if(hit) n++; if(q&&hit) el.closest('details.fold').open=true; });
    document.querySelectorAll('.srcmap details.fold').forEach(fd=>{ fd.hidden=!!q&&!fd.querySelector('details.fe:not([hidden])'); });
    out.textContent=q?`${n}개 파일`:`파일 ${all.length}개`; };
  box.addEventListener('input',apply); apply();
}
"""

CARD_CSS = """
/* 0.16.0: the file card under a frame, and the src/ map */
.fcard{margin:12px 0 4px;padding:10px 14px;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:6px;background:var(--surface);font-size:13.5px;line-height:1.6}
.fcard .fh{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;margin-bottom:4px}
.fcard .fk{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.fcard code,.srcmap code{font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;font-size:.92em}
.fcard .ln,.srcmap .ln{color:var(--muted);font-size:12px}
.fcard a{margin-left:auto;font-size:12px;color:var(--accent)}
.fcard .fr{font-weight:600;margin-bottom:2px}
.fcard p{margin:0}
.fcard.author{border-left-color:var(--author,#9a5b13)}
.srcmap{margin:28px 0 40px}
.srcmap .looptbl{margin:10px 0 18px}
.srcmap .looptbl td:first-child{white-space:nowrap;font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--accent)}
.srcmap .seq{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin:8px 0 18px}
.srcmap .seq div{border:1px solid var(--line);border-radius:8px;background:var(--surface);padding:10px 16px;font-size:13.5px;line-height:1.6}
.srcmap .seq h4{margin:4px 0 6px;font-size:14px}
.srcmap .seq ol{margin:0;padding-left:1.3em}
.srcmap .q{display:flex;gap:10px;align-items:center;margin:8px 0 14px;flex-wrap:wrap}
.srcmap .q input{flex:1;min-width:220px;padding:8px 12px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink);font:inherit}
.srcmap .q span{color:var(--muted);font-size:13px}
.srcmap details.fold{border:1px solid var(--line);border-radius:8px;background:var(--surface);margin:10px 0;padding:0 14px}
.srcmap details.fold>summary{cursor:pointer;padding:10px 0;display:flex;flex-wrap:wrap;gap:10px;align-items:baseline}
.srcmap details.fold>summary code{font-weight:600;color:var(--accent);font-size:14px}
.srcmap .an{color:var(--muted);font-size:13px}
.srcmap .cnt{margin-left:auto;color:var(--muted);font-size:12px}
.srcmap .fs{margin:0 0 10px;font-size:14px;line-height:1.65}
.srcmap .sub{margin:12px 0 6px;font-size:13px;color:var(--ink-2);border-top:1px dashed var(--line);padding-top:10px}
.srcmap .sub code{color:var(--accent)}
.srcmap details.fe{border-top:1px solid var(--line-2);padding:0}
.srcmap details.fe>summary{cursor:pointer;padding:7px 0;display:grid;grid-template-columns:minmax(150px,auto) 60px 1fr auto;gap:10px;align-items:baseline;font-size:13.5px}
.srcmap details.fe>summary .role{color:var(--ink-2)}
.srcmap .hits{font-size:11.5px;color:var(--accent);white-space:nowrap}
.srcmap .fb{padding:2px 0 12px 12px;border-left:2px solid var(--accent-bg);margin:0 0 8px 4px;font-size:13.5px;line-height:1.65}
.srcmap .fb p{margin:4px 0 8px}
.srcmap .fb ul{margin:4px 0 8px;padding-left:1.2em}
.srcmap .fb .ub{color:var(--muted);font-size:12.5px}
.srcmap .fb .fr{margin-top:6px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12.5px;color:var(--muted)}
.srcmap .jump{border:1px solid var(--line);background:var(--accent-bg);color:var(--accent);border-radius:4px;padding:1px 8px;font:inherit;font-size:12px;cursor:pointer}
@media (max-width:640px){.srcmap details.fe>summary{grid-template-columns:1fr auto}.srcmap details.fe>summary .role{grid-column:1/-1}}
"""

SHELF_CSS = """
/* 0.16.0: the shelf under a scene's story, the chronicle, and the analogy table */
.shelf{margin:12px 0 2px;padding:10px 14px;border:1px dashed var(--accent);border-radius:8px;background:var(--surface);font-size:13.5px;line-height:1.55;color:var(--ink)}
.shelf .sh{font-size:.72rem;letter-spacing:.08em;color:var(--muted);font-weight:600;margin-bottom:4px}
.shelf .cmd{margin:8px 0 2px;color:var(--ink-2)}
.shelf ul{list-style:none;margin:2px 0 4px;padding:0}
.shelf li{display:flex;gap:8px;align-items:baseline;padding:2px 0;word-break:break-all}
.shelf .tag{flex:none;font-size:11px;padding:0 6px;border-radius:4px;background:var(--accent-bg);color:var(--accent);white-space:nowrap}
.shelf li.rew .tag{background:var(--warn-bg);color:var(--warn)}
.shelf li.gone .tag{background:var(--bad-bg);color:var(--bad)}
.shelf li.none{color:var(--muted);font-style:italic}
.shelf .same{margin-top:6px;color:var(--muted);font-size:12.5px}
.chron td code{word-break:break-all}
.chron .muted{color:var(--muted);font-size:12.5px}
.analogy td:first-child{white-space:nowrap;font-weight:600}
.analogy td code{white-space:nowrap}
"""


def analogy_html(rows: list[tuple[str, str, str]]) -> str:
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return (
        "<h2>비유 — 창고 한 채</h2>\n"
        '<div class="tablewrap analogy"><table>\n<tr><th>창고에서</th><th>vqapr에서</th><th>자리 (파일)</th></tr>\n'
        + body
        + "\n</table></div>\n"
    )


def _replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) < 1:
        raise ValueError(f"template anchor not found: {old[:60]!r}")
    return text.replace(old, new, 1)


def render(scenes_path: Path, traces_dir: Path, out: Path) -> None:
    traces = load_traces(traces_dir)
    spec = load_scenes(scenes_path, traces)
    changes = disk_changes(traces)
    src_map = json.loads(SRC_MAP.read_text(encoding="utf-8"))
    template = base.TEMPLATE.read_text(encoding="utf-8")

    head = template[: template.index("<main>")]
    head = _replace_once(head, "<title>vqapr 0.6.0 척추 디버거</title>", f"<title>{spec['HEADER']['title']}</title>")
    head = _replace_once(head, "</style>", base.EXTRA_CSS + CARD_CSS + SHELF_CSS + "</style>")

    middle = template[template.index("<h2>척추 지도") : template.index("<h2>트레이스가 확인한 것")]
    middle = _replace_once(middle, "<h2>척추 지도 — 클릭하면 그 단계로</h2>", "<h2>장면 지도 — 클릭하면 그 장면으로</h2>")
    middle = _replace_once(
        middle,
        '<div class="tabs" id="tabs" role="tablist"></div>',
        '<div class="tabs" id="tabs" role="tablist"></div>\n<div class="intro" id="intro"></div>',
    )

    script = template[template.index("<script>") :]
    script = _replace_once(script, "$('remember').innerHTML=", "$('intro').innerHTML=sc.story||''; $('remember').innerHTML=")
    script = _replace_once(script, '<div class="what">${fr.what}</div>${code}', '<div class="what">${fr.what}</div>${code}${fileCard(fr.loc)}')
    script = _replace_once(script, "grp('메모리','mem')+grp('디스크','disk')", "grp('작업대 — 메모리','mem')+grp('창고 — 디스크의 파일','disk')")
    script = _replace_once(script, "buildMap(); buildTabs();", "buildMap(); buildTabs(); buildFrameIndex(); buildMapSearch();")
    data_start = script.index("const S = [];\n") + len("const S = [];\n")
    data_end = script.index("const $ = id =>")
    map_fn_start = script.index("function buildMap(){")
    map_fn_end = script.index("function buildTabs(){")
    script_prefix = script[:data_start]
    script_between = script[data_end:map_fn_start]
    script_suffix = script[map_fn_end:].replace("vqapr-stepper-041", spec["HEADER"]["storage_key"])

    scenes = []
    for scene in spec["SCENES"]:
        scene = dict(scene)
        if scene.get("shelf"):
            scene["story"] = scene.get("story", "") + shelf_html(scene["shelf"], traces, changes, scene.get("shelf_note", ""))
        scenes.append(scene)
    scene_js = "".join(base.scene_js(scene, traces) for scene in scenes)
    files_js = "const FILES = " + json.dumps(files_const(src_map), ensure_ascii=False) + ";\n"

    page = (
        head
        + base.header_html(spec["HEADER"])
        + analogy_html(spec["ANALOGY"])
        + chronicle_html(traces, changes, spec.get("CHRONICLE_NOTES", {}))
        + middle
        + base.table_html(spec["TABLE"])
        + srcmap_html(src_map, spec["SRCMAP_LEDE"])
        + script_prefix
        + scene_js
        + files_js
        + HELPERS_JS
        + script_between
        + base.map_js(spec["MAP"])
        + script_suffix
    )
    out.write_text(page, encoding="utf-8", newline="\n")

    # The practice from exp_246: every frame's trace / index / qualname / ms beside its title,
    # printed before anyone reads the page.
    frames = 0
    for scene in spec["SCENES"]:
        for frame in scene["frames"]:
            call = traces[frame["trace"]]["calls"][frame["idx"]]
            frames += 1
            print(f"{scene['key']} {frame['trace']:>22} #{frame['idx']:<6} {call['qualname']:<48} {call['ms']!s:>10} ms | {strip(frame['title'])[:60]}")
    print(f"wrote {out} ({len(page):,} bytes): {len(spec['SCENES'])} scenes, {frames} frames")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: render_0_16_0.py SCENES.py TRACES_DIR OUT.html")
    render(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
