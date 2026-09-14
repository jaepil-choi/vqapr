# ruff: noqa: E501, RUF001, F821 -- prose data: long lines and typographic characters are the content; REPO and TRACES are bound by the renderer
# The scenario stepper on redesign/registration-cleanup f862c147 (develop f639add0 + records 280-281),
# re-traced and told as the 0.16.0 page's warehouse. exp_280's frames were moved onto these traces by
# the k-th call of the same qualname (README); the frames records 280-281 changed are rewritten and
# tagged [280] / [281]. Owner feedback 2026-09-14: short and clear, the call chain folded beneath.
#
# Rendered by `render.py`, which binds `REPO` and `TRACES`. A frame names a trace and a call index;
# the renderer fills in the location, qualname, milliseconds, code window and the command badge.
# Chains use `c(trace, idx, label)` and the table uses `h(trace, idx, label)`: both refuse a label
# that is not the qualname at that index. Outcome numbers come from the traced runs' envelopes.

DECL = "experiments/exp_280_the_scenario_trace_0_16_0/declarations/"
REG = "src/vqapr/workspace/registration.py"


def at(file: str, needle: str, n: int = 8, before: int = 0) -> list[str]:
    """`n` source lines of `file` starting `before` lines above the first line holding `needle`."""
    lines = (REPO / file).read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if needle in line:
            start = max(0, index - before)
            return [item.rstrip() for item in lines[start : start + n]]
    raise KeyError((file, needle))


def _call(trace: str, idx: int) -> dict:
    call = TRACES[trace]["calls"][idx]
    assert call["idx"] == idx, (trace, idx)
    return call


def _same(call: dict, label: str) -> bool:
    return call["qualname"].split(".")[-1] == label.split("(")[0].strip().split(".")[-1]


def fmt(value: float | None) -> str:
    if value is None:
        return "?"
    if value >= 1:
        return f"{value:,.1f}"
    if value >= 0.01:
        return f"{value:.2f}"
    return f"{value:.3f}"


def ms(trace: str, idx: int) -> str:
    return fmt(_call(trace, idx)["ms"])


def c(trace: str, idx: int, label: str | None = None, note: str = "") -> str:
    """`<code>label</code>(#idx, ms)` -- refusing a label that is not the call at that index."""
    call = _call(trace, idx)
    if label is not None:
        assert _same(call, label), f"{trace} #{idx}: {label!r} is {call['qualname']!r}"
    took = f", {fmt(call['ms'])} ms" if call["ms"] is not None else ""
    return f"<code>{label or call['qualname']}</code>(#{idx}{took}{note})"


def h(trace: str, idx: int, label: str) -> str:
    """`#idx` for the table's evidence column, refusing a label that is not the call at that index."""
    call = _call(trace, idx)
    assert _same(call, label), f"{trace} #{idx}: {label!r} is {call['qualname']!r}"
    return f"#{idx}"


class Chain:
    """A folded call chain -- each step `(idx, label)` or `(idx, label, note)` -- that also hands
    its steps to the renderer, which draws them as a call stack with what went in and came out."""

    def __init__(self, trace: str, steps: tuple) -> None:
        self.trace = trace
        self.steps = steps
        self.html = " → ".join(c(trace, *step) for step in steps)

    def __str__(self) -> str:
        return self.html


def chain(trace: str, *steps) -> Chain:
    return Chain(trace, steps)


def count(trace: str, name: str) -> int:
    return sum(
        1 for call in TRACES[trace]["calls"] if call["qualname"] == name or call["qualname"].endswith("." + name)
    )


def writes(trace: str) -> int:
    return sum(count(trace, name) for name in ("write_atomically", "Workspace._write", "_write_compact"))


def outcome(trace: str, strategy: str) -> str:
    """orders · fills · account version, from the run's own envelope."""
    run = TRACES[trace]["envelope"]["strategies"][strategy]
    return f"{run['fills']['orders']} · {run['fills']['dealt']} · v{run['account_version']}"


def nc(trace: str) -> str:
    return f"{len(TRACES[trace]['calls']):,}"


def el(trace: str) -> str:
    return f"{TRACES[trace]['elapsed_ms']:,.0f}"


def F(trace: str, idx: int, title: str, story: str, calls: Chain | str | None = None, **extra) -> dict:
    what = f'<p class="story">{story}</p>'
    if isinstance(calls, Chain):
        extra.setdefault("stack", [(calls.trace, step[0], step[1] if len(step) > 1 else None) for step in calls.steps])
    if calls:
        what += f'<details class="tr"><summary>함수 이름과 호출 번호</summary><p>{calls}</p></details>'
    return {"trace": trace, "idx": idx, "title": title, "what": what, **extra}


R, B, RA = "01_register", "02_register_bad", "04_register_again"
CK, RF, DM = "03_check_changed", "05_register_features", "06_run_features"
FR, FA, SR, SL = "07_register_factor", "08_run_factor", "09_register_stoploss", "10_run_stoploss"
ER, EN, LD, SH = "11_register_enhanced", "12_run_enhanced", "13_list_datasets", "14_show_run_enhanced"
BA, WK = "15_run_batch", "16_worker_factor"

FACTOR_DIR = "…/strategies/sample-factor@0696c8f4/"
FEAT_DIR = "…/datamodels/sample-features@4327b244/"
ORIGINALS = len({f for f in TRACES[R]["files_after"] if not f.startswith(".vqapr/")})

HEADER = {
    "title": "vqapr 시나리오 디버거 · 등록 정리",
    "storage_key": "vqapr-stepper-f862c147",
    "eyebrow": "vqapr 0.16.0 + records 280-281 · redesign/registration-cleanup f862c147 · 2026-09-14 · sys.setprofile 트레이스",
    "h1": "vqapr 시나리오 디버거 — 등록 정리 후",
    "lede": (
        "샘플 프로젝트(10종목 · 735거래일)에서 여덟 장면을 실제로 돌리고 한 호출씩 따라갑니다. "
        "프레임마다 어느 명령인지, 한두 문장, 접힌 곳에 함수와 호출 번호가 있습니다. "
        "0.16.0 판 이후 바뀐 곳은 <b>[280]</b> · <b>[281]</b>입니다. "
        "숫자는 모두 트레이스와 run 기록에서 읽었습니다(<code>experiments/exp_282_the_scenario_trace_registration_cleanup/</code>)."
    ),
    "facts": [
        {"k": "흐름", "v": "송장 → 입고 문 → 장부 → 점검 → 라인 → 일지", "s": "YAML을 검사해 장부에 적고, run은 점검 뒤 루프를 돌아 기록을 남긴다"},
        {"k": "[280] 송장 읽기", "v": "등록 쪽에서", "s": "<code>read_declaration</code>은 <code>workspace/registration.py</code>에, <code>apply</code>는 하나"},
        {"k": "[281] 입고 문", "v": "<code>stage_measured</code> 하나", "s": "선언 · <code>register_dataset</code> · run 출력이 같은 문으로 들어온다"},
        {"k": "기록 순서", "v": "표지 → 팻말 → 본문 → 도장", "s": "<code>run.json</code> → <code>.running</code> → <code>all.parquet</code> → <code>strategy.json</code>"},
        {"k": "명령 16개", "v": f"호출 {nc(SH)} ~ {nc(SL)}", "s": f"등록 {nc(R)} · factor run {nc(FA)} · stop-loss run {nc(SL)}"},
    ],
    "fix": (
        f"<strong>ms</strong>는 프로파일러 아래 값이라 실제보다 큽니다. 같은 트레이스 안에서만 비교하십시오. "
        f"첫 parquet 스캔은 {ms(R, 216)} ms, 두 번째는 {ms(R, 397)} ms입니다(식은 디스크)."
    ),
    "glossary": [],
}

ANALOGY = [
    ("송장", "선언 YAML", "<code>sample.yaml</code>"),
    ("검수대", "파일을 열어 재는 곳", "<code>data/verification.py</code>"),
    ("봉인 번호", "파일 지문 (sha256)", "<code>data/source.py</code>"),
    ("입고 문", "재고 → 걸리면 거절 → 잰 카드를 카트로", "<code>workspace/registration.py</code> <code>stage_measured</code>"),
    ("입고 카트", "모았다가 한 번에 쓰기", "<code>workspace/registry.py</code> <code>Transaction</code>"),
    ("장부", "등록부", "<code>.vqapr/workspace.yaml</code>"),
    ("출고 전 점검", "preflight (판정 + 얼리기)", "<code>run/preflight/</code>"),
    ("작업 키트", "FrozenRun", "<code>run/preflight/freeze.py</code>"),
    ("조립 라인", "RunLoop: 08:00 결정 → 15:30 체결", "<code>run/engine/</code>"),
    ("작업대", "메모리의 행 버퍼", "<code>record/writer.py</code>"),
    ("작업일지 · 도장", "run 기록 · <code>strategy.json</code>", "<code>.vqapr/runs/</code>"),
    ("반제품", "run이 만든 dataset", "<code>.vqapr/materialized/</code>"),
    ("재료판", "cube (<code>--jobs</code>)", "<code>data/cube.py</code>"),
]

MAP = [
    ("①", "데이터 등록", "송장 → 입고 문 → 장부"),
    ("②", "등록 거절", "없는 컬럼"),
    ("③", "바뀐 파일", "점검 · 다시 등록"),
    ("④", "DataModel", "반제품을 만들어 입고"),
    ("⑤", "factor 전략", "롱 3 · 숏 3"),
    ("⑥", "stop-loss", "수첩(memory)"),
    ("⑦", "enhanced index", "반제품을 재료로"),
    ("⑧", "--jobs 배치", "cube 한 번 굽기"),
]

CHRONICLE_NOTES = {
    B: "거절",
    CK: "직전에 <code>execution.parquet</code>을 바꿔 둠 · 거절",
    RA: "잰 값만 교체. 이후 원본으로 되돌림",
    BA: "cube는 만들었다 지움 · 일지는 작업자가 다시 씀",
    WK: "작업자 단독 추적 — 파일 목록 없음",
}

SRCMAP_LEDE = "프레임이 선 파일을 포함한 199개 파일 설명. 0.16.0 판에서 옮기고, 등록 정리가 바꾼 일곱 파일의 설명과 줄 수를 f862c147에 맞췄습니다."

SCENES = [
    {
        "id": "reg", "key": "①", "title": "데이터 등록",
        "sub": f"register sample.yaml · {el(R)} ms · {nc(R)} 호출",
        "story": "송장(<code>sample.yaml</code>)의 dataset마다 입고 문을 지납니다. 검수대가 parquet을 직접 열어 재고, 전부 통과해야 장부를 한 번에 씁니다.",
        "shelf": [R],
        "frames": [
            F(R, 0, "[280] 송장을 창구에 낸다", "송장을 읽는 함수는 이제 등록 쪽에 있고, 창구는 불러 쓸 뿐입니다. 결과는 JSON 영수증 한 장입니다.",
              chain(R, (12, "register.run"), (13, "read_declaration"), (14, "apply")),
              fn="main()", code=at("src/vqapr/cli/main.py", "def main(", 8),
              disk={".vqapr/": "없음"}),
            F(R, 14, "[280] 입고 카트를 연다", "함수 하나가 카트를 열어 모았다가 끝에 한 번 씁니다(예전엔 둘). 하나라도 거절되면 장부는 그대로입니다.",
              chain(R, (16, "Workspace.transaction"), (44, "_instruments"), (137, "stage_measured"), (475, "_component"), (915, "Transaction.commit")),
              fn="apply()", code=at(REG, 'for dataset_id, body in section("datasets")', 7)),
            F(R, 47, "종목 명단부터", f"종목 명단 파일(<code>instruments_stock.parquet</code>: 종목 코드 · 종류, 10행)을 엽니다. {ms(R, 47)} ms는 pyarrow를 처음 올리는 비용입니다.",
              chain(R, (47, "verify_roster"), (51, "build_roster")),
              fn="verify_roster()", code=("def", 8), data="roster"),
            F(R, 137, "[281] 입고 문 — 하나", "dataset은 모두 이 문으로 들어옵니다: 재고, 걸리면 거절, 통과하면 잰 카드를 카트에. run이 만든 출력도 같은 문입니다.",
              chain(R, (137, "stage_measured"), (138, "verify_source"), (284, "raise_if_failed"), (285, "Transaction.register_dataset")),
              fn="stage_measured()", code=at(REG, "def stage_measured(", 15)),
            F(R, 138, "[281] 검수대 — 이름, 그리고 여섯 가지", "카드와 파일의 이름부터 맞춰 보고, 컬럼 → 키 중복 → 기간 → NaN → 체결 가격 → 지문. 파일 내용을 보는 곳은 여기뿐입니다.",
              chain(R, (139, "mismatched_source"), (140, "describe"), (152, "check_schema"), (195, "check_key"), (216, "check_span"), (227, "check_values"), (281, "physical_digest")),
              fn="verify_source()", code=at("src/vqapr/data/verification.py", "def verify_source", 8), data="prices",
              mem={"sample-prices": "기간 2022-01-03 ~ 2024-12-30 · 지문 18bb7017…"}),
            F(R, 442, "체결표도 같은 문으로", "거래 가능한 행마다 가격이 양수인지 재서 <code>['close']</code>를 적어 둡니다.",
              chain(R, (332, "stage_measured"), (333, "verify_source"), (442, "check_execution_prices")),
              fn="check_execution_prices()", code=("def", 8), data="execution",
              mem={"sample-execution": "체결 가격 ['close'] · 지문 49e4b4ab…"}),
            F(R, 560, "부품 시운전", "전략 · 거래소 코드를 import해 필요한 메서드가 있는지 봅니다.",
              chain(R, (479, "fingerprint_component"), (560, "conformance"), (732, "conformance")),
              fn="conformance()", code=("def", 8)),
            F(R, 915, "카트를 장부로", "잠금을 잡고 장부를 다시 읽어, 카트의 카드를 한 번 더 합칩니다.",
              chain(R, (915, "Transaction.commit"), (922, "_merge_dataset"), (939, "Workspace._write")),
              fn="Transaction.commit()", code=("def", 10)),
            F(R, 975, "임시 파일에 쓰고 바꿔 끼운다", "그래서 반쯤 쓴 장부는 보이지 않습니다. 여기서 처음 파일이 생깁니다.",
              chain(R, (975, "write_atomically"), (976, "_swap"), (978, "Workspace._write_roster")),
              fn="write_atomically()", code=at("src/vqapr/_internal/atomic.py", "staged = Path(staged_name)", 10), data="ledger_prices",
              disk={".vqapr/workspace.yaml": "생김", ".vqapr/instruments.json": "생김"}),
        ],
        "remember": ["dataset은 모두 입고 문 하나로 — 재고, 거절하거나, 잰 카드를 담는다.", "장부는 카트에 모아 한 번에, 원자적으로 쓴다."],
    },
    {
        "id": "bad", "key": "②", "title": "등록 거절",
        "sub": f"register bad.yaml · {el(B)} ms · {nc(B)} 호출",
        "story": "파일에 없는 컬럼(<code>adj_close</code>)을 적은 송장입니다. 입고 문 안의 검수대에서 걸려, 카트에 아무것도 담기지 않습니다.",
        "shelf": [B],
        "frames": [
            F(B, 402, "없는 컬럼 — 첫 단계에서 멈춘다", "<code>adj_close</code>가 파일에 없어 뒤 단계는 돌지 않습니다.",
              chain(B, (387, "stage_measured"), (388, "verify_source"), (402, "check_schema")),
              fn="check_schema()", code=("def", 8), data="prices"),
            F(B, 418, "[281] 문에서 되돌린다", "실패가 담긴 판정을 예외로 바꿔 던집니다. 문은 카트에 담는 줄까지 가지 않습니다.",
              chain(B, (387, "stage_measured"), (418, "raise_if_failed")),
              fn="Diagnosis.raise_if_failed()", code=("def", 6)),
            F(B, 424, "거절 봉투", f"code · 이유 · 고치는 법 · 위치가 담깁니다. 쓰기 호출 {writes(B)}, 장부 그대로.",
              chain(B, (424, "failure")),
              fn="envelope.failure()", code=("def", 8),
              disk={".vqapr/workspace.yaml": "그대로"}),
        ],
        "remember": ["검수에 걸리면 카트에 담기지 않는다.", "거절은 장부를 바꾸지 않는다."],
    },
    {
        "id": "changed", "key": "③", "title": "바뀐 파일",
        "sub": f"check sample-run · {nc(CK)} 호출 — 다시 등록 · {nc(RA)} 호출",
        "story": "등록 뒤 <code>execution.parquet</code>에서 마지막 날을 지웠습니다. 점검이 지문으로 잡고, 같은 송장으로 다시 등록하면 잰 값만 바뀝니다. <b>[바뀔 예정]</b> 바뀐 파일은 거절 대신 다시 검수(오너 판정 9/13).",
        "shelf": [CK, RA],
        "frames": [
            F(CK, 340, "점검 — preflight", "check와 run이 같은 함수를 지납니다. 판정과 얼리기가 같은 사실을 한 번 읽습니다.",
              chain(CK, (340, "preflight"), (342, "judgments"), (49684, "freeze")),
              fn="preflight()", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 8, before=1)),
            F(CK, 342, "판정 일곱, 사실은 한 번", f"시간표는 처음 한 번 만들고({ms(CK, 369)} ms) 이후엔 돌려주기만 합니다.",
              chain(CK, (365, "_judge_execution_ordering"), (367, "_once"), (369, "derived_schedule")),
              fn="judgments()", code=at("src/vqapr/run/preflight/facts.py", "def _once(", 10)),
            F(CK, 365, "실제로 걷는 날만", "run 기간의 조각(<code>inclusive_slice</code>)만 검사합니다.",
              chain(CK, (43683, "inclusive_slice"), (47352, "RunFacts.execution_table")),
              fn="_judge_execution_ordering()", code=at("src/vqapr/run/preflight/checks.py", "events = facts.schedule().inclusive_slice(", 4)),
            F(CK, 47367, "지문 대조", "장부 <code>49e4b4ab…</code> ≠ 지금 <code>34c1d63c…</code> → <code>source_changed</code>(412). 파일은 다시 읽지 않습니다.",
              chain(CK, (47365, "physical_digest"), (47367, "require_verified")),
              fn="require_verified()", code=at("src/vqapr/data/verification.py", "def require_verified", 8)),
            F(RA, 651, "같은 송장으로 다시 등록", "두 dataset이 입고 문을 다시 지나며 파일을 다시 잽니다.",
              chain(RA, (455, "stage_measured"), (456, "verify_source"), (650, "stage_measured"), (651, "verify_source")),
              fn="verify_source()", code=("def", 8)),
            F(RA, 787, "[281] 잰 값만 교체", "이름 대조는 검수대와 같은 규칙입니다(어긋나면 400). 당신이 쓴 부분이 같으면 기간 · 지문만 바꾸고, 다르면 409로 거절합니다.",
              chain(RA, (787, "_merge_dataset"), (788, "mismatched_source"), (1263, "Workspace._write")),
              fn="_merge_dataset()", code=at("src/vqapr/workspace/merge.py", "remeasured = replace(", 7),
              disk={".vqapr/workspace.yaml": "지문 49e4b4ab… → 34c1d63c…"}),
        ],
        "remember": ["바뀐 파일은 지문으로 잡는다 — 지금은 거절, 앞으로는 다시 검수.", "다시 등록하면 잰 값만 바뀐다."],
    },
    {
        "id": "dm", "key": "④", "title": "DataModel",
        "sub": f"run sample-features-run · {el(DM)} ms · {nc(DM)} 호출 · 16일 · 108행",
        "story": "DataModel이 16일간 5일 모멘텀을 계산해 108행 dataset으로 등록합니다. run 기록이 처음 생깁니다.",
        "shelf": [RF, DM],
        "frames": [
            F(DM, 475, "run도 점검을 받는다", f"판정 {ms(DM, 477)} ms, 얼리기 {ms(DM, 1798)} ms. 모델 import는 판정이 한 것을 재사용합니다.",
              chain(DM, (475, "preflight"), (477, "judgments"), (1798, "freeze")),
              fn="preflight()", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 8, before=1)),
            F(DM, 2016, "키트에 지문을 싣는다", "입력 파일이 등록 때 그대로인지 지문만 봅니다.",
              chain(DM, (2005, "Workspace.require_verified"), (2016, "require_verified")),
              fn="require_verified()", code=("def", 8)),
            F(DM, 2056, "공구 봉지", "점검이 만든 객체를 그대로 넘겨받습니다. 다시 만들지 않습니다.",
              chain(DM, (2056, "RunResources.of"), (2066, "run")),
              fn="RunResources.of()", code=("def", 8)),
            F(DM, 2116, "선반은 기간을 안다", "이후 모든 읽기가 01-04 ~ 01-25로 잘립니다.",
              chain(DM, (2113, "_run_member"), (2116, "_horizon")),
              fn="_horizon()", code=("def", 8)),
            F(DM, 2119, "표지 run.json이 먼저", "중간에 죽어도 무엇을 하려 했는지 남깁니다.",
              chain(DM, (2119, "freeze_run_record"), (2162, "write_atomically")),
              fn="freeze_run_record()", code=at("src/vqapr/run/recording.py", "def freeze_run_record", 8),
              disk={".vqapr/runs/sample-features-run/run.json": "생김"}),
            F(DM, 2167, "작업 중 팻말", "기록 칸과 <code>.running</code>(pid)을 만듭니다. 같은 run을 동시에 돌리면 거절됩니다.",
              chain(DM, (2167, "RunRecordWriter.open"), (2404, "write_atomically", ": progress.json")),
              fn="RunRecordWriter.open()", code=at("src/vqapr/record/writer.py", "def _claim(self)", 10),
              disk={FEAT_DIR + ".running": "생김", FEAT_DIR + "progress.json": "생김"}),
            F(DM, 2181, "라인 하나, 사건은 시간표가", "<code>ScheduledEvent</code> 16개를 시각 순서로 처리합니다. 시장 시계는 없습니다.",
              chain(DM, (2181, "datamodel_loop"), (2297, "RunLoop.run"), (7737, "RunLoop.finish")),
              fn="datamodel_loop()", code=at("src/vqapr/run/engine/loop.py", "def datamodel_loop", 8)),
            F(DM, 2485, "읽을 범위부터", f"6행 lookback을 위해 01-03 15:30부터 읽습니다(첫 스캔 {ms(DM, 3233)} ms).",
              chain(DM, (2485, "_scan_bounds"), (3233, "observation_table")),
              fn="_scan_bounds()", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 8, before=2),
              mem={"범위": "2022-01-03 15:30 ~ 01-25 23:00"}),
            F(DM, 3270, "행렬 17 × 10", "이후 계산은 이 행렬을 복사 없이 봅니다.",
              chain(DM, (3270, "Panel.from_table"), (3282, "PanelWindow.matrix")),
              fn="Panel.from_table()", code=("def", 8),
              mem={"panel": "(17, 10)"}),
            F(DM, 2449, "첫날 — 빈 결과", "종가가 2개뿐이라 빈 목록을 돌려줍니다.",
              chain(DM, (2449, "SampleFeatures.compute"), (3290, "RunOutput.append")),
              fn="SampleFeatures.compute()", code=at(DECL + "features.py", "closes = window.matrix()", 6), author=True),
            F(DM, 3639, "다섯째 날 — 9행", "한 식으로 9종목을 계산합니다. 행은 아직 메모리에만 있습니다.",
              chain(DM, (3639, "SampleFeatures.compute"), (3938, "RunOutput.append")),
              fn="SampleFeatures.compute()", code=at(DECL + "features.py", "momentum = closes[-1]", 6, before=2), author=True,
              mem={"메모리": "9행 … 16일째 108행"}),
            F(DM, 7771, "[281] dataset으로 등록", "<code>all.parquet</code> 108행을 쓰고 ①과 같은 입고 문을 지나 장부에 올립니다.",
              chain(DM, (7800, "RunOutput._seal"), (7820, "stage_measured"), (7821, "verify_source"), (7951, "Workspace._write")),
              fn="RunOutput.register()", code=at("src/vqapr/run/engine/output.py", "# The rows land here, once, and only now", 6), data="features",
              disk={".vqapr/materialized/sample-features/all.parquet": "생김 · 108행", ".vqapr/workspace.yaml": "+ sample-features"}),
            F(DM, 8030, "마감 도장", "<code>datamodel.json</code>을 쓰고 팻말을 치웁니다. 도장이 있으면 본문이 있습니다.",
              chain(DM, (8030, "RunRecordWriter.finish"), (8150, "write_atomically"), (8152, "RunRecordWriter._unlock")),
              fn="RunRecordWriter.finish()", code=at("src/vqapr/record/writer.py", "# The tables land BEFORE the record", 3),
              disk={FEAT_DIR + "datamodel.json": "생김", FEAT_DIR + ".running": "지움"}),
        ],
        "remember": ["run도 preflight 한 번.", "run의 출력도 입고 문으로 들어간다."],
    },
    {
        "id": "factor", "key": "⑤", "title": "factor 전략",
        "sub": f"run sample-factor-run · {el(FA)} ms · {nc(FA)} 호출 · 10일 · 사건 20",
        "story": "④의 모멘텀으로 상위 3 매수 · 하위 3 공매도. 08:00 결정, 15:30 체결. 행은 끝까지 메모리에 있다가 한 번에 기록됩니다.",
        "shelf": [FR, FA],
        "frames": [
            F(FA, 730, "점검 — 12일만 읽는다", f"시간표는 run 기간 ±1일만 읽고, 얼리기는 그것을 받아 씁니다({ms(FA, 1904)} ms).",
              chain(FA, (756, "_judge_execution_ordering"), (774, "distinct_values"), (1904, "RunFacts.schedule")),
              fn="preflight()", code=("def", 8)),
            F(FA, 2290, "dataset은 출처를 가리지 않는다", "run이 만든 <code>sample-features</code>도 지문으로 묶습니다.",
              chain(FA, (2290, "_validate_requirement"), (2291, "Workspace.require_verified")),
              fn="_validate_requirement()", code=("def", 8)),
            F(FA, 2351, "공구 봉지", "전략 · 거래소 · 기간을 꺼내기만 합니다.",
              chain(FA, (2351, "RunResources.of"), (2367, "run")),
              fn="RunResources.of()", code=("def", 8)),
            F(FA, 2376, "종목 명단은 매번 새로", "명단은 늘어나므로 얼리지 않습니다(이슈 009).",
              chain(FA, (2376, "registered_roster"), (2383, "verify_roster")),
              fn="registered_roster()", code=("def", 8)),
            F(FA, 2567, "표지 · 팻말 · 진행 메모", "run이 도는 동안 디스크엔 이 셋뿐입니다.",
              chain(FA, (2490, "freeze_run_record"), (2567, "RunRecordWriter.open"), (3118, "write_atomically", ": progress.json")),
              fn="RunRecordWriter.open()", code=at("src/vqapr/record/writer.py", "def _claim(self)", 10),
              data="run_json", disk={".vqapr/runs/sample-factor-run/run.json": "생김", FACTOR_DIR + ".running": "생김", FACTOR_DIR + "progress.json": "생김"}),
            F(FA, 3270, "읽을 범위 — 11 × 10", "run 기간만큼 행렬을 만듭니다.",
              chain(FA, (3270, "_scan_bounds"), (3295, "observation_table"), (3332, "Panel.from_table")),
              fn="_scan_bounds()", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 8, before=2)),
            F(FA, 3228, "여섯 종목을 고른다", "하위 3에 −1/6, 상위 3에 +1/6. 사건은 <code>ScheduledEvent</code>, 시각은 <code>call.at</code>.",
              chain(FA, (3120, "RunLoop.handle"), (3228, "SampleFactor.decide"), (3563, "_stamp_intent")),
              fn="SampleFactor.decide()", code=at(DECL + "factor.py", "def decide(self, call):", 10), author=True, data="factor_weight"),
            F(FA, 3823, "행은 메모리에", f"weight 행을 Arrow 버퍼에 쌓을 뿐 파일은 쓰지 않습니다(이 run {count(FA, 'RunRecordWriter.append_chunk')}번).",
              chain(FA, (3821, "RunStateRepository.publish"), (3823, "RunRecordWriter.append_chunk")),
              fn="append_chunk()", code=at("src/vqapr/record/writer.py", "def append_chunk(self, chunk: RecordChunk)", 8)),
            F(FA, 3858, "15:30 체결", "+23 · +8 · +94 / −55 · −19 · −12주. 현금 99,463,501.24.",
              chain(FA, (3850, "RunLoop.handle"), (3858, "ExecutionHandler.fill"), (4332, "AcademicExchange.execute")),
              fn="ExecutionHandler.fill()", code=("def", 8), data="factor_fill",
              mem={"계좌 v1": "롱 3 · 숏 3 · NAV 1억"}),
            F(FA, 4892, "계좌가 스스로 평가", "<code>Account.mark</code>가 보유 × 가격을 계산합니다.",
              chain(FA, (4892, "ValuationHandler.mark"), (4941, "Account.mark")),
              fn="ValuationHandler.mark()", code=("def", 8), data="factor_account"),
            F(FA, 24218, "마감 — 본문, 그다음 도장", "<code>all.parquet</code> 셋(70 · 73 · 60행) → <code>strategy.json</code> → 팻말 치움.",
              chain(FA, (24221, "_write_compact"), (24267, "write_atomically"), (24269, "RunRecordWriter._unlock")),
              fn="RunRecordWriter._seal()", code=at("src/vqapr/record/writer.py", "def _seal(self)", 8),
              disk={FACTOR_DIR + "tables/ (3)": "생김", FACTOR_DIR + "strategy.json": "생김", FACTOR_DIR + ".running": "지움"}),
            F(FA, 24476, "[281] 비중을 dataset으로", "60행을 <code>materialized/</code>에 쓰고 같은 입고 문을 지나 장부에 올립니다.",
              chain(FA, (24476, "RunOutput.register"), (24520, "stage_measured"), (24651, "Workspace._write")),
              fn="RunOutput.register()", code=("def", 8),
              disk={".vqapr/materialized/sample-factor-weights/": "생김 · 60행"}),
        ],
        "remember": ["도는 동안 디스크엔 표지 · 팻말 · 메모뿐.", "본문 → 도장 → 팻말 치움 → 출력 dataset."],
    },
    {
        "id": "stop", "key": "⑥", "title": "stop-loss",
        "sub": f"run sample-stoploss-run · {el(SL)} ms · {nc(SL)} 호출 · 37일",
        "story": "진입가를 <code>self.memory</code>에 적고 3% 빠지면 팝니다. 9종목으로 시작해 02-23에 전부 팝니다.",
        "shelf": [SR, SL],
        "frames": [
            F(SL, 6434, "memory 복원", "결정 전마다 memory를 복원합니다. 첫날은 비어 있습니다.",
              chain(SL, (6415, "_visible_callback_state"), (6434, "_restore_callback_state")),
              fn="_restore_callback_state()", code=("def", 8)),
            F(SL, 6551, "행렬 하나로 37일", "38 × 10 행렬 하나를 모든 결정이 나눠 봅니다.",
              chain(SL, (6551, "_scan_bounds"), (9990, "_scan_bounds")),
              fn="_scan_bounds()", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 8, before=2)),
            F(SL, 6515, "첫 결정 — 9종목 진입", "종가 9개를 memory에 적고 같은 비중으로 삽니다.",
              chain(SL, (6515, "SampleStopLoss.decide")),
              fn="SampleStopLoss.decide()", code=at(DECL + "stoploss.py", 'if not self.memory.get("entered"):', 8, before=4), author=True),
            F(SL, 7750, "결정 후 저장", "memory를 JSON으로 정리해 계좌와 함께 저장합니다.",
              chain(SL, (7750, "_candidate_callback_state"), (7947, "publish")),
              fn="_candidate_callback_state()", code=("def", 8)),
            F(SL, 9956, "둘째 날 첫 손절", "K000005가 −3%를 넘어 팝니다. 보유: 9 → 8 → 7 → 5 → 4 → 3 → 2 → 1.",
              chain(SL, (9873, "_restore_callback_state"), (9956, "SampleStopLoss.decide")),
              fn="SampleStopLoss.decide()", code=at(DECL + "stoploss.py", "for name, price in list(entry.items()):", 5), author=True, data="stop_weight"),
            F(SL, 58156, "전부 팔 땐 빈 Rebalance", "Hold면 포지션이 남습니다. K000008 −52주, 현금 84,184,068.92.",
              chain(SL, (58156, "SampleStopLoss.decide"), (58596, "fill")),
              fn="SampleStopLoss.decide()", code=at(DECL + "stoploss.py", "held = {name: 1 for name in sorted(entry)}", 7), author=True, data="stop_last"),
            F(SL, 59285, "그 뒤는 Hold", "주문이 없으니 오후엔 평가만 합니다.",
              chain(SL, (59285, "SampleStopLoss.decide"), (59668, "ValuationHandler.mark")),
              fn="SampleStopLoss.decide()", code=at(DECL + "stoploss.py", "if any(quantity != 0 for quantity in call.account.positions.values()):", 4), author=True),
        ],
        "remember": ["상태는 memory에만 — 결정마다 복원 · 저장.", "전부 비울 땐 빈 Rebalance."],
    },
    {
        "id": "enh", "key": "⑦", "title": "enhanced index",
        "sub": f"run sample-enhanced-run · {el(EN)} ms · {nc(EN)} 호출 · 9일",
        "story": "⑤가 남긴 비중을 alpha로 읽어 롱온리 지수를 만듭니다. run이 만든 dataset도 원본 파일과 똑같이 읽힙니다.",
        "shelf": [ER, EN, LD, SH],
        "frames": [
            F(EN, 2621, "alpha도 지문으로", "run이 만든 파일과 원본 파일이 같은 취급을 받습니다.",
              chain(EN, (2621, "_validate_requirement"), (2640, "_validate_requirement")),
              fn="_validate_requirement()", code=("def", 8)),
            F(EN, 3610, "1/9에 alpha의 절반", "01-13 08:00의 비중을 읽어 0.1944 · 0.0278 · 0.1111로 나눕니다.",
              chain(EN, (3610, "SampleEnhancedIndex.decide"), (4431, "Panel.from_table"), (4543, "Panel.from_table")),
              fn="SampleEnhancedIndex.decide()", code=at(DECL + "enhanced.py", "tilted = {", 5), author=True, data=["factor_alpha", "enhanced_weight"]),
            F(EN, 5223, "롱온리 체결", "9종목을 삽니다. 9일 뒤 계좌 v9.",
              chain(EN, (5223, "ExecutionHandler.fill"), (27420, "RunOutput.register")),
              fn="ExecutionHandler.fill()", code=("def", 8)),
            F(LD, 13, "list datasets — 6개", "그중 4개가 run이 만든 것입니다. 파일은 생기지 않습니다.",
              chain(LD, (13, "Workspace.open"), (1087, "success")),
              fn="Workspace.open()", code=("def", 6)),
            F(SH, 19, "show run — 기록만 읽는다", "읽은 파일의 지문이 run.json에 남아 있습니다.",
              chain(SH, (19, "read_run_record"), (29, "success")),
              fn="read_run_record()", code=("def", 8)),
        ],
        "remember": ["run의 출력은 다음 run의 입력.", "list · show는 읽기만 한다."],
    },
    {
        "id": "jobs", "key": "⑧", "title": "--jobs 배치",
        "sub": f"run … --jobs 2 · {nc(BA)} 호출 (지휘) · 작업자 {nc(WK)} 호출",
        "story": "⑤와 ⑥을 동시에. 지휘 프로세스가 입력을 cube로 한 번 굽고, 작업자는 그걸 매핑해 읽습니다. 끝나면 cube를 지웁니다.",
        "shelf": [BA, WK],
        "frames": [
            F(BA, 13, "서로 독립인지", "각 run이 읽는 것을 묻고, 서로의 출력을 읽지 않는지 봅니다.",
              chain(BA, (1076, "batch_reads"), (1249, "require_independent_batch")),
              fn="_run_each_in_workers()", code=("def", 8)),
            F(BA, 1258, "굽기 준비", "배치 폴더를 만들고 잠급니다.",
              chain(BA, (1258, "batch_cubes"), (1260, "_bake_for_batch")),
              fn="batch_cubes()", code=("def", 8),
              disk={".vqapr/cubes/<batch>/": "생김"}),
            F(BA, 1375, "굽기", "close를 735 × 10 행렬 파일로 한 번 저장합니다.",
              chain(BA, (1273, "bake"), (1375, "bake")),
              fn="bake()", code=("def", 8), data="cube",
              disk={".vqapr/cubes/<batch>/sample-prices/close.npy": "(735, 10) 58,928 B"}),
            F(BA, 2918, "작업자 호출", "여기부터는 다른 프로세스라 트레이스를 따로 떴습니다.",
              chain(BA, (2918, "in_workers")),
              fn="in_workers()", code=("def", 8)),
            F(WK, 16, "작업자도 preflight", "check가 거절할 run은 작업자도 거절합니다.",
              chain(WK, (16, "preflight"), (1194, "freeze"), (1649, "RunResources.of")),
              fn="preflight()", code=at("src/vqapr/run/assemble.py", "def run_registered_strategy", 8)),
            F(WK, 2616, "스캔 대신 매핑", f"cube의 지문이 맞으면 파일을 매핑해 읽습니다. 스캔 {count(WK, 'observation_table')}회.",
              chain(WK, (2590, "open_cube"), (2616, "panel_from_cube")),
              fn="panel_from_cube()", code=("def", 8)),
            F(BA, 2921, "끝나면 cube 삭제", "성공이든 실패든 지웁니다. 결과 봉투는 run마다 하나.",
              chain(BA, (2921, "batch_cubes"), (3506, "success")),
              fn="batch_cubes()", code=at("src/vqapr/run/batch.py", "def batch_cubes", 8),
              disk={".vqapr/cubes/<batch>/": "지움"}),
        ],
        "remember": ["작업자도 같은 점검을 받는다.", "cube는 한 번 굽고, 끝나면 없다."],
    },
]

TABLE = {
    "title": "트레이스로 확인한 것",
    "rows": [
        ("[281] 입고 문 하나", f"01 {h(R, 137, 'stage_measured')} · {h(R, 332, 'stage_measured')} · 02 {h(B, 387, 'stage_measured')} · 06 {h(DM, 7820, 'stage_measured')} · 08 {h(FA, 24520, 'stage_measured')} · 12 {h(EN, 27464, 'stage_measured')}", "선언 · 거절 · run 출력이 같은 문을 지난다"),
        ("[281] 이름 대조는 규칙 하나", f"01 {h(R, 139, 'mismatched_source')} 검수대 · {h(R, 290, 'mismatched_source')} 카트", "검수대와 장부 합치기가 같은 함수를 묻는다 · 400"),
        ("[280] 송장 읽기", f"01 {h(R, 13, 'read_declaration')} → {h(R, 14, 'apply')}", "등록 쪽이 읽고, 적용은 함수 하나"),
        ("preflight · freeze", f"03 {h(CK, 340, 'preflight')} · 06 {h(DM, 475, 'preflight')} · 08 {h(FA, 730, 'preflight')} · 16 {h(WK, 16, 'preflight')}", "check · run · 작업자가 같은 함수를 지난다"),
        ("schedule", f"03 {h(CK, 369, 'derived_schedule')} {ms(CK, 369)} ms(734일) · 08 {h(FA, 760, 'derived_schedule')} {ms(FA, 760)} ms", "run 기간만큼만 시간표를 만든다"),
        ("쓰기는 .vqapr/ 뿐", f"원본 {ORIGINALS}개는 쓰지 않음 · 거절 두 번(02 · 03)엔 쓰기 호출 {writes(B) + writes(CK)}", "등록은 읽기만 한다"),
        ("기록 순서", f"08: {h(FA, 2490, 'freeze_run_record')} → {h(FA, 2567, 'RunRecordWriter.open')} → {h(FA, 3118, 'write_atomically')} → {h(FA, 24221, '_write_compact')} → {h(FA, 24267, 'write_atomically')} → {h(FA, 24269, '_unlock')} → {h(FA, 24651, 'Workspace._write')}", "도장이 있으면 본문이 있다"),
        ("결과 숫자 (주문 · 체결 · 계좌)", f"factor {outcome(FA, 'sample-factor')} · stop-loss {outcome(SL, 'sample-stoploss')} · enhanced {outcome(EN, 'sample-enhanced')}", "0.16.0 판과 같다"),
        ("[바뀔 예정] source_changed", f"03 {h(CK, 47367, 'require_verified')}", "바뀐 파일은 다시 검수 (오너 판정 9/13, 구조 보류)"),
    ],
}
