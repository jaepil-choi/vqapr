# 288 — 차입 계좌는 현금이 0 밑으로 갈 수 있다: `CashMode`와 그것을 읽는 주문 계획

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 차입 계좌 (`redesign/borrowing-account`), M1 — 계획 `.agent/plans/active/borrowing-account-campaign.md` |
| **앞선 기록** | `287` |
| **계기** | 오너: "academic exchange 에서 할 때는 매수 비중이 100%를 넘어서 레버리지 롱을 할 수도 있거든? 이걸 허용하려면 어떻게 해야 하지?" 한도는 전략의 `Budget`이 정하고(오너 선택), 켜는 run에만 적용한다. |
| **깨지는 변화** | 없음. 기본값 `FUNDED`는 지금과 같다. 현금 음수 거절문에 "in a funded account"가 붙고, NAV ≤ 0 거절문이 바뀌었다. |

---

## 왜 이 변경이 있는가

현금 음수는 세 곳에서 막혀 있었다. 전략의 `Rebalance.signed(..., gross=2)`은 현금 비중 −1을 이미 통과시켰지만,
주문 계획이 매수를 현금 안으로 깎았고(`_apply_venue_rules` · `_settle_payable`), 계좌가 음수 현금을 거절했다
(`Account.append`). 계좌만 풀면 주문 계획이 여전히 깎아서 에러 없이 레버리지가 조용히 안 걸린다. 그래서 둘이
같은 사실 하나를 읽어야 한다.

architecture §9.4는 `현금 >= 0`을 모든 모드의 불변식으로 두었다("비용 없는 차입은 공짜 돈 버튼"). 오너는 대안
(차입 금리로 오르는 금융 자산을 숏, §16-1)을 본 뒤 음수 현금을 켜는 쪽을 골랐다. 그래서 켜는 run에만 적용하고,
이자가 없다는 것을 기록과 문서에 적는다(M2 · M4).

## 무엇이 어떻게 바뀌었는가

- `domain/account.py`: `CashMode {FUNDED, BORROWING}`. `AccountMode`(보유가 음수일 수 있나) 옆의 두 번째
  사실(현금이 음수일 수 있나)이다. 두 사실은 따로 움직인다 — 레버리지 롱은 빌리고 숏하지 않으며, 달러 중립은
  숏하고 빌리지 않는다 — 그래서 enum 하나로 합치면 짝마다 멤버가 필요하다. `Account(mode=, cash_mode=FUNDED)`,
  `append`는 funded 계좌에서만 음수 현금을 거절한다. 선언된 시작 스냅샷은 여전히 현금 ≥ 0이다(가진 돈으로
  시작한다). 체결 뒤 스냅샷은 `trusted`로 만들어져 다시 검증되지 않는다.
- `domain/order.py`: `plan_orders(..., cash_mode=)`. 차입 계좌면 `_apply_venue_rules`가 단위 반올림만 하고 현금
  맞춤(clip · settle)을 건너뛴다. NAV ≤ 0이면 "the book is worth X at this instant ... no margin call is
  modelled"로 멈춘다(전에는 `execution_time_nav must be positive`).
- `run/engine/stages/execute.py`: 주문 계획에 계좌의 `cash_mode`를 넘긴다. 사실은 계좌 하나에 있고 주문
  계획은 그것을 읽는다.

## 대안과 선택

- 계좌에 금액 한도 / NAV 비율 한도: 금액은 NAV가 커지면 실효 레버리지가 조용히 준다. 비율은 계좌가 체결
  시점 가격을 알아야 한다. `Budget.cash_lower`가 이미 NAV 기준 한도다(오너 선택).
- `AccountMode`에 멤버 추가(`LONG_ONLY_BORROWING` 등): 두 축을 한 enum에 접으면 짝마다 멤버가 는다.
- 제한을 모두에게 제거: 비용 있는 venue에서 100% 투자한 run은 지금 매수를 깎아 현금 ≥ 0을 지킨다. 없애면
  그 run들의 숫자가 바뀐다.

## 검증

- `uv run python -m pytest tests/domain tests/run tests/component -q`: 534 passed.
- 새 테스트(`tests/domain/test_planning.py`): funded는 150 매수를 거절하고 borrowing은 현금 −50 · NAV 100으로
  받는다(long-only 차입 계좌는 여전히 숏을 거절); 2배 롱 목표를 borrowing은 전부, funded는 현금만큼만 계획한다;
  NAV −5는 이유를 말하며 멈춘다.
- `uv run python -m pyright` 바뀐 세 파일 오류 0, `uv run ruff check src/` 통과.
