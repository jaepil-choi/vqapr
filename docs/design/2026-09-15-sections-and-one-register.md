# 보고서 절은 하나씩, 등록 창구는 하나 — 2026-09-15 testbed 보고 다섯

**Status: 진행 중 (2026-09-15, 브랜치 `redesign/sections-and-one-register`).** 근거는 시나리오 testbed run 5의
보고 다섯(`docs/issues/report-2026-09-15-*`, 트리아지 `docs/handoff/2026-09-15-scenario-testbed-run-5-findings.md`).
오너 결정 2026-09-15: 두 구조 제안을 받아들이고, worktree의 redesign 캠페인으로 진행해 develop에 merge한다.
문서 보고(체결 직후의 결정)는 skill만 바뀌므로 develop에 먼저 들어갔다(`ab0a6b81`).

## 1. 등록 창구 하나

**문제.** 컴포넌트를 등록하는 길이 둘이고, "예전 것을 바꿨다"는 한쪽만 말한다.

| 길 | 어디 | 옛 fingerprint를 보나 |
|---|---|---|
| `vqapr register strategy <id> <file.py>` | `workspace/registration.py::register_authored` | 쓰기 전에 `Workspace.create(...).components`를 따로 읽는다 → `replaced` |
| `vqapr register <declaration.yaml>` | `apply` → `_component` → `Transaction.register_component` | 안 본다. `merge.py::_merge_component`가 조용히 바꾼다 |

옛 항목을 아는 곳은 병합(`_merge_component`의 `existing`) 한 곳뿐인데, 세 인자 형식은 그 옆에서 같은 사실을 한 번 더
읽는다. 문 둘에 접수원 둘, 한 명만 "교체했습니다"라고 말한다.

**결정.** 교체는 병합이 말한다. `Transaction.register_component(ref)`가 그것이 바꾼 옛 `ComponentRef`를(새 id이거나
바이트가 같으면 `None`) 돌려주고, 두 길이 모두 그 답을 싣는다.

- 세 인자 형식: 지금 그대로 `replaced: {fingerprint: <옛것>}`. 따로 읽던 조회는 없어진다.
- 선언 형식: `replaced: {<id>: {fingerprint: <옛것>}}` — 한 문서가 여러 컴포넌트를 싣기 때문. 없으면 키도 없다.
- exchange처럼 세 인자 형식이 없는 종류도 선언 형식으로 같은 답을 받는다.
- skill `register-dataset/references/correcting-a-registration.md`가 두 형식을 같이 말한다.

## 2. 보고서 절은 하나씩

**문제.** `report/compose.py::strategy_report`가 여섯 절을 차례로 부르고, 한 절이 `ValueError`를 던지면 보고서
전체가 사라진다. NAV가 0 이하로 간 record(`bd-a`, 38 세션)에서 `performance`의 수익률 계산
(`metrics.returns`)이 던지고, `vqapr export`는 `report.json`을 통째로 빼며, Python 호출은 맨 `ValueError`를 받는다.
빠진 절을 말하는 길(`omitted`)은 이미 있지만 두 경우(positions 없음 · 규칙 없음)를 손으로 적은 것뿐이다.

**결정.** 절마다 "결과, 아니면 이유"를 돌려주고 보고서는 모으기만 한다. 건강검진에서 혈액검사 하나가 안 됐다고
X-ray 결과까지 버리지 않는 것처럼.

- 절을 만드는 함수가 답할 수 없으면 이유를 든 예외(`SectionUndefined`) 하나를 던지고, `compose`가 절 하나씩 받아
  `None`과 `omitted[<절>]`로 옮긴다. 기존의 두 경우도 같은 문을 지난다.
- 모든 수가 NAV의 몫인 절(`performance` · `book` · `intent`)은 NAV가 0 이하인 시점이 있으면 빠지고, 이유는
  첫 시점 · 개수 · 가장 낮은 값을 말한다. NAV로 나누지 않는 절(`attribution` · `compliance`)은 그대로 계산된다.
- `trading`은 남는다. 비용 · 체결 · 보유 기간은 금액과 개수라서 그대로이고, NAV 몫인 것만 비운다: 그 기간이
  0 이하의 NAV에서 시작한 점의 회전율은 `None`(`Curve`가 이미 "값을 매길 수 없는 점"으로 쓰는 뜻), 연율
  회전율과 평균 NAV 대비 비용은 `None`.
- `StrategyReport.performance`는 `None`일 수 있게 된다. 전에는 그 경우 호출이 죽었다. `run_report`의 headline은
  그 전략의 수익 칸을 비우고, 상관행렬과 벤치마크 비교는 그 전략을 빼며 빠진 이유를 말한다.
- `vqapr export`는 `report.json`을 쓰고, 빠진 절은 문서 안의 `omitted`가 말한다.

## 3. 같은 브랜치의 작은 둘

- **버전.** `vqapr.__version__`, `vqapr --version`(다른 명령처럼 JSON 봉투), 그리고 `run.json`·`strategy.json`의
  `package_version`. run identity에는 넣지 않는다(오너 결정 2026-09-15: 버전은 영수증이다). 같은 fingerprint라서
  거절할 때 그 기록을 쓴 버전을 말한다. showcase digest 스크립트는 이 키를 `timing`처럼 뺀다.
- **배치 시간.** envelope에 배치 `elapsed`와 `bake`, run마다 `elapsed`. `timing.total`은 이벤트 루프만 잰다는
  것을 `run-backtest/references/watching-and-failures.md`가 말한다. record는 바뀌지 않는다.

## 4. 하지 않는 것

- 수량 비율 주문("보유 수량을 k배"): 평가자가 문서 보고로 재분류했다.
- F-022 · F-029 · F-031(오너 질문)과 "이번 버전에서 바뀐 것"을 skill과 함께 설치하는 일: 판정 전.
- 데이터셋 재측정의 옛 digest를 `replaced`로 말하는 일: 이 보고의 범위 밖. 같은 문으로 나중에 더할 수 있다.
