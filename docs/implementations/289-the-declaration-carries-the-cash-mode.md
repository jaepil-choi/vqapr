# 289 — 선언이 `cash_mode`를 계좌까지 나른다: `initial_account.cash_mode: BORROWING`

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 차입 계좌 (`redesign/borrowing-account`), M2 — 계획 `.agent/plans/active/borrowing-account-campaign.md` |
| **앞선 기록** | `288` |
| **계기** | `288`이 계좌와 주문 계획에 `CashMode`를 두었다. run이 그것을 선언할 길이 필요하다. |
| **깨지는 변화** | 없음. `FUNDED`는 어디에도 쓰지 않는다: 선언의 저장 모양 · run identity · `run.json`이 전과 바이트 단위로 같다. |

---

## 왜 이 변경이 있는가

차입은 run의 선언이다(오너: 켜는 사람만). 계좌 모드처럼 run 시작에 얼고 도중에 바뀌지 않으며, 차입 run과
funded run은 다른 run이다. 그래서 `mode`가 지나는 길을 그대로 지난다: 선언 → `RunDefinition` → `FrozenRun`
(identity) → `Account` → `run.json`.

## 무엇이 어떻게 바뀌었는가

- `workspace/run_definition.py`: `_InitialAccount.cash_mode`(이름으로 읽고 쓴다, `BORROWING`), 없으면
  `FUNDED`이고 `FUNDED`이면 쓰지 않는다. `RunDefinition.initial_account_cash_mode`. 초기 계좌 없이 차입을
  선언하면 거절한다.
- `workspace/registration.py`: `cash_mode` 오타는 `mode`처럼 허용 목록 전체와 가장 가까운 값을 말하며
  거절한다(`declaration.value_not_permitted`).
- `run/preflight/frozen.py`: `FrozenRun.initial_account_cash_mode`. identity는 차입일 때만 그것을 접는다 —
  funded run의 identity는 그대로다. `freeze.py`가 넘기고, `assemble.py`가 `Account(cash_mode=)`로 만들고,
  `loop.py`가 계좌의 cash mode가 frozen run과 같은지 확인한다(mode 확인 옆).
- `run/recording.py`: `run.json`의 `initial_account`에 차입일 때만 `"cash_mode": "borrowing"`.
- `public.py`: `CashMode`를 내보낸다. `vqapr new run` 템플릿이 주석으로 `cash_mode`를 보인다(값 목록은 enum에서
  만든다, `_CASH_MODES`) — 이자가 없다는 것과 KRX가 매수를 현금으로 자른다는 것도 거기서 말한다.

## 대안과 선택

- identity와 `run.json`에 항상 `cash_mode`를 쓰기: 명시적이지만 모든 funded run의 identity와 기록 digest가
  바뀌어, 깨지는 변화 없이 출시할 수 없다. 기본값을 쓰지 않는 규칙 하나로 세 곳(저장 모양 · identity · 기록)이
  같은 답을 낸다.
- 불리언 `borrowing: true`: 두 번째 closed set을 `mode`와 같은 방식(이름, 목록 거절, 템플릿 파생)으로 두면
  한도 있는 차입 같은 다음 멤버가 들어갈 자리가 있다.

## 검증

- 새 `tests/run/test_a_borrowing_account_leverages.py`(subprocess로 등록 → freeze → run, academic, 두 종목 ×
  3 세션): 같은 `Rebalance.signed({...}, gross=2)`를 차입 계좌는 10,000 × 100 + 20,000 × 50 = NAV의 2배로
  사고 현금 −1,000,000으로 끝난다; funded 계좌는 현금만큼만 산다; funded run의 저장 모양 · `run.json`에
  `cash_mode`가 없고 identity가 차입 필드 없이 계산한 것과 같다; 차입 run은 셋 모두에 차입을 말하고 다시 읽힌다.
- `tests/cli/test_a_closed_set_refusal_names_the_set.py`: `cash_mode: LEVERAGED`가 `funded, borrowing`을
  말하며 거절된다. `tests/cli/test_the_template_offers_modes_that_exist.py`: 템플릿이 cash mode를 enum에서 보인다.
- `tests/workspace/test_run_definition.py`의 필드 목록과 `tests/boundaries/test_public.py`의 export 목록에 새 이름.
- `uv run python -m pytest tests/cli tests/boundaries tests/run tests/workspace tests/domain -q`: 651 passed.
  `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
