# 291 — budget은 전략 클래스에 한 번 선언된다: `Budget.fixed` · `Budget.flexible`, 결정은 weight만

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | strategy budget (`redesign/strategy-budget`, worktree), M1 — 설계 `docs/design/strategy-budget.md`, 계획 `.agent/plans/active/strategy-budget.md` |
| **앞선 기록** | `290` (develop의 borrowing 캠페인이 288-290을 먼저 썼다) |
| **계기** | 오너의 질문(2026-09-15): "전략 budget은 어떻게 설정하게 되지? … 지금 이런걸 설정하고 전략을 짜나? 아니면 그냥 어떤 기본값이 있나?" 이어서 flexible budget의 비교 문제: "long 0.5만 쓰고 short 0.3만 쓰는 경우도 가능하다고 열어놓는다면, 이걸 어떻게 long short 1, -1 을 다 쓰는 전략과 비교할 수 있지?" 오너 판정: 비교는 리포트가 한다; 선언은 클래스에 한 번; 기본값은 fixed 1, -1; flexible 인자는 `long_limit`/`short_limit`; short는 음수; 생성자는 문 하나(1안); fixed long 0.5 / short -0.5도 된다(long-only 1과 gross를 맞추는 방법) |
| **깨지는 변화** | 예 — 0.17.0. `Rebalance.of` · `Rebalance.signed` · `Rebalance(target_weights=, cash_weight=, budget=)` · `PortfolioDirection` · 옛 다섯 경계의 `Budget` 삭제. `budget()`을 선언하지 않은 전략은 dollar neutral `fixed(1, -1)`로 검사되므로 long-only 전략은 선언해야 한다. 전략의 identity가 budget을 접는다 |

---

## 왜 이 변경이 있는가

budget이 결정마다 붙어 있었다. `Rebalance`가 `budget=`을 싣고, 그 값이 intent를 타고 `validate_economic_intent`와
`plan_orders`에서 두 번 더 검사됐다. 세 가지가 잘못이었다.

- **전략이 자기 한도를 매일 바꿀 수 있었다.** 스스로 바꿀 수 있는 한도는 한도가 아니다.
- **run 기록에 남지 않았다.** `strategy.json`에도 weight 표에도 budget이 없어서, 리포트는 성과를 무엇에 대해 재야
  하는지 몰랐다. long 0.5 / short -0.3을 쓴 전략과 1 / -1을 다 쓴 전략을 비교할 분모가 없었다.
- **표현할 수 없는 조건이 있었다.** 옛 `Budget`은 cash 범위와 종목별 범위였다. cash는 net만 말하므로 long 0.3 /
  short -0.3도 "dollar neutral"을 통과했고, "long 합 = 1, short 합 = -1"은 선언할 수 없었다. `Rebalance.of`는
  `invested`를 양쪽에 반씩 나눠 0.5 / -0.5가 한계였고, `signed`는 `gross`를 따로 말했다. 크기를 적는 곳이 둘이었다.

비유: 펀드의 운용 한도는 매매표마다 적지 않고 약관에 한 번 적는다. 매매는 약관 안에서 하고, 성과는 약관 기준으로 잰다.

## 무엇이 어떻게 바뀌었는가

- **`portfolio/budget.py`(새 모듈)** — `Budget(kind, long, short)`.
  - `Budget.fixed(long=1, short=-1)`: 각 side 합이 정확히 그 값. `Budget.flexible(long_limit=1, short_limit=-1)`: long은
    0부터 한도까지, short는 한도부터 0까지. short는 음수로 쓰고, `short=0`이 long-only다. 값은 canonical grid(1e-12)
    위여야 하고, 음수 long · 양수 short · 두 쪽 모두 0은 거절된다.
  - `check(weights)`: side 합과 선언을 이름으로 대며 `BudgetRefusal`(ValueError)로 거절한다. 자르지도, 채우지도 않는다.
  - `fill(signal, use=1)`: 부호 있는 신호의 각 side를 선언된 크기로 `rescale(..., grid=QUANTUM)`한다. side 안의 비율이
    상대 확신도이고, 0은 0으로 남는다. `use`(0 < use ≤ 1)는 flexible에서만 받는다. fixed에서 신호에 채울 side가 없으면
    "Hold를 반환하거나 flexible을 선언하라"로 거절한다.
  - `encoded()`: 생성자의 철자 그대로(`{"kind": "fixed", "long": "1", "short": "-1"}`). `1.0`과 `1`은 같게 접힌다.
  - 왜 `domain`이 아니라 `portfolio`인가: `fill`이 `rescale`을 쓰는데 `domain`(층 0)은 `portfolio`(층 10)를 import할 수
    없다. 그래서 intent가 budget을 싣던 것도 함께 끊었다.
- **`StrategyModel.budget()`** — `inputs()` 옆의 선언 메서드. 기본값 `DEFAULT_BUDGET = Budget.fixed(long=1, short=-1)`.
- **등록** — `component/conformance.py::_check_budget`: `budget()`을 한 번 불러 `Budget`이 아니거나 예외면
  `component.budget_invalid`로 거절한다. 인자가 없어 run 전에 값을 판정할 수 있는, 이 suite가 반환값을 보는 유일한 곳이다.
- **freeze** — `FrozenStrategy.budget`, identity가 `budget.encoded()`를 접는다. freeze도 타입을 한 번 더 본다
  (등록 뒤 파일이 고쳐졌을 수 있다).
- **decide 단계** — `stages/decide.py`: intent를 찍기 직전 `layer.budget.check(result.target_weights)`. 위반은
  작성자의 계약 위반 `rebalance.outside_budget`(422, `strategies.<id>`와 전략 파일)이다. `Budget.check`가 패키지
  안에서 raise하므로 그대로 두면 envelope이 맨 안쪽 프레임을 보고 프레임워크 crash(500)로 불렀다(`_outside_budget`). 검사가 셋에서
  하나가 됐다: `EconomicPortfolioIntent.budget`, `validate_economic_intent`의 budget 검사, `plan_orders(budget=)`,
  `AccountCommitEvidence.planning_budget` 삭제. `plan_orders`는 `sum + cash == 1`만 본다.
- **`Rebalance(weights)`** — 위치 인자 하나. `cash_weight`는 `1 - sum(weights)` property. 옛 키워드는 새 철자를
  말하는 `TypeError`. `_relative_side` · `_offenders` 삭제. `_as_decimal`은 numpy 스칼라도 받는다(`numbers.Real`).
- **공개 표면** — `vq.Budget`과 `vq.BudgetRefusal`이 `vqapr.portfolio.budget`에서 온다. `PortfolioDirection` 삭제.
- **샘플 · scaffold** — 둘 다 `Budget.flexible(long_limit=1, short_limit=0)`을 선언하고
  `Rebalance(self.budget().fill(..., use=...))`를 돌려준다. 샘플은 이제 `vqapr.public`만 import한다 —
  `report-2026-09-14-sample-strategy-imports-from-private-vqapr-domain-intent`를 닫는다.
- **`vqapr show model`** — `budget` 키.
- **docstring** — `bounds`(`Rebalance(optimize(...).weights)`), `optimize`의 `cash_range`.

## 대안과 선택

- **Compliance에 두기**: Compliance는 체결 뒤의 book을 보는 관측자라 결정을 막지 못한다. 한도는 전략 자신의 약속이라
  결정하는 순간에 본다.
- **`of`/`signed` 유지(2안)**: `invested`/`gross`가 선언과 어긋나면 거절이 생기고, 크기를 적는 곳이 둘로 남는다. 오너가 1안.
- **옛 cash 범위 유지**: net만 말하므로 side 크기를 강제하지 못한다.
- **`short_max` · `short_cap`**: max는 음수와 만나면 부등호가 뒤집혀 읽히고, cap은 `single_name_cap`에서 0 이상의 크기다.
  `_limit`(오너).
- **엔진이 잘라내거나 채우기**: 전략이 쓰지 않은 book이 돈다. 거절한다.
- **fixed에서 빈 날**: 거절. 그런 날이 있는 전략은 flexible을 선언하거나 `Hold`를 돌려준다.

## 검증

- `uv run python -m pytest tests/ -q`: 1780 passed, 6 skipped.
- `uv run python -m pytest tests/ -q -m "" -k "not show_004"`: 1808 passed, 6 skipped. show_004는 이 worktree에
  `data/DW`가 없어 전략 코드보다 먼저 `FileNotFoundError`로 멈추므로 뺐다 — 데이터가 있는 checkout에서 M4에 돈다.
  show_003은 늘 그렇듯 수동 게이트.
- `uv run ruff check src/` 통과, `uv run pyright` 0 errors.
- 새 `tests/portfolio/test_the_budget_is_declared_once.py`(31): 기본값, `fixed(0.5, -0.5)`, 선언 거절, `check`의
  문장, flexible, long-only, `fill`의 비율 · 격자 · 0, `use`, 채울 side가 없는 신호, `encoded`, identity가 budget을
  접는다, `Rebalance`의 cash와 옛 키워드, 등록의 `component.budget_invalid`, 그리고 끝에서 끝: budget을 선언하지
  않은 long-only 전략의 run이 첫 결정에서 `rebalance.outside_budget`(422)로 멈추고 기록을 남기지 않는다.
- 지운 test 둘(`invested`의 천장, `signed`의 비율)은 주제가 사라졌다. 남은 불변식(각 side가 정확히 target, 격자
  아래의 side 거절, 0 유지, cash = `1 - sum`)은 새 파일로 옮겼다. `test_planning`의 "`plan_orders`가 budget의
  방향 · 경계를 거절한다"도 지웠다 — 그 거절은 decide 단계로 옮겼다.
- 거절 코드 baseline(`python -m tests.characterization.refusal_codes`): `component.budget_invalid`(runtime),
  `rebalance.outside_budget`(static, 422).
- showcase 여덟: 신호와 크기는 그대로다. `fill`의 격자 때문에 show005-alpha와 show006/008 member의 weight가 1e-12
  이하로 달라지고, 전략의 identity가 budget을 접으므로 digest baseline의 일곱 run이 달라진다 — M4에서 다시 기록.
  show009는 "`fill`과 손으로 만든 book이 같은 book"을 보이고, 둘이 다르면 `main()`이 raise한다.
