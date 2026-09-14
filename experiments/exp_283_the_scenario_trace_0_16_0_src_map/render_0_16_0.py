"""Render the 0.16.0 scenario stepper: exp_230's renderer, then a file card and the src/ map.

    uv run python experiments/exp_283_the_scenario_trace_0_16_0_src_map/render_0_16_0.py TRACES_DIR OUT.html [ARTIFACT.html]

The stepper itself is `exp_230/render.py` over `scenes_0_16_0.py`, unchanged. This adds two things
the owner asked for with it (2026-09-12: "src/ 내의 폴더와 파일들을 하나하나 설명해 줘"):

- under every frame's code window, a card saying what the frame's file is for (from
  `src_map_0_16_0.json`), with a link down to the file's entry;
- after the closing table, the src/ map: every folder and every file of `src/vqapr/` with what it
  holds, its main names, who imports it, and the frames of this page that stand in it.

`src_map_0_16_0.json` was written by reading each file of the 0.16.0 tree (one reader per package,
imports found by grep); it is prose about the code, not something a trace measured.

With a third argument, a copy without the document wrapper (`<!DOCTYPE>`, `<html>`, `<head>`,
`<body>`) is written for publishing as an artifact, which supplies its own.
"""

# ruff: noqa: E501, RUF001 -- one-line CSS/HTML/JS templates, and prose whose typographic characters are the content

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCENES = HERE / "scenes_0_16_0.py"
SRC_MAP = HERE / "src_map_0_16_0.json"
DECL = "experiments/exp_283_the_scenario_trace_0_16_0_src_map/declarations/"

# The author's files appear on the page as `sample/<name>` (exp_230's display_path).
AUTHOR = {
    "sample/features.py": ("저자 코드 · DataModel", "`SampleFeatures`. 날마다 종목별 5일 모멘텀(여섯 종가 중 마지막 ÷ 첫 번째 − 1)을 계산해 행으로 돌려준다. `inputs()`로 `sample-prices`의 `close`를 여섯 행 읽겠다고 선언하고, `compute(call)`에서 `call.read(...).matrix()`로 행렬을 본다. 시나리오 ③."),
    "sample/factor.py": ("저자 코드 · 전략", "`SampleFactor`. ③이 만든 `sample-features`의 최신 행 하나를 읽어 상위 3종목 +1/6, 하위 3종목 −1/6의 `vq.Rebalance.signed`를 돌려준다. 시나리오 ④."),
    "sample/stoploss.py": ("저자 코드 · 전략", "`SampleStopLoss`. 첫날 같은 비중으로 사고 진입가를 `self.memory`에 적은 뒤, 3% 넘게 빠진 종목을 팔고 날짜를 남긴다. 다 팔 때는 `Hold`가 아니라 빈 `Rebalance`. 시나리오 ⑤."),
    "sample/enhanced.py": ("저자 코드 · 전략", "`SampleEnhancedIndex`. ④가 저장한 `sample-factor-weights`를 alpha로 읽어 같은 비중(1/9)에 그 절반을 얹고 0 아래를 자르는 롱온리 enhanced index. 시나리오 ⑥."),
    "sample/exchange_signed.py": ("저자 코드 · 거래소", "`SampleSignedExchange`. `AcademicExchange`에 종목마다 SIGNED 상장(`ListingAccess`)을 주어 공매도 주문이 통과하게 한다. 시나리오 ④."),
}

# The map follows the loop: what everything passes, what reads, what decides, what runs, what reports.
ORDER = [
    "src/vqapr",
    "src/vqapr/domain",
    "src/vqapr/data",
    "src/vqapr/record",
    "src/vqapr/signals",
    "src/vqapr/portfolio",
    "src/vqapr/component",
    "src/vqapr/workspace",
    "src/vqapr/run",
    "src/vqapr/report",
    "src/vqapr/cli",
    "src/vqapr/agent",
    "src/vqapr/_internal",
]

LOOP = [
    ("domain/", "고리가 주고받는 값과 Account — 개념 하나에 모듈 하나(account · fill · order · intent · listing · schedule · valuation …)"),
    ("data/ · record/", "모든 읽기(dataset · panel · window · 파일의 문 · 집행표) · run이 남기는 기록(쓰기 · 읽기 · 표 이름)"),
    ("signals/ · portfolio/", "신호의 변환과 평가 · 비중 만들기, 최적화, 상계"),
    ("component/", "확장점: 역할마다 계약(base.py)과 기본 구현을 따로, 그리고 부품이 들어오는 문"),
    ("workspace/", "명령과 명령 사이에 프로젝트가 기억하는 것(registry · declarations · run_definition)"),
    ("run/", "run의 일생: preflight/(사실 · 판정 · 얼리기 · 평결) · engine/(루프 · 사건 · 부르는 메서드 이름의 단계) · assemble · batch · recording"),
    ("report/", "끝난 기록에서 지표와 보고서를 만든다"),
    ("cli/ · agent/", "사람과 에이전트가 들어오는 문: 명령줄 · scaffold · 샘플 · 스킬"),
]

MAP_CSS = """
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

MAP_JS = r"""
function fileKey(loc){ return String(loc||'').replace(/:\d+$/,''); }
function slug(p){ return 'f-'+p.replace(/[^A-Za-z0-9]+/g,'-'); }
function fileCard(loc){ const p=fileKey(loc), f=FILES[p]; if(!f) return ''; const link=f.author?'':`<a href="#${slug(p)}" data-open="${p}">src 지도에서 보기 ↓</a>`; return `<div class="fcard${f.author?' author':''}"><div class="fh"><span class="fk">${f.author?'당신의 코드':'이 파일'}</span><code>${esc(p)}</code>${f.lines?`<span class="ln">${f.lines}줄</span>`:''}${link}</div><div class="fr">${f.role}</div><p>${f.explain}</p></div>`; }
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


def slug(path: str) -> str:
    """The element id of a file's entry; `slug` in MAP_JS computes the same one."""
    return "f-" + re.sub(r"[^A-Za-z0-9]+", "-", path)


def md(text: str) -> str:
    """Escape, then turn the readers' `backticks` into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text, quote=False))


def load_renderer():
    spec = importlib.util.spec_from_file_location(
        "render_230", REPO / "experiments" / "exp_230_the_spine_trace" / "render.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rank(folder: str) -> tuple[int, str]:
    best = max((p for p in ORDER if folder == p or folder.startswith(p + "/")), key=len)
    return ORDER.index(best), folder


def map_html(src_map: dict) -> str:
    folders = {f["path"]: f for f in src_map["folders"]}
    by_parent: dict[str, list[dict]] = {}
    for entry in src_map["files"]:
        by_parent.setdefault(entry["path"].rsplit("/", 1)[0], []).append(entry)
    # One fold per top-level concept; its subfolders are sections inside it.
    tops: dict[str, list[str]] = {}
    for parent in by_parent:
        top = ORDER[rank(parent)[0]]
        tops.setdefault(top, []).append(parent)

    def file_block(entry: dict) -> str:
        path = entry["path"]
        name = path.rsplit("/", 1)[1]
        key = "".join(f"<li>{md(k)}</li>" for k in entry.get("key") or [])
        used = entry.get("used_by") or []
        used_html = (
            f'<div class="ub">쓰는 곳: {", ".join(f"<code>{html.escape(u.replace("src/vqapr/", ""))}</code>" for u in used)}</div>'
            if used
            else ""
        )
        search = " ".join([path, entry.get("role", ""), entry.get("explain", ""), " ".join(entry.get("key") or [])]).lower()
        return (
            f'<details class="fe" id="{slug(path)}" data-search="{html.escape(search)}">'
            f'<summary><code>{html.escape(name)}</code><span class="ln">{entry.get("lines", "")}줄</span>'
            f'<span class="role">{md(entry.get("role", ""))}</span><span class="hits" data-hits="{path}"></span></summary>'
            f'<div class="fb"><p>{md(entry.get("explain", ""))}</p>{f"<ul>{key}</ul>" if key else ""}{used_html}'
            f'<div class="fr" data-frames="{path}"></div></div></details>'
        )

    blocks = []
    for top in ORDER:
        if top not in tops:
            continue
        info = folders.get(top, {})
        parents = sorted(tops[top], key=lambda p: (p != top, p))
        count = sum(len(by_parent[p]) for p in parents)
        inner = []
        for parent in parents:
            if parent != top:
                sub = folders.get(parent, {})
                label = parent.replace(top + "/", "") if top != "src/vqapr" else parent
                note = f" — {md(sub['summary'])}" if sub.get("summary") else ""
                inner.append(f'<div class="sub"><code>{html.escape(label)}/</code>{note}</div>')
            inner.extend(file_block(e) for e in sorted(by_parent[parent], key=lambda e: e["path"]))
        title = "src/vqapr/ (패키지 루트)" if top == "src/vqapr" else top.replace("src/vqapr/", "") + "/"
        blocks.append(
            f'<details class="fold"><summary><code>{html.escape(title)}</code>'
            f'<span class="an">{md(info.get("analogy", ""))}</span><span class="cnt">파일 {count}</span></summary>'
            f'<p class="fs">{md(info.get("summary", ""))}</p>{"".join(inner)}</details>'
        )

    loop_rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>" for k, v in LOOP)
    seq = ""
    if src_map.get("run_sequence") or src_map.get("one_event"):
        cols = []
        if src_map.get("run_sequence"):
            cols.append("<div><h4><code>vqapr run &lt;id&gt;</code> 한 번의 순서</h4><ol>" + "".join(f"<li>{md(s)}</li>" for s in src_map["run_sequence"]) + "</ol></div>")
        if src_map.get("one_event"):
            cols.append("<div><h4>사건 하나 안에서 (결정 → 체결)</h4><ol>" + "".join(f"<li>{md(s)}</li>" for s in src_map["one_event"]) + "</ol></div>")
        seq = '<div class="seq">' + "".join(cols) + "</div>"
    total = len(src_map["files"])
    return (
        '<section class="srcmap" id="srcmap">\n'
        f"<h2>src/ 지도 — 폴더 {len(tops)}묶음, 파일 {total}개를 하나하나</h2>\n"
        '<p class="lede">위의 프레임이 선 파일은 여기 모두 있습니다(파일 이름 옆 <b>프레임 N</b>, 펼치면 그 프레임으로 가는 단추). '
        "0.16.0의 폴더는 고리의 개념을 따릅니다: 데이터가 들어오고 → 전략이 판단하고 → 거래소가 체결하고 → 계좌가 적고 평가하고 → 전략이 다음에 그 계좌를 봅니다. "
        "설명은 0.16.0 트리의 파일을 하나씩 읽고 쓴 것이고(쓰는 곳은 import를 grep한 것), 위의 트레이스처럼 잰 값은 아닙니다.</p>\n"
        f'<div class="tablewrap looptbl"><table><tr><th>폴더</th><th>고리에서 맡는 것</th></tr>{loop_rows}</table></div>\n'
        f"{seq}\n"
        '<div class="q"><input id="mapq" type="search" placeholder="파일 이름 · 역할 · 함수 이름으로 찾기 (예: freeze, 계좌, cube)" aria-label="src 지도 검색"><span id="mapn"></span></div>\n'
        + "\n".join(blocks)
        + "\n</section>\n"
    )


def files_js(src_map: dict) -> str:
    table: dict[str, dict] = {}
    for entry in src_map["files"]:
        table[entry["path"]] = {
            "role": md(entry.get("role", "")),
            "explain": md(entry.get("explain", "")),
            "lines": entry.get("lines"),
        }
    for path, (role, explain) in AUTHOR.items():
        table[path] = {"role": md(role), "explain": md(explain) + f" <code>{DECL}{path.split('/')[1]}</code>", "author": True}
    return "const FILES = " + json.dumps(table, ensure_ascii=False).replace("</", "<\\/") + ";\n"


def main(traces_dir: Path, out: Path, artifact: Path | None) -> None:
    load_renderer().render(SCENES, traces_dir, out)
    page = out.read_text(encoding="utf-8")
    src_map = json.loads(SRC_MAP.read_text(encoding="utf-8"))

    def swap(old: str, new: str) -> None:
        nonlocal page
        assert old in page, old
        page = page.replace(old, new, 1)

    swap("</style>", MAP_CSS + "</style>")
    swap("<script>", map_html(src_map) + "<script>")
    swap("const S = [];\n", "const S = [];\n" + files_js(src_map) + MAP_JS)
    swap('<div class="what">${fr.what}</div>${code}', '<div class="what">${fr.what}</div>${code}${fileCard(fr.loc)}')
    swap("buildMap(); buildTabs();", "buildMap(); buildTabs(); buildFrameIndex(); buildMapSearch();")
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(page):,} bytes) with the src/ map: {len(src_map['files'])} files")
    if artifact is not None:
        bare = re.sub(r"<!DOCTYPE[^>]*>|</?html[^>]*>|</?head>|</?body[^>]*>", "", page, flags=re.I)
        artifact.write_text(bare, encoding="utf-8", newline="\n")
        print(f"wrote {artifact} ({len(bare):,} bytes, no document wrapper)")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: render_0_16_0.py TRACES_DIR OUT.html [ARTIFACT.html]")
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) == 4 else None)
