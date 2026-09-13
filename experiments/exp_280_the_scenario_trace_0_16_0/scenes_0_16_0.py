# ruff: noqa: E501, RUF001, F821 -- prose data: long lines and typographic characters are the content; REPO and TRACES are bound by the renderer
# The 0.16.0 scenario stepper, traced again on develop 26726b1f and written around one picture: a
# warehouse. The seven scenarios are exp_235's; the declarations are exp_235's moved to the 0.16.0
# author surface (`from vqapr import public as vq`, `schedule:`), in `declarations/` beside this file.
#
# Rendered by `render_0_16_0.py`, which executes this file with `REPO` and `TRACES` bound. A frame
# names its trace and call index; the renderer fills in the definition line, the qualified name,
# the milliseconds and the code window. Every call named in a frame's folded chain is written with
# `c(trace, idx, label)`, which reads the milliseconds from the trace and refuses a label that is
# not the qualname at that index -- so no number of calls, index or millisecond is typed by hand.
# The outcome numbers (fills, cash, weights) are read from the records the traced runs wrote
# (`README.md` beside this file says how).

DECL = "experiments/exp_280_the_scenario_trace_0_16_0/declarations/"


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


def c(trace: str, idx: int, label: str | None = None, note: str = "", timed: bool = True) -> str:
    """`<code>label</code>(#idx, ms)` -- refusing a label that is not the call at that index."""
    call = _call(trace, idx)
    qualname = call["qualname"]
    if label is not None:
        want = label.split("(")[0].strip().split(".")[-1]
        assert qualname.split(".")[-1] == want, f"{trace} #{idx}: {label!r} is {qualname!r}"
    shown = label or qualname
    took = f", {fmt(call['ms'])} ms" if timed and call["ms"] is not None else ""
    return f"<code>{shown}</code>(#{idx}{took}{note})"


def count(trace: str, name: str) -> int:
    return sum(
        1 for call in TRACES[trace]["calls"] if call["qualname"] == name or call["qualname"].endswith("." + name)
    )


def nc(trace: str) -> str:
    return f"{len(TRACES[trace]['calls']):,}"


def el(trace: str) -> str:
    return f"{TRACES[trace]['elapsed_ms']:,.0f}"


def W(story: str, calls: str | None = None) -> str:
    """A frame's prose: the plain story first, the trace's call order folded beneath it."""
    html = f'<p class="story">{story}</p>'
    if calls:
        html += f'<details class="tr"><summary>함수 이름과 호출 번호로 보면</summary><p>{calls}</p></details>'
    return html


def F(trace: str, idx: int, title: str, story: str, calls: str | None = None, **extra) -> dict:
    return {"trace": trace, "idx": idx, "title": title, "what": W(story, calls), **extra}


R, B, RA = "01_register", "02_register_bad", "04_register_again"
CK, RF, DM = "03_check_changed", "05_register_features", "06_run_features"
FR, FA, SR, SL = "07_register_factor", "08_run_factor", "09_register_stoploss", "10_run_stoploss"
ER, EN, LD, SH = "11_register_enhanced", "12_run_enhanced", "13_list_datasets", "14_show_run_enhanced"
BA, WK = "15_run_batch", "16_worker_factor"

FACTOR_DIR = ".vqapr/runs/sample-factor-run/strategies/sample-factor@0696c8f4/"
STOP_DIR = ".vqapr/runs/sample-stoploss-run/strategies/sample-stoploss@6db3d49b/"
FEAT_DIR = ".vqapr/runs/sample-features-run/datamodels/sample-features@4327b244/"

HEADER = {
    "title": "vqapr 0.16.0 시나리오 디버거",
    "storage_key": "vqapr-stepper-0160-shelf",
    "eyebrow": "vqapr 0.16.0 · develop 26726b1f · 2026-09-14 · 16개 명령을 sys.setprofile로 다시 추적 · 창고 비유판",
    "h1": "vqapr 0.16.0 시나리오 디버거 — 일곱 가지 일을 창고 한 채로, 파일이 생기는 순서까지",
    "lede": (
        "<b>이 페이지는 vqapr이 실제로 무엇을 하는지를, 실제로 돌린 기록으로 보여 줍니다.</b> "
        "<code>vqapr new sample</code>이 만든 작은 프로젝트(종목 10개, 2022-01-03 ~ 2024-12-30, 거래일 735일)에서 일곱 가지 일을 합니다: "
        "① 데이터를 <b>등록</b>하고, ② 등록이 <b>거절</b>되는 두 경우를 보고, ③ 종목별 지표(5일 모멘텀)를 만드는 <b>DataModel</b>을 돌리고, "
        "④ 그 지표로 상위 3개는 사고 하위 3개는 파는 <b>factor 전략</b>을, ⑤ 진입가를 <b>기억</b>해 3% 빠지면 파는 <b>stop-loss 전략</b>을 돌리고, "
        "⑥ ④가 남긴 비중을 읽어 <b>enhanced index</b>를 만들고, ⑦ ④와 ⑤를 <b>동시에</b>(<code>--jobs 2</code>) 돌립니다. "
        "<b>이 판의 새 점:</b> 모든 설명을 <b>창고 한 채</b>의 비유로 풀었고(아래 표), 장면마다 <b>그 명령이 디스크에 남긴 파일</b>을 트레이스의 파일 목록에서 뽑아 보여 줍니다(“창고” 상자, 그리고 “창고 연대기” 표). "
        "파일이 생기는 순간(장부 쓰기, run.json, 작업 중 팻말, 표 봉인, 마감 도장)은 따로 프레임을 두었습니다. "
        "<b>읽는 법:</b> 프레임마다 <b>위쪽 문장</b>은 보통 말이고, <b>아래 접힌 곳</b>에 함수 이름과 호출 번호(<code>#idx</code>)와 ms가 있습니다. 코드 아래 카드는 그 파일이 무슨 파일인지, 맨 아래 <b>src/ 지도</b>엔 <code>src/vqapr/</code>의 파일 199개가 있습니다. "
        "모든 번호와 ms는 <code>sys.setprofile</code>이 이번에 실제로 기록한 값이고(렌더러가 트레이스에서 직접 읽어 넣음), 체결 · 현금 · 비중은 그 run들이 쓴 기록에서 읽었습니다 — 상상한 것은 없습니다(<code>experiments/exp_280_the_scenario_trace_0_16_0/</code>)."
    ),
    "facts": [
        {"k": "한 줄 요약", "v": "송장 → 검수 → 장부 → 점검 → 라인 → 일지", "s": "사용자가 <b>송장</b>(YAML)을 내면 검수대가 상자(parquet)를 열어 재고 <b>장부</b>에 적는다. run은 출고 전 <b>점검</b>(preflight)을 받고 작업 키트를 <b>얼린</b> 뒤 조립 <b>라인</b>(루프)을 돌고, 결과는 <b>작업일지</b>(기록)와 반제품(dataset)이 되어 다시 창고에 들어온다"},
        {"k": "데이터", "v": "10 × 735", "s": "종목 × 거래일. run들은 2022년 1~2월의 짧은 구간만 쓴다: DataModel 16일 · factor 10일 · stop-loss 37일 · enhanced 9일"},
        {"k": "명령 16개", "v": f"호출 {nc(SH)} … {nc(SL)}", "s": f"register {nc(R)} · 거절 {nc(B)} · check(거절) {nc(CK)} · 재등록 {nc(RA)} · DataModel run {nc(DM)} · factor {nc(FA)} · stop-loss {nc(SL)} · enhanced {nc(EN)} · list {nc(LD)} · show {nc(SH)} · 배치 지휘자 {nc(BA)} · 일꾼 {nc(WK)}"},
        {"k": "창고에 쓰는 곳", "v": ".vqapr/ 하나", "s": "16개 명령의 트레이스에 기록된 쓰기는 모두 <code>.vqapr/</code> 아래다. 원본 parquet · py · yaml은 이름도 내용도 그대로 두고, 장부 · 작업일지 · 반제품만 생긴다"},
        {"k": "파일이 생기는 순서", "v": "표지 → 팻말 → 본문 → 도장", "s": "run 하나: <code>run.json</code>(표지) → <code>.running</code>(작업 중 팻말) → <code>progress.json</code>(진행 메모) → 행은 메모리에 → 끝에 <code>all.parquet</code> 셋(본문) → <code>strategy.json</code>(마감 도장) → 팻말 치움 → 비중이 반제품으로 → 장부에 입고"},
        {"k": "[0.16.0] 이름 · 자리", "v": "preflight · freeze · schedule", "s": "<code>verify_run</code> → <code>preflight</code>, <code>preflight_run</code> → <code>freeze</code>, <code>agenda</code> → <code>schedule</code>(루프가 받는 것은 <code>ScheduledEvent</code> · <code>MarketEvent</code>), <code>flow/</code> → <code>run/</code>, <code>project/</code> → <code>workspace/</code>, 저자 코드는 <code>from vqapr import public as vq</code>"},
        {"k": "factor run", "v": "롱 3 · 숏 3", "s": "첫날 K000003 +23주 · K000008 +8 · K000009 +94 / K000004 −55 · K000005 −19 · K000006 −12, 현금 99,463,501.24 · NAV 100,000,000 (수수료 0). 주문 73 · 체결 54 · 계좌 v10"},
        {"k": "stop-loss run", "v": "9 → 0", "s": "첫날 9종목 진입 → 손절이 이어져 01-26부터 K000008 하나 → 02-23에 52주 전량 매도 → 현금 84,184,068.92 (계좌 v34)"},
    ],
    "fix": (
        "<strong>ms를 읽을 때.</strong> 프로파일러가 켜진 채 잰 값이라 절대치는 실제보다 큽니다. 같은 트레이스 안에서 <b>서로 비교</b>만 하십시오. "
        f"이 판도 디스크 캐시가 식은 상태에서 떠서 등록의 첫 parquet 스캔(<code>check_span</code>)이 {ms(R, 214)} ms, 두 번째 표의 같은 단계는 {ms(R, 392)} ms입니다. "
        "구조를 견줄 땐 ms가 아니라 <b>호출 횟수</b>와 <b>같은 자리의 유무</b>를 보십시오."
    ),
    "glossary_title": "먼저 알아 두면 편한 낱말 열둘",
    "glossary": [
        ("선언 (declaration) = 송장", "당신이 쓰는 YAML. “이 parquet은 가격이다, 이 파일은 내 전략이다, 이 run은 이렇게 돌려라.” 창고는 송장을 믿지 않고 상자를 연다."),
        ("저자 표면 (vq)", "<code>from vqapr import public as vq</code>. 저자가 쓰는 이름(<code>StrategyModel</code> · <code>DataModel</code> · <code>Rebalance</code> · <code>Hold</code> · <code>DatasetInput</code> …)은 전부 <code>vqapr.public</code> 한 곳에 있다."),
        ("등록부 (workspace) = 장부", "<code>.vqapr/workspace.yaml</code>. <code>register</code>가 쓰고 모든 명령이 맨 처음 펼쳐 읽는다. 항목마다 <b>당신이 쓴 반쪽</b>(컬럼 · 키 · 타입)과 <b>검수대가 잰 반쪽</b>(기간 · 지문 · 체결 가격)이 있다."),
        ("파일의 문 = 검수대", "물리 파일을 실제로 열어 재는 <b>한 곳</b>(<code>data/verification.py</code>): 컬럼 · 키 · 기간 · 값 · 체결 가격 · 지문. 등록 때 한 번 재고, 그 뒤엔 내용이 아니라 <b>지문</b>만 대조한다."),
        ("digest = 봉인 번호", "파일 바이트의 sha256. 한 바이트라도 바뀌면 번호가 달라진다. 이 트리(26726b1f)는 번호가 다르면 거절한다 — <b>바뀔 예정</b>(오너 판정 2026-09-13: 다시 재고, 신고와 다를 때만 거절)."),
        ("preflight = 출고 전 점검", "“이 run을 돌려도 되나”에 답하는 판정 일곱과 얼리기를 한 번의 읽기로(<code>run/preflight/verdict.py</code>). <code>check</code>도 <code>run</code>도 <code>--jobs</code> 일꾼도 이 한 함수를 지난다."),
        ("freeze = 작업 키트", "장부의 <i>이름</i>들을 실제 <i>값</i>(코드 지문, parquet 경로와 지문, 시간표, 초기 계좌)으로 풀어 밀봉한 것 = <code>FrozenRun</code>. run 도중 장부가 바뀌어도 키트는 그대로다."),
        ("시간표와 사건 (schedule · event)", "선언의 <code>schedule:</code>이 결정 시각 목록을 만들고, 루프는 그 시각마다 <code>ScheduledEvent</code> 하나를, 체결 가격이 있는 시각마다 <code>MarketEvent</code> 하나를 시각 순서로 처리한다 — 조립 라인의 하루."),
        ("두 시계", "<b>시간표 시계</b>: 결정하는 시각(08:00 · 09:00 · 16:00). <b>시장 시계</b>: 체결표에 가격이 있는 시각(15:30). 아침에 주문서를 쓰고 오후에 체결 · 평가한다. 트레이스의 시각은 UTC라 06:30 = 15:30 KST."),
        ("창 (window) · panel = 재료판", "전략이 읽는 데이터의 사각형: 시각 × 종목 행렬. run 기간 + lookback만큼만 한 번 읽어 두고, 결정마다 복사 없이 그 일부(view)를 본다."),
        ("memory = 작업자의 수첩", "전략의 <code>self.memory</code>. 엄격한 JSON. 매 결정 전에 복원되고 뒤에 저장된다. 수첩에 적은 것만 믿을 수 있다."),
        ("run 기록 = 작업일지", "<code>.vqapr/runs/&lt;run&gt;/</code>. 표지(<code>run.json</code>)가 먼저, 본문(<code>tables/*/all.parquet</code>)이 끝에 한 번, 마감 도장(<code>strategy.json</code>)이 마지막. 도장이 있으면 본문이 다 있다는 뜻이다."),
    ],
}

ANALOGY = [
    ("창고 건물", "프로젝트 폴더", "<code>sample/</code> — 원본 상자(<code>observations.parquet</code> · <code>execution.parquet</code> · <code>*.py</code> · <code>*.yaml</code>)는 창고가 고치지 않는다"),
    ("사무실 서랍", "vqapr이 쓰는 유일한 곳", "<code>.vqapr/</code>"),
    ("송장", "선언 YAML", "<code>sample.yaml</code> · <code>features.yaml</code> · <code>factor.yaml</code> …"),
    ("창구", "명령줄", "<code>cli/main.py</code> → <code>cli/register.py</code> · <code>cli/run.py</code> · <code>cli/check.py</code>"),
    ("입고 카트", "Transaction — 담아 두었다가 한 번에 쓴다", "<code>workspace/registry.py</code> (<code>Transaction</code>) · 순서는 <code>workspace/registration.py</code>"),
    ("검수대 · 봉인 번호", "파일의 문 · digest", "<code>data/verification.py</code> (<code>verify_source</code> · <code>require_verified</code>) · <code>data/source.py</code> (<code>physical_digest</code>)"),
    ("부품 시운전", "코드를 import해 규격 확인", "<code>component/conformance.py</code> · <code>component/loading.py</code>"),
    ("장부 · 거래처 명단", "등록부 · 종목 명단", "<code>.vqapr/workspace.yaml</code> · <code>.vqapr/instruments.json</code>"),
    ("출고 전 점검 · 작업 키트 · 공구 봉지", "preflight · FrozenRun · RunResources", "<code>run/preflight/</code>(<code>verdict.py</code> · <code>checks.py</code> · <code>facts.py</code> · <code>freeze.py</code>)"),
    ("재료 선반 · 재료판", "store(run 기간을 앎) · panel", "<code>data/store.py</code> · <code>data/panel.py</code>"),
    ("조립 라인의 하루", "RunLoop: 08:00 결정 → 15:30 체결 · 평가 · 규칙", "<code>run/engine/loop.py</code> · <code>run/engine/stages/</code>(decide · accrue · execute · value · observe)"),
    ("작업자의 수첩", "<code>self.memory</code>", "<code>run/engine/stages/decide.py</code>가 복원하고 저장한다"),
    ("작업대", "메모리의 Arrow 버퍼 — 행은 run이 끝날 때까지 여기", "<code>record/writer.py</code> (<code>RunRecordWriter</code>)"),
    ("작업일지 · 작업 중 팻말 · 마감 도장", "run 기록 · <code>.running</code> · <code>strategy.json</code>", "<code>.vqapr/runs/&lt;run&gt;/</code> · <code>run/recording.py</code> · <code>record/writer.py</code>"),
    ("반제품", "run이 만든 dataset — 같은 검수대를 지나 장부에 입고", "<code>.vqapr/materialized/&lt;id&gt;/all.parquet</code> · <code>run/engine/output.py</code>"),
    ("작업반장 · 작업자 · 미리 구운 재료판", "<code>--jobs</code> 지휘자 · 일꾼 · cube", "<code>run/batch.py</code> · <code>run/assemble.py</code> · <code>data/cube.py</code> · <code>.vqapr/cubes/</code>(끝나면 없음)"),
]

MAP = [
    ("①", "데이터 등록", "송장 → 검수대 → 장부"),
    ("②", "등록 오류", "없는 품목 · 바뀐 상자"),
    ("③", "DataModel", "반제품을 만들어 입고"),
    ("④", "factor 전략", "롱 3 · 숏 3 · 일지 · 비중"),
    ("⑤", "stop-loss", "수첩(memory)이 진입가를 든다"),
    ("⑥", "enhanced index", "반제품을 재료로"),
    ("⑦", "--jobs 배치", "작업반장 · 작업자 · 재료판"),
]

CHRONICLE_NOTES = {
    B: "거절 — 장부는 그대로",
    CK: "이 명령 전에 <code>execution.parquet</code>을 다른 바이트로 덮어썼다(마지막 날을 뺀 유효한 파일, 트레이스 밖). check는 읽기만 하고 거절",
    RA: "같은 송장으로 다시 등록 — 장부의 잰 반쪽만 바뀜. 이 뒤 원본 바이트로 되돌려 한 번 더 등록했다(트레이스 밖)",
    LD: "장부만 읽는다",
    SH: "작업일지만 읽는다",
    BA: "cube는 <code>.vqapr/cubes/&lt;배치&gt;/</code>에 구웠다가 명령이 끝나기 전에 지웠다. 두 run의 일지는 일꾼 프로세스가 다시 썼다(<code>--force</code>; 파일 이름은 그대로)",
    WK: "일꾼 하나를 이 프로세스에서 다시 추적한 것 — 파일 목록을 남기지 않는다",
}

SRCMAP_LEDE = (
    "위의 프레임이 선 파일은 여기 모두 있습니다(파일 이름 옆 <b>프레임 N</b>, 펼치면 그 프레임으로 가는 단추). 폴더 묶음마다 한 줄 비유가 붙어 있습니다. "
    "0.16.0의 폴더는 고리의 개념을 따릅니다: 데이터가 들어오고 → 전략이 판단하고 → 거래소가 체결하고 → 계좌가 적고 평가하고 → 전략이 다음에 그 계좌를 봅니다. "
    "이 설명은 2026-09-12 판에서 옮겨 온 것이고, 이번에 파일마다 <b>경로가 있는지와 줄 수가 26726b1f 트리와 같은지</b>를 대조했습니다(199개 모두 있음, 줄 수 197개 일치, parquet 둘은 줄 수 없음). "
    "트레이스처럼 잰 값이 아니라 파일을 읽고 쓴 설명입니다."
)

SCENES = [
    # ---------------------------------------------------------------- ① register
    {
        "id": "reg", "key": "①", "title": "데이터 등록 — 입고",
        "sub": f"vqapr register sample.yaml · {el(R)} ms · {nc(R)} 호출 (그중 {ms(R, 214)} ms는 식은 디스크의 첫 parquet 스캔)",
        "story": (
            "<b>무슨 일인가:</b> 창고에 물건을 들이려면 송장을 냅니다. <code>sample.yaml</code>이 그 송장입니다: “거래처 명단은 이 파일, 가격은 이 상자, 체결 가격은 저 상자, 기계 부품(전략 · 거래소 코드)은 이 파일들, 작업지시서(run)는 이렇게.” "
            "창고는 송장을 믿지 않습니다. 검수대에서 <b>상자를 실제로 열어</b> 적힌 대로인지 재고 봉인 번호(digest)를 찍고, 부품은 <b>실제로 끼워 보고</b>(import), 전부 통과한 뒤에야 <b>장부 한 권을 한 번에</b> 씁니다. "
            "상자 자체는 제자리에 그대로 둡니다 — 창고가 새로 만드는 파일은 사무실 서랍(<code>.vqapr/</code>)의 장부 둘뿐입니다."
        ),
        "shelf": [R],
        "frames": [
            F(R, 0, "송장을 창구에 낸다",
              f"터미널에서 <code>vqapr register sample.yaml</code>을 칩니다. 창구(명령줄)는 어느 업무인지(register) 알아보고 어느 창고인지(<code>--project-root</code>)를 정한 뒤, 송장을 읽어 입고 담당(<code>cli/register.py</code> → <code>workspace/registration.py</code>)에게 넘깁니다. {el(R)} ms의 거의 전부가 그 담당 안에서 쓰입니다. 무엇이 잘못되든 결과는 같은 모양의 영수증(JSON 봉투) 한 장입니다.",
              f"{c(R, 1, 'build_parser')} → {c(R, 11, '_resolve_project_root')} → {c(R, 12, 'register.run')} → {c(R, 13, 'read_yaml_mapping')} → {c(R, 14, 'apply')}.",
              fn="main() → register.run()", code=at("src/vqapr/cli/main.py", "def main(", 14),
              mem={"argv": "['--project-root', '.../sample', 'register', '.../sample/sample.yaml']"},
              disk={"sample/ (원본 19개)": "그대로 — 창고는 원본 상자를 고치지 않는다", ".vqapr/": "없음 — 아직 장부가 없다"}),
            F(R, 15, "입고 카트를 연다 — 장부는 맨 끝에 한 번만",
              "장부를 바로 고치지 않고 <b>입고 카트</b>(Transaction)를 엽니다. 명단 → 데이터 → 부품 → 작업지시서 순서로 검사한 것을 카트에 담았다가 맨 끝에 한 번에 씁니다. 중간에 하나라도 반송되면 카트째 버리므로 장부는 한 글자도 바뀌지 않습니다. "
              "순서가 이런 이유: 작업지시서는 부품 이름과 데이터 이름을 가리키므로 그것들이 먼저 카트에 있어야 찾을 수 있습니다.",
              f"{c(R, 16, 'Workspace.transaction')} → {c(R, 26, '_require_declared_ids')} → {c(R, 44, '_instruments')} → datasets({c(R, 137, 'verify_source')} · {c(R, 329, 'verify_source')}) → components({c(R, 469, '_component')} · {c(R, 617, '_component')}) → {c(R, 883, 'register_run')} → {c(R, 909, 'Transaction.commit')}.",
              fn="_apply() — 섹션 순서", code=at("src/vqapr/workspace/registration.py", 'for dataset_id, body in section("datasets")', 7),
              mem={"document": "dict (instruments 1 · datasets 2 · components 2 · runs 1)", "카트": "[] — 비어 있음"}),
            F(R, 47, "거래처 명단부터 열어 본다",
              f"종목 명단 상자(<code>instruments_stock.parquet</code>, 10종목)를 엽니다. 파일이 없거나 필요한 칸이 없으면 예외로 터지는 게 아니라 “무엇이 없다”는 전표로 돌아와 다른 반송 사유 옆에 나란히 놓입니다. {ms(R, 47)} ms는 10행짜리 표의 값이 아니라 이 프로세스가 parquet 라이브러리(pyarrow)를 처음 올리는 비용입니다.",
              f"{c(R, 47, 'verify_roster')} → {c(R, 51, 'build_roster')} → {c(R, 84, 'Transaction.register_instruments')}.",
              fn="verify_roster()", code=at("src/vqapr/data/verification.py", "def verify_roster", 12),
              mem={"카트": "[명단: 주식 10 · 봉인 875b5fe1…]"}),
            F(R, 137, "검수대 — 가격 상자를 열어 여섯 가지를 잰다",
              "송장은 “<code>available_at</code>이 시각이고 <code>close</code>가 실수이고 (시각, 종목)이 겹치지 않는다”고 말합니다. 검수대는 상자를 열어 순서대로 확인합니다: "
              "① 품목표 대조(컬럼 · 타입) → ② 같은 물건이 두 번 들었나(키의 빈 값 · 중복) → ③ 유통기한 범위(첫 날 · 끝 날) → ④ 파손품(NaN · 무한대) → ⑤ 체결 가격 역할(이 상자엔 없음) → ⑥ 봉인 번호(sha256). "
              f"여기가 이 상자가 <b>내용으로</b> 검사되는 유일한 자리입니다. 뒤의 모든 명령은 봉인 번호만 대조합니다. 재서 알게 된 것(기간 · 봉인 번호)은 카드의 빈칸에 적혀 카트로 갑니다. 기간 재기({ms(R, 214)} ms)가 큰 것은 이 프로세스의 첫 duckdb 스캔이라서이고, 두 번째 상자의 같은 단계는 {ms(R, 392)} ms입니다.",
              f"{c(R, 137, 'verify_source')} → {c(R, 138, 'describe')} → {c(R, 150, 'check_schema')} → {c(R, 193, 'check_key')} → {c(R, 214, 'check_span')} → {c(R, 225, 'check_values')} → {c(R, 277, 'check_execution_prices')} → {c(R, 279, 'physical_digest')} → {c(R, 283, 'Transaction.register_dataset')} → {c(R, 289, 'spoken')}.",
              fn="verify_source() — 여섯 단계", code=at("src/vqapr/data/verification.py", "def verify_source", 14),
              mem={"카드 sample-prices": "당신이 쓴 반쪽(컬럼 · 키 · 타입) + 잰 반쪽(기간 2022-01-03 15:30 ~ 2024-12-30 15:30 · 봉인 18bb7017…)", "카트": "[명단, sample-prices]"},
              disk={"sample/observations.parquet": "열어서 읽기만 — 그대로"}),
            F(R, 437, "체결 가격표는 한 가지를 더 잰다",
              "체결에 쓸 상자(<code>sample-execution</code>)는 송장에 “이 칸이 거래 가능 여부다”라고 적었습니다. 그래서 검수대가 한 가지를 더 묻습니다: 거래 가능하다고 적힌 행마다 가격이 양수인가? 답(<code>['close']</code>)을 카드에 적어 두면, 나중에 run이 “close로 체결”이라고 할 때 상자를 다시 열지 않고 이 답만 봅니다.",
              f"{c(R, 329, 'verify_source')} → {c(R, 339, 'check_schema')} → {c(R, 371, 'check_key')} → {c(R, 392, 'check_span')} → {c(R, 403, 'check_values')} → {c(R, 437, 'check_execution_prices')} → {c(R, 454, 'physical_digest')} → {c(R, 460, 'Transaction.register_dataset')}.",
              fn="check_execution_prices()", code=at("src/vqapr/data/verification.py", "def check_execution_prices", 14),
              mem={"카드 sample-execution": "잰 반쪽: 체결 가능 가격 ['close'] · 봉인 49e4b4ab…", "카트": "[명단, sample-prices, sample-execution]"},
              disk={"sample/execution.parquet": "열어서 읽기만 — 그대로"}),
            F(R, 554, "기계 부품은 실제로 끼워 보고 규격을 본다",
              "전략 파일(<code>reversal_5d.py</code>)의 지문을 찍고, 실제로 import해서 “전략이라면 있어야 할 메서드가 맞는 모양으로 있나”를 봅니다. 거래소 코드도 같은 길입니다. 규격에 안 맞는 부품은 여기서 이름을 대며 반송됩니다. 오늘은 둘 다 통과해 카트에 담깁니다.",
              f"{c(R, 469, '_component')} → {c(R, 473, 'fingerprint_component')} → {c(R, 554, 'conformance')} → {c(R, 602, '_check_methods')} → {c(R, 611, 'register_component')} · 거래소 {c(R, 617, '_component')} → {c(R, 726, 'conformance')} → {c(R, 817, 'register_component')}.",
              fn="conformance()", code=("def", 10),
              mem={"카트": "[명단, sample-prices, sample-execution, sample-reversal-5d, sample-exchange]"}),
            F(R, 909, "작업지시서를 담고, 카트를 장부로 옮긴다",
              "마지막으로 작업지시서(run: 어느 전략, 어느 데이터, 언제부터 언제까지, 초기 현금)를 담습니다. 그리고 송장이 무엇을 약속하는지 사람 말로 푼 문장이 영수증에 들어갑니다: “<i>dataset 'sample-prices'의 행은 available_at 시각부터 알 수 있고 그보다 먼저는 아니다</i>”, “<i>run 'sample-run'의 모델은 매일 08:00(Asia/Seoul)에 불린다 — 체결표에 행이 있는 날마다</i>”. "
              "그 다음 commit이 장부실 문을 잠그고(<code>.vqapr/.workspace.lock</code>), 장부를 한 번 다시 읽어 카트의 것을 합칩니다 — 그사이 다른 프로세스가 적은 것이 있으면 여기서 보입니다.",
              f"{c(R, 883, 'register_run')} → {c(R, 895, 'RunDefinition.spoken')} → {c(R, 909, 'Transaction.commit')} → {c(R, 931, 'Workspace._write')}.",
              fn="Transaction.commit()", code=("def", 16),
              mem={"카트": "5개 + run 1 → 장부로"}),
            F(R, 967, "장부는 임시 종이에 먼저 쓰고, 한 번에 바꿔 끼운다",
              "장부 파일을 쓰는 방법이 중요합니다. 제자리에 덮어쓰지 않고 <b>옆에 임시 파일</b>(<code>.workspace.yaml.…tmp</code>)을 만들어 끝까지 쓰고, 디스크에 확실히 내린 뒤(fsync) <b>한 번에 이름을 바꿔 끼웁니다</b>(<code>os.replace</code>). 그래서 누가 장부를 읽는 순간에도 반쯤 쓴 장부는 절대 보이지 않습니다 — 옛 장부 아니면 새 장부입니다. "
              "이어서 같은 잠금 안에서 거래처 명단 옆 파일(<code>instruments.json</code>)을 씁니다. 여기서 처음으로 디스크에 파일이 생깁니다.",
              f"{c(R, 931, 'Workspace._write')} → {c(R, 933, 'write_workspace')} → {c(R, 967, 'write_atomically')} → {c(R, 968, '_swap')} → {c(R, 970, 'Workspace._write_roster')} → {c(R, 974, 'success')}.",
              fn="write_atomically() — 임시 파일 → 바꿔 끼우기", code=at("src/vqapr/_internal/atomic.py", "staged = Path(staged_name)", 11),
              disk={".vqapr/workspace.yaml": "새로 생김 — datasets 2(잰 반쪽 포함) · components 2 · runs 1", ".vqapr/instruments.json": "새로 생김 — stock 10 · 봉인 875b5fe1…", ".vqapr/": "생김 (사무실 서랍)"}),
        ],
        "remember": [
            "상자는 등록될 때 검수대에서 한 번 잰다: 품목 → 중복 → 기간 → 파손 → 체결 가격 → 봉인 번호. 잰 값은 장부에 남고 상자는 그대로다.",
            "장부는 카트에 모았다가 잠금 안에서 한 번 쓴다 — 임시 파일에 쓰고 바꿔 끼우므로 반쯤 쓴 장부는 없다.",
        ],
    },
    # ---------------------------------------------------------------- ② registration errors
    {
        "id": "err", "key": "②", "title": "등록 오류 — 없는 품목, 바뀐 상자",
        "sub": f"register bad.yaml · {el(B)} ms · {nc(B)} 호출 (반송) — check sample-run · {el(CK)} ms · {nc(CK)} 호출 (반송) — register sample.yaml 다시 · {el(RA)} ms · {nc(RA)} 호출",
        "story": (
            "<b>무슨 일인가:</b> 실수를 두 가지 합니다. 먼저 상자에 <b>없는 품목</b>(<code>adj_close</code>)을 적은 송장을 냅니다 — 검수대가 상자를 열어 보고 “그런 품목 없다”고 이름을 대며 반송하고, 장부는 그대로입니다. "
            "다음엔 입고가 끝난 뒤 창고 밖에서 누군가 체결 가격 상자를 <b>다른 내용으로 바꿔 넣습니다</b>(마지막 날을 뺀 유효한 파일). 출고 전 점검(<code>check</code>)은 상자를 다시 열지 않고 봉인 번호 하나만 대조해 “상자가 바뀌었다”고 막고, 고치는 법을 말합니다: 같은 송장으로 다시 입고하라. 다시 입고하면 잰 반쪽만 새로 적힙니다. "
            "<b>[바뀔 예정]</b> 이 “바뀌면 반송”은 이 트리(26726b1f)의 지금 동작입니다. 오너 판정(2026-09-13): daily batch가 새 날짜를 덧붙일 수 있으니, 봉인이 바뀌면 반송하지 말고 <b>등록과 같은 기준으로 다시 검수</b>해 신고와 다를 때만 반송한다. 그 결과를 어디에 적을지는 보류입니다."
        ),
        "shelf": [B, CK, RA],
        "shelf_note": "02와 03 사이에 <code>execution.parquet</code>을 다른 바이트로 덮어썼고(준비 스크립트, 트레이스 밖), 04 뒤에 원본 바이트로 되돌려 한 번 더 등록했습니다(트레이스 밖). 뒤의 run들은 원본 위에서 돌았습니다.",
        "frames": [
            F(B, 400, "검수대가 상자를 열고 첫 단계에서 멈춘다",
              "송장은 “<code>observations.parquet</code>에 <code>adj_close</code>가 있다”고 말합니다. 검수대가 상자의 품목표(컬럼 목록)를 읽어 대조합니다: 없습니다. 그 뒤 단계(중복 · 기간 · 파손 · 봉인)는 돌지 않습니다 — 품목이 틀린 상자에 중복을 묻는 건 뜻이 없으니까요.",
              f"{c(B, 358, '_dataset')} → {c(B, 387, 'verify_source')} → {c(B, 388, 'describe')} → {c(B, 400, 'check_schema')} → {c(B, 415, 'Diagnosis.ok')} = False → {c(B, 416, 'raise_if_failed')}.",
              fn="check_schema()", code=at("src/vqapr/data/verification.py", "def check_schema", 12),
              mem={"상자에 있는 품목": "available_at, close, high, instrument, low, open, volume"}),
            F(B, 421, "반송 전표 — 무엇이 · 왜 · 어떻게 고치나, 그리고 장부는 그대로",
              "전표 한 장이 나옵니다: code <code>dataset.field_missing</code>(400) · 요구 “<i>fields[adj_close]가 말한 컬럼 'adj_close'가 있어야 한다</i>” · 관찰 “<i>있는 컬럼은 available_at, close, high, …</i>” · 고치는 법 “<i>adj_close 컬럼을 넣거나 있는 컬럼을 가리켜라</i>” · 위치 <code>datasets.sample-adjusted.fields[adj_close]</code> · 원인 자리 <code>vqapr/data/verification.py:152 (check_schema)</code>. "
              "<code>mutation: false</code> — 카트는 열렸지만 장부로 가지 않았습니다. 이 트레이스엔 쓰기 호출이 하나도 없습니다. exit 1.",
              f"{c(B, 416, 'raise_if_failed')} → {c(B, 421, 'failure')} → {c(B, 430, 'emit')} → exit 1.",
              fn="envelope.failure()", code=("def", 10),
              disk={".vqapr/workspace.yaml": "그대로 (mutation: false)"}),
            F(CK, 340, "[0.16.0] 출고 전 점검 — check도 run도 이 한 함수를 지난다",
              "상자가 바뀐 채로 <code>check sample-run</code>. check는 장부를 열고 작업지시서를 꺼내 <b>preflight</b> 한 함수에 넘깁니다. 이 함수가 두 가지를 한 번의 읽기로 합니다: 판정 여럿을 <b>모아서</b> 답하기(check가 보여 줄 것)와 작업 키트 얼리기 시도(freeze, run이 쓸 것). 둘은 같은 사실 그릇(<code>RunFacts</code>)에서 읽으므로 같은 것을 두 번 읽지 않습니다. "
              "[0.16.0] 이름: <code>verify_run</code> → <code>preflight</code>, <code>preflight_run</code> → <code>freeze</code>, 자리는 <code>run/preflight/</code>.",
              f"{c(CK, 13, 'check')} → {c(CK, 15, 'Workspace.open')} → {c(CK, 338, 'run_definition')} → {c(CK, 340, 'preflight')} → {c(CK, 341, 'RunFacts.__init__')} → {c(CK, 342, 'judgments')} → … → {c(CK, 49684, 'freeze')} → {c(CK, 49792, 'Failure.as_dict')} → {c(CK, 49806, 'emit')}.",
              fn="preflight() — run의 문", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 10, before=1),
              mem={"verdict": "failures 1 (dataset.source_changed) · blocked 1 (execution_ordering) · frozen 없음 · refusal VqaprError"},
              disk={"sample/execution.parquet": "창고 밖에서 바뀜 (마지막 날을 뺀 파일)"}),
            F(CK, 342, "판정 일곱이 차례로 답한다 — 사실은 한 번만 읽는다",
              f"판정은 일곱입니다: 종목 집합 · 명단 · 기간 · <b>체결 순서</b> · 읽을 dataset들 · 비중 · 출력. 체결 순서 판정이 “시간표(schedule)를 달라”고 하자 그릇이 처음이라 만듭니다 — 이 run은 3년짜리라 734일, {ms(CK, 369)} ms(대부분은 하루마다 결정 시각을 만드는 Python 시간). 그 뒤 얼리기가 같은 시간표를 물으면 그릇이 <b>돌려주기만</b> 합니다.",
              f"{c(CK, 342, 'judgments')} → {c(CK, 354, '_judge_universe')} · {c(CK, 356, '_judge_roster')} · {c(CK, 363, '_judge_period')} · {c(CK, 365, '_judge_execution_ordering')} → {c(CK, 366, 'RunFacts.schedule')} → {c(CK, 367, '_once')} → {c(CK, 369, 'derived_schedule')} → … {c(CK, 43683, 'inclusive_slice')} → {c(CK, 47352, 'RunFacts.execution_table')} · {c(CK, 47394, '_judge_member_datasets')} · {c(CK, 49681, '_judge_weights')} · {c(CK, 49683, '_judge_outputs')}.",
              fn="judgments() → RunFacts._once()", code=at("src/vqapr/run/preflight/facts.py", "def _once(", 10),
              tip="여기서 큰 것은 표 스캔이 아니라 시간표 만들기입니다(프로파일러 아래). 프로파일러 없이 재면 이 check는 약 0.1 s입니다(기록 240)."),
            F(CK, 365, "체결 순서 판정은 run이 실제로 걷는 날들만 묻는다",
              "이 판정은 “결정마다 그 다음에 체결할 시각이 있나”를 봅니다. 얼리기가 쓰는 것과 같은 조각(<code>inclusive_slice(start, end)</code>)만 봅니다 — 날짜 범위의 상위집합을 보면 end가 체결과 결정 사이에 놓인 옳은 지시서가 500으로 죽었습니다(testbed 보고 099, 기록 237). 조각을 내는 것은 <code>Schedule</code>(<code>domain/schedule.py</code>)입니다.",
              f"{c(CK, 365, '_judge_execution_ordering')} → {c(CK, 366, 'RunFacts.schedule')} → … → {c(CK, 43683, 'Schedule.inclusive_slice')} → {c(CK, 47352, 'RunFacts.execution_table')} → {c(CK, 47356, 'Workspace.require_verified')}.",
              fn="_judge_execution_ordering() — inclusive_slice", code=at("src/vqapr/run/preflight/checks.py", "events = facts.schedule().inclusive_slice(", 10, before=3)),
            F(CK, 47367, "상자를 다시 열지 않는다 — 봉인 번호 하나를 대조한다",
              f"체결표를 쓰려면 장부에 “이 상자는 아직 입고 때 그대로인가”를 물어야 합니다. 장부의 봉인 <code>49e4b4abef4f…</code>와 지금 상자의 봉인 <code>34c1d63c3ab4…</code>({ms(CK, 47365)} ms)가 다릅니다 → <code>dataset.source_changed</code>(412): “<i>run이 읽는 바이트는 등록이 잰 바이트여야 한다</i>”, 고치는 법 “<i>vqapr register &lt;선언 파일&gt;로 다시 등록하라</i>”. "
              f"그릇은 실패도 기억합니다: 뒤에 얼리기가 같은 표를 물으면 저장해 둔 같은 예외를 다시 던집니다({ms(CK, 49684)} ms) — 다시 해시하지 않습니다. "
              "<b>[바뀔 예정]</b> 오너 판정(2026-09-13)대로 바뀌면, 이 자리는 “반송” 대신 “다시 검수”가 되고, 새 바이트가 송장과 맞으면 통과합니다.",
              f"{c(CK, 47352, 'RunFacts.execution_table')} → {c(CK, 47356, 'Workspace.require_verified')} → {c(CK, 47365, 'physical_digest')} → {c(CK, 47367, 'require_verified')} → 반송 · 판정을 blocked로 감싼다 → {c(CK, 47394, '_judge_member_datasets')} … {c(CK, 49684, 'freeze', note=': 저장된 예외')}.",
              fn="require_verified()", code=at("src/vqapr/data/verification.py", "def require_verified", 14),
              mem={"장부의 봉인": "49e4b4abef4f…", "지금 상자의 봉인": "34c1d63c3ab4…"},
              caution="영수증: checked [workspace, run, judgments, preflight] · passed [workspace, run] · failures [dataset.source_changed] · blocked [judgment.blocked: “every judgment answers before a run is accepted”, cause에 예외 전체]. 답하지 못한 판정과 그 원인은 따로따로 실린다(오너 결정 2026-09-04)."),
            F(RA, 647, "같은 송장으로 다시 입고 — 잰 반쪽만 다시 잰다",
              f"<code>register sample.yaml</code>을 다시 칩니다. 송장은 한 글자도 안 바뀌었고 상자만 다릅니다. 검수대가 두 상자를 다시 엽니다(가격 상자 {ms(RA, 455)} ms · 체결 상자 {ms(RA, 647)} ms): 기간, 봉인 번호(<code>34c1d63c…</code>), 체결 가격. 카트에 담을 때 장부의 기존 항목과 비교합니다.",
              f"{c(RA, 15, '_apply')} → {c(RA, 455, 'verify_source')} → {c(RA, 605, '_merge_dataset')} · {c(RA, 647, 'verify_source')} → {c(RA, 782, '_merge_dataset')}.",
              fn="verify_source() 다시", code=("def", 8)),
            F(RA, 782, "당신이 쓴 반쪽이 같으면 잰 반쪽만 갈아 끼운다",
              "장부 항목엔 두 반쪽이 있습니다. 당신이 쓴 반쪽(컬럼 · 키 · 타입)과 검수대가 잰 반쪽(기간 · 봉인 · 체결 가격). 비교기는 “기존 항목의 잰 반쪽을 새 측정으로 바꾸면 새 항목과 같은가”를 봅니다. 같다 → 송장은 그대로이니 받아들입니다. 컬럼 이름 하나라도 달랐다면 “이미 등록된 이름”(409)으로 반송했을 겁니다. "
              "그 다음은 ①과 같은 길: 잠금 → 다시 읽기 → 합치기 → 임시 파일에 쓰고 바꿔 끼우기. <code>workspace.yaml</code> 안의 봉인 번호 한 줄이 바뀝니다.",
              f"{c(RA, 782, '_merge_dataset')} → … {c(RA, 1227, 'Transaction.commit')} → {c(RA, 1255, 'Workspace._write')} → {c(RA, 1291, 'write_atomically')} → {c(RA, 1298, 'success')}.",
              fn="_merge_dataset() — remeasured", code=at("src/vqapr/workspace/merge.py", "remeasured = replace(", 12, before=6),
              disk={".vqapr/workspace.yaml": "고쳐 씀 — sample-execution의 source_digest 49e4b4ab… → 34c1d63c… (그 뒤 원본으로 되돌려 한 번 더 등록)"}),
        ],
        "remember": [
            "반송 전표는 code · 요구 · 관찰 · 고치는 법 · 위치를 들고, 장부는 안 바뀐다(쓰기 호출 0).",
            "입고 뒤 상자가 바뀌면 봉인 번호 하나로 알아챈다. 지금은 반송, 오너 판정대로라면 다시 검수(보류 중).",
        ],
    },
    # ---------------------------------------------------------------- ③ datamodel
    {
        "id": "dm", "key": "③", "title": "DataModel — 반제품을 만들어 입고",
        "sub": f"register features.yaml · {el(RF)} ms · {nc(RF)} 호출 — run sample-features-run · {el(DM)} ms · {nc(DM)} 호출 · 16일 · 108행",
        "story": (
            "<b>무슨 일인가:</b> <code>features.py</code>의 <code>SampleFeatures</code>는 창고 안의 작은 공장입니다. 날마다 종목별 <b>5일 모멘텀</b>(여섯 종가 중 마지막 ÷ 첫 번째 − 1)을 만듭니다. 사고파는 게 없으니 이 작업엔 시간표 시계(매일 16:00)만 있고 시장 시계가 없습니다. "
            "첫 나흘은 종가가 여섯 개가 안 돼 빈손, 2022-01-10부터 종목당 한 행(K000010은 이 구간에 종가 여섯 개가 없어 빠짐). 끝나면 108행(12일 × 9종목)이 <b>반제품 상자</b>(parquet) 하나로 포장되고, <b>①과 똑같은 검수대</b>를 지나 장부에 <code>sample-features</code>로 입고됩니다. 다음 작업은 이 반제품을 벤더 상자와 똑같이 씁니다. "
            "이 장면에서 처음으로 <b>작업일지</b>가 생깁니다: 표지(<code>run.json</code>) → 작업 중 팻말(<code>.running</code>) → 반제품 → 마감 도장(<code>datamodel.json</code>)."
        ),
        "shelf": [RF, DM],
        "frames": [
            F(DM, 475, "작업지시서도 출고 전 점검을 받는다",
              f"장부를 열고 작업지시서를 꺼내 <code>preflight</code>에 넘깁니다({ms(DM, 475)} ms): 판정 {ms(DM, 477)} ms, 얼리기 {ms(DM, 1798)} ms. 얼리기는 모델을 import해 “무엇을 읽나”를 묻는데, 이 import는 판정이 이미 한 것을 그릇에서 받습니다. 체결표가 없는 DataModel 작업은 <code>days_from</code>의 가격 상자에서 거래일을 읽는데, 작업 기간 ± 1일만 읽습니다(<code>_local_date</code> ×{count(DM, '_local_date')}, 기록 247).",
              f"{c(DM, 13, '_run_one')} → {c(DM, 15, 'Workspace.open')} → {c(DM, 475, 'preflight')} → {c(DM, 477, 'judgments')} → {c(DM, 1798, 'freeze')} → {c(DM, 1810, '_freeze_datamodel')} → {c(DM, 2003, '_freeze_sources')}.",
              fn="preflight()", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 10, before=1),
              mem={"거래일 읽기": f"_local_date ×{count(DM, '_local_date')}"}),
            F(DM, 2016, "작업 키트 — 쓸 상자가 입고 때 그대로인지 봉인으로",
              f"이 모델이 쓸 <code>sample-prices</code>가 아직 입고 때 상자인지 봉인 번호로 봅니다({ms(DM, 2005)} ms). 같습니다. 키트에 그 봉인 번호가 들어가 “이 작업은 이 바이트를 썼다”가 작업일지에 남습니다. 상자 내용은 여기서도 읽지 않습니다.",
              f"{c(DM, 2003, '_freeze_sources')} → {c(DM, 2005, 'Workspace.require_verified')} → {c(DM, 2016, 'require_verified')}.",
              fn="require_verified()", code=at("src/vqapr/data/verification.py", "def require_verified", 14),
              mem={"키트의 봉인": "{sample-prices-source: 18bb7017…}"}),
            F(DM, 2056, "공구 봉지 — 점검이 꺼내 둔 것을 작업이 그대로 받는다",
              f"작업 키트는 작업일지에 적히는 <b>값</b>이라 살아 있는 모델 객체를 들 수 없습니다. 그래서 점검이 이미 꺼낸 객체와 잘라 둔 기간을 <code>RunResources</code>라는 공구 봉지에 담아 함께 넘기고({ms(DM, 2056)} ms — 새로 만드는 건 없음), 작업은 그것을 씁니다. 다른 작업의 봉지면 거절합니다.",
              f"{c(DM, 2056, 'RunResources.of')} → {c(DM, 2064, 'RunVerdict.require_ready')} → {c(DM, 2066, 'run')} → {c(DM, 2074, '_run_datamodels')} → {c(DM, 2075, '_run_datamodel')} → {c(DM, 2113, '_run_member')}.",
              fn="RunResources.of()", code=("def", 12),
              mem={"공구 봉지": "datamodel=SampleFeatures 인스턴스(점검이 import한 것) · strategy 없음 · exchange 없음"}),
            F(DM, 2116, "재료 선반은 작업 기간을 안다",
              "작업 하나의 도구들(스캔 세션 · 재료 선반 · 작업일지 쓰기 · 창 만들기)을 준비합니다. 선반(store)은 이 작업의 기간(01-04 ~ 01-25)과 모델이 쓰겠다고 말한 재료를 받아 두고, 뒤의 모든 읽기를 그 범위로 자릅니다. 3년치 상자에서 3주만 꺼내는 이유가 여기 있습니다.",
              f"{c(DM, 2113, '_run_member')} → {c(DM, 2116, '_horizon')} → <code>DuckDbObservationStore(horizon=…)</code>.",
              fn="_horizon() → DuckDbObservationStore(horizon=…)", code=("def", 10),
              mem={"horizon": "(2022-01-04 00:00, 2022-01-25 23:00) +09:00", "요구": "[sample-prices.close, RowsLookback(rows=6)]"}),
            F(DM, 2119, "작업일지의 표지가 가장 먼저 생긴다 — run.json",
              "작업을 시작하기 <b>전에</b> 표지(<code>run.json</code>)부터 씁니다: 기간 · 쓸 상자와 그 봉인 번호 · 출력 이름 · 작업지시서의 지문. 작업이 중간에 죽어도 “무엇을 하려 했나”는 남게 하려는 것입니다. 쓰는 방법은 장부와 같습니다(임시 파일 → 바꿔 끼우기). 같은 이름의 표지가 다른 지시서로 이미 있으면 여기서 거절합니다.",
              f"{c(DM, 2119, 'freeze_run_record')} → <code>write_run_record</code> → {c(DM, 2162, 'write_atomically')}.",
              fn="freeze_run_record()", code=at("src/vqapr/run/recording.py", "def freeze_run_record", 11),
              disk={".vqapr/runs/sample-features-run/run.json": "새로 생김 — 표지 (datasets: sample-prices 18bb7017…)"}),
            F(DM, 2167, "작업 칸을 차지하고 ‘작업 중’ 팻말을 건다",
              f"작업일지 칸(<code>datamodels/sample-features@4327b244/</code>)과 그 안의 <code>tables/</code> 폴더를 만들고, 팻말 <code>.running</code>에 프로세스 번호(pid)를 적습니다. 폴더 만들기와 팻말 쓰기는 <b>한 프로세스만 성공</b>하는 방식이라, 같은 작업을 두 터미널에서 동시에 돌려도 한쪽은 “작업 중”이라고 거절됩니다. 첫 박동에서 진행 메모(<code>progress.json</code>)도 한 번 씁니다({ms(DM, 2404)} ms). 행 자체는 아직 디스크에 없습니다.",
              f"{c(DM, 2167, 'RunRecordWriter.open')} → … 첫 {c(DM, 2398, 'RunRecordWriter.heartbeat')} → {c(DM, 2401, 'RunRecordWriter.checkpoint')} → {c(DM, 2404, 'write_atomically')}.",
              fn="RunRecordWriter.open()", code=at("src/vqapr/record/writer.py", "def _claim(self)", 12),
              disk={FEAT_DIR + "tables/": "새로 생김 (빈 폴더)", FEAT_DIR + ".running": "새로 생김 — pid (작업 중 팻말)", FEAT_DIR + "progress.json": "새로 생김 — 진행 메모"}),
            F(DM, 2181, "[0.16.0] 조립 라인은 하나, 사건은 시간표가 만든다",
              "전략 작업과 <b>같은</b> 라인(<code>RunLoop</code>, <code>run/engine/loop.py</code>)을 씁니다. 다른 건 두 가지뿐: 부품이 DataModel용이고, 시장 시계가 없습니다. 조립하면서 모델의 <code>inputs()</code>를 <b>한 번</b> 물어 무엇을 읽을지 알아 둡니다. 라인이 열리고 16개의 사건을 차례로 처리합니다. "
              "[0.16.0] 라인이 받는 것의 이름: <code>ScheduledEvent(event_id='sample-features-run.schedule-2022-01-04T1600', …)</code> — 시간표가 사건을 만들고 라인은 사건을 시각 순서로 처리한다(이산 사건 시뮬레이션).",
              f"{c(DM, 2181, 'datamodel_loop')} → {c(DM, 2183, 'SampleFeatures.inputs')} → {c(DM, 2297, 'RunLoop.run')} → {c(DM, 2298, 'start')} → {c(DM, 2301, 'events')} → <code>RunLoop.handle</code> ×16 (#2406 …) → {c(DM, 7737, 'RunLoop.finish')}.",
              fn="datamodel_loop()", code=at("src/vqapr/run/engine/loop.py", "def datamodel_loop", 12)),
            F(DM, 2485, "첫 재료 — 어디부터 어디까지 꺼낼지 먼저 정한다",
              f"2022-01-04 16:00, 모델이 처음으로 “종가를 달라”고 합니다. 선반은 꺼내기 전에 범위를 정합니다: 여섯 행이 필요하니 작업 시작(01-04) 앞의 가장 이른 날을 상자의 날짜 격자에서 세고(하한 01-03 15:30), 상한은 작업 끝(01-25 23:00). 그 사이만 스캔합니다({ms(DM, 3233)} ms — 이 프로세스의 첫 스캔).",
              f"{c(DM, 2449, 'SampleFeatures.compute')} → {c(DM, 2450, '_DeclaredReads.read')} → {c(DM, 2469, 'ModelWindow.panel')} → {c(DM, 2470, 'panel_window')} → {c(DM, 2485, '_scan_bounds')} → {c(DM, 3233, 'observation_table')} → {c(DM, 3270, 'Panel.from_table')}.",
              fn="_scan_bounds() — lookback 하한", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 10, before=2),
              mem={"bounds": "2022-01-03 15:30 ~ 2022-01-25 23:00 +09:00 (probe_panel.py로 잰 값)"},
              disk={"sample/observations.parquet": "17일 × 10종목만 읽음 — 그대로"}),
            F(DM, 3270, "재료판 — 날짜 × 종목 행렬 한 벌",
              f"스캔이 준 표(시각 · 종목 · 종가)를 (17일 × 10종목) 숫자 행렬 하나로 접습니다({ms(DM, 3270)} ms). 없는 칸은 NaN. 이 뒤 16번의 작업은 전부 이 판의 일부를 <b>복사 없이</b> 봅니다(view).",
              f"{c(DM, 3270, 'Panel.from_table')} → {c(DM, 3271, 'placement')} → {c(DM, 3273, 'dense_block')} → {c(DM, 3282, 'PanelWindow.matrix')}.",
              fn="Panel.from_table() — 블록", code=("def", 12),
              mem={"panel.blocks['close'].shape": "(17, 10)", "panel.bounds": "01-03 15:30 ~ 01-25 23:00"}),
            F(DM, 2449, "첫날 — 종가가 두 개뿐이라 빈손",
              f"저자 코드입니다. <code>window.matrix()</code>로 판을 보니 01-04 16:00에 알 수 있는 행은 2개(01-03 · 01-04). 여섯 개가 필요하니 <code>[]</code>를 돌려줍니다. 공장은 빈손을 그대로 받습니다. 이 첫 작업 {ms(DM, 2449)} ms는 거의 전부 위의 첫 스캔이고, 다음 날부터는 {ms(DM, 3336)} ms입니다.",
              f"{c(DM, 2406, 'RunLoop.handle', note=', ScheduledEvent 01-04 16:00')} → {c(DM, 2413, '_window_factory.at')} → {c(DM, 2449, 'SampleFeatures.compute')} → … → {c(DM, 3282, 'PanelWindow.matrix')} → {c(DM, 3290, 'RunOutput.append', note=', rows=[]')}. 둘째 날 {c(DM, 3336, 'compute')}.",
              fn="SampleFeatures.compute() — 저자 코드", code=at(DECL + "features.py", "closes = window.matrix()", 12, before=1), author=True,
              mem={"closes.shape": "(2, 10) — 날 2 × 종목 10", "돌려준 것": "[]"}),
            F(DM, 3639, "다섯째 날 — 9종목의 모멘텀을 한 식으로, 행은 작업대에",
              "2022-01-10 16:00. 여섯 행이 찼습니다. <code>closes[-1] / closes[0] - 1</code>이 열마다(종목마다) 한 번에 계산되고, 여섯 값이 다 있는 열만 행으로 나갑니다: 9행(K000010은 열이 비어 빠짐). 행의 시각(<code>available_at</code>)은 저자가 아니라 공장이 찍습니다(16:00): “이 값은 이 시각에야 알 수 있다.” "
              "9행은 Arrow 표 하나로 타입되어 <b>작업대(메모리)</b>에 쌓입니다 — 디스크엔 아직 아무것도 없습니다. 16일째에 108행.",
              f"{c(DM, 3596, 'RunLoop.handle')} → {c(DM, 3603, '_window_factory.at', note=', 01-10 16:00')} → {c(DM, 3639, 'SampleFeatures.compute')} → {c(DM, 3938, 'RunOutput.append', note=', 9행')}.",
              fn="SampleFeatures.compute() — 행 9", code=at(DECL + "features.py", "momentum = closes[-1]", 8, before=2), author=True,
              mem={"작업대 (output._buffered)": "[Arrow 9행] … → 16일째 108행", "디스크": "아직 없음"}),
            F(DM, 7771, "반제품이 한 상자로 포장되고, 같은 검수대로 입고된다",
              f"16일이 끝나면 작업대의 행을 <b>반제품 상자 하나</b>로 포장합니다: 옆에 <code>.all.parquet.tmp</code>로 끝까지 쓰고 <code>all.parquet</code>로 바꿔 끼웁니다({ms(DM, 7800)} ms). 그 상자를 <b>①에서 벤더 상자가 지난 바로 그 검수대</b>에 넣습니다({ms(DM, 7802)} ms): 품목 · 중복 · 기간(01-10 ~ 01-25) · 파손 · 봉인. "
              "통과하면 장부에 <code>sample-features</code>가 “어느 작업의 어느 코드 버전이 만들었다”와 함께 입고됩니다(장부 고쳐 씀). 공장이 만든 것이라고 검수를 건너뛰지 않습니다. 검수에서 떨어지면 반제품 상자를 지우고 장부는 그대로입니다.",
              f"{c(DM, 7771, 'RunOutput.register')} → {c(DM, 7800, 'RunOutput._seal')} → {c(DM, 7801, 'RunOutput._write')} → {c(DM, 7802, 'verify_source')} → {c(DM, 7933, 'Transaction.commit')} → {c(DM, 7947, 'Workspace._write')}.",
              fn="RunOutput.register()", code=at("src/vqapr/run/engine/output.py", "# The rows land here, once, and only now", 9),
              disk={".vqapr/materialized/sample-features/all.parquet": "새로 생김 — 108행 (available_at · instrument · momentum_5d) · 봉인 54f8fd04…", ".vqapr/workspace.yaml": "고쳐 씀 — datasets + sample-features (produced_by sample-features-run · sample-features@4327b244)"}),
            F(DM, 8026, "마감 도장 — datamodel.json을 쓰고 팻말을 치운다",
              f"마지막으로 작업일지의 마감 도장(<code>datamodel.json</code>: 행 수 · 세션별 행 수 · 봉인 · 코드 지문)을 씁니다. 순서가 약속입니다: 본문이 먼저, 도장이 나중 — <b>도장이 있으면 본문이 다 있다</b>. 도장도 임시 파일 → 바꿔 끼우기로 쓰고({ms(DM, 8146)} ms), 그 뒤에야 팻말(<code>.running</code>)을 치우고 진행 메모를 지웁니다. 영수증: rows 108 · sessions 16.",
              f"{c(DM, 8000, 'freeze_datamodel_record')} → {c(DM, 8026, 'RunRecordWriter.finish')} → {c(DM, 8142, 'RunRecordWriter._seal')} → {c(DM, 8146, 'write_atomically')} → {c(DM, 8148, 'RunRecordWriter._unlock')} → {c(DM, 8156, 'read_datamodel_record')} → {c(DM, 8163, 'success')}.",
              fn="RunRecordWriter.finish()", code=at("src/vqapr/record/writer.py", "# The tables land BEFORE the record", 4),
              disk={FEAT_DIR + "datamodel.json": "새로 생김 — 마감 도장 (rows 108 · sessions 16)", FEAT_DIR + ".running": "없어짐 — 팻말 치움", FEAT_DIR + "progress.json": "없어짐"}),
        ],
        "remember": [
            "작업은 출고 전 점검 한 번으로 판정받고 키트로 얼려지며, 점검이 꺼낸 모델을 공구 봉지로 그대로 받는다.",
            "작업일지: 표지(run.json) → 팻말 → 행은 작업대 → 반제품 상자 → 검수 → 장부 → 마감 도장 → 팻말 치움.",
        ],
    },
    # ---------------------------------------------------------------- ④ factor strategy
    {
        "id": "factor", "key": "④", "title": "factor 전략 — 롱 3 · 숏 3",
        "sub": f"register factor.yaml · {el(FR)} ms · {nc(FR)} 호출 — run sample-factor-run · {el(FA)} ms · {nc(FA)} 호출 · 10일 · 사건 20",
        "story": (
            "<b>무슨 일인가:</b> <code>factor.py</code>의 <code>SampleFactor</code>는 ③이 만든 반제품(모멘텀)을 <b>벤더 상자와 똑같이</b> 한 줄로 선언해 읽고(최신 행 하나), 상위 3종목은 사고 하위 3종목은 팝니다(각 1/6, 달러 중립). "
            "공매도가 있으니 거래소가 SIGNED 상장을 허용해야 합니다 — <code>exchange_signed.py</code>. 작업은 2022-01-12 ~ 01-25, 매일 아침 8시에 주문서를 쓰고(<code>ScheduledEvent</code>) 오후 3시 반에 체결 · 평가합니다(<code>MarketEvent</code>). "
            "달리는 동안 디스크엔 표지와 팻말과 진행 메모뿐이고, 행은 전부 작업대(메모리)에 쌓였다가 끝에 <b>한 번</b> 본문 셋(account · fill · weight)으로 떨어집니다. 끝나면 비중이 반제품 <code>sample-factor-weights</code>로 입고됩니다(⑥이 씁니다)."
        ),
        "shelf": [FR, FA],
        "frames": [
            F(FA, 730, "출고 전 점검 — 판정이 읽고, 키트는 받는다",
              f"판정 일곱 중 무거운 건 체결 순서({ms(FA, 756)} ms)입니다: 시간표를 만들려고 체결표의 시각 열을 읽습니다. 읽는 범위가 작업 기간 ± 1일(01-11 ~ 01-26)이라 12일만 옵니다(<code>_local_date</code> ×{count(FA, '_local_date')}, 기록 247). 이어서 얼리기({ms(FA, 1900)} ms)가 같은 시간표를 물으면 그릇이 {ms(FA, 1904)} ms에 돌려줍니다. 얼리기는 전략을 새 인스턴스로 한 번 더 만들어 초기 수첩이 JSON인지 증명하고, 시간표와 체결 목표를 얼립니다.",
              f"{c(FA, 730, 'preflight')} → {c(FA, 732, 'judgments')} → {c(FA, 756, '_judge_execution_ordering')} → {c(FA, 757, 'RunFacts.schedule')} → {c(FA, 760, 'derived_schedule')} → {c(FA, 766, 'evaluation_times')} → {c(FA, 774, 'distinct_values', note=': 12 instants')} · {c(FA, 1680, '_judge_member_datasets')} · {c(FA, 1808, '_judge_weights')} · {c(FA, 1899, '_judge_outputs')} → {c(FA, 1900, 'freeze')} → {c(FA, 1904, 'RunFacts.schedule')} → {c(FA, 1948, '_freeze_strategy')} → {c(FA, 1955, '_validate_initial_model_state')} → {c(FA, 2046, '_freeze_schedule')} → {c(FA, 2134, '_validate_execution_targets')}.",
              fn="preflight()", code=("def", 16),
              mem={"거래일 읽기": f"_local_date ×{count(FA, '_local_date')}", "그릇에 든 사실": "schedule · execution_table · horizon · component:sample-factor · exchange"}),
            F(FA, 2290, "작업 키트 — 쓸 반제품과 체결표를 봉인으로 묶는다",
              f"이 전략이 쓰는 <code>sample-features</code>는 다른 작업이 만든 반제품이지만 여기선 벤더 상자와 똑같이 취급됩니다: 봉인 번호 한 번({ms(FA, 2291)} ms). 체결표는 입고 때 적어 둔 “체결 가능한 가격” 목록에 close가 있는지만 봅니다. 키트는 두 봉인을 들고 불변식을 검사합니다.",
              f"{c(FA, 2289, '_freeze_sources')} → {c(FA, 2290, '_validate_requirement')} → {c(FA, 2291, 'Workspace.require_verified')} → {c(FA, 2323, 'FrozenRun.__post_init__')}.",
              fn="_validate_requirement()", code=at("src/vqapr/run/preflight/freeze.py", "def _validate_requirement", 14),
              mem={"키트의 봉인": "{materialized-sample-features: 54f8fd04…, sample-execution-source: 49e4b4ab…}"}),
            F(FA, 2351, "공구 봉지 — 전략 · 거래소 · 기간을 다시 만들지 않는다",
              f"점검이 꺼낸 전략 객체 · 거래소 · 규칙(없음) · 체결 기간을 봉지 하나에 담습니다({ms(FA, 2351)} ms). 세 번의 조회가 각각 {ms(FA, 2358)} ms 안팎 — 만드는 게 아니라 꺼내는 겁니다. 작업이 여기서 전략을 다시 import하거나 체결표를 다시 스캔하지 않습니다(기록 242).",
              f"{c(FA, 2351, 'RunResources.of')} → {c(FA, 2358, 'RunFacts.component')} · {c(FA, 2360, 'exchange')} · {c(FA, 2363, 'horizon')} → {c(FA, 2365, 'RunVerdict.require_ready')} → {c(FA, 2367, 'run')}.",
              fn="RunResources.of()", code=("def", 12),
              mem={"공구 봉지": "strategy=SampleFactor · exchange=AcademicExchange(SIGNED) · rules=() · horizon=01-12 15:30 ~ 01-25 15:30"}),
            F(FA, 2376, "작업 시작 — 거래처 명단은 얼리지 않고 그때그때 읽는다",
              f"작업이 시작하며 거래처 명단을 새로 읽습니다({ms(FA, 2376)} ms). 얼리지 않는 건 일부러입니다(이슈 009): 명단은 날마다 자라고, 새 이름을 안 쓰는 작업까지 아침마다 막을 이유가 없어서요. 대신 그날 명단의 봉인을 작업일지에 적습니다. 이 ms는 10행짜리 표의 값이 아니라 프로세스가 pyarrow를 처음 올리는 비용입니다(⑦의 일꾼에선 {ms(WK, 1665)} ms). "
              "그 다음 계좌(현금 1억, SIGNED) · 규칙 자리 · 라인을 조립하고, 결정 담당이 전략에게 “무엇을 읽나”를 여기서 한 번 묻습니다. [0.16.0] 결정 담당 <code>CallbackHandler</code>는 <code>run/engine/stages/decide.py</code>, 규칙 담당은 <code>stages/observe.py</code> — 단계 파일 이름은 그 단계가 부르는 저자 메서드의 이름입니다.",
              f"{c(FA, 2367, 'run')} → {c(FA, 2376, 'registered_roster')} → {c(FA, 2383, 'verify_roster')} → {c(FA, 2387, 'build_roster')} → {c(FA, 2422, '_run_strategy')} → {c(FA, 2890, 'CallbackHandler.__init__')} → {c(FA, 2891, 'SampleFactor.inputs')} → {c(FA, 2970, 'ComplianceHandler.__init__')} → {c(FA, 2972, 'RunLoop.__init__')} → {c(FA, 2974, 'Account.bind')} → {c(FA, 2975, 'RunLoop.run')}.",
              fn="registered_roster()", code=("def", 10),
              tip=f"<code>inputs()</code>는 이 run 전체에서 {count(FA, 'SampleFactor.inputs')}번 불린다: 검증의 import · 판정 · 얼리기 · 작업 시작의 요구 목록 · 결정 담당 조립 — 그리고 결정마다는 0번(기록 246)."),
            F(FA, 2567, "표지 · 칸 · 팻말 — 달리는 동안 디스크에 있는 것의 전부",
              f"③과 같은 준비가 전략 작업에도 있습니다: 표지(<code>run.json</code>, {ms(FA, 2490)} ms) → 작업일지 칸 <code>strategies/sample-factor@0696c8f4/</code>와 <code>tables/</code> → 팻말 <code>.running</code>(pid) → 첫 박동의 진행 메모 <code>progress.json</code>({ms(FA, 3118)} ms). "
              f"이 작업이 도는 동안 <b>디스크에 있는 것은 이게 전부</b>입니다. 행은 작업대(메모리)로만 가고, 박동(<code>heartbeat</code>, 이 run {count(FA, 'RunRecordWriter.heartbeat')}번)은 팻말의 시각을 초당 한 번만 만지며, 진행 메모는 5초마다 다시 씁니다(이 run은 5초 안에 끝나 한 번).",
              f"{c(FA, 2490, 'freeze_run_record')} → {c(FA, 2496, 'write_run_record')} → {c(FA, 2562, 'write_atomically')} → {c(FA, 2567, 'RunRecordWriter.open')} → {c(FA, 2570, 'RunRecordWriter._open')} → {c(FA, 2571, 'RunRecordWriter._claim')} · 첫 {c(FA, 3112, 'RunRecordWriter.heartbeat')} → {c(FA, 3115, 'RunRecordWriter.checkpoint')} → {c(FA, 3118, 'write_atomically')}.",
              fn="RunRecordWriter.open() · _claim()", code=at("src/vqapr/record/writer.py", "def _claim(self)", 12),
              disk={".vqapr/runs/sample-factor-run/run.json": "새로 생김 — 표지", FACTOR_DIR + "tables/": "새로 생김 (빈 폴더)", FACTOR_DIR + ".running": "새로 생김 — pid (작업 중 팻말)", FACTOR_DIR + "progress.json": "새로 생김 — 진행 메모"}),
            F(FA, 3270, "아침 8시 — 모멘텀 반제품을 어디까지 꺼낼지",
              f"2022-01-12 08:00, 첫 결정. 전략이 모멘텀 표의 최신 행 하나를 달라고 합니다. 선반은 작업 시작 앞의 격자 한 칸(01-11 16:00)부터 작업 끝(01-25 23:59:59)까지만 스캔하고({ms(FA, 3295)} ms) (11일 × 10종목) 판 하나를 만듭니다({ms(FA, 3332)} ms).",
              f"{c(FA, 3228, 'SampleFactor.decide')} → <code>panel_window</code> → {c(FA, 3270, '_scan_bounds')} → {c(FA, 3295, 'observation_table')} → {c(FA, 3332, 'Panel.from_table')} → <code>PanelWindow.matrix</code>.",
              fn="_scan_bounds()", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 10, before=2),
              mem={"bounds": "2022-01-11 16:00 ~ 2022-01-25 23:59:59 +09:00", "panel.blocks['momentum_5d'].shape": "(11, 10) (probe_panel.py)"}),
            F(FA, 3228, "[0.16.0] 한 행을 읽고 여섯 이름을 고른다 — 사건 하나, 도장 하나",
              f"저자 코드. 판은 01-11 16:00의 행(전날 저녁에 알 수 있던 값) 하나 × 종목 10. 정렬해서 하위 3(K000004 · 5 · 6)에 −1/6, 상위 3(K000003 · 8 · 9)에 +1/6. <code>vq.Rebalance.signed</code>는 부호가 방향입니다. "
              f"결정이 돌아오면 공장은 “이 결정이 실제로 어떤 상자의 어떤 봉인을 읽었나”(source refs)를 한 번 만들어({ms(FA, 3457)} ms) 주문서 도장과 증거 양쪽에 씁니다. 그 뒤 도장을 찍고 받아들여 계좌 · 수첩 · 대기 주문서를 한 번에 게시합니다. "
              "[0.16.0] 라인이 넘긴 사건은 <code>ScheduledEvent(event_id='sample-factor-run.schedule-2022-01-12T0800')</code>이고, 저자 코드가 보는 시각은 <code>call.at</code>입니다.",
              f"{c(FA, 3120, 'RunLoop.handle', note=', ScheduledEvent 01-12 08:00')} → {c(FA, 3121, 'StrategyPart.dispatch')} → {c(FA, 3123, 'CallbackHandler.dispatch')} → {c(FA, 3228, 'SampleFactor.decide')} → {c(FA, 3457, '_callback_actual_source_refs')} → {c(FA, 3462, '_actual_source_refs')} → {c(FA, 3563, '_stamp_intent')} → {c(FA, 3630, '_accept_intent')} → {c(FA, 3702, '_candidate_callback_state')} → {c(FA, 3785, '_callback_evidence')} → {c(FA, 3821, 'RunStateRepository.publish')}. 둘째 날 {c(FA, 5317, 'decide')}.",
              fn="SampleFactor.decide() — 저자 코드", code=at(DECL + "factor.py", "def decide(self, call):", 16), author=True,
              mem={"weights": "K000003 +0.1667 · K000008 +0.1667 · K000009 +0.1667 · K000004 −0.1667 · K000005 −0.1667 · K000006 −0.1667", "대기 주문서": "1장 (계좌 v0 기준)", "source refs": f"결정당 1회 (이 run {count(FA, '_actual_source_refs')}회)"}),
            F(FA, 3823, "결정의 흔적은 작업대에 쌓인다 — 디스크엔 아무것도",
              f"게시가 일어나면 이번 결정이 남긴 행(weight 6행)이 작업일지 쓰개(<code>RunRecordWriter</code>)로 흘러갑니다. 쓰개는 그 행을 <b>그 자리에서 Arrow 표로 타입</b>해(한 열에 두 종류가 섞이면 여기서 거절) 작업대(메모리)에 올려 둘 뿐, 파일을 쓰지 않습니다. 이 run에서 {count(FA, 'RunRecordWriter.append_chunk')}번 이렇게 쌓입니다. "
              "작업대가 256 MB를 넘으면 그때만 안전 밸브로 조각 파일을 씁니다 — 이 run은 넘지 않았습니다.",
              f"{c(FA, 3821, 'RunStateRepository.publish')} → {c(FA, 3822, 'RunStateRepository._deliver')} → {c(FA, 3823, 'RunRecordWriter.append_chunk')} → {c(FA, 3825, '_arrow_table')}.",
              fn="RunRecordWriter.append_chunk()", code=at("src/vqapr/record/writer.py", "def append_chunk(self, chunk: RecordChunk)", 16),
              mem={"작업대 (writer._buffer)": "{vqapr.weight: [Arrow 6행]} … 끝까지 쌓임"},
              disk={FACTOR_DIR + "tables/": "여전히 비어 있음"}),
            F(FA, 3858, "오후 3시 반 — 숏 셋이 실제로 팔린다",
              f"시장 사건 01-12 15:30(트레이스엔 UTC 06:30). 기다리던 주문서가 때가 되어 주문을 계획합니다(비중 → 주 수, {ms(FA, 3946)} ms, <code>domain/order.py</code>의 <code>plan_orders</code>). SIGNED 상장이라 음수 주 수가 통과합니다. "
              "체결: K000003 +23 · K000008 +8 · K000009 +94, K000004 −55 · K000005 −19 · K000006 −12(close 가격, 학술 프로파일이라 수수료 0). 계좌 v1: 현금 99,463,501.24, NAV 1억. 체결 행도 작업대로 갑니다.",
              f"{c(FA, 3850, 'RunLoop.handle', note=', MarketEvent 06:30 UTC')} → {c(FA, 3851, 'MarketClock.at')} → {c(FA, 3858, 'ExecutionHandler.fill')} → {c(FA, 3946, 'plan_orders')} → {c(FA, 4332, 'AcademicExchange.execute')} → {c(FA, 4577, 'Account.append')} → {c(FA, 4854, 'commit_append')}.",
              fn="ExecutionHandler.fill()", code=("def", 12),
              mem={"계좌 v1": "롱 3 · 숏 3 · 현금 99,463,501.24 · NAV 100,000,000.00"}),
            F(FA, 4892, "[0.16.0] 같은 시각에 이어서 — 계좌가 자기를 평가하고, 규칙이 보고, 다음으로",
              f"체결 직후 보유를 종가로 평가합니다({ms(FA, 4892)} ms). [0.16.0] 곱하는 것은 계좌 자신입니다: <code>Account.mark(state, prices)</code>가 자기 보유 × 가격을 계산하고({ms(FA, 4941)} ms), <code>domain/valuation.py</code>는 어느 가격을 쓸지만 고릅니다(기록 276). 규칙이 없으니 “규칙이 본다”는 자리는 {ms(FA, 5177)} ms에 지나갑니다. "
              "시장 사건 하나는 늘 이 순서입니다: 발생(accrue) → 체결(execute) → 평가(value) → 판정(observe). 이 run엔 열 번.",
              f"{c(FA, 4892, 'ValuationHandler.mark')} → {c(FA, 4941, 'Account.mark')} → {c(FA, 5177, 'ComplianceHandler.observe')} → 다음 아침 {c(FA, 5207, 'RunLoop.handle')}.",
              fn="ValuationHandler.mark()", code=("def", 12)),
            F(FA, 24218, "마감 — 작업대의 표 셋이 본문 파일 셋으로, 그다음 도장",
              f"10일(계좌 v10, 주문 73 · 체결 54)이 끝나면 작업일지를 닫습니다. 먼저 <b>본문</b>: 작업대의 Arrow 표를 표마다 <code>tables/&lt;표&gt;/all.parquet</code> 하나로 씁니다({ms(FA, 24221)} ms) — account 70행 · fill 73행 · weight 60행. 그 다음 <b>마감 도장</b> <code>strategy.json</code>을 임시 파일 → 바꿔 끼우기로({ms(FA, 24267)} ms). 그 뒤에야 팻말을 치우고 진행 메모를 지웁니다. "
              "도장을 본문 뒤에 쓰는 것이 약속입니다: 읽는 쪽이 도장을 찾으면 모든 행이 그 옆에 있습니다. 중간에 죽은 작업은 도장이 없어 “끝나지 않은 일지”로 보입니다.",
              f"{c(FA, 24052, 'RunLoop.finish')} → {c(FA, 24079, 'freeze_strategy_record')} → {c(FA, 24124, 'RunRecordWriter.finish')} → {c(FA, 24218, 'RunRecordWriter._seal')} → {c(FA, 24221, '_write_compact')} → {c(FA, 24267, 'write_atomically')} → {c(FA, 24269, 'RunRecordWriter._unlock')}.",
              fn="RunRecordWriter._seal() → strategy.json", code=at("src/vqapr/record/writer.py", "def _seal(self)", 12),
              disk={FACTOR_DIR + "tables/vqapr.account/all.parquet": "새로 생김 — 70행", FACTOR_DIR + "tables/vqapr.fill/all.parquet": "새로 생김 — 73행", FACTOR_DIR + "tables/vqapr.weight/all.parquet": "새로 생김 — 60행", FACTOR_DIR + "strategy.json": "새로 생김 — 마감 도장", FACTOR_DIR + ".running": "없어짐", FACTOR_DIR + "progress.json": "없어짐"}),
            F(FA, 24476, "비중이 반제품이 되어 입고된다 — 역시 같은 검수대",
              f"도장까지 찍힌 일지에서 weight 표 60행을 읽어 반제품 <code>sample-factor-weights</code>로 냅니다. 각 행의 시각은 그 결정의 시각(08:00). 상자는 <code>.vqapr/materialized/sample-factor-weights/all.parquet</code>로 포장되고({ms(FA, 24500)} ms) 검수대({ms(FA, 24502)} ms)를 지나 장부에 입고됩니다. "
              "[0.16.0] 일지의 모양은 schema v2(schedule 블록)라 0.16.0 전의 일지는 “다시 run 하라”는 고치는 법과 함께 거절됩니다.",
              f"{c(FA, 24275, '_publish_allocation')} → {c(FA, 24476, 'RunOutput.register')} → {c(FA, 24500, 'RunOutput._seal')} → {c(FA, 24502, 'verify_source')} → {c(FA, 24633, 'Transaction.commit')} → {c(FA, 24647, 'Workspace._write')}.",
              fn="RunOutput.register()", code=at("src/vqapr/run/engine/output.py", "# The rows land here, once, and only now", 9),
              disk={".vqapr/materialized/sample-factor-weights/all.parquet": "새로 생김 — 60행 (01-12 08:00 ~ 01-25 08:00 · weight ±0.1667) · 봉인 76a9b69b…", ".vqapr/workspace.yaml": "고쳐 씀 — + sample-factor-weights (produced_by sample-factor-run · sample-factor@0696c8f4)"}),
        ],
        "remember": [
            "한 사실은 한 번 읽고 나눠 쓴다 — 점검 쪽(RunFacts)도, 결정 쪽(source refs · inputs)도.",
            "달리는 동안 디스크엔 표지 · 팻말 · 진행 메모뿐. 행은 작업대에서 끝에 한 번 본문으로, 도장은 그 뒤, 팻말은 그 뒤.",
        ],
    },
    # ---------------------------------------------------------------- ⑤ stop-loss with memory
    {
        "id": "stop", "key": "⑤", "title": "stop-loss — 수첩(memory)이 진입가를 든다",
        "sub": f"register stoploss.yaml · {el(SR)} ms · {nc(SR)} 호출 — run sample-stoploss-run · {el(SL)} ms · {nc(SL)} 호출 · 37일 · 사건 74",
        "story": (
            "<b>무슨 일인가:</b> <code>stoploss.py</code>의 <code>SampleStopLoss</code>는 첫날 종가가 있는 종목을 전부 같은 비중으로 사고, 각 종목의 진입가를 <b>수첩</b>(<code>self.memory</code>)에 적어 둡니다. 그 뒤 날마다 최신 종가를 진입가와 견줘 3% 넘게 빠진 종목은 팔고 날짜를 적습니다. "
            "수첩은 엄격한 JSON이고 매 결정 전에 공장이 <b>복원</b>해 주고 뒤에 <b>저장</b>합니다 — 같은 작업을 다시 돌리면 같은 손절이 같은 날 납니다. 합성 데이터라 잘 빠져서 손절이 이어지고, 01-26부터는 K000008 하나, 02-23에 전량 매도, 그 뒤는 현금만."
        ),
        "shelf": [SR, SL],
        "frames": [
            F(SL, 6434, "결정 전 — 빈 수첩이 전략에게 건네진다",
              "2022-01-04 08:00, 첫 결정. 공장이 현재 상태의 수첩(첫날이라 <code>{}</code>)과 payload(빈 바이트)를 전략 객체에 넣습니다. 전략은 하나의 객체로 작업 전체를 살지만 믿을 건 이 복원된 수첩뿐입니다 — 다른 <code>self</code> 속성은 작업일지가 재현하지 못합니다. [0.16.0] 복원하는 곳은 <code>run/engine/stages/decide.py</code>.",
              f"{c(SL, 891, 'preflight')} … {c(SL, 5965, 'RunLoop.run')} → {c(SL, 6402, 'checkpoint')} → {c(SL, 6415, '_visible_callback_state')} → {c(SL, 6434, '_restore_callback_state', note=': strategy.memory = {} · load_payload(b\'\')')} → 창 → 계좌 view → decide.",
              fn="_restore_callback_state()", code=("def", 12),
              mem={"수첩 (strategy.memory)": "{}"}),
            F(SL, 6551, "첫 재료 — 38일짜리 판 하나가 작업 전체를 든다",
              f"작업 시작(01-04) 앞 한 칸(01-03 15:30)부터 끝(02-28)까지, 38일 × 10종목 판 하나를 만듭니다. 37번의 결정이 전부 이 판의 일부를 봅니다. 둘째 날의 범위 계산은 {ms(SL, 9990)} ms — 같은 창, 같은 판.",
              f"{c(SL, 6515, 'SampleStopLoss.decide')} → {c(SL, 6516, '_DeclaredReads.read')} → {c(SL, 6535, 'ModelWindow.panel')} → {c(SL, 6536, 'panel_window')} → {c(SL, 6551, '_scan_bounds')} → … 둘째 날 {c(SL, 9977, 'panel_window')} → {c(SL, 9990, '_scan_bounds')}.",
              fn="_scan_bounds()", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 10, before=2),
              mem={"bounds": "2022-01-03 15:30 ~ 2022-02-28 23:59:59 +09:00", "panel.blocks['close'].shape": "(38, 10) (probe_panel.py)"}),
            F(SL, 6515, "첫 결정 — 9종목에 들어가고 진입가 9개를 수첩에",
              "저자 코드. 최신 종가(01-03)가 있는 종목은 9개(K000010은 아직 없음). “처음이다” 표시가 없으니 entry에 종가 9개를 적고 표시를 세웁니다. 아무도 3%를 안 깼으니 9종목 같은 비중(투자 90%). 표시를 따로 두는 이유: 나중에 entry가 비었을 때 “처음”으로 오해해 다시 사지 않으려고요.",
              f"{c(SL, 6515, 'SampleStopLoss.decide')} → {c(SL, 6516, '_DeclaredReads.read')} → matrix → <code>vq.Rebalance.of</code>.",
              fn="SampleStopLoss.decide() — 저자 코드", code=at(DECL + "stoploss.py", 'if not self.memory.get("entered"):', 12, before=4), author=True,
              mem={"수첩 (self.memory)": "{entry: {K000001: …, …, K000009: …} 9개, stopped: {}, entered: true}"}),
            F(SL, 7750, "결정 후 — 읽은 것 한 번, 수첩 정리 한 번, 저장 한 번",
              f"결정이 돌아오면 순서대로: 읽은 것(source refs)을 한 번 만들고({ms(SL, 7469)} ms) → 주문서에 도장 → 받아들임 → 수첩을 엄격한 JSON으로 한 번 정리(Decimal · datetime · set이 있으면 여기서 거절; 기록 239) → 계좌 · 수첩 · 대기 주문서를 한 번에 게시(v1). 그리고 15:30에 9종목이 체결됩니다. 행은 역시 작업대로만 갑니다.",
              f"{c(SL, 7469, '_callback_actual_source_refs')} → {c(SL, 7567, '_stamp_intent')} → {c(SL, 7654, '_accept_intent')} → {c(SL, 7750, '_candidate_callback_state')} → {c(SL, 7926, 'RunStateRepository.prepare_callback')} → {c(SL, 7947, 'publish')} → {c(SL, 7948, '_deliver')} · {c(SL, 7984, 'ExecutionHandler.fill')} → {c(SL, 8674, 'execute')} → {c(SL, 9436, 'mark')}.",
              fn="_candidate_callback_state()", code=("def", 12),
              mem={"root": "v1 (계좌 v0 · 수첩 entry 9 · 대기 주문서 1)", "source refs": f"이 run {count(SL, '_actual_source_refs')}회 — 결정당 1회"}),
            F(SL, 9956, "둘째 날 — 복원된 수첩으로 첫 손절",
              "01-05 08:00. 복원된 수첩에 진입가 9개가 있습니다. 최신 종가(01-04)를 견주니 K000005가 −3%를 넘겼습니다 → <code>stopped['K000005'] = '2022-01-05'</code>, entry에서 지웁니다. 남은 8종목 같은 비중; 15:30에 K000005를 팝니다. "
              "이어지는 날들(보유 종목 수, 이 run의 weight 표에서): 9 → 8(01-05) → 7(01-06) → 5(01-11) → 4(01-19) → 3(01-24) → 2(01-25) → 1(01-26 ~ 02-22, K000008 하나).",
              f"{c(SL, 9873, '_restore_callback_state')} → {c(SL, 9956, 'SampleStopLoss.decide')} → {c(SL, 10212, '_stamp_intent')} → {c(SL, 10293, '_accept_intent')} → {c(SL, 10381, '_candidate_callback_state')} → {c(SL, 10557, 'prepare_callback')} · {c(SL, 10615, 'fill')}.",
              fn="SampleStopLoss.decide() — 손절", code=at(DECL + "stoploss.py", "for name, price in list(entry.items()):", 5), author=True,
              mem={"수첩 (self.memory)": "{entry: 8, stopped: {K000005: '2022-01-05'}, entered: true}"}),
            F(SL, 58156, "마지막 종목이 깨지면 — 전량 매도는 Hold가 아니라 빈 Rebalance",
              "02-23 08:00. K000008이 02-22 종가로 −3%를 넘겼습니다. entry가 비었고 계좌엔 K000008 52주가 있습니다. <code>Hold</code>는 “아무것도 하지 마라”라 포지션이 그대로 남습니다. 그래서 “목표 비중 없음, 현금 100%”를 돌려줍니다. 15:30에 K000008 −52가 1,441,901.11에 체결되고 계좌(v34)는 현금 84,184,068.92뿐입니다.",
              f"{c(SL, 58020, 'RunLoop.handle', note=', ScheduledEvent 02-23 08:00')} → {c(SL, 58156, 'SampleStopLoss.decide')} → <code>MarketClock.at</code> → {c(SL, 58596, 'fill')} → {c(SL, 58719, 'AcademicExchange.execute')} → {c(SL, 58774, 'Account.append')}.",
              fn="SampleStopLoss.decide() — 마지막", code=at(DECL + "stoploss.py", "held = {name: 1 for name in sorted(entry)}", 7), author=True,
              mem={"수첩 (self.memory)": "{entry: {}, stopped: 9개, entered: true}", "계좌 v34": "보유 {} · 현금 84,184,068.92"}),
            F(SL, 59285, "그 뒤 — Hold, 기다리는 주문서 없음, 오후엔 평가만",
              f"02-24 08:00부터 entry도 포지션도 없습니다 → <code>Hold</code>(“모든 종목이 손절선을 깼다, 현금으로 둔다”). 기다리는 주문서가 없으니 15:30의 체결 단계는 {ms(SL, 59667)} ms에 지나가고 평가만 합니다({ms(SL, 59668)} ms). 작업은 74 사건, 계좌 v34로 끝나고, ④와 같은 순서로 본문 셋 → 도장 → 팻말 치움 → 비중 반제품(102행, 01-04 ~ 02-22) 입고. "
              f"[0.16.0] 체결 앞의 발생 단계(<code>stages/accrue.py</code>)는 배당 · 이자 같은 것이 들어올 자리로, 지금은 받은 계좌를 그대로 돌려줍니다({ms(SL, 59664)} ms).",
              f"{c(SL, 59285, 'SampleStopLoss.decide', note=' → Hold')} · {c(SL, 59664, 'AccrualHandler.accrue')} → {c(SL, 59667, 'fill', note=', 기다리는 주문서 없음')} → {c(SL, 59668, 'ValuationHandler.mark')} … {c(SL, 61353, 'RunRecordWriter.finish')} → {c(SL, 61572, '_publish_allocation')} → {c(SL, 61899, 'RunOutput.register')}.",
              fn="SampleStopLoss.decide() — Hold", code=at(DECL + "stoploss.py", "if any(quantity != 0 for quantity in call.account.positions.values()):", 5), author=True,
              disk={STOP_DIR + "tables/ (account · fill · weight)": "새로 생김 — 139 · 111 · 102행", STOP_DIR + "strategy.json": "새로 생김 — 마감 도장", ".vqapr/materialized/sample-stoploss-weights/all.parquet": "새로 생김 — 102행 · 봉인 e09f29f7…", ".vqapr/workspace.yaml": "고쳐 씀 — + sample-stoploss-weights"},
              tip="strategy.json엔 수첩의 내용이 없다. 트레이스에 보이는 건 결정마다 복원 → 결정 → 한 번의 정리 → 저장이고, 일지엔 그 상태의 참조가 남는다."),
        ],
        "remember": [
            "수첩은 결정 전에 복원되고 뒤에 한 번 정리되어 저장된다. 첫 결정엔 {}. JSON이 아닌 것은 여기서 거절된다.",
            "“처음인가”는 따로 표시로 기억한다. 포지션을 다 비우려면 Hold가 아니라 빈 Rebalance.",
        ],
    },
    # ---------------------------------------------------------------- ⑥ enhanced index
    {
        "id": "enh", "key": "⑥", "title": "enhanced index — 반제품을 재료로",
        "sub": f"register enhanced.yaml · {el(ER)} ms · {nc(ER)} 호출 — run sample-enhanced-run · {el(EN)} ms · {nc(EN)} 호출 · 9일 — list datasets {el(LD)} ms · show run {el(SH)} ms",
        "story": (
            "<b>무슨 일인가:</b> <code>enhanced.py</code>의 <code>SampleEnhancedIndex</code>는 ④가 입고한 반제품(<code>sample-factor-weights</code>)을 alpha로 읽고, 종가가 있는 종목의 같은 비중(1/9)에 그 alpha의 절반을 더한 뒤 0 아래를 잘라 냅니다 — 롱온리 enhanced index. "
            "④가 08:00에 정한 비중을 알 수 있게 된 뒤인 09:00에 결정합니다. 두 상자를 각자 자기 기간으로 꺼냅니다(가격 10 × 10, alpha 10 × 10). 마지막으로 <code>list datasets</code>와 <code>show run</code>으로 창고에 무엇이 남았는지 봅니다: 장부에 dataset 6개, 그중 4개가 작업이 만든 반제품."
        ),
        "shelf": [ER, EN, LD, SH],
        "frames": [
            F(EN, 2621, "작업 키트 — 입고된 alpha가 dataset으로 묶인다",
              f"쓸 것 둘: <code>sample-factor-weights</code>(④가 만든 반제품)와 <code>sample-prices</code>(벤더 상자). 둘 다 같은 한 줄 — 봉인 확인({ms(EN, 2621)} · {ms(EN, 2640)} ms). 작업이 만든 반제품과 벤더 상자가 여기서 같은 취급을 받는다는 것이 이 장면의 요점입니다.",
              f"{c(EN, 1052, 'preflight')} → … {c(EN, 2620, '_freeze_sources')} → {c(EN, 2621, '_validate_requirement')} → {c(EN, 2622, 'Workspace.require_verified')} · {c(EN, 2640, '_validate_requirement')}.",
              fn="_validate_requirement()", code=at("src/vqapr/run/preflight/freeze.py", "def _validate_requirement", 14),
              mem={"키트의 봉인": "{materialized-sample-factor-weights: 76a9b69b…, sample-prices-source: 18bb7017…}"}),
            F(EN, 3610, "9시 — 두 판을 읽고 기본 비중에 alpha를 얹는다",
              f"2022-01-13 09:00. 가격 판: 01-12 15:30부터 (10 × 10) → 종가가 있는 종목 9개 → 기본 1/9 = 0.1111. alpha 판: 01-12 08:00부터 (10 × 10) → 최신 행은 <b>01-13 08:00</b>의 factor 비중(롱 K000002 · 3 · 8, 숏 K000004 · 5 · 9, 각 ±1/6)이고 그 절반(±0.0833)을 얹습니다: 롱 셋 0.1944, 숏 셋 0.0278, 나머지(K000001 · 6 · 7) 0.1111 — 합이 정확히 1이라 따로 맞출 게 없습니다. "
              f"첫 결정 {ms(EN, 3610)} ms(두 상자의 첫 스캔), 다음 날 {ms(EN, 7170)} ms. (2026-09-12 판은 이 결정이 01-12의 비중을 읽는다고 적었는데, 기록의 weight 표로 보면 01-13 08:00의 것입니다.)",
              f"{c(EN, 3540, '_window_factory.at', note=', 01-13 09:00')} → {c(EN, 3610, 'SampleEnhancedIndex.decide')} → prices: {c(EN, 4394, 'observation_table')} → {c(EN, 4431, 'Panel.from_table')} → alpha: {c(EN, 4506, 'observation_table')} → {c(EN, 4543, 'Panel.from_table')} → <code>Rebalance.of</code>. 둘째 날 {c(EN, 7170, 'decide')}.",
              fn="SampleEnhancedIndex.decide() — 저자 코드", code=at(DECL + "enhanced.py", "def decide(self, call):", 24), author=True,
              mem={"판": "prices (10 × 10) 01-12 15:30 ~ · alpha (10 × 10) 01-12 08:00 ~ (probe_panel.py)", "01-13 09:00의 비중": "K000002 · 3 · 8 = 0.1944 · K000004 · 5 · 9 = 0.0278 · K000001 · 6 · 7 = 0.1111 (sample-enhanced-weights)"}),
            F(EN, 5223, "3시 반 — 롱온리 체결, 그리고 아홉 날",
              f"첫 체결 {ms(EN, 5223)} ms: 9종목 전부 매수(K000001 +76 · K000002 +87 · K000003 +27 …), 현금 2,431,839.06 남음. 9일 동안 사건 18, 계좌 v9(주문 81 · 체결 41). 끝나면 ④와 같은 마감(본문 셋 → 도장 → 팻말 치움)을 하고 비중이 <code>sample-enhanced-weights</code>(81행)로 입고됩니다.",
              f"<code>MarketClock.at</code> → {c(EN, 5223, 'ExecutionHandler.fill')} … {c(EN, 27005, 'RunRecordWriter.finish')} → {c(EN, 27156, '_publish_allocation')} → {c(EN, 27420, 'RunOutput.register')} → <code>verify_source</code>.",
              fn="ExecutionHandler.fill()", code=("def", 12),
              disk={".vqapr/runs/sample-enhanced-run/strategies/sample-enhanced@371d7e0c/": "새로 생김 — strategy.json · tables 셋 (90 · 81 · 81행)", ".vqapr/materialized/sample-enhanced-weights/all.parquet": "새로 생김 — 81행 · 봉인 fa7c2f8e…", ".vqapr/workspace.yaml": "고쳐 씀 — + sample-enhanced-weights"}),
            F(LD, 13, "list datasets — 여섯, 그중 넷은 작업이 만든 반제품",
              f"장부를 열어({ms(LD, 13)} ms) dataset 목록을 냅니다: <code>sample-prices</code> · <code>sample-execution</code>(벤더), <code>sample-features</code>(③), <code>sample-factor-weights</code>(④), <code>sample-stoploss-weights</code>(⑤), <code>sample-enhanced-weights</code>(⑥). 어느 작업의 어느 코드 버전(<code>sample-factor@0696c8f4</code>)이 만들었는지가 이름 옆에 있습니다. 파일은 하나도 새로 생기지 않습니다.",
              f"{c(LD, 12, 'list_.run')} → {c(LD, 13, 'Workspace.open')} → {c(LD, 16, 'Workspace._read')} → {c(LD, 1073, 'datasets')} → {c(LD, 1081, '_summarize')} ×6 → {c(LD, 1087, 'success')}.",
              fn="Workspace.open()", code=("def", 6)),
            F(SH, 19, f"show run — 작업일지만 읽는다, {nc(SH)}호출",
              "<code>show run sample-enhanced-run</code>은 작업일지의 표지(<code>run.json</code>)만 읽습니다: 쓴 상자 둘과 각각의 봉인 번호, 거래소 코드의 지문, 체결 조건(close · 15:30 · Asia/Seoul), 초기 계좌, 기간. 이 작업이 어떤 바이트를 썼는지가 표지에 있으니, 나중에 상자가 바뀌어도 “그때 무엇이었나”는 남습니다. [0.16.0] 읽는 쪽은 <code>record/reader.py</code>이고, schema v1 일지(0.16.0 전)면 여기서 “다시 run 하라”고 거절합니다.",
              f"{c(SH, 0, 'main')} → {c(SH, 12, 'show.run')} → {c(SH, 13, 'run_ids')} → {c(SH, 19, 'read_run_record')} → {c(SH, 23, 'record_view')} → {c(SH, 24, 'strategy_refs')} → {c(SH, 28, 'datamodel_refs')} → {c(SH, 29, 'success')}.",
              fn="read_run_record()", code=("def", 10),
              disk={".vqapr/": "workspace.yaml · instruments.json · materialized/ 4 · runs/ 4 — 이 장면 끝의 창고 전체"}),
        ],
        "remember": [
            "작업이 입고한 반제품은 dataset이다: 다음 작업이 한 줄로 읽고, 키트는 봉인으로 묶고, 읽기는 자기 기간만큼.",
            "list · show는 장부와 작업일지만 읽는다. 일지의 표지는 쓴 상자의 봉인 번호를 든다.",
        ],
    },
    # ---------------------------------------------------------------- ⑦ --jobs batch
    {
        "id": "jobs", "key": "⑦", "title": "--jobs 배치 — 작업반장 · 작업자 · 미리 구운 재료판",
        "sub": f"run sample-factor-run sample-stoploss-run --jobs 2 --force · {el(BA)} ms · {nc(BA)} 호출 (작업반장) — 작업자 하나를 따로 추적: {el(WK)} ms · {nc(WK)} 호출",
        "story": (
            "<b>무슨 일인가:</b> ④와 ⑤를 한 배치로 동시에 돌립니다(<code>--jobs 2</code>; 일지가 이미 있으니 <code>--force</code>). 작업반장(driver)은 작업자(worker)를 부르기 전에 각 작업이 무엇을 쓰는지 한 번 묻고, 서로가 만드는 걸 쓰지는 않는지 보고, 쓸 상자를 <b>재료판(cube)으로 미리 한 번 구워</b> 둡니다 — 전 종목 × 전 기간 행렬 파일. "
            "작업자는 자기 기간만큼을 그 파일의 일부로 메모리에 매핑해 씁니다 — 스캔이 없습니다. 배치가 끝나면 구운 판은 지워집니다. 작업자도 단일 작업과 똑같이 출고 전 점검을 받습니다. "
            "작업반장의 트레이스는 프로세스 경계에서 끝나므로, 작업자 쪽은 같은 작업자 함수를 같은 프로파일러 아래서 따로 돌려 얻었습니다."
        ),
        "shelf": [BA, WK],
        "shelf_note": "구운 판(<code>.vqapr/cubes/&lt;배치&gt;/</code>)은 명령이 끝나기 전에 지워져 파일 목록에 남지 않습니다. 판에 무엇이 있었는지는 같은 굽기를 따로 돌린 <code>probe_cubes.py</code>로 쟀습니다(프레임 03). 두 작업의 일지는 작업자 프로세스가 같은 이름으로 다시 썼습니다.",
        "frames": [
            F(BA, 13, "작업반장 — 무엇을 쓰는지 한 번 묻고, 서로 독립인지 본다",
              f"작업이 둘이고 jobs가 2니 배치 경로입니다. 장부를 열고({ms(BA, 16)} ms) 작업마다 부품을 올려 “무엇을 읽나”를 한 번씩 묻습니다 — factor는 <code>sample-features</code>, stop-loss는 <code>sample-prices</code>. 그 답으로 둘이 서로가 만드는 걸 쓰지 않는지 봅니다({ms(BA, 1249)} ms). 병렬이면 순서를 약속할 수 없으니 그런 쪽이 있으면 배치 전체를 거절합니다.",
              f"{c(BA, 12, 'run')} → {c(BA, 13, '_run_each_in_workers')} → {c(BA, 16, 'Workspace.open')} → {c(BA, 1076, 'batch_reads')} → {c(BA, 1079, '_reads')} · {c(BA, 1170, '_reads')} → {c(BA, 1249, 'require_independent_batch')} → {c(BA, 1258, 'batch_cubes')}.",
              fn="_run_each_in_workers()", code=("def", 12),
              mem={"작업": "[sample-factor-run, sample-stoploss-run]", "쓰는 것": "factor → sample-features[momentum_5d] · stop-loss → sample-prices[close]"}),
            F(BA, 1258, "굽기 전에 — 묵은 판을 치우고, 판 칸을 잠근다",
              "<code>.vqapr/cubes/</code> 아래에 이 배치의 칸을 만들고 잠금 파일에 pid를 적습니다. 먼저 이전 배치가 남긴 묵은 칸(잠금이 오래 갱신 안 된 것)을 치우고, 따로 도는 스레드가 잠금을 주기적으로 만져 “살아 있다”고 표시합니다. 그리고 굽기.",
              f"{c(BA, 1258, 'batch_cubes')} → {c(BA, 1260, '_bake_for_batch')} → {c(BA, 1270, 'source_digest')} → {c(BA, 1273, 'bake', note=': sample-features')} → {c(BA, 1372, 'source_digest')} → {c(BA, 1375, 'bake', note=': sample-prices')}.",
              fn="batch_cubes()", code=("def", 14),
              disk={".vqapr/cubes/<pid>-<hex>/": "새로 생김 — 잠금 (pid)"}),
            F(BA, 1375, "굽기 — 가격 상자의 close를 전 종목 × 전 기간으로 한 번",
              f"상자마다 한 번: 종목 전부(10)를 세고, 입고 때 잰 기간 전체를 스캔하고, (735 × 10) 숫자 행렬로 접어 <code>close.npy</code>(58,928 B)로 저장합니다. 옆에 어느 칸에 값이 있었나(<code>present.npy</code>), 날짜 목록, 종목 목록, 원천 상자의 봉인 번호(<code>cube.json</code>). 앞의 <code>sample-features</code>는 12 × 9({ms(BA, 1273)} ms는 이 프로세스의 첫 스캔). 구울 수 없는 상자는 조용히 빠지고 그 작업자는 스캔합니다.",
              f"{c(BA, 1273, 'bake', note=': sample-features')} → {c(BA, 1274, 'distinct_values')} → {c(BA, 1327, 'placement')} · {c(BA, 1375, 'bake', note=': sample-prices')} → {c(BA, 1376, 'distinct_values')} → {c(BA, 1431, 'placement')}.",
              fn="bake()", code=("def", 12),
              disk={".vqapr/cubes/<배치>/sample-prices/": "close.npy (735, 10) float64 58,928 B · present.npy (735, 10) 7,478 B · instants.npy (735,) · instruments.json 10 · cube.json (봉인 18bb7017…)", ".vqapr/cubes/<배치>/sample-features/": "momentum_5d.npy (12, 9) 992 B · present.npy · instants.npy (12,) · instruments.json 9 · cube.json (봉인 54f8fd04…) — probe_cubes.py"}),
            F(BA, 2918, "작업자를 부른다 — 작업반장의 트레이스는 여기서 경계를 만난다",
              f"두 작업이 두 프로세스에 하나씩 갑니다. 넘기는 건 문자열과 bool뿐(프로젝트 경로, 작업 이름, 저장소, force, 판 칸). {ms(BA, 2918)} ms 동안 작업반장은 기다립니다. 이 프로파일러는 이 프로세스의 것이라 작업자 안의 호출은 여기 없습니다 — 다음 두 프레임은 작업자를 따로 추적한 것입니다.",
              f"{c(BA, 2918, 'in_workers')} — 안쪽 호출 없음(다른 프로세스).",
              fn="in_workers()", code=("def", 12)),
            F(WK, 16, "[0.16.0] 작업자 — 출고 전 점검을 지나고 판정을 받는다",
              f"작업자 프로세스는 장부를 열고({ms(WK, 1)} ms — 이미 데워진 파일) 자기 작업을 <code>preflight</code>에 넘깁니다: 판정 {ms(WK, 18)} ms · 얼리기 {ms(WK, 1194)} ms · 공구 봉지 {ms(WK, 1649)} ms. 판정이 거절하면 check와 같은 code로 거절되고 일지는 안 쓰입니다 — 작업자가 판정 없이 얼려, check가 거절한 작업을 배치가 돌리던 사고(이슈 015)가 다시 날 수 없는 이유입니다. 그 뒤는 단일 작업과 같습니다(표지 → 팻말 → 작업대 → 본문 → 도장).",
              f"{c(WK, 0, 'run_registered_strategy')} → {c(WK, 1, 'Workspace.open')} → {c(WK, 16, 'preflight')} → {c(WK, 18, 'judgments')} → {c(WK, 1194, 'freeze')} → {c(WK, 1246, '_freeze_strategy')} → {c(WK, 1587, '_freeze_sources')} → {c(WK, 1649, 'RunResources.of')} → {c(WK, 1663, 'require_ready')} → {c(WK, 1665, 'registered_roster')} → {c(WK, 1711, '_run_strategy')} → {c(WK, 2271, 'RunLoop.run')}.",
              fn="run_registered_strategy() — 작업자", code=at("src/vqapr/run/assemble.py", "def run_registered_strategy", 16)),
            F(WK, 2616, "작업자 — 스캔 대신 구운 판을 매핑한다",
              f"작업자의 첫 결정(01-12 08:00). 범위는 평소처럼 정하고({ms(WK, 2566)} ms), 그 다음이 다릅니다: 선반에 판 칸이 있으니 <code>cube.json</code>의 원천 봉인이 작업자가 방금 확인한 봉인과 같은지 본 뒤({ms(WK, 2590)} ms), <code>momentum_5d.npy</code>를 메모리 매핑으로 열어 자기 기간의 행만 잘라 씁니다({ms(WK, 2616)} ms). "
              f"작업이 선언한 종목(10)이 판의 종목(9)과 달라 한 번 모으기(gather)를 합니다(11 × 10, K000010 열은 NaN). 이 트레이스 어디에도 스캔(<code>observation_table</code>)이 없습니다(×{count(WK, 'observation_table')}).",
              f"{c(WK, 2524, 'SampleFactor.decide')} → {c(WK, 2551, 'panel_window')} → {c(WK, 2566, '_scan_bounds')} → {c(WK, 2590, 'open_cube')} → {c(WK, 2616, 'panel_from_cube')} → {c(WK, 2629, 'PanelWindow.matrix')} → {c(WK, 2742, '_callback_actual_source_refs')}. 다음 날 {c(WK, 4602, 'decide')}.",
              fn="panel_from_cube()", code=("def", 12),
              mem={"cube": "sample-features: instants 12 · names 9 · 봉인 54f8fd04… = 작업자의 봉인", "panel": "(11 × 10) gather — K000010 열 NaN"}),
            F(BA, 2921, "배치가 돌아오면 구운 판은 없다 — 영수증은 작업마다 하나",
              f"작업자 둘이 결과를 돌려주면 <code>batch_cubes</code>의 finally가 스레드를 멈추고 판 칸을 지웁니다({ms(BA, 2921)} ms). 성공이든 거절이든 예외든 같습니다 — 쌓이는 게 없습니다. 작업마다 일지를 읽어 영수증을 만듭니다: factor 계좌 v10 · 주문 73 · 체결 54, stop-loss 계좌 v34 · 주문 111 · 체결 59 — ④ · ⑤와 같은 수. 영수증의 <code>jobs: 2</code>가 실제로 돈 프로세스 수입니다.",
              f"{c(BA, 2918, 'in_workers')} → {c(BA, 2921, 'batch_cubes', note=': finally → rmtree')} → {c(BA, 2922, '_worker_entry', note=': sample-factor-run')} → {c(BA, 2923, '_strategy_envelope')} → {c(BA, 3155, '_worker_entry', note=': sample-stoploss-run')} → {c(BA, 3502, '_runs_envelope')} → {c(BA, 3506, 'success')}.",
              fn="batch_cubes() — finally", code=at("src/vqapr/run/batch.py", "def batch_cubes", 14),
              disk={".vqapr/cubes/<pid>-<hex>/": "없어짐 — 배치 칸 삭제", ".vqapr/runs/": "sample-factor-run · sample-stoploss-run 다시 씀 (--force, 같은 이름)"}),
        ],
        "remember": [
            "작업자도 출고 전 점검을 지난다: check가 거절하는 작업은 배치도 거절하고 일지를 쓰지 않는다.",
            "배치는 무엇을 쓰는지 한 번 묻고, 상자마다 재료판을 한 번 굽고, 작업자는 매핑한다. 끝나면 판은 없다.",
        ],
    },
]

TABLE = {
    "title": "트레이스가 확인한 것 — 0.16.0에서 바뀐 자리, 그대로인 자리, 파일이 생기는 자리",
    "rows": [
        ("<b>[0.16.0] run의 문은 preflight, 얼리기는 freeze</b> (기록 279)",
         f"<code>preflight</code>: 03 #340 · 06 #475 · 08 #730 · 10 #891 · 12 #1052 · 16 #16. <code>freeze</code>: 03 #49684(저장된 예외, {ms(CK, 49684)} ms) · 06 #1798 · 08 #1900 · 16 #1194",
         "check · run · 작업자가 같은 함수를 지나고 선언은 명령당 한 번 읽힌다(기록 240–242)"),
        ("<b>[0.16.0] 시간표가 사건을 만든다</b> (기록 278)",
         f"<code>RunFacts.schedule</code>: 08 #757 → #1904({ms(FA, 1904)} ms). <code>derived_schedule</code>: 03 #369 {ms(CK, 369)} ms(734일) · 08 #760 {ms(FA, 760)} ms. <code>RunLoop.handle</code>: 08 #3120 <code>ScheduledEvent(…schedule-2022-01-12T0800)</code> · #3850 <code>MarketEvent(06:30 UTC)</code>",
         "선언의 <code>agenda:</code>는 <code>schedule:</code>, 저자가 보는 시각은 <code>call.at</code>"),
        ("<b>[0.16.0] 계좌가 자기 보유를 곱한다</b> (기록 276)",
         f"08: <code>ValuationHandler.mark</code> #4892 → <code>Account.mark</code> #4941({ms(FA, 4941)} ms). 가격 고르기만 <code>domain/valuation.py</code>",
         "상태 없는 <code>ValuationService</code>가 없어졌다"),
        ("<b>쓰기는 .vqapr/ 아래에서만</b>",
         "16개 명령의 <code>files_after</code>에서 원본 19개는 이름이 그대로이고, 기록된 쓰기 호출(<code>write_atomically</code> · <code>_write_roster</code> · <code>RunOutput._write</code> · <code>_write_compact</code>)의 대상은 모두 <code>.vqapr/</code> 아래. 거절 둘(02 · 03)엔 쓰기 호출이 없다",
         "창고는 원본 상자를 고치지 않는다. 등록은 읽고 재기만 한다"),
        ("<b>작업일지가 생기는 순서</b>",
         f"08: 표지 <code>run.json</code> #2562 → 칸·팻말 <code>RunRecordWriter.open</code> #2567 → 진행 메모 #3118 → 작업대에 {count(FA, 'RunRecordWriter.append_chunk')}번 → 본문 <code>_write_compact</code> #24221 → 도장 <code>strategy.json</code> #24267 → 팻말 치움 #24269 → 반제품 #24500 → 장부 #24647. 06(DataModel)은 반제품 입고 #7771이 도장 #8146보다 먼저",
         "도장이 있으면 본문이 있다. 달리는 동안 디스크엔 표지 · 팻말 · 진행 메모뿐(기록 087 · 164 · 255)"),
        ("<b>계산된 숫자는 그대로</b>",
         "factor: 주문 73 · 체결 54 · 계좌 v10, 첫날 +23 · +8 · +94 / −55 · −19 · −12, 현금 99,463,501.24. stop-loss: 111 · 59 · v34, 02-23 K000008 −52 @ 1,441,901.11, 현금 84,184,068.92. enhanced: 81 · 41 · v9. features 108행 · factor 비중 60행. 봉인 18bb7017… · 49e4b4ab… · 54f8fd04… · 76a9b69b…",
         "기록에서 직접 읽었다. 2026-09-12 판과 같다. 코드 지문 sample-factor@0696c8f4 · sample-features@4327b244 · sample-enhanced@371d7e0c도 같고, sample-stoploss는 @6db3d49b(이번 선언의 import 줄이 달라서)"),
        ("<b>한 사실은 한 번</b> (기록 246–248)",
         f"<code>_actual_source_refs</code>: 08 ×{count(FA, '_actual_source_refs')} · 10 ×{count(SL, '_actual_source_refs')} · 12 ×{count(EN, '_actual_source_refs')}. <code>_local_date</code>: 06 ×{count(DM, '_local_date')} · 08 ×{count(FA, '_local_date')} · 10 ×{count(SL, '_local_date')} · 03 ×{count(CK, '_local_date')}. <code>heartbeat</code>: 08 ×{count(FA, 'RunRecordWriter.heartbeat')} · 10 ×{count(SL, 'RunRecordWriter.heartbeat')} (팻말은 초당 한 번만 만진다)",
         "0.14.3 · 2026-09-12 판과 같은 수"),
        ("호출 수",
         f"register {nc(R)} · check {nc(CK)} · DataModel {nc(DM)} · factor {nc(FA)} · stop-loss {nc(SL)} · enhanced {nc(EN)} · 작업자 {nc(WK)} (0.14.3: 973 · 48,329 · 8,158 · 24,374 · 61,659 · 27,311 · 23,353)",
         "2026-09-12 판(980 · 49,807 · 8,171 · 24,985 · 62,541 · 27,993 · 23,963)과 거의 같다 — 선언 파일의 줄이 조금 달라 저자 코드의 호출이 두어 개 다를 뿐"),
        ("식은 읽기가 절대치를 지배한다",
         f"등록의 <code>check_span</code> #214 {ms(R, 214)} ms(두 번째 상자 #392 {ms(R, 392)} ms) · 명단 #47 {ms(R, 47)} ms(첫 pyarrow) · DataModel 첫 <code>observation_table</code> #3233 {ms(DM, 3233)} ms · 작업 시작의 명단 08 #2376 {ms(FA, 2376)} ms, 작업자 #1665 {ms(WK, 1665)} ms",
         "판끼리 절대치를 비교하지 말 것"),
        ("<b>[바뀔 예정] 바뀐 상자의 반송</b>",
         "03: <code>require_verified</code> #47367 → <code>dataset.source_changed</code>(412), 49e4b4ab… ≠ 34c1d63c…",
         "이 트리의 지금 동작. 오너 판정(2026-09-13): 봉인이 바뀌면 등록과 같은 기준으로 다시 검수하고 신고와 다를 때만 반송(daily batch append). 결과를 적을 자리(장부를 고쳐 쓰기 / 선언과 측정을 분리)는 보류"),
    ],
}
