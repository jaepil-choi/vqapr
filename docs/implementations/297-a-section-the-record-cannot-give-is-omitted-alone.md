# 297 — 보고서 절은 하나씩 만든다: 답할 수 없는 절은 이유와 함께 `None`, 나머지는 계산된다

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 보고서 절과 등록 창구 (`redesign/sections-and-one-register`), M2 — 설계 `docs/design/2026-09-15-sections-and-one-register.md` §2 |
| **앞선 기록** | `296` |
| **계기** | `docs/issues/report-2026-09-15-strategy-report-raises-bare-valueerror-when-nav-goes-nonpositive.md` — NAV가 0 이하로 간 record(`bd-a`, 38 세션)에서 `strategy_report`가 맨 `ValueError`(`nav[1943] must be positive to define a return`)로 여섯 절을 모두 잃었고, `vqapr export`는 `report.json`을 통째로 뺐다 |
| **깨지는 변화** | 없음. 전에 죽던 경우에만 모양이 다르다: `StrategyReport.performance`와 `HeadlineRow`의 수익 칸이 `None`일 수 있다 |

---

## 무엇이 어떻게 바뀌었는가

빠진 절을 말하는 길(`omitted`)은 있었지만 두 경우(positions 없음 · 규칙 없음)를 손으로 적은 것이었고, 그 밖의
실패는 보고서 전체를 가져갔다. 이제 절 하나하나가 한 문을 지난다. 건강검진에서 혈액검사 하나가 안 됐다고
X-ray 결과까지 버리지 않는 것처럼.

- `report/measure.py::SectionUndefined`(`ValueError`의 하위): 절을 만드는 함수가 답할 수 없을 때 이유를 들고
  던진다. `nonpositive_nav(grid)`가 그 이유를 한 문장으로 만든다 — 몇 개의 평가 중 몇 개, 첫 시점, 가장 낮은
  값과 그 시점.
- `report/compose.py::strategy_report`: `section(name, build)`가 절 하나씩 받아 `SectionUndefined`를 `None`과
  `omitted[name]`으로 옮긴다. positions 없음과 규칙 없음도 같은 문을 지난다(`from_positions`, `monitored`).
- NAV 몫으로만 된 절 — `performance`(수익률) · `book`(비중) · `intent`(실현 비중) — 은 NAV가 0 이하인 평가가
  있으면 빠진다. `attribution`(금액)과 `compliance`는 그대로다.
- `trading`은 남는다: 0 이하의 NAV에서 시작한 기간의 회전율은 `None`(`Curve`가 이미 쓰는 "값을 매길 수 없는
  점"), 연율 회전율과 평균 NAV 대비 비용은 `None`, 비용 · 체결액 · 체결 요약 · 보유 기간은 그대로.
- `run_report`: 수익이 없는 전략은 `headline`에 남되 수익 칸이 비고, `correlation`과 `relative`에서 빠진다.
  `measure.relative`는 어느 쪽이든 수익이 없으면 `None`.
- `vqapr export`는 이제 `report.json`을 쓴다. 빠진 절은 문서 안의 `omitted`가 말한다.
- skill `analyze-result/references/report-sections.md`가 무엇이 빠지고 무엇이 남는지 말한다.

- 0.17.0(budget 캠페인) 위로 rebase하며: record `292`의 `budget` 절도 같은 문을 지난다. 기록에 budget이
  없거나(0.17.0 이전), positions 없이 기록됐거나, `book`·`performance`가 빠졌으면 이유와 함께 `None`이다.

## 대안과 선택

- 필드 단위로 비우기(book의 개수는 두고 비중만 `None`): 절마다 모양이 둘로 갈린다. NAV 몫으로만 된 절은 절째로
  빼고, 금액과 몫이 섞인 `trading`만 몫을 비웠다.
- NAV가 양수인 구간만으로 계산하기: 기간이 조용히 짧아진 수를 내놓는다. `metrics.returns`가 0 이하의 시작값을
  건너뛰지 않고 거절하는 것과 같은 이유로 하지 않았다.
- run이 NAV ≤ 0을 envelope에 알리는 일(F-029): 오너 질문으로 남았다. `nonpositive_nav`가 그 측정의 자리다.

## 검증

- 새 `tests/report/test_a_section_the_record_cannot_give_is_omitted_alone.py`(3): NAV 100 → 100 → 10 → -40 → -10인
  signed 공매도 기록. `performance` · `book` · `intent`는 한 이유("2 of 5", 첫 시점, -40)로 빠지고,
  `attribution`은 0 · -90 · -50 · 30, 합 -110 = -10 - 100(잔차 0), `trading`의 회전율은 0.3 · 0 · 0 · `None`,
  체결액 60. `run_report`는 수익 칸이 빈 행과 `correlation None` · `relative []`. `vqapr export`는
  `omitted == {}`로 `report.json`을 쓴다.
- report · export · public · address 묶음: 45 passed. fast set(`uv run python -m pytest tests/ -q`): 1792 passed,
  6 skipped — M0 기준 1787에 M1의 2와 이 기록의 3.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
