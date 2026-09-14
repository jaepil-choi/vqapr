# ruff: noqa: E501, RUF001 -- prose data: long lines and typographic characters are the content
# The 0.16.0 scenario stepper: the seven scenarios of the 0.14.3 page traced again on the stamped
# 0.16.0 tree. What a run computes did not change; where things live and what they are called did
# (the concept-tree campaign, records 268-279), so every frame stands in a file of the new tree and
# the frames where a name or a place changed are marked [0.16.0].
#
# Ported from `exp_249/scenes_0_14_3.py` by `port_scenes.py` (indices, milliseconds, anchors), then
# the prose rewritten by hand against the new traces. Frames inside a long loop were re-placed by the
# event they handle, not by index (README). Rendered by `render_0_16_0.py`, which runs `exp_230`'s
# renderer with `REPO` bound to the tree the traces were taken on. A number that appears here appears
# in a trace, in a record the traced commands wrote, or in `exp_238/probe_panel.py` /
# `probe_cubes.py` output (the same project and the same numbers as the 0.13.0-0.14.3 pages).

DECL = "experiments/exp_283_the_scenario_trace_0_16_0_src_map/declarations/"


def at(file: str, needle: str, n: int = 8, before: int = 0) -> list[str]:
    """`n` source lines of `file` starting `before` lines above the first line holding `needle`."""
    lines = (REPO / file).read_text(encoding="utf-8").splitlines()  # noqa: F821 - bound by render.py
    for index, line in enumerate(lines):
        if needle in line:
            start = max(0, index - before)
            return [item.rstrip() for item in lines[start : start + n]]
    raise KeyError((file, needle))


def W(story: str, calls: str | None = None) -> str:
    """A frame's prose: the plain story first, the trace's call order folded beneath it."""
    html = f'<p class="story">{story}</p>'
    if calls:
        html += f'<details class="tr"><summary>함수 이름과 호출 번호로 보면</summary><p>{calls}</p></details>'
    return html


def F(trace: str, idx: int, title: str, story: str, calls: str | None = None, **extra) -> dict:
    return {"trace": trace, "idx": idx, "title": title, "what": W(story, calls), **extra}


HEADER = {
    "title": "vqapr 0.16.0 시나리오 디버거",
    "storage_key": "vqapr-stepper-0160",
    "eyebrow": "vqapr 0.16.0 · develop 26726b1f (records 268–279, 개념 트리) · 2026-09-12 · 실제 실행을 sys.setprofile로 추적한 결과",
    "h1": "vqapr 0.16.0 시나리오 디버거 — 같은 일곱 가지 일을, 새 폴더 트리 위에서 한 프레임씩",
    "lede": (
        "<b>이 페이지는 vqapr이 실제로 무엇을 하는지를, 실제로 돌린 기록으로 보여 줍니다.</b> "
        "<code>vqapr new sample</code>이 만든 작은 프로젝트(종목 10개, 2022-01-03 ~ 2024-12-30, 거래일 735일)에서 사용자가 할 법한 일곱 가지를 차례로 합니다: "
        "① 데이터를 <b>등록</b>하고, ② 등록이 <b>거절</b>되는 두 경우를 보고, ③ 종목별 지표(5일 모멘텀)를 만드는 <b>DataModel</b>을 돌리고, "
        "④ 그 지표로 상위 3개는 사고 하위 3개는 파는 <b>factor 전략</b>을 돌리고, ⑤ 진입가를 <b>기억</b>해 3% 빠지면 파는 <b>stop-loss 전략</b>을 돌리고, "
        "⑥ ④가 남긴 비중을 읽어 <b>enhanced index</b>를 만들고, ⑦ ④와 ⑤를 <b>동시에</b>(<code>--jobs 2</code>) 돌립니다. "
        "<b>0.16.0에서 달라진 것:</b> 하는 일은 그대로입니다 — 체결 · 계좌 · 저장된 비중이 0.14.3 판과 같습니다. 달라진 것은 <b>자리와 이름</b>입니다. "
        "폴더가 고리의 개념을 따르게 되어(<code>flow/</code> → <code>run/</code>, <code>project/</code> → <code>workspace/</code>, <code>data/validation.py</code> → <code>data/verification.py</code>) 프레임마다 서 있는 파일이 바뀌었고, "
        "run의 문은 <code>preflight</code>, 얼리기는 <code>freeze</code>, 결정 시각 목록은 <code>schedule</code>이 되었습니다. 그런 자리에 <b>[0.16.0]</b>을 붙였습니다. "
        "<b>읽는 법:</b> 프레임마다 <b>위쪽 문장</b>은 지금 일어나는 일을 보통 말로 적은 것이고, <b>아래 접힌 곳</b>에 함수 이름과 호출 번호(<code>#idx</code>)와 ms가 있습니다. "
        "코드 아래 <b>이 파일</b> 카드는 그 프레임이 선 파일이 무슨 파일인지 말하고, 맨 아래 <b>src/ 지도</b>에는 <code>src/vqapr/</code>의 파일 199개가 하나씩 설명되어 있습니다. "
        "모든 번호와 ms는 <code>sys.setprofile</code>이 실제로 기록한 값이고, 스니펫은 그 시점의 소스 줄입니다 — 상상한 것은 없습니다(<code>experiments/exp_283_the_scenario_trace_0_16_0_src_map/</code>)."
    ),
    "facts": [
        {"k": "한 줄 요약", "v": "선언 → 문 → 얼리기 → 루프 → 기록", "s": "사용자는 YAML로 <b>선언</b>하고, 파일의 문(<code>data/verification.py</code>)이 파일을 실제로 열어 재고, run의 문(<code>preflight</code>)이 판정한 뒤 <code>freeze</code>가 이름을 값으로 <b>얼리고</b>, 루프가 사건을 시각 순서로 <b>처리하고</b>, 결과는 <b>기록</b>이 되며 그 표가 다시 dataset이 된다"},
        {"k": "데이터", "v": "10 × 735", "s": "종목 × 거래일. run들은 2022년 1~2월의 짧은 구간만 쓴다: DataModel 16일 · factor 10일 · stop-loss 37일 · enhanced 9일"},
        {"k": "명령 16개", "v": "호출 35 … 62,541", "s": "register 980 · 거절 431 · check(거절) 49,807 · 재등록 1,304 · DataModel run 8,171 · factor 24,985 · stop-loss 62,541 · enhanced 27,993 · list 1,093 · show 35 · 배치 driver 3,512 · worker 23,963"},
        {"k": "[0.16.0] 이름", "v": "preflight · freeze · schedule", "s": "<code>verify_run</code> → <code>preflight</code>, <code>preflight_run</code> → <code>freeze</code> (기록 279) · <code>agenda</code> → <code>schedule</code>, 루프가 처리하는 것은 <code>ScheduledEvent</code>와 <code>MarketEvent</code> (기록 278) · 저자 코드는 <code>from vqapr import public as vq</code> 한 줄"},
        {"k": "[0.16.0] 자리", "v": "flow/ → run/", "s": "<code>run/preflight/</code>(사실 · 판정 · 얼리기 · 평결) · <code>run/engine/</code>(루프, 그리고 부르는 메서드 이름의 단계: decide · execute · value · observe · accrue) · <code>run/assemble.py</code> · <code>run/batch.py</code> (기록 268–277)"},
        {"k": "계산은 그대로", "v": "73 · 54 · v10", "s": "factor run의 주문 · 체결 · 계좌 버전 — 0.14.3과 같다. stop-loss 111 · 59 · v34, enhanced 81 · 41 · v9. 달라진 값은 컴포넌트 지문뿐이다(저자 코드의 import 줄이 바뀌어서): <code>sample-factor@9bba20c4</code> → <code>@0696c8f4</code>"},
        {"k": "factor run", "v": "롱 3 · 숏 3", "s": "첫날 K000003 +23주 · K000008 +8 · K000009 +94 / K000004 −55 · K000005 −19 · K000006 −12, 현금 99,463,501.24 · NAV 100,000,000 (수수료 0)"},
        {"k": "stop-loss run", "v": "9 → 0", "s": "첫날 9종목 진입 → 손절이 이어져 02-22엔 K000008 하나 → 02-23에 52주 전량 매도 → 현금 84,184,068.92"},
    ],
    "fix": (
        "<strong>ms를 읽을 때.</strong> 프로파일러가 켜진 채 잰 값이라 절대치는 실제보다 큽니다(특히 generator를 많이 쓰는 코드). 같은 트레이스 안에서 <b>서로 비교</b>만 하십시오. "
        "이 판도 디스크 캐시가 식은 상태에서 떠서 등록의 첫 parquet 스캔(<code>check_span</code>)이 1,677 ms, 명단의 첫 pyarrow 읽기가 804 ms입니다 — 두 번째 표의 같은 단계는 11 ms입니다. "
        "구조를 견줄 땐 ms가 아니라 <b>호출 횟수</b>와 <b>같은 자리의 유무</b>를 보십시오."
    ),
    "glossary_title": "먼저 알아 두면 편한 낱말 열셋",
    "glossary": [
        ("선언 (declaration)", "당신이 쓰는 YAML. “이 parquet은 가격이다, 이 파일은 내 전략이다, 이 run은 이렇게 돌려라.” 레시피에 해당한다."),
        ("저자 표면 (vq)", "<code>from vqapr import public as vq</code>. 저자가 쓰는 이름(<code>StrategyModel</code> · <code>DataModel</code> · <code>Rebalance</code> · <code>Hold</code> · <code>DatasetInput</code> …)은 전부 <code>vqapr.public</code> 한 곳에 있다. 0.16.0 전엔 <code>vqapr.authoring</code>이 따로 있었다."),
        ("등록부 (workspace)", "<code>.vqapr/workspace.yaml</code>. <code>register</code>가 쓰고 모든 명령이 맨 처음 펼쳐 읽는 장부. 코드에선 <code>Workspace</code>(<code>workspace/registry.py</code>, 0.16.0 전엔 <code>project/</code>)."),
        ("파일의 문", "물리 파일을 실제로 열어 재는 <b>한 곳</b>(<code>data/verification.py</code>): 컬럼 · 키 · 기간 · 값 · 집행 가격 · digest. 등록될 때 한 번 재고, 그 뒤엔 내용이 아니라 <b>digest</b>(지문)만 대조한다."),
        ("digest (지문)", "파일 바이트의 sha256. 파일이 한 바이트라도 바뀌면 지문이 달라져 읽는 쪽이 알아챈다."),
        ("판정 · run의 문 (preflight)", "“이 run을 돌려도 되나”에 답하는 예/아니오 여럿. <code>check</code>는 전부 모아 보여 주고 <code>run</code>은 첫 거절에서 멈춘다. 둘 다 <code>preflight</code> 한 함수(<code>run/preflight/verdict.py</code>)를 지나며 같은 사실(<code>RunFacts</code>)을 한 번만 읽는다."),
        ("얼리기 (freeze)", "등록부의 <i>이름</i>들을 실제 <i>값</i>(코드 지문, parquet 경로와 digest, 시간표, 초기 계좌)으로 풀어 밀봉한 것 = <code>FrozenRun</code>(<code>run/preflight/freeze.py</code>). 도시락에 해당한다: run 도중 레시피(등록부)가 바뀌어도 도시락은 그대로다."),
        ("시간표와 사건 (schedule · event)", "선언의 <code>schedule:</code>이 결정 시각 목록을 만들고, 루프는 그 시각마다 <code>ScheduledEvent</code> 하나를 처리한다. 집행표에 가격이 있는 시각은 <code>MarketEvent</code>가 된다. 사건을 시각 순서로 하나씩 — 이산 사건 시뮬레이션(DES)의 말이다."),
        ("두 시계", "<b>시간표 시계</b>(<code>Clock.SCHEDULE</code>): 결정하는 시각(매일 08:00이나 09:00, 16:00). <b>시장 시계</b>: 집행표에 가격이 있는 시각(매일 15:30). 아침에 결정하고 오후에 체결·평가한다. 트레이스의 시각은 UTC라 06:30 = 15:30 KST."),
        ("창 (window) · panel", "전략이 읽는 데이터의 사각형: 시각 × 종목. panel은 그 행렬(float64) 한 벌이고, <code>matrix()</code>는 복사 없이 그 일부를 보는 view다. run의 기간 + lookback만큼만 읽는다."),
        ("memory", "전략의 <code>self.memory</code>. 엄격한 JSON. 매 결정 전에 복원되고 뒤에 저장된다. 이것만 믿을 수 있다 — 다른 self 속성은 기록이 재현하지 못한다."),
        ("의도서 (intent)", "전략이 돌려준 목표 비중에 프레임워크가 도장을 찍은 것. 체결 시각이 올 때까지 하나만 기다린다(pending). <code>Hold</code>면 없다."),
        ("봉투 (envelope)", "모든 명령이 stdout에 내는 JSON 한 덩어리. 성공이든 거절이든 모양이 같다: <code>ok · stage · failures[code · status · requirement · observed · fix]</code>."),
    ],
}

MAP = [
    ("①", "데이터 등록", "선언 → 문 → 등록부"),
    ("②", "등록 오류", "없는 컬럼 · 바뀐 파일"),
    ("③", "DataModel", "지표를 만들어 dataset으로"),
    ("④", "factor 전략", "롱 3 · 숏 3 · 비중 저장"),
    ("⑤", "stop-loss", "memory가 진입가를 든다"),
    ("⑥", "enhanced index", "저장된 비중을 읽는다"),
    ("⑦", "--jobs 배치", "worker도 preflight · cube 한 번"),
]

SCENES = [
    # ---------------------------------------------------------------- ① register
    {
        "id": "reg", "key": "①", "title": "데이터 등록",
        "sub": "vqapr register sample.yaml · 2,818 ms · 980 호출 (그중 1,677 ms는 식은 디스크의 첫 parquet 스캔)",
        "story": (
            "<b>무슨 일인가:</b> 당신이 YAML 한 장(<code>sample.yaml</code>)을 건넵니다. 거기엔 “종목 명단은 이 파일, 가격은 이 parquet, 체결 가격은 저 parquet, 전략 코드는 이 파일, run은 이렇게”가 적혀 있습니다. "
            "vqapr은 이 문서를 그대로 믿지 않습니다. 세관처럼 <b>파일을 실제로 열어</b> 적힌 대로인지 재고 지문(digest)을 남기고, 전략 코드를 <b>실제로 import</b>해 약속한 모양인지 본 다음에야 장부(등록부) 한 파일을 씁니다. "
            "뒤의 여섯 시나리오는 전부 이 장부 위에서 일어납니다. <b>[0.16.0]</b> 장부를 쓰는 코드는 <code>workspace/</code>에, 파일을 재는 문은 <code>data/verification.py</code>에 있습니다."
        ),
        "frames": [
            F("01_register", 0, "명령줄이 register 핸들러를 고른다",
              "터미널에서 <code>vqapr register sample.yaml</code>을 칩니다. 프로그램은 어느 동사인지(register) 알아보고 프로젝트 폴더를 정한 뒤 register 담당(<code>cli/register.py</code>)에게 넘깁니다. 2,818 ms의 거의 전부는 그 담당 안에서 씁니다. 무엇이 잘못되든 결과는 같은 모양의 JSON 봉투로 나옵니다.",
              "<code>build_parser</code>(#1, 10.1 ms) → <code>_resolve_project_root</code>(#11) → <code>register.run</code>(#12, 2,804.8 ms) → <code>read_yaml_mapping</code>(#13, 31.7 ms) → <code>apply</code>(#14, 2,772.7 ms).",
              fn="main() → register.run()", code=at("src/vqapr/cli/main.py", "def main(", 14),
              mem={"argv": "['--project-root', '.../sample', 'register', '.../sample/sample.yaml']"}, disk={".vqapr/": "없음"}),
            F("01_register", 15, "장부는 마지막에 한 번만 쓴다 — 트랜잭션",
              "장부를 바로 고치지 않고 <b>장바구니</b>를 하나 엽니다. 명단 → 데이터 → 코드 → run 순서로 검사한 것을 장바구니에 담아 두었다가 맨 끝에 한 번에 씁니다. 중간에 하나라도 거절되면 장바구니째 버려서 장부는 한 글자도 안 바뀝니다. 순서가 이런 이유: run은 전략 이름과 데이터 이름을 가리키므로 그것들이 먼저 있어야 합니다. "
              "<b>[0.16.0]</b> 이 순서를 가진 파일은 <code>workspace/registration.py</code>(예전 <code>project/registration.py</code>)입니다.",
              "<code>Workspace.transaction</code>(#16, 1.1 ms) → <code>_require_declared_ids</code>(#26) → <code>_instruments</code>(#44, 820.1 ms) → datasets(#137 · #329) → components(#469 · #617) → runs(#883) → <code>commit</code>(#909).",
              fn="_apply() — 섹션 순서", code=at("src/vqapr/workspace/registration.py", 'for dataset_id, body in section("datasets")', 7),
              mem={"document": "dict (instruments 1, datasets 2, components 2, runs 1)", "transaction.staged": "[]"}),
            F("01_register", 47, "종목 명단부터 실제로 열어 본다",
              "종목 명단 parquet(10종목)을 엽니다. 파일이 없거나 필요한 컬럼이 없으면 예외로 터지는 게 아니라 “무엇이 없다”는 진단으로 돌아와 다른 거절 옆에 나란히 놓입니다. 804 ms는 10행짜리 표의 값이 아니라 이 프로세스가 parquet 라이브러리(pyarrow)를 처음 올리는 비용입니다.",
              "<code>verify_roster</code>(#47, 804.5 ms) → <code>build_roster</code>(#51, 2.1 ms: <code>instrument</code> ×10) → <code>Transaction.register_instruments</code>(#84).",
              fn="verify_roster()", code=("def", 12),
              mem={"transaction.staged": "[instruments: stock 10, digest 875b5fe1…]"}),
            F("01_register", 137, "가격 parquet을 열어 여섯 가지를 잰다 — 파일의 문",
              "선언은 “<code>available_at</code>이 시각이고 <code>close</code>가 숫자이고 (시각, 종목)이 겹치지 않는다”고 말합니다. 문은 파일을 열어 순서대로 확인합니다: ① 컬럼과 타입이 맞나 → ② 키에 빈 값·중복이 없나 → ③ 첫 날과 끝 날은 언제인가 → ④ 숫자에 NaN·무한대가 없나 → ⑤ 체결 가격 역할이 있나(이 표엔 없음) → ⑥ 지문(sha256). "
              "여기가 이 파일이 <b>내용으로</b> 검사되는 유일한 자리입니다. 뒤의 모든 명령은 지문만 대조합니다. 1,677 ms는 이 프로세스의 첫 duckdb 스캔(디스크 캐시가 식음)이고 두 번째 표의 같은 단계는 11 ms입니다. "
              "<b>[0.16.0]</b> 문의 파일 이름이 <code>validation.py</code>에서 <code>verification.py</code>로 — 거절 봉투의 <code>where</code>도 이 이름을 댑니다.",
              "<code>verify_source</code>(#137, 1,796.8 ms) → <code>describe</code>(#138, 36.7 ms) → <code>check_schema</code>(#150, 23.9 ms) → <code>check_key</code>(#193, 40.9 ms) → <code>check_span</code>(#214, 1,677.1 ms) → <code>check_values</code>(#225, 16.6 ms) → <code>check_execution_prices</code>(#277, 0.002 ms) → <code>physical_digest</code>(#279, 0.54 ms) → <code>Transaction.register_dataset</code>(#283) → <code>spoken</code>(#289).",
              fn="verify_source() — 여섯 단계", code=("def", 14),
              mem={"measured.span": "2022-01-03 15:30 ~ 2024-12-30 15:30 +09:00", "measured.source_digest": "18bb7017…"}),
            F("01_register", 437, "집행표는 한 가지를 더 잰다 — 거래 가능한 날엔 가격이 있나",
              "체결에 쓸 표(<code>sample-execution</code>)는 “이 컬럼이 거래 가능 여부다”라고 선언했습니다. 그래서 문이 한 가지를 더 묻습니다: 거래 가능하다고 적힌 행마다 가격이 양수인가? 답(<code>['close']</code>)을 장부에 적어 두면, 나중에 run이 “close로 체결”이라고 할 때 표를 다시 뒤지지 않고 이 답만 봅니다.",
              "<code>verify_source</code>(#329, 86.1 ms) → <code>check_schema</code>(#339, 13.7 ms) → <code>check_key</code>(#371, 15.0 ms) → <code>check_span</code>(#392, 11.2 ms) → <code>check_values</code>(#403, 13.6 ms) → <b><code>check_execution_prices</code>(#437, 12.5 ms)</b> → <code>physical_digest</code>(#454, 0.42 ms) → <code>register_dataset</code>(#460).",
              fn="check_execution_prices()", code=("def", 14),
              mem={"measured.execution_prices": "('close',)", "measured.source_digest": "49e4b4ab…"}),
            F("01_register", 554, "전략과 거래소 코드는 실제로 import해서 약속한 모양인지 본다",
              "전략 파일(<code>reversal_5d.py</code>)의 지문을 찍고, 실제로 import해서 “전략이라면 있어야 할 메서드가 맞는 시그니처로 있나”를 봅니다. 거래소 코드도 같은 길입니다. 옛날 시그니처로 쓴 코드는 여기서 이름을 대며 거절됩니다. 오늘은 둘 다 통과해 장바구니에 담깁니다. "
              "<b>[0.16.0]</b> 부품이 들어오는 이 문은 <code>component/conformance.py</code>에 있고, 역할마다 계약(<code>component/strategy/base.py</code> …)과 구현이 파일을 나눕니다.",
              "<code>_component</code>(#469, 19.0 ms) → <code>fingerprint_component</code>(#473, 9.6 ms) → <code>conformance</code>(#554, 5.7 ms) → <code>_check_methods</code>(#602) → <code>register_component</code>(#611) · 거래소 <code>_component</code>(#617, 18.5 ms) → <code>conformance</code>(#726, 6.7 ms) → <code>register_component</code>(#817).",
              fn="conformance()", code=("def", 10),
              mem={"transaction.staged": "[instruments, sample-prices, sample-execution, sample-reversal-5d, sample-exchange]"}),
            F("01_register", 909, "run을 담고, 장부를 한 번에 쓴다",
              "마지막으로 run 선언(어느 전략, 어느 데이터, 언제부터 언제까지, 초기 현금)을 담습니다. 그리고 사람 말로 푼 문장이 봉투에 들어갑니다: “<i>dataset 'sample-prices'의 행은 available_at 시각부터 알 수 있고 그보다 먼저는 아니다</i>”, “<i>run 'sample-run'의 모델은 매일 08:00(Asia/Seoul)에 불린다 — 집행표에 행이 있는 날마다</i>”. "
              "<b>[0.16.0]</b> 둘째 문장이 <code>schedule:</code> 블록을 읽은 것입니다(옛 <code>agenda:</code>는 이제 고치는 법과 함께 거절됩니다). commit이 잠금을 잡고 장부를 한 번 읽어 담아 둔 것을 합친 뒤 <b>한 번</b> 씁니다. 디스크에 처음으로 <code>.vqapr/workspace.yaml</code>이 생깁니다.",
              "<code>register_run</code>(#883) → <code>RunDefinition.spoken</code>(#895) → <code>Transaction.commit</code>(#909, 10.0 ms) → <code>Workspace._write</code>(#931, 7.0 ms) → <code>_write_roster</code>(#970) → <code>success</code>(#974).",
              fn="Transaction.commit()", code=("def", 16),
              disk={".vqapr/workspace.yaml": "datasets 2 (source_digest · execution_prices) · components 2 · runs 1", ".vqapr/instruments.json": "stock 10, digest 875b5fe1…"}),
        ],
        "remember": [
            "파일은 등록될 때 문(data/verification.py)에서 한 번 잰다: 컬럼 → 키 → 기간 → 값 → 체결 가격 → 지문. 그 결과가 장부에 남는다.",
            "명단 · 가격표 · 집행표 · 코드, 넷 다 실제로 열어 본 뒤에야 장부를 쓴다. 쓰기는 마지막에 한 번.",
        ],
    },
    # ---------------------------------------------------------------- ② registration errors
    {
        "id": "err", "key": "②", "title": "등록 오류 — 없는 컬럼, 바뀐 파일",
        "sub": "register bad.yaml · 69 ms · 431 호출 (거절) — check sample-run · 2,093 ms · 49,807 호출 (거절) — register sample.yaml 다시 · 1,113 ms · 1,304 호출",
        "story": (
            "<b>무슨 일인가:</b> 실수를 두 가지 저지릅니다. 먼저 파일에 <b>없는 컬럼</b>(<code>adj_close</code>)을 선언한 dataset을 등록해 봅니다 — 문이 파일을 열어 보고 “그런 컬럼 없다”고 이름을 대며 거절하고, 장부는 그대로입니다. "
            "다음엔 등록이 끝난 뒤 집행표 parquet을 <b>다른 내용으로 덮어씁니다</b>(마지막 날을 뺀 유효한 파일). <code>check</code>는 표를 다시 뒤지지 않고 지문 하나를 대조해 “파일이 바뀌었다”고 막고, 고치는 법까지 말합니다: 같은 선언으로 다시 등록하라. 그러면 잰 값만 새로 갈립니다."
        ),
        "frames": [
            F("02_register_bad", 400, "문이 파일을 열어 첫 단계에서 멈춘다",
              "선언은 “<code>observations.parquet</code>에 <code>adj_close</code>가 있다”고 말합니다. 문이 파일의 컬럼 목록을 읽어 대조합니다: 없습니다. 그 뒤 단계(키 · 기간 · 값 · 지문)는 돌지 않습니다 — 컬럼이 틀린 파일에 키를 묻는 건 뜻이 없으니까요.",
              "<code>_dataset</code>(#358) → <code>verify_source</code>(#387, 19.3 ms) → <code>describe</code>(#388, 14.8 ms) → <code>check_schema</code>(#400, 4.3 ms) → <code>Diagnosis.ok</code>(#415) = False → <code>raise_if_failed</code>(#416).",
              fn="check_schema()", code=("def", 12),
              mem={"observed": "available_at, close, high, instrument, low, open, volume"}),
            F("02_register_bad", 421, "거절 봉투: 무엇이 · 왜 · 어떻게 고치나 — 그리고 장부는 그대로",
              "봉투 한 장이 나옵니다. code <code>dataset.field_missing</code>(400) · 요구 “<i>fields[adj_close]가 말한 컬럼 'adj_close'가 있어야 한다</i>” · 관찰 “<i>있는 컬럼은 available_at, close, high, …</i>” · 고치는 법 “<i>adj_close 컬럼을 넣거나 있는 컬럼을 가리켜라</i>” · 위치 <code>datasets.sample-adjusted.fields[adj_close]</code> · 원인 자리 <code>vqapr/data/verification.py:152 (check_schema)</code>. "
              "<code>mutation: false</code> — 장바구니는 열렸지만 쓰이지 않았습니다. exit 1.",
              "<code>raise_if_failed</code>(#416) → <code>envelope.failure</code>(#421, stage register) → <code>emit</code>(#430) → exit 1.",
              fn="envelope.failure()", code=("def", 10),
              disk={".vqapr/workspace.yaml": "바뀌지 않음 (mutation: false)"}),
            F("03_check_changed", 340, "[0.16.0] check는 run의 문 하나를 지난다 — preflight",
              "집행표가 바뀐 채로 <code>check sample-run</code>. check는 장부를 열고 run 선언을 꺼내 <b>preflight</b> 한 함수에 넘깁니다. 이 함수가 두 가지를 한 번의 읽기로 합니다: 판정 여럿을 <b>모아서</b> 답하기(check가 보여 줄 것)와 얼리기 시도(<code>freeze</code>, run이 쓸 것). "
              "둘은 같은 사실 그릇(<code>RunFacts</code>)에서 읽으므로 같은 것을 두 번 읽지 않습니다. 돌아오는 답(<code>RunVerdict</code>)엔 거절 · 답하지 못한 판정 · 얼린 run 또는 얼리기가 낸 거절이 함께 들어 있습니다. "
              "<b>[0.16.0]</b> 이름만 바뀌었습니다: <code>verify_run</code> → <code>preflight</code>, <code>preflight_run</code> → <code>freeze</code>, 자리는 <code>run/preflight/</code>(사실 <code>facts.py</code> · 판정 <code>checks.py</code> · 얼리기 <code>freeze.py</code> · 평결 <code>verdict.py</code>). 0.14.3의 같은 자리(#336)와 호출 순서가 같습니다.",
              "<code>check</code>(#13, 2,084.7 ms) → <code>Workspace.open</code>(#15, 25.4 ms) → <code>run_definition</code>(#338) → <code>preflight</code>(#340, 2,058.6 ms) → <code>RunFacts.__init__</code>(#341) → <code>judgments</code>(#342, 2,052.5 ms) → … → <code>freeze</code>(#49684, 6.0 ms) → <code>Failure.as_dict</code>(#49792) → <code>emit</code>(#49806).",
              fn="preflight() — run의 문", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 10, before=1),
              mem={"verdict": "failures 1 (dataset.source_changed) · blocked 1 (judgment.blocked: execution_ordering) · frozen None · refusal VqaprError"}),
            F("03_check_changed", 342, "판정 일곱 개가 차례로 답한다 — 사실은 한 번만 읽는다",
              "판정은 일곱입니다: 종목 집합 · 명단 · 기간 · <b>집행 순서</b> · 읽을 dataset들 · 비중 · 출력. 집행 순서 판정이 “시간표(schedule)를 달라”고 하자 그릇이 처음이라 만듭니다 — 이 run은 3년짜리라 734일, 1,814 ms(그중 집행표의 시각 열 읽기는 일부, 나머지는 하루마다 결정 시각 객체를 만드는 Python 시간). "
              "그 뒤 얼리기가 같은 시간표를 물으면 그릇이 <b>돌려주기만</b> 합니다. <b>[0.16.0]</b> <code>RunFacts.agenda</code> → <code>RunFacts.schedule</code>, <code>derived_agenda</code> → <code>derived_schedule</code>.",
              "<code>judgments</code>(#342) → <code>_judge_universe</code>(#354) · <code>_judge_roster</code>(#356, 7.1 ms) · <code>_judge_period</code>(#363) · <code>_judge_execution_ordering</code>(#365, 1,950.5 ms) → <code>RunFacts.schedule</code>(#366) → <code>_once</code>(#367) → <code>derived_schedule</code>(#369, 1,813.9 ms) → <code>_session_bounds</code>(#370) … <code>inclusive_slice</code>(#43683, 131.2 ms) → <code>RunFacts.execution_table</code>(#47352, 5.1 ms) · <code>_judge_member_datasets</code>(#47394, 89.2 ms) · <code>_judge_weights</code>(#49681) · <code>_judge_outputs</code>(#49683).",
              fn="RunFacts._once() — 한 번 읽고 나눠 준다", code=at("src/vqapr/run/preflight/facts.py", "def _once(", 10),
              tip="여기서 큰 것은 표 스캔이 아니라 시간표 만들기(1.8 s, 프로파일러 아래)입니다. 프로파일러 없이 재면 이 check는 약 0.1 s입니다(기록 240)."),
            F("03_check_changed", 365, "집행 순서 판정은 run이 실제로 걷는 날들만 묻는다",
              "이 판정은 “결정마다 그 다음에 체결할 시각이 있나”를 봅니다. 얼리기가 쓰는 것과 같은 조각(<code>inclusive_slice(start, end)</code>)만 돕니다 — 날짜 범위의 상위집합을 돌면 end가 체결과 결정 사이에 놓인 옳은 선언이 500으로 죽었습니다(testbed 보고 099, 기록 237). 이 run은 end가 23:59:59라 잘리는 건 없지만, 자리가 트레이스에 보입니다. "
              "<b>[0.16.0]</b> 조각을 내는 것은 <code>Schedule</code>(<code>domain/schedule.py</code>)입니다 — 예전 <code>OperationAgenda</code>.",
              "<code>_judge_execution_ordering</code>(#365) → <code>RunFacts.schedule</code>(#366) → … → <code>Schedule.inclusive_slice</code>(#43683, 131.2 ms) → <code>RunFacts.execution_table</code>(#47352, 5.1 ms) → <code>Workspace.require_verified</code>(#47356).",
              fn="_judge_execution_ordering() — inclusive_slice", code=at("src/vqapr/run/preflight/checks.py", "inclusive_slice(", 12, before=3)),
            F("03_check_changed", 47367, "표를 다시 뒤지지 않는다 — 지문 하나를 대조한다",
              "집행표를 쓰려면 장부에 “이 dataset은 아직 등록 때 그대로인가”를 물어야 합니다. 장부에 적힌 지문 <code>49e4b4ab…</code>와 지금 파일의 지문 <code>bf30cb34…</code>(0.54 ms)가 다릅니다 → <code>dataset.source_changed</code>(412): “<i>run이 읽는 바이트는 등록이 잰 바이트여야 한다</i>”, 고치는 법 “<i>vqapr register &lt;선언 파일&gt;로 다시 등록하라</i>”. "
              "그릇은 실패도 기억합니다: 뒤에 <code>freeze</code>가 같은 표를 물으면 저장해 둔 같은 예외를 다시 던집니다(6.0 ms) — 다시 해시하지 않습니다.",
              "<code>RunFacts.execution_table</code>(#47352) → <code>Workspace.require_verified</code>(#47356, 4.9 ms) → <code>physical_digest</code>(#47365, 0.54 ms) → <code>require_verified</code>(#47367, 3.9 ms) → 거절 · 판정을 blocked로 감싼다 → <code>_judge_member_datasets</code>(#47394) … <code>freeze</code>(#49684, 6.0 ms: 저장된 예외).",
              fn="require_verified()", code=at("src/vqapr/data/verification.py", "def require_verified", 14),
              mem={"registered": "49e4b4abef4f…", "file now": "bf30cb34b1ca…"},
              caution="봉투: checked [workspace, run, judgments, preflight] · passed [workspace, run] · failures [dataset.source_changed] · blocked [judgment.blocked: “every judgment answers before a run is accepted”, cause에 예외 전체]. 답하지 못한 판정과 그 원인은 따로따로 실린다(오너 결정 2026-09-04)."),
            F("04_register_again", 647, "같은 선언으로 다시 등록한다 — 잰 값만 다시 잰다",
              "<code>register sample.yaml</code>을 다시 칩니다. 선언은 한 글자도 안 바뀌었고 파일만 다릅니다. 문이 두 표를 다시 잽니다(가격표 133.8 ms · 집행표 79.9 ms): 기간, 지문(<code>bf30cb34…</code>), 체결 가격. 장바구니에 담을 때 기존 등록과 비교합니다.",
              "<code>_apply</code>(#15, 1,086.1 ms) → <code>verify_source</code>(#455, 133.8 ms) → <code>_merge_dataset</code>(#605) · <code>verify_source</code>(#647, 79.9 ms) → <code>_merge_dataset</code>(#782).",
              fn="verify_source() 다시", code=("def", 8)),
            F("04_register_again", 782, "선언한 반쪽이 같으면 잰 반쪽만 갈아 끼운다",
              "등록엔 두 반쪽이 있습니다. 당신이 쓴 반쪽(컬럼 · 키 · 단위)과 문이 잰 반쪽(기간 · 지문 · 체결 가격). 비교기는 “기존 등록의 잰 반쪽을 새 측정으로 바꾸면 새 등록과 같은가”를 봅니다. 같다 → 선언은 그대로이니 받아들입니다. 컬럼 이름 하나라도 달랐다면 “이미 등록된 이름”(409)으로 거절했을 겁니다. "
              "이 페이지의 run들은 원본 파일로 되돌린 뒤 한 번 더 등록한 상태에서 돌았습니다. <b>[0.16.0]</b> 비교기는 <code>workspace/merge.py</code>.",
              "<code>_merge_dataset</code>(#782) → … <code>Transaction.commit</code>(#1227, 10.3 ms) → <code>Workspace._write</code>(#1255, 7.0 ms) → <code>success</code>(#1298).",
              fn="_merge_dataset() — remeasured", code=at("src/vqapr/workspace/merge.py", "remeasured = replace(", 12, before=6),
              disk={".vqapr/workspace.yaml": "sample-execution.source_digest: 49e4b4ab… → bf30cb34… (그 뒤 원본으로 되돌려 한 번 더 등록)"}),
        ],
        "remember": [
            "거절 봉투는 code · 요구 · 관찰 · 고치는 법 · 위치를 들고, 장부는 안 바뀐다.",
            "등록 뒤 파일이 바뀌면 지문 하나로 알아챈다. check도 run도 preflight 한 함수를 지나 같은 답을 받는다.",
        ],
    },
    # ---------------------------------------------------------------- ③ datamodel
    {
        "id": "dm", "key": "③", "title": "DataModel — 지표를 만들어 dataset으로",
        "sub": "register features.yaml · 62 ms · 653 호출 — run sample-features-run · 1,631 ms · 8,171 호출 · 16일 · 108행",
        "story": (
            "<b>무슨 일인가:</b> <code>features.py</code>의 <code>SampleFeatures</code>는 날마다 종목별 <b>5일 모멘텀</b>(여섯 종가 중 마지막 ÷ 첫 번째 − 1)을 계산하는 DataModel입니다. 사고파는 게 없으니 이 run엔 시간표 시계(매일 16:00)만 있고 시장 시계가 없습니다. "
            "첫 나흘은 종가가 여섯 개가 안 돼 빈 목록, 2022-01-10부터 종목당 한 행(K000010은 이 구간에 종가 여섯 개가 없어 빠짐). run이 끝나면 108행(12일 × 9종목)이 parquet이 되고 <b>①과 똑같은 문</b>을 지나 dataset <code>sample-features</code>로 등록됩니다. 다음 run은 이것을 벤더 표와 똑같이 읽습니다."
        ),
        "frames": [
            F("06_run_features", 475, "run도 같은 문을 지난다 — 판정하고 얼린다",
              "장부를 열고 run 선언을 꺼내 <code>preflight</code>에 넘깁니다(148 ms): 판정 136 ms, 얼리기(<code>freeze</code>) 10.5 ms. 얼리기는 모델을 import해 “무엇을 읽나”를 묻는데, 이 import는 판정이 이미 한 것을 그릇에서 받습니다. 집행표가 없는 datamodel run은 <code>days_from</code>의 가격표에서 거래일을 읽는데, run 기간 ± 1일(18일)만 읽습니다(기록 247).",
              "<code>_run_one</code>(#13) → <code>Workspace.open</code>(#15, 39.5 ms) → <code>preflight</code>(#475, 147.6 ms) → <code>judgments</code>(#477, 136.4 ms) → <code>freeze</code>(#1798, 10.5 ms) → <code>_freeze_datamodel</code>(#1810, 7.2 ms) → <code>_freeze_sources</code>(#2003, 1.5 ms).",
              fn="preflight()", code=at("src/vqapr/run/preflight/verdict.py", "facts = RunFacts(workspace, definition)", 10, before=1),
              mem={"거래일 읽기": "_local_date ×18"}),
            F("06_run_features", 2016, "얼리기 — 읽을 dataset이 등록 때 그대로인지 지문으로 확인",
              "이 모델이 읽는 <code>sample-prices</code>가 아직 등록 때 파일인지 지문 한 번으로 봅니다(1.1 ms). 같습니다. 얼린 run에 그 지문이 들어가 “이 run은 이 바이트를 읽었다”가 기록에 남습니다. 파일 내용은 여기서도 읽지 않습니다.",
              "<code>_freeze_sources</code>(#2003) → <code>Workspace.require_verified</code>(#2005, 1.1 ms) → <code>require_verified</code>(#2016, 0.04 ms).",
              fn="require_verified()", code=at("src/vqapr/data/verification.py", "def require_verified", 14),
              mem={"frozen.source_digests": "{sample-prices-source: 18bb7017…}"}),
            F("06_run_features", 2056, "문이 만든 것을 run이 그대로 받는다 — RunResources",
              "얼린 run은 기록에 적히는 <b>값</b>이라 살아 있는 모델 객체를 들 수 없습니다. 그래서 문이 이미 든 객체와 잘라 둔 기간을 <code>RunResources</code>라는 봉지에 담아 함께 넘기고(0.40 ms — 새로 읽는 건 없음), run은 그것을 씁니다. 다른 run의 봉지면 거절합니다. "
              "<b>[0.16.0]</b> run을 조립하는 곳은 <code>run/assemble.py</code>(예전 <code>flow/orchestration.py</code>)입니다.",
              "<code>RunResources.of</code>(#2056, 0.40 ms) → <code>RunVerdict.require_ready</code>(#2064) → <code>run</code>(#2066, 1,434.8 ms, resources=…) → <code>_run_datamodels</code>(#2074) → <code>_run_datamodel</code>(#2075) → <code>_run_member</code>(#2113, 1,432.4 ms).",
              fn="RunResources.of()", code=("def", 12),
              mem={"resources": "datamodel=SampleFeatures 인스턴스(판정이 import한 것) · strategy None · exchange None"}),
            F("06_run_features", 2116, "데이터 창고가 run의 기간을 안다",
              "run 하나의 도구들(스캔 세션 · 데이터 창고 · 기록 쓰기 · 창 만들기)을 만듭니다. 창고(store)는 이 run의 기간(01-04 ~ 01-25)과 모델이 읽겠다고 선언한 것들을 받아 두고, 뒤의 모든 읽기를 그 범위로 자릅니다. 3년 표에서 3주만 읽는 이유가 여기 있습니다.",
              "<code>_run_member</code>(#2113) → <code>_horizon</code>(#2116) → <code>DuckDbObservationStore.__init__</code> → <code>body</code>(#2174, 1,409.5 ms) → <code>RunOutput.__init__</code>(#2177) → <code>datamodel_loop</code>(#2181).",
              fn="_horizon() → DuckDbObservationStore(horizon=…)", code=at("src/vqapr/run/assemble.py", "horizon=_horizon(frozen)", 10, before=4),
              mem={"horizon": "(2022-01-04 00:00, 2022-01-25 23:00) +09:00", "requirements": "[sample-prices.close, RowsLookback(rows=6)]"}),
            F("06_run_features", 2181, "[0.16.0] 루프는 하나, 사건은 시간표가 만든다",
              "전략 run과 <b>같은</b> 루프 클래스(<code>RunLoop</code>, <code>run/engine/loop.py</code>)를 씁니다. 다른 건 두 가지뿐: 부품이 DataModel용이고, 시장 시계가 없습니다. 조립하면서 모델의 <code>inputs()</code>를 <b>한 번</b> 물어 무엇을 읽을지 알아 둡니다. 루프가 열리고 16개의 사건을 차례로 처리합니다. "
              "<b>[0.16.0]</b> 루프가 받는 것은 이제 이렇게 불립니다: <code>ScheduledEvent(event_id='sample-features-run.schedule-2022-01-04T1600', …)</code> — 시간표가 사건을 만들고 루프는 사건을 시각 순서로 처리한다(DES).",
              "<code>datamodel_loop</code>(#2181, 4.3 ms) → <code>SampleFeatures.inputs</code>(#2183) → <code>RunLoop.run</code>(#2297, 1,303.0 ms) → <code>start</code>(#2298) → <code>events</code>(#2301) → <code>RunLoop.handle</code> ×16 (#2406 …) → <code>finish</code>(#7739).",
              fn="datamodel_loop()", code=("def", 12)),
            F("06_run_features", 2485, "첫 창 — 어디부터 어디까지 읽을지 먼저 정한다",
              "2022-01-04 16:00, 모델이 처음으로 “종가를 달라”고 합니다. 창고는 읽기 전에 범위를 정합니다: 여섯 행이 필요하니 run 시작(01-04) 앞의 가장 이른 날을 원천의 날짜 격자에서 세고(하한 01-03 15:30), 상한은 run 끝(01-25 23:00). 그 사이만 스캔합니다(1,064 ms — 이 프로세스의 첫 스캔이고 디스크 캐시가 식어 있었습니다).",
              "<code>compute</code>(#2449) → <code>_DeclaredReads.read</code>(#2450) → <code>ModelWindow.panel</code>(#2469) → <code>panel_window</code>(#2470, 1,127.5 ms) → <code>_scan_bounds</code>(#2485, 48.6 ms) → <code>observation_table</code>(#3233, 1,064.2 ms) → <code>Panel.from_table</code>(#3270).",
              fn="_scan_bounds() — lookback 하한", code=at("src/vqapr/data/store.py", "for lookback in lookbacks:", 10, before=2),
              mem={"bounds": "2022-01-03 15:30 ~ 2022-01-25 23:00 +09:00 (probe_panel.py로 잰 값)"}),
            F("06_run_features", 3270, "panel — 날짜 × 종목 행렬 한 벌",
              "스캔이 준 표(시각 · 종목 · 종가)를 (17일 × 10종목) 숫자 행렬 하나로 접습니다(13 ms). 없는 칸은 NaN. 이 뒤 16번의 계산은 전부 이 행렬의 일부를 <b>복사 없이</b> 봅니다(view).",
              "<code>Panel.from_table</code>(#3270, 13.1 ms) → <code>placement</code>(#3271, 12.5 ms) → <code>dense_block</code>(#3273, 0.06 ms) → <code>PanelWindow.matrix</code>(#3282, 0.09 ms).",
              fn="Panel.from_table() — 블록", code=at("src/vqapr/data/panel.py", "blocks[name] = dense_block(", 10, before=6),
              mem={"panel.blocks['close'].shape": "(17, 10)", "panel.bounds": "01-03 15:30 ~ 01-25 23:00"}),
            F("06_run_features", 2449, "첫날 — 종가가 두 개뿐이라 빈 목록",
              "저자 코드입니다. <code>window.matrix()</code>로 행렬을 보니 01-04 16:00에 알 수 있는 행은 2개(01-03 · 01-04). 여섯 개가 필요하니 <code>[]</code>를 돌려줍니다. 프레임워크는 빈 목록을 그대로 받습니다. 이 첫 계산 1,129 ms는 거의 전부 위의 첫 스캔이고, 다음 날부터는 2 ms입니다.",
              "<code>RunLoop.handle</code>(#2406, 1,130.4 ms, 사건 01-04 16:00) → <code>_window_factory.at</code>(#2413) → <code>SampleFeatures.compute</code>(#2449, 1,128.5 ms) → … → <code>PanelWindow.matrix</code>(#3282) → <code>RunOutput.append</code>(#3290, rows=[]). 둘째 날 <code>compute</code>(#3338, 2.0 ms).",
              fn="SampleFeatures.compute() — 저자 코드", code=at(DECL + "features.py", "closes = window.matrix()", 12, before=1), author=True,
              mem={"closes.shape": "(2, 10) — 날 2 × 종목 10", "returned": "[]"}),
            F("06_run_features", 3641, "다섯째 날 — 종목 9개의 모멘텀을 한 식으로",
              "2022-01-10 16:00. 여섯 행이 찼습니다. <code>closes[-1] / closes[0] - 1</code>이 열마다(종목마다) 한 번에 계산되고, 여섯 값이 다 있는 열만 행으로 나갑니다: 9행(K000010은 열이 비어 빠짐). 이번 계산은 2.1 ms. "
              "행의 시각(<code>available_at</code>)은 저자가 아니라 프레임워크가 찍습니다(16:00): “이 값은 이 시각에야 알 수 있다”는 뜻이라서요.",
              "<code>RunLoop.handle</code>(#3598, 12.9 ms) → <code>_window_factory.at</code>(#3605, 01-10 16:00) → <code>compute</code>(#3641, 2.1 ms) → <code>RunOutput.append</code>(#3940, 0.48 ms, rows=[{available_at: 2022-01-10 16:00+09:00, instrument: 'K000001', momentum_5d: …}, …]).",
              fn="SampleFeatures.compute() — 행 9", code=at(DECL + "features.py", "momentum = closes[-1]", 8, before=2), author=True,
              mem={"rows this session": "9", "rows so far": "9 → 16일째에 108"}),
            F("06_run_features", 7773, "출력이 dataset이 된다 — 같은 문을 지나서",
              "16일이 끝나면 모은 행을 parquet으로 굳히고(4.7 ms) 그 파일을 <b>①에서 벤더 표가 지난 바로 그 문</b>에 넣습니다(72 ms): 컬럼 · 키 · 기간(01-10 ~ 01-25) · 값 · 지문. 통과하면 장부에 <code>sample-features</code>가 “어느 run의 어느 코드 버전이 만들었다”와 함께 적힙니다. 프레임워크가 만든 표라고 문을 건너뛰지 않습니다. 봉투는 rows 108 · sessions 16. "
              "<b>[0.16.0]</b> 코드 버전의 지문이 <code>20c2acad</code>에서 <code>4327b244</code>로 바뀐 것은 저자 파일의 import 줄(<code>vq</code>)이 바뀌어서입니다 — 108행의 값과 표의 지문(<code>54f8fd04…</code>)은 같습니다.",
              "<code>RunLoop.finish</code>(#7739) → <code>RunOutput.register</code>(#7773, 90.3 ms) → <code>_seal</code>(#7802, 4.7 ms) → <code>verify_source</code>(#7804, 72.3 ms) → <code>Transaction.commit</code>(#7935, 10.3 ms) → <code>freeze_datamodel_record</code>(#8002, 10.2 ms) → <code>RunRecordWriter._seal</code>(#8144) → <code>read_datamodel_record</code>(#8158) → <code>success</code>(#8165).",
              fn="RunOutput.register()", code=("def", 14),
              disk={".vqapr/materialized/sample-features/all.parquet": "108행 (available_at · instrument · momentum_5d)", ".vqapr/runs/sample-features-run/": "run.json · datamodels/sample-features@4327b244/datamodel.json", ".vqapr/workspace.yaml": "datasets + sample-features (source_digest 54f8fd04…)"}),
        ],
        "remember": [
            "run은 preflight 한 번으로 판정받고 얼려지며, 문이 import한 모델을 그대로 받는다.",
            "읽기는 run 기간 + lookback만큼만. 출력 parquet도 등록될 때 같은 문을 지난다.",
        ],
    },
    # ---------------------------------------------------------------- ④ factor strategy
    {
        "id": "factor", "key": "④", "title": "factor 전략 — 롱 3 · 숏 3",
        "sub": "register factor.yaml · 100 ms · 1,069 호출 — run sample-factor-run · 1,850 ms · 24,985 호출 · 10일 · 사건 20 (0.14.3은 24,374 호출)",
        "story": (
            "<b>무슨 일인가:</b> <code>factor.py</code>의 <code>SampleFactor</code>는 ③이 만든 모멘텀 표를 <b>벤더 표와 똑같이</b> 한 줄로 선언해 읽고(최신 행 하나), 상위 3종목은 사고 하위 3종목은 팝니다(각 1/6, 달러 중립). "
            "공매도가 있으니 거래소가 SIGNED 상장을 허용해야 합니다 — <code>exchange_signed.py</code>가 그것입니다. run은 2022-01-12 ~ 01-25, 매일 아침 8시에 결정하고 오후 3시 반에 체결. 끝나면 비중이 <code>sample-factor-weights</code>로 저장됩니다(⑥이 읽습니다). "
            "<b>[0.16.0]</b>이 가장 많이 보이는 run입니다: 결정은 <code>ScheduledEvent</code>, 체결은 <code>MarketEvent</code>로 루프에 들어오고, 단계마다 파일이 하나씩입니다 — 결정 <code>stages/decide.py</code> · 체결 <code>stages/execute.py</code> · 평가 <code>stages/value.py</code> · 규칙 <code>stages/observe.py</code>. 계좌는 자기 보유를 스스로 곱합니다."
        ),
        "frames": [
            F("08_run_factor", 730, "preflight — 판정이 읽고, 얼리기는 받는다",
              "판정 일곱 중 무거운 건 집행 순서(118 ms)입니다: 시간표를 만들려고 집행표의 시각 열을 읽습니다. 읽는 범위가 run 기간 ± 1일(01-11 ~ 01-26)이라 12일만 옵니다(기록 247). "
              "이어서 <code>freeze</code>(20 ms)가 같은 시간표를 물으면 그릇이 0.04 ms에 돌려줍니다. 얼리기는 전략을 새 인스턴스에 한 번 더 만들어 초기 memory가 JSON인지 증명하고(의도된 두 번째 import), 시간표와 체결 목표를 얼립니다. <b>[0.16.0]</b> <code>_freeze_agenda</code> → <code>_freeze_schedule</code>.",
              "<code>preflight</code>(#730, 154.4 ms) → <code>judgments</code>(#732, 133.1 ms) → <code>_judge_execution_ordering</code>(#756, 118.3 ms) → <code>RunFacts.schedule</code>(#757) → <code>derived_schedule</code>(#760, 109.5 ms) → <code>evaluation_times</code>(#766, 84.5 ms) → <code>distinct_values</code>(#774, 83.7 ms: 12 instants) · <code>_judge_member_datasets</code>(#1680, 6.4 ms) · <code>_judge_weights</code>(#1808) · <code>_judge_outputs</code>(#1899) → <code>freeze</code>(#1900, 20.0 ms) → <code>RunFacts.schedule</code>(#1904, 0.04 ms) → <code>_freeze_strategy</code>(#1948, 14.3 ms) → <code>_validate_initial_model_state</code>(#1955) → <code>_freeze_schedule</code>(#2046) → <code>_validate_execution_targets</code>(#2134).",
              fn="preflight()", code=("def", 16),
              mem={"거래일 읽기": "_local_date ×12", "facts settled": "schedule · execution_table · horizon · component:sample-factor · exchange"}),
            F("08_run_factor", 2290, "얼리기 — 읽을 표와 집행표를 지문으로 묶는다",
              "이 전략이 읽는 <code>sample-features</code>는 다른 run이 만든 표지만 여기선 벤더 표와 똑같이 취급됩니다: 지문 한 번(1.4 ms). 집행표는 등록 때 적어 둔 “체결 가능한 가격 컬럼” 목록에 <code>close</code>가 있는지만 봅니다. 얼린 run은 두 지문을 들고 불변식을 검사합니다.",
              "<code>_freeze_sources</code>(#2289, 1.9 ms) → <code>_validate_requirement</code>(#2290) → <code>Workspace.require_verified</code>(#2291, 1.4 ms) → <code>FrozenRun.__post_init__</code>(#2323, 1.0 ms).",
              fn="_validate_requirement()", code=("def", 14)),
            F("08_run_factor", 2351, "전략 · 거래소 · 기간을 다시 만들지 않는다 — RunResources",
              "문이 든 전략 객체 · 거래소 · 규칙(없음) · 체결 기간을 봉지 하나에 담습니다. 세 번의 조회가 각각 0.04 ms 안팎 — 만드는 게 아니라 꺼내는 겁니다. run이 여기서 전략을 다시 import하거나 집행표를 다시 스캔하지 않습니다(기록 242).",
              "<code>RunResources.of</code>(#2351, 1.1 ms) → <code>RunFacts.component</code>(#2358, 0.04 ms) · <code>exchange</code>(#2360) · <code>horizon</code>(#2363) → <code>RunVerdict.require_ready</code>(#2365) → <code>run</code>(#2367, 1,618.8 ms).",
              fn="RunResources.of()", code=("def", 12),
              mem={"resources": "strategy=SampleFactor · exchange=AcademicExchange(SIGNED) · rules=() · horizon=01-12 15:30 ~ 01-25 15:30"}),
            F("08_run_factor", 2376, "run 시작 — 종목 명단은 얼리지 않고 그때그때 읽는다",
              "run이 시작하며 종목 명단을 <b>새로</b> 읽습니다(498 ms). 얼리지 않는 건 일부러입니다(이슈 009): 명단은 날마다 자라고, 새 이름을 안 쓰는 run까지 아침마다 막을 이유가 없어서요. 대신 그날 명단의 지문을 기록에 적습니다. 498 ms는 10행짜리 표의 값이 아니라 프로세스가 pyarrow를 처음 올리는 비용입니다(⑦의 worker에선 25 ms). "
              "그 다음 계좌(현금 1억, SIGNED) · 규칙 자리 · 루프를 조립하고, 결정 담당이 전략에게 “무엇을 읽나”를 <b>여기서 한 번</b> 묻습니다. <b>[0.16.0]</b> 결정 담당 <code>CallbackHandler</code>는 <code>run/engine/stages/decide.py</code>에, 규칙 담당 <code>ComplianceHandler</code>는 <code>stages/observe.py</code>에 있습니다 — 단계 파일은 그 단계가 부르는 저자 메서드의 이름입니다.",
              "<code>run</code>(#2367) → <code>registered_roster</code>(#2376, 497.8 ms) → <code>verify_roster</code>(#2383, 495.6 ms) → <code>build_roster</code>(#2387) → <code>_run_strategy</code>(#2422, 1,120.2 ms) → <code>CallbackHandler.__init__</code>(#2890, 0.47 ms) → <code>SampleFactor.inputs</code>(#2891) → <code>ComplianceHandler.__init__</code>(#2970) → <code>RunLoop.__init__</code>(#2972) → <code>Account.bind</code>(#2974) → <code>RunLoop.run</code>(#2975, 917.6 ms).",
              fn="registered_roster()", code=("def", 12),
              tip="inputs()는 run 전체에서 7번 불린다: 검증의 import 둘 · 판정 · 얼리기 · run 시작의 요구 목록 · 결정 담당 조립 — 그리고 결정마다는 0번(기록 246, 0.14.3과 같다)."),
            F("08_run_factor", 3270, "아침 8시 — 모멘텀 표를 어디까지 읽을지",
              "2022-01-12 08:00, 첫 결정. 전략이 모멘텀 표의 최신 행 하나를 달라고 합니다. 창고는 run 시작 앞의 격자 한 칸(01-11 16:00)부터 run 끝(01-25 23:59:59)까지만 스캔하고(4.3 ms) (11일 × 10종목) 행렬 하나를 만듭니다(1.7 ms).",
              "<code>decide</code>(#3228) → <code>panel_window</code> → <code>_scan_bounds</code>(#3270, 13.6 ms) → <code>observation_table</code>(#3295, 4.3 ms) → <code>Panel.from_table</code>(#3332, 1.7 ms) → <code>PanelWindow.matrix</code>.",
              fn="_scan_bounds()", code=("def", 12),
              mem={"bounds": "2022-01-11 16:00 ~ 2022-01-25 23:59:59 +09:00", "panel.blocks['momentum_5d'].shape": "(11, 10)"}),
            F("08_run_factor", 3228, "[0.16.0] 한 행을 읽고 여섯 이름을 고른다 — 사건 하나, 도장 하나",
              "저자 코드. 창은 01-11 16:00의 행(전날 저녁에 알 수 있던 값) 하나 × 종목 10. 정렬해서 하위 3(K000004 · 5 · 6)에 −1/6, 상위 3(K000003 · 8 · 9)에 +1/6. <code>vq.Rebalance.signed</code>는 부호가 방향입니다. "
              "결정이 돌아오면 프레임워크는 “이 콜백이 실제로 어떤 표의 어떤 지문을 읽었나”(source refs)를 <b>한 번</b> 만들어(3.6 ms) 의도서 도장과 증거 양쪽에 씁니다. 그 뒤 도장을 찍고 받아들여 계좌 · memory · 대기 의도서를 한 번에 publish합니다. "
              "<b>[0.16.0]</b> 루프가 넘긴 사건은 <code>ScheduledEvent(event_id='sample-factor-run.schedule-2022-01-12T0800')</code>이고, 저자 코드가 보는 시각은 <code>call.at</code>, 파일 첫머리는 <code>from vqapr import public as vq</code>입니다.",
              "<code>RunLoop.handle</code>(#3120, 47.0 ms, ScheduledEvent 01-12 08:00) → <code>StrategyPart.dispatch</code>(#3121) → <code>CallbackHandler.dispatch</code>(#3123) → <code>SampleFactor.decide</code>(#3228, 27.0 ms) → <b><code>_callback_actual_source_refs</code>(#3457, 3.6 ms) → <code>_actual_source_refs</code>(#3462)</b> → <code>_stamp_intent</code>(#3563, 0.98 ms) → <code>_accept_intent</code>(#3630, 0.64 ms) → <code>_candidate_callback_state</code>(#3702, 2.8 ms) → <code>_callback_evidence</code>(#3785, 0.33 ms) → <code>RunStateRepository.publish</code>(#3821, 1.4 ms). 둘째 날: <code>decide</code>(#5317, 6.5 ms) → refs(#5483) → 도장(#5589).",
              fn="SampleFactor.decide() — 저자 코드", code=at(DECL + "factor.py", "ranked = sorted(", 10, before=3), author=True,
              mem={"weights": "K000003 +0.1667 · K000008 +0.1667 · K000009 +0.1667 · K000004 −0.1667 · K000005 −0.1667 · K000006 −0.1667", "pending": "intent 1 (계좌 v0 기준)", "source refs": "콜백당 1회"}),
            F("08_run_factor", 3858, "오후 3시 반 — 숏 셋이 실제로 팔린다",
              "시장 사건 01-12 15:30(트레이스엔 UTC 06:30). 기다리던 의도서가 때가 되어 주문을 계획합니다(비중 → 주 수, 13.9 ms, <code>domain/order.py</code>의 <code>plan_orders</code>). SIGNED 상장이라 음수 주 수가 통과합니다. 체결: K000003 +23 · K000008 +8 · K000009 +94, K000004 <b>−55</b> · K000005 <b>−19</b> · K000006 <b>−12</b>(close 가격, 학술 프로파일이라 수수료 0). 계좌 v1: 현금 99,463,501.24, NAV 1억.",
              "<code>RunLoop.handle</code>(#3850, 60.8 ms, MarketEvent 06:30 UTC) → <code>MarketClock.at</code>(#3851) → <code>ExecutionHandler.fill</code>(#3858, 44.0 ms) → <code>plan_orders</code>(#3946, 13.9 ms) → <code>AcademicExchange.execute</code>(#4332, 6.8 ms) → <code>Account.append</code>(#4577, 1.0 ms) → <code>commit_append</code>(#4854).",
              fn="ExecutionHandler.fill()", code=("def", 12),
              mem={"account v1": "롱 3 · 숏 3 · cash 99,463,501.24 · NAV 100,000,000.00"}),
            F("08_run_factor", 4892, "[0.16.0] 같은 시각에 이어서 — 계좌가 자기를 평가하고, 규칙이 보고, 다음으로",
              "체결 직후 보유를 종가로 평가합니다(13.4 ms). <b>[0.16.0]</b> 곱하는 것은 계좌 자신입니다: <code>Account.mark(state, prices)</code>가 자기 보유 × 가격을 계산하고(3.8 ms), <code>domain/valuation.py</code>는 어느 가격을 쓸지(새 행 · 이어 온 마지막 가격 · 없음)만 고릅니다(기록 276). "
              "compliance 규칙이 없으니 “규칙이 본다”는 자리는 0.002 ms에 지나갑니다 — 자리는 있고 할 일이 없을 뿐입니다. 시장 사건 하나는 늘 이 순서입니다: 발생(accrue) → 체결(execute) → 평가(value) → 판정(observe). 이 run엔 열 번.",
              "<code>ValuationHandler.mark</code>(#4892, 13.4 ms) → <code>Account.mark</code>(#4941, 3.8 ms) → <code>ComplianceHandler.observe</code>(#5177, 0.002 ms) → 다음 아침 <code>RunLoop.handle</code>(#5207, 28.5 ms).",
              fn="ValuationHandler.mark()", code=("def", 10)),
            F("08_run_factor", 24476, "run이 끝나면 비중이 dataset이 된다 — 역시 같은 문",
              "10일(계좌 v10, 주문 73 · 체결 54)이 끝나면 기록을 굳히고(표 3: account · fill · weight) 비중 60행을 <code>sample-factor-weights</code>로 냅니다. 각 행의 시각은 그 결정의 시각(08:00). 이 파일도 문(82 ms)을 지나 등록됩니다. "
              "기록을 쓰는 동안 “살아 있다”는 표시(<code>heartbeat</code>)는 chunk마다 불리지만(110번) lock 파일은 초당 한 번만 만집니다(기록 248). <b>[0.16.0]</b> 기록의 모양은 schema v2(<code>schedule</code> 블록)라 0.16.0 전의 기록은 “다시 run 하라”는 고치는 법과 함께 거절됩니다.",
              "<code>RunLoop.finish</code>(#24052) → <code>RunRecordWriter._seal</code>(#24218, 21.1 ms) → <code>_publish_allocation</code>(#24275, 118.0 ms) → <code>RunOutput.register</code>(#24476, 99.5 ms) → <code>verify_source</code>(#24502, 81.7 ms) → <code>Transaction.commit</code>(#24633, 12.7 ms).",
              fn="RunOutput.register()", code=("def", 8),
              disk={".vqapr/runs/sample-factor-run/strategies/sample-factor@0696c8f4/": "strategy.json · tables/vqapr.{account,fill,weight}/all.parquet", ".vqapr/materialized/sample-factor-weights/all.parquet": "60행 (available_at 01-12 08:00 ~ 01-25 08:00 · instrument · weight ±0.1667) · digest 76a9b69b…"}),
        ],
        "remember": [
            "한 사실은 한 번 읽고 나눠 쓴다 — 선언 쪽(RunFacts)도, 콜백 쪽(source refs · inputs)도.",
            "시장 사건 하나 = accrue → execute → value → observe. 단계마다 run/engine/stages/의 파일 하나.",
        ],
    },
    # ---------------------------------------------------------------- ⑤ stop-loss with memory
    {
        "id": "stop", "key": "⑤", "title": "stop-loss — memory가 진입가를 든다",
        "sub": "register stoploss.yaml · 104 ms · 1,124 호출 — run sample-stoploss-run · 4,506 ms · 62,541 호출 · 37일 · 사건 74 (0.14.3은 61,659 호출)",
        "story": (
            "<b>무슨 일인가:</b> <code>stoploss.py</code>의 <code>SampleStopLoss</code>는 첫날 종가가 있는 종목을 전부 같은 비중으로 사고, 각 종목의 <b>진입가를 <code>self.memory</code>에 적어 둡니다</b>. 그 뒤 날마다 최신 종가를 진입가와 견줘 3% 넘게 빠진 종목은 팔고 날짜를 적습니다. "
            "memory는 엄격한 JSON이고 매 결정 전에 복원되고 뒤에 저장됩니다 — 같은 run을 다시 돌리면 같은 손절이 같은 날 납니다. 이 합성 데이터는 잘 빠져서 손절이 이어지고, 02-22엔 K000008 하나, 02-23에 전량 매도, 그 뒤는 현금만."
        ),
        "frames": [
            F("10_run_stoploss", 6434, "결정 전 — 비어 있는 memory가 전략에 복원된다",
              "2022-01-04 08:00, 첫 콜백. 프레임워크가 현재 상태의 memory(첫날이라 <code>{}</code>)와 payload(빈 바이트)를 전략 객체에 넣습니다. 전략은 하나의 객체로 run 전체를 살지만 <b>믿을 건 이 복원된 memory뿐</b>입니다 — 다른 self 속성은 기록이 재현하지 못합니다. "
              "<b>[0.16.0]</b> 복원하는 곳은 <code>run/engine/stages/decide.py</code>(예전 <code>flow/run/callback.py</code>).",
              "<code>preflight</code>(#891, 250.9 ms) … <code>RunLoop.run</code>(#5965, 2,707.2 ms) → <code>checkpoint</code>(#6402) → <code>_visible_callback_state</code>(#6415) → <code>_restore_callback_state</code>(#6434: <code>strategy.memory = {}</code> · <code>load_payload(b'')</code>) → 창 → 계좌 view → decide.",
              fn="_restore_callback_state()", code=("def", 4),
              mem={"strategy.memory": "{}"}),
            F("10_run_stoploss", 6551, "첫 창 — 38일짜리 행렬 하나가 run 전체를 든다",
              "run 시작(01-04) 앞 한 칸(01-03 15:30)부터 끝(02-28)까지, 38일 × 10종목 행렬 하나를 만듭니다. 37번의 결정이 전부 이 행렬의 일부를 봅니다. 둘째 날의 범위 계산은 0.16 ms — 같은 창, 같은 행렬.",
              "<code>SampleStopLoss.decide</code>(#6515, 63.7 ms) → <code>_DeclaredReads.read</code>(#6516, 58.9 ms) → <code>ModelWindow.panel</code>(#6535) → <code>panel_window</code>(#6536, 57.9 ms) → <code>_scan_bounds</code>(#6551, 48.6 ms) → … 둘째 날 <code>panel_window</code>(#9977, 1.1 ms) → <code>_scan_bounds</code>(#9990, 0.16 ms).",
              fn="_scan_bounds()", code=("def", 8),
              mem={"bounds": "2022-01-03 15:30 ~ 2022-02-28 23:59:59 +09:00", "panel.blocks['close'].shape": "(38, 10)"}),
            F("10_run_stoploss", 6515, "첫 결정 — 9종목에 들어가고 진입가 9개를 적는다",
              "저자 코드. 최신 종가(01-03)가 있는 종목은 9개(K000010은 아직 없음). “처음이다” 플래그가 없으니 <code>entry</code>에 종가 9개를 적고 플래그를 세웁니다. 아무도 3%를 안 깼으니 9종목 같은 비중(투자 90%). 플래그를 따로 두는 이유: 나중에 <code>entry</code>가 비었을 때 “처음”으로 오해해 다시 사지 않으려고요.",
              "<code>SampleStopLoss.decide</code>(#6515, 63.7 ms) → <code>read</code>(#6516) → <code>matrix</code> → <code>vq.Rebalance.of</code>.",
              fn="SampleStopLoss.decide() — 저자 코드", code=at(DECL + "stoploss.py", "entry: dict[str, float]", 12), author=True,
              mem={"self.memory": "{entry: {K000001: …, …, K000009: …} 9개, stopped: {}, entered: true}"}),
            F("10_run_stoploss", 7750, "결정 후 — 읽은 것 한 번, memory 정리 한 번, 저장 한 번",
              "결정이 돌아오면 순서대로: 읽은 것(source refs)을 한 번 만들고(3.3 ms) → 의도서에 도장 → 받아들임 → memory를 엄격한 JSON으로 <b>한 번</b> 정리(Decimal · datetime · set이 있으면 여기서 거절; 기록 239) → 계좌 · memory · 대기 의도서를 한 번에 저장(v1). 그리고 15:30에 9종목이 체결됩니다.",
              "<code>_callback_actual_source_refs</code>(#7469, 3.3 ms) → <code>_stamp_intent</code>(#7567, 1.2 ms) → <code>_accept_intent</code>(#7654) → <code>_candidate_callback_state</code>(#7750, 5.6 ms) → <code>RunStateRepository.prepare_callback</code>(#7926, 0.84 ms) → <code>publish</code>(#7947, 1.4 ms) → <code>_deliver</code>(#7948) · <code>ExecutionHandler.fill</code>(#7984, 59.7 ms) → <code>execute</code>(#8674, 10.2 ms) → <code>mark</code>(#9436, 15.0 ms).",
              fn="_candidate_callback_state()", code=("def", 10),
              mem={"root": "v1 (account v0 · memory entry 9 · pending 1)", "source refs": "이 run 37회 — 콜백당 1회"}),
            F("10_run_stoploss", 9956, "둘째 날 — 복원된 memory로 첫 손절",
              "01-05 08:00. 복원된 memory에 진입가 9개가 있습니다. 최신 종가(01-04)를 견주니 K000005가 −3%를 넘겼습니다 → <code>stopped['K000005'] = '2022-01-05'</code>, <code>entry</code>에서 지웁니다. 남은 8종목 같은 비중; 15:30에 K000005를 팝니다. "
              "이어지는 날들(보유 종목 수): 9 → 8(01-05) → 7(01-06) → 5(01-11) → 4(01-19) → 3(01-24) → 2(01-25) → 1(01-26 ~ 02-22, K000008 하나).",
              "<code>_restore_callback_state</code>(#9873) → <code>SampleStopLoss.decide</code>(#9956, 6.3 ms) → <code>_stamp_intent</code>(#10212) → <code>_accept_intent</code>(#10293) → <code>_candidate_callback_state</code>(#10381, 5.5 ms) → <code>prepare_callback</code>(#10557) · <code>fill</code>(#10615, 50.6 ms).",
              fn="SampleStopLoss.decide() — 손절", code=at(DECL + "stoploss.py", "for name, price in list(entry.items())", 6), author=True,
              mem={"self.memory": "{entry: 8, stopped: {K000005: '2022-01-05'}, entered: true}"}),
            F("10_run_stoploss", 58156, "마지막 종목이 깨지면 — 전량 매도는 Hold가 아니라 빈 Rebalance",
              "02-23 08:00. K000008이 02-22 종가로 −3%를 넘겼습니다. <code>entry</code>가 비었고 계좌엔 K000008 52주가 있습니다. <code>Hold</code>는 “아무것도 하지 마라”라 포지션이 그대로 남습니다. 그래서 “목표 비중 없음, 현금 100%”를 돌려줍니다. 15:30에 <b>K000008 −52</b>가 1,441,901.11에 체결되고 계좌(v34)는 현금 84,184,068.92뿐입니다.",
              "<code>RunLoop.handle</code>(#58020, ScheduledEvent 02-23 08:00) → <code>decide</code>(#58156, 2.5 ms) → <code>MarketClock.at</code> → <code>fill</code>(#58596, 14.9 ms) → <code>AcademicExchange.execute</code>(#58719, 1.3 ms) → <code>Account.append</code>(#58774, 0.70 ms).",
              fn="SampleStopLoss.decide() — 마지막", code=at(DECL + "stoploss.py", "if any(quantity != 0", 5, before=3), author=True,
              mem={"self.memory": "{entry: {}, stopped: 9개, entered: true}", "account v34": "positions {} · cash 84,184,068.92"}),
            F("10_run_stoploss", 59285, "그 뒤 — Hold, 기다리는 의도서 없음, 오후엔 평가만",
              "02-24 08:00부터 <code>entry</code>도 포지션도 없습니다 → <code>Hold</code>(“모든 종목이 손절선을 깼다, 현금으로 둔다”). 기다리는 의도서가 없으니 15:30의 체결 단계는 0.002 ms에 지나가고 평가만 합니다(7.5 ms). run은 74 사건, 계좌 v34로 끝나고 비중 dataset이 문을 지나 등록됩니다. "
              "<b>[0.16.0]</b> 체결 앞의 발생 단계(<code>stages/accrue.py</code>)는 배당 · 이자 같은 것이 들어올 자리로, 지금은 받은 계좌를 그대로 돌려줍니다(0.09 ms).",
              "<code>decide</code>(#59285, 2.1 ms) → Hold · <code>AccrualHandler.accrue</code>(#59664, 0.09 ms) → <code>fill</code>(#59667, 0.002 ms, 기다리는 의도서 없음) → <code>ValuationHandler.mark</code>(#59668, 7.5 ms) … <code>_publish_allocation</code> → <code>RunOutput.register</code> → <code>verify_source</code>.",
              fn="SampleStopLoss.decide() — Hold", code=at(DECL + "stoploss.py", "return vq.Hold(", 1, before=0), author=True,
              disk={".vqapr/runs/sample-stoploss-run/strategies/sample-stoploss@94e51128/": "strategy.json · tables 3 (weight 표 33일분, 02-23부터 없음)", ".vqapr/materialized/sample-stoploss-weights/all.parquet": "등록됨"},
              tip="strategy.json엔 memory dict가 없다. 트레이스에 보이는 건 매 콜백의 복원 → 결정 → 한 번의 정리 → 저장이고, 기록엔 그 상태의 ref가 남는다."),
        ],
        "remember": [
            "memory는 결정 전에 복원되고 뒤에 한 번 정리되어 저장된다. 첫 콜백엔 {}. JSON이 아닌 것은 여기서 거절된다.",
            "“처음인가”는 별도 플래그로 기억한다. 포지션을 다 비우려면 Hold가 아니라 빈 Rebalance.",
        ],
    },
    # ---------------------------------------------------------------- ⑥ enhanced index
    {
        "id": "ei", "key": "⑥", "title": "enhanced index — 저장된 비중을 읽는다",
        "sub": "register enhanced.yaml · 108 ms · 1,329 호출 — run sample-enhanced-run · 2,683 ms · 27,993 호출 · 9일 — list datasets 75 ms · show run 19 ms",
        "story": (
            "<b>무슨 일인가:</b> <code>enhanced.py</code>의 <code>SampleEnhancedIndex</code>는 ④가 저장한 비중(<code>sample-factor-weights</code>)을 <b>alpha로 읽고</b>, 종가가 있는 종목의 같은 비중(1/9)에 그 alpha의 절반을 더한 뒤 0 아래를 잘라 냅니다 — 롱온리 enhanced index. "
            "④가 08:00에 정한 비중을 알 수 있게 된 뒤인 09:00에 결정합니다. 두 표를 각각 자기 기간으로 읽습니다(가격 10 × 10, alpha 10 × 10). 마지막으로 <code>list datasets</code>와 <code>show run</code>으로 이 프로젝트에 무엇이 남았는지 봅니다: dataset 6개, 그중 4개가 run이 만든 것."
        ),
        "frames": [
            F("12_run_enhanced", 2621, "얼리기 — 저장된 alpha가 dataset으로 묶인다",
              "읽을 것 둘: <code>sample-factor-weights</code>(④가 만든 표)와 <code>sample-prices</code>(벤더 표). 둘 다 같은 한 줄 — 지문 확인(1.8 · 1.1 ms). run이 만든 표와 벤더 표가 <b>여기서 같은 취급</b>을 받는다는 것이 이 시나리오의 요점입니다.",
              "<code>preflight</code>(#1052, 156.1 ms) → … <code>_freeze_sources</code>(#2620, 3.3 ms) → <code>_validate_requirement</code>(#2621, 1.8 ms) → <code>Workspace.require_verified</code>(#2622, 1.5 ms) · <code>_validate_requirement</code>(#2640, 1.1 ms).",
              fn="_validate_requirement()", code=("def", 14),
              mem={"frozen.source_digests": "{materialized-sample-factor-weights: 76a9b69b…, sample-prices-source: 18bb7017…}"}),
            F("12_run_enhanced", 3610, "9시 — 두 창을 읽고 기본 비중에 alpha를 얹는다",
              "2022-01-13 09:00. 가격 창: 01-12 15:30부터 (10 × 10) 행렬 → 종목 9개 → 기본 1/9 = 0.111. alpha 창: 01-12 08:00부터 (10 × 10) 행렬 → 01-13 08:00의 factor 비중(±1/6)의 절반 → K000003 · 8 · 9엔 +0.083, K000004 · 5 · 6엔 −0.083. 합이 1이 되게 정규화합니다. 첫 결정 74 ms(두 표의 첫 스캔), 다음 날 9 ms.",
              "<code>_window_factory.at</code>(#3540, 01-13 09:00) → <code>SampleEnhancedIndex.decide</code>(#3610, 74.3 ms) → prices: <code>observation_table</code>(#4394, 4.3 ms) → <code>from_table</code>(#4431, 1.4 ms) → alpha: <code>observation_table</code>(#4506, 3.4 ms) → <code>from_table</code>(#4543, 0.57 ms) → <code>Rebalance.of</code>. 둘째 날 <code>decide</code>(#7170, 9.0 ms).",
              fn="SampleEnhancedIndex.decide() — 저자 코드", code=at(DECL + "enhanced.py", "tilted = {", 6, before=0), author=True,
              mem={"panels": "prices (10 × 10) 01-12 15:30 ~ · alpha (10 × 10) 01-12 08:00 ~ (probe_panel.py)"}),
            F("12_run_enhanced", 5223, "3시 반 — 롱온리 체결, 그리고 아홉 날",
              "첫 체결 59 ms. 9일 동안 사건 18, 계좌 v9(주문 81 · 체결 41). 끝나면 비중이 <code>sample-enhanced-weights</code>로 나가고 문(<code>RunOutput.register</code>, 98 ms)을 지나 등록됩니다.",
              "<code>MarketClock.at</code> → <code>fill</code>(#5223, 58.8 ms) … <code>_publish_allocation</code>(#27158, 120.8 ms) → <code>RunOutput.register</code>(#27422, 97.8 ms) → <code>verify_source</code>.",
              fn="ExecutionHandler.fill()", code=("def", 8)),
            F("13_list_datasets", 13, "list datasets — 여섯, 그중 넷은 run이 만들었다",
              "장부를 열어(66 ms) dataset 목록을 냅니다: <code>sample-prices</code> · <code>sample-execution</code>(벤더), <code>sample-features</code>(③), <code>sample-factor-weights</code>(④), <code>sample-stoploss-weights</code>(⑤), <code>sample-enhanced-weights</code>(⑥). 어느 run의 어느 코드 버전(<code>sample-factor@0696c8f4</code>)이 만들었는지가 이름 옆에 있습니다.",
              "<code>list_.run</code>(#12, 67.1 ms) → <code>Workspace.open</code>(#13, 66.3 ms) → <code>Workspace._read</code>(#16) → <code>datasets</code>(#1073) → <code>_summarize</code> ×6(#1081 …) → <code>success</code>(#1087, count 6).",
              fn="Workspace.open()", code=("def", 8)),
            F("14_show_run_enhanced", 19, "show run — 기록만 읽는다, 35호출 19 ms",
              "<code>show run sample-enhanced-run</code>은 기록(<code>run.json</code>)만 읽습니다: 읽은 표 둘과 각각의 지문, 거래소 코드의 지문, 체결 조건(close · 15:30 · Asia/Seoul), 초기 계좌, 기간. 이 run이 어떤 바이트를 읽었는지가 기록에 있으니 나중에 파일이 바뀌어도 “그때 무엇이었나”는 남습니다. "
              "<b>[0.16.0]</b> 읽는 쪽은 <code>record/reader.py</code>이고, schema v1 기록(0.16.0 전)이면 여기서 “다시 run 하라”고 거절합니다.",
              "<code>main</code>(#0, 18.5 ms) → <code>show.run</code>(#12, 10.7 ms) → <code>run_ids</code>(#13) → <code>read_run_record</code>(#19, 8.6 ms) → <code>record_view</code>(#23) → <code>strategy_refs</code>(#24) → <code>datamodel_refs</code>(#28) → <code>success</code>(#29).",
              fn="read_run_record()", code=("def", 8),
              disk={".vqapr/": "workspace.yaml · instruments.json · materialized/ 4 · runs/ 4"}),
        ],
        "remember": [
            "run이 저장한 비중은 dataset이다: 다음 run이 한 줄로 읽고, 얼리기는 지문으로 묶고, 읽기는 자기 기간만큼.",
            "list · show는 장부와 기록만 읽는다. 기록은 읽은 파일의 지문을 든다.",
        ],
    },
    # ---------------------------------------------------------------- ⑦ --jobs batch
    {
        "id": "batch", "key": "⑦", "title": "--jobs 배치 — worker도 preflight, cube 한 번",
        "sub": "run sample-factor-run sample-stoploss-run --jobs 2 --force · 2,917 ms · 3,512 호출 (driver) — worker 하나를 따로 추적: 1,247 ms · 23,963 호출",
        "story": (
            "<b>무슨 일인가:</b> ④와 ⑤를 <b>한 배치</b>로 동시에 돌립니다(<code>--jobs 2</code>; 기록이 이미 있으니 <code>--force</code>). 지휘자(driver)는 일꾼(worker)을 띄우기 <b>전에</b> 각 run이 무엇을 읽는지 한 번 묻고, 서로가 만드는 걸 읽지는 않는지 보고, 읽을 표를 미리 <b>한 번 구워 둡니다</b>(cube: 전 종목 × 전 기간 행렬 파일). "
            "일꾼은 자기 기간만큼을 그 파일의 일부로 메모리에 <b>매핑</b>해 읽습니다 — 스캔이 없습니다. 배치가 끝나면 구운 파일은 지워집니다. 일꾼도 단일 run과 똑같이 <code>preflight</code>를 지나 판정을 받습니다. "
            "지휘자의 트레이스는 프로세스 경계에서 끝나므로 일꾼 쪽은 같은 일꾼 함수를 같은 프로파일러 아래서 따로 돌려 얻었습니다. <b>[0.16.0]</b> 배치의 코드는 <code>run/batch.py</code>, 일꾼 함수는 <code>run/assemble.py</code>에 있습니다."
        ),
        "frames": [
            F("15_run_batch", 13, "지휘자 — 무엇을 읽는지 한 번 묻고, 서로 독립인지 본다",
              "run이 둘이고 jobs가 2니 배치 경로입니다. 장부를 열고(57 ms) run마다 부품을 올려 “무엇을 읽나”를 <b>한 번씩</b> 묻습니다 — factor는 <code>sample-features</code>, stop-loss는 <code>sample-prices</code>. 그 답으로 둘이 서로가 만드는 걸 읽지 않는지 봅니다(0.16 ms). 병렬이면 순서를 약속할 수 없으니 읽는 쪽이 있으면 배치 전체를 거절합니다.",
              "<code>run</code>(#12) → <code>_run_each_in_workers</code>(#13, 2,907.9 ms) → <code>Workspace.open</code>(#16, 57.1 ms) → <code>batch_reads</code>(#1076, 10.1 ms) → <code>_reads</code>(#1079, 5.1 ms · #1170, 4.7 ms) → <code>require_independent_batch</code>(#1249, 0.16 ms) → <code>batch_cubes</code>(#1258).",
              fn="_run_each_in_workers()", code=at("src/vqapr/cli/run.py", "with batch_cubes(workspace, targets, reads) as cubes:", 12, before=6),
              mem={"targets": "[sample-factor-run, sample-stoploss-run]", "reads": "factor → sample-features[momentum_5d] · stop-loss → sample-prices[close]"}),
            F("15_run_batch", 1258, "굽기 전에 — 묵은 것을 치우고, 잠그고",
              "<code>.vqapr/cubes/</code> 아래에 이 배치의 폴더를 만들고 잠금 파일에 pid를 적습니다. 먼저 이전 배치가 남긴 묵은 폴더(잠금이 10분 넘게 갱신 안 된 것)를 치우고, 30초마다 잠금을 만지는 스레드가 “살아 있다”고 표시합니다. 그리고 굽기.",
              "<code>batch_cubes</code>(#1258, 780.2 ms) → <code>_bake_for_batch</code>(#1260, 775.7 ms) → <code>source_digest</code>(#1270) → <code>bake</code>(#1273, 670.5 ms: sample-features) → <code>source_digest</code>(#1372) → <code>bake</code>(#1375, 98.6 ms: sample-prices).",
              fn="batch_cubes()", code=("def", 14),
              disk={".vqapr/cubes/<pid>-<hex>/": "cube.lock (pid)"}),
            F("15_run_batch", 1375, "굽기 — 가격표의 close를 전 종목 × 전 기간으로 한 번",
              "표마다 한 번: 종목 전부(10)를 세고, 등록된 기간 전체를 스캔하고, (735 × 10) 숫자 행렬로 접어 <code>close.npy</code>(58,928 B)로 저장합니다. 옆에 어느 칸에 값이 있었나(<code>present.npy</code>), 날짜 목록, 종목 목록, 원천의 지문(<code>cube.json</code>). 앞의 <code>sample-features</code>는 12 × 9(670 ms는 이 프로세스의 첫 스캔). 구울 수 없는 표(문자열 필드 등)는 조용히 빠지고 그 일꾼은 스캔합니다.",
              "<code>bake</code>(#1273, 670.5 ms: sample-features) → <code>distinct_values</code>(#1274, 17.7 ms) → <code>placement</code>(#1327, 7.0 ms) · <code>bake</code>(#1375, 98.6 ms: sample-prices) → <code>distinct_values</code>(#1376, 14.8 ms) → <code>placement</code>(#1431, 2.4 ms) → <code>dense_block</code> → <code>open_cube</code>.",
              fn="bake()", code=at("src/vqapr/data/cube.py", "instants, keep, rows, cols = placement(table, names, keyed)", 12, before=0),
              disk={".vqapr/cubes/<batch>/sample-prices/": "close.npy (735, 10) float64 58,928 B · present.npy (735, 10) bool 7,478 B · instants.npy (735,) · instruments.json 10 · cube.json", ".vqapr/cubes/<batch>/sample-features/": "momentum_5d.npy (12, 9) 992 B · present.npy · instants.npy (12,) · instruments.json 9 · cube.json (probe_cubes.py)"}),
            F("15_run_batch", 2918, "일꾼을 띄운다 — 여기서 지휘자의 트레이스는 경계를 만난다",
              "두 run이 두 프로세스에 하나씩 갑니다. 넘기는 건 문자열과 bool뿐(프로젝트 경로, run 이름, 저장소, force, cube 폴더). 2,016 ms 동안 지휘자는 기다립니다. 이 프로파일러는 이 프로세스의 것이라 일꾼 안의 호출은 여기 없습니다 — 다음 두 프레임은 일꾼을 따로 추적한 것입니다.",
              "<code>in_workers</code>(#2918, 2,016.2 ms) — 안쪽 호출 없음(다른 프로세스).",
              fn="in_workers()", code=("def", 10)),
            F("16_worker_factor", 16, "[0.16.0] 일꾼 — run의 문을 지나고 판정을 받는다",
              "일꾼 프로세스는 장부를 열고(0.8 ms — 이미 데워진 파일) 자기 run을 <code>preflight</code>에 넘깁니다: 판정 122 ms · 얼리기 20 ms · 봉지 0.6 ms. 판정이 거절하면 <code>check</code>와 같은 code로 거절되고 기록은 안 쓰입니다 — 일꾼이 판정 없이 얼려 check가 거절한 run을 배치가 돌리던 사고(이슈 015)가 다시 날 수 없는 이유입니다. 그 뒤는 단일 run과 같습니다. "
              "<b>[0.16.0]</b> 일꾼 함수의 한 줄이 이 페이지의 새 이름을 다 보여 줍니다: <code>preflight(workspace, workspace.run_definition(run_id)).require_ready()</code>.",
              "<code>run_registered_strategy</code>(#0, 1,244.6 ms) → <code>Workspace.open</code>(#1, 0.81 ms) → <code>preflight</code>(#16, 143.4 ms) → <code>judgments</code>(#18, 122.1 ms) → <code>freeze</code>(#1194, 20.4 ms) → <code>_freeze_strategy</code>(#1246) → <code>_freeze_sources</code>(#1587) → <code>RunResources.of</code>(#1649, 0.64 ms) → <code>require_ready</code>(#1663) → <code>registered_roster</code>(#1665, 24.5 ms) → <code>_run_strategy</code>(#1711, 1,075.2 ms) → <code>RunLoop.run</code>(#2271, 914.3 ms).",
              fn="run_registered_strategy() — worker", code=at("src/vqapr/run/assemble.py", "frozen, resources = preflight(workspace, workspace.run_definition(run_id)).require_ready()", 8, before=1)),
            F("16_worker_factor", 2616, "일꾼 — 스캔 대신 구운 파일을 매핑한다",
              "일꾼의 첫 결정(01-12 08:00). 범위는 평소처럼 정하고(12.5 ms), 그 다음이 다릅니다: 창고에 cube 폴더가 있으니 <code>cube.json</code>의 원천 지문이 일꾼이 방금 확인한 지문과 같은지 본 뒤(1.7 ms), <code>momentum_5d.npy</code>를 메모리 매핑으로 열어 자기 기간의 행만 잘라 씁니다(3.4 ms). "
              "run이 선언한 종목(10)이 cube의 종목(9)과 달라 한 번 모으기(gather)를 합니다(11 × 10, K000010 열은 NaN). 이 트레이스 어디에도 스캔(<code>observation_table</code>)이 없습니다. 첫 결정 25 ms, 다음부터 6.7 ms.",
              "<code>SampleFactor.decide</code>(#2524, 24.8 ms) → <code>panel_window</code>(#2551, 19.5 ms) → <code>_scan_bounds</code>(#2566, 12.5 ms) → <code>open_cube</code>(#2590, 1.7 ms) → <code>panel_from_cube</code>(#2616, 3.4 ms) → <code>PanelWindow.matrix</code>(#2629) → <code>_callback_actual_source_refs</code>(#2742, 3.6 ms). 다음 날 <code>decide</code>(#4602, 6.7 ms).",
              fn="panel_from_cube()", code=at("src/vqapr/data/cube.py", "if whole and identical:", 8, before=2),
              mem={"cube": "sample-features: instants 12 · names 9 · digest 54f8fd04… = worker의 digest", "panel": "(11 × 10) gather — K000010 열 NaN"}),
            F("15_run_batch", 2921, "배치가 돌아오면 구운 파일은 없다 — 봉투는 run마다 하나",
              "일꾼 둘이 결과를 돌려주면 <code>batch_cubes</code>의 <code>finally</code>가 스레드를 멈추고 cube 폴더를 지웁니다(5.0 ms). 성공이든 거절이든 예외든 같습니다 — 쌓이는 게 없습니다. run마다 기록을 읽어 봉투를 만듭니다: factor 계좌 v10 · 주문 73 · 체결 54, stop-loss 계좌 v34 · 주문 111 · 체결 59 — ④·⑤와 같은 수. 봉투의 <code>jobs: 2</code>가 실제로 돈 프로세스 수입니다.",
              "<code>in_workers</code>(#2918) → <code>batch_cubes</code>(#2921, 5.0 ms: finally → rmtree) → <code>_worker_entry</code>(#2922, 17.1 ms: sample-factor-run) → <code>_strategy_envelope</code>(#2923) → <code>_worker_entry</code>(#3155, 20.5 ms: sample-stoploss-run) → <code>_runs_envelope</code>(#3502) → <code>success</code>(#3506).",
              fn="batch_cubes() — finally", code=at("src/vqapr/run/batch.py", "_bake_for_batch(", 9, before=1),
              disk={".vqapr/cubes/": "비어 있음 (배치 폴더 삭제됨)", ".vqapr/runs/": "sample-factor-run · sample-stoploss-run 다시 씀 (--force)"}),
        ],
        "remember": [
            "일꾼도 preflight를 지난다: check가 거절하는 run은 배치도 거절하고 기록을 쓰지 않는다.",
            "배치는 무엇을 읽는지 한 번 묻고, 표마다 cube를 한 번 굽고, 일꾼은 매핑한다. 끝나면 cube는 없다.",
        ],
    },
]

TABLE = {
    "title": "트레이스가 확인한 것 — 0.16.0에서 바뀐 자리와 그대로인 자리",
    "rows": [
        ["<b>[0.16.0] run의 문은 preflight, 얼리기는 freeze</b> (기록 279)",
         "<code>preflight</code>: 03 #340 · 06 #475 · 08 #730 · 10 #891 · 12 #1052 · 16 #16. <code>freeze</code>: 03 #49684(저장된 예외) · 06 #1798 · 08 #1900 · 16 #1194. 0.14.3의 <code>verify_run</code> 자리(03 #336 · 08 #722 · 16 #16)와 순서 · 깊이가 같다",
         "이름만 바뀌었다. check · run · worker가 같은 함수를 지나고 선언은 명령당 한 번 읽힌다(기록 240–242)"],
        ["<b>[0.16.0] 시간표가 사건을 만든다</b> (기록 278)",
         "<code>RunFacts.schedule</code>: 08 #757(읽음) → #1904(0.04 ms). <code>derived_schedule</code>: 03 #369 1,813.9 ms(734일) · 08 #760 109.5 ms(12일). <code>RunLoop.handle</code>의 event: 08 #3120 <code>ScheduledEvent(event_id='sample-factor-run.schedule-2022-01-12T0800')</code> · #3850 <code>MarketEvent(06:30 UTC)</code>",
         "선언의 <code>agenda:</code>는 <code>schedule:</code>, 저자가 보는 시각은 <code>call.at</code>, 사건의 이름은 <code>call.event_id</code>"],
        ["<b>[0.16.0] 폴더가 고리를 따른다</b> (기록 268–277)",
         "프레임이 선 파일: <code>data/verification.py</code>(파일의 문) · <code>workspace/</code>{registry · registration · merge} · <code>run/preflight/</code>{verdict · checks · facts · freeze} · <code>run/assemble.py</code> · <code>run/batch.py</code> · <code>run/engine/loop.py</code> · <code>run/engine/stages/</code>{decide · execute · value · observe · accrue} · <code>run/engine/output.py</code> · <code>record/reader.py</code> · <code>component/conformance.py</code>",
         "같은 함수가 개념의 폴더로 옮겨 갔다. 각 파일이 무엇인지는 코드 아래 카드와 맨 아래 src/ 지도에"],
        ["<b>[0.16.0] 계좌가 자기 보유를 곱한다</b> (기록 276)",
         "08: <code>ValuationHandler.mark</code> #4892 → <code>Account.mark</code> #4941(3.8 ms). 가격 고르기만 <code>domain/valuation.py</code>",
         "상태 없는 <code>ValuationService</code>가 없어졌다. 기록은 0.15.0과 같은 입력에 같은 값"],
        ["<b>계산된 숫자는 그대로</b>",
         "factor: 주문 73 · 체결 54 · 계좌 v10, 첫날 +23 · +8 · +94 / −55 · −19 · −12, 현금 99,463,501.24. stop-loss: 111 · 59 · v34, 02-23 K000008 −52, 현금 84,184,068.92. enhanced: 81 · 41 · v9. features 108행 · factor 비중 60행. 지문 18bb7017… · 49e4b4ab… · 54f8fd04…",
         "기록에서 직접 읽어 0.14.3 판과 대조했다. 달라진 것은 컴포넌트 지문(sample-factor@9bba20c4 → @0696c8f4 등) — 저자 파일의 import 줄이 바뀌어서"],
        ["<b>한 사실은 한 번 — 캠페인이 흐트리지 않았다</b> (기록 246–248)",
         "<code>_actual_source_refs</code>: 08 ×10 · 10 ×37 · 12 ×9. <code>inputs()</code>: 08 · 10 · 12 ×7. <code>_local_date</code>: 08 ×12 · 06 ×18 · 10 ×38 · 03 ×734. <code>heartbeat</code>: 08 ×110 · 10 ×404 (lock touch는 초당 한 번)",
         "0.14.3 판의 수와 하나도 다르지 않다"],
        ["호출 수는 1~3% 늘었다",
         "register 973 → 980 · check 48,329 → 49,807 · DataModel 8,158 → 8,171 · factor 24,374 → 24,985 · stop-loss 61,659 → 62,541 · enhanced 27,311 → 27,993 · worker 23,353 → 23,963",
         "원인은 이 판에서 가르지 않았다: 0.14.3의 트레이스는 커밋되지 않아 호출을 함수별로 견줄 수 없다. 늘어난 만큼 루프 안의 같은 함수가 뒤로 밀려, 이 판의 긴 run 프레임은 번호가 아니라 사건의 날짜로 다시 찾았다"],
        ["cold 읽기가 절대치를 지배한다",
         "등록의 <code>check_span</code> #214 1,677.1 ms(식은 디스크의 첫 duckdb 스캔; 두 번째 표는 #392 11.2 ms) · 명단 #47 804.5 ms(첫 pyarrow) · DataModel 첫 <code>observation_table</code> #3233 1,064.2 ms · 둘째 날부터 2 ms · run 시작의 명단 08 #2376 497.8 ms, worker #1665 24.5 ms(이슈 009, 설계)",
         "판끼리 절대치를 비교하지 말 것. 이 판은 로컬 디스크이되 캐시가 식은 상태였다"],
    ],
}
