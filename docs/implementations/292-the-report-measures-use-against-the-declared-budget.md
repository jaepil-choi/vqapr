# 292 — 리포트는 선언된 budget에 대어 사용률을 잰다: `strategy.json`의 `budget`, 리포트의 `budget` 절

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | strategy budget (`redesign/strategy-budget`, worktree), M2 — 설계 `docs/design/strategy-budget.md` |
| **앞선 기록** | `291` |
| **계기** | 오너(2026-09-15): "flexible budget을 해본 적이 있는데 문제점은 성과의 비교가 어렵다는 점이었어 … long 0.5만 쓰고 short 0.3만 쓰는 경우 … 어떻게 long short 1, -1 을 다 쓰는 전략과 비교할 수 있지?" 이어서 "당연히 비교는 리포트가 할껀데" |
| **깨지는 변화** | 기록 모양: `strategy.json`에 `budget` 키가 생긴다. 리포트에 `budget` 절, headline에 `mean_use` 열. 0.16의 기록은 그대로 읽히고, 리포트가 `omitted["budget"]`으로 이유를 말한다 |

---

## 왜 이 변경이 있는가

record `291`이 budget을 전략의 선언으로 만들었지만, 그것이 기록에 남지 않으면 비교할 분모가 여전히 없다. NAV 수익만으로는
한도의 절반을 쓴 전략과 전부 쓴 전략을 비교할 수 없다 — 앞의 것이 신호가 약해서 덜 벌었는지, 덜 써서 덜 벌었는지 가를 수
없다.

## 무엇이 어떻게 바뀌었는가

- **기록** — `StrategyRecord.budget`(`record/schema.py`): `Budget.encoded()` 그대로(`{"kind": "fixed", "long": "1",
  "short": "-1"}`). `run/recording.py`가 frozen layer의 budget을 쓴다. 0.17.0 이전의 기록에는 없고, 읽기는 그대로 된다.
- **리포트 문서** — `report/document.py::BudgetUse`, `StrategyReport.budget`, `HeadlineRow.mean_use`.
  - valuation마다 `long_use`(long 노출 / 선언된 long), `short_use`(short 노출 / 선언된 short; 그 쪽이 없는 budget이면
    `None`), `use`(gross / 선언된 gross).
  - 한 기간의 수익은 그 기간을 연 valuation의 book이 번다. 연 book이 무언가를 든(`use > 0`) 기간에 대해
    `mean_return = mean_use_held × mean_return_at_full_use + timing`. `mean_return_at_full_use`는 `return / use`의 평균
    — 한도를 다 쓴 전략과 비교할 숫자다. `timing`은 사용률과 그 수익의 공분산이고, 두 항이 `mean_return`과 정확히 맞도록
    차로 계산한다. 이긴 기간에 더 썼으면 양수다.
- **계산** — `report/measure.py::budget_use`: book과 performance가 같은 valuation grid에서 나오므로 `use[i]`가
  `returns[i]` 기간을 연 book이다.
- **문** — `report/compose.py`: 기록에 budget이 있으면 절을 계산하고, 없으면 `omitted["budget"]`에 "0.17.0 이전의
  기록"이라고 쓴다. 보유를 기록하지 않은 run이면 book과 같은 이유로 빠진다.
- **skill** — analyze-result의 `report-sections.md`가 일곱째 절을 설명한다: 일부만 쓴 전략은 NAV 수익이 아니라
  `mean_return_at_full_use`와 Sharpe로 비교한다.

## 대안과 선택

- **수익을 사용률로 나눈 곡선 하나만**: 타이밍(더 쓸 때 벌었는가)이 사라진다. 분해가 그 둘을 가른다.
- **변동성을 맞춘 누적 수익**: 보기 좋은 그림이지만 기록에서 곧바로 나오는 숫자가 아니고, Sharpe가 이미 같은 비교를 한다.
  그림은 analyze-result가 동의를 받고 그린다.
- **짝꿍 fixed run 강제**: 가장 정확하지만 실행이 두 배다. 필요하면 같은 신호로 `fixed`를 선언한 run을 하나 더 돌리면 된다
  — 강제하지 않는다(오너가 B안).
- **옛 기록에 기본 budget을 가정**: 0.16의 전략은 cash 범위와 종목별 범위를 결정마다 실었다. 무엇을 가정해도 그 run의
  분모가 아니다. 빠뜨리고 이유를 말한다.

## 검증

- `uv run python -m pytest tests/report tests/record tests/cli/test_show.py tests/run/test_run_freezes_its_record.py
  tests/cli/test_commands.py tests/portfolio/test_the_budget_is_declared_once.py -q -m ""`: 150 passed.
- 새 `tests/report/test_the_budget_section_splits_the_mean_return.py`: 손으로 계산되는 네 valuation(현금 → A 절반 →
  A 60 · B -20, NAV 110 → 현금 99). 기간 둘, 평균 수익 0, 손실 직전에 더 썼으므로 `timing < 0`, 두 항의 합이 평균 수익과
  정확히 같다. `fixed(long=1, short=0)`이면 `short_use`는 `None`이고 선언된 gross는 1.
- `test_the_report_reads_the_record_back.py`: fixture가 `flexible(1, -1)`을 기록하고, `use`가 gross / 2, 분해가 맞고,
  headline의 `mean_use`가 절의 값이다. budget이 없는 0.16 모양의 기록은 `omitted["budget"]`으로 빠진다.
- `test_show.py`: `strategy.json`의 필드 집합에 `budget`.
- `uv run ruff check src/` 통과, `uv run pyright` 0 errors.
