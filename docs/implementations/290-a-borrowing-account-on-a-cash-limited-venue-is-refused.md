# 290 — 매수를 현금으로 자르는 venue 위의 차입 계좌는 run 전에 거절된다: `weights.cash_conflict`

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 차입 계좌 (`redesign/borrowing-account`), M3 — 계획 `.agent/plans/active/borrowing-account-campaign.md` |
| **앞선 기록** | `289` |
| **계기** | `KrxExchange.execute`는 매수를 자기 purse(계좌 현금)로 자른다. 차입 계좌를 KRX에 두면 run은 에러 없이 돌고 레버리지는 한 번도 걸리지 않는다 — SIGNED 계좌를 long-only listing에 둔 조합(`weights.venue_conflict`)과 같은 모양의 모순이다. |
| **깨지는 변화** | 없음. 차입 계좌에만 묻는다. 거절 코드 하나가 늘었다. |

---

## 무엇이 어떻게 바뀌었는가

- `run/preflight/checks.py::_judge_weights`: 계좌가 `BORROWING`이고 venue의 `settings`가
  `partial_fills: cash-limited`를 선언하면 `weights.cash_conflict`(412, `runs.<id>.initial_account.cash_mode`).
  fix는 `FUNDED`로 두거나 현금 너머로 체결하는 venue(academic, 또는 `AcademicExchange` 하위 클래스)를 쓰라고 말한다.
- 판단 근거는 venue가 스스로 기록에 남기는 settings다. 클래스로 묻지 않는 이유: 경로로 불러온 builtin은 이
  패키지가 내보내는 클래스와 다른 클래스 객체라 `isinstance`가 거짓이 된다(`component/compliance/shipped.py`의
  같은 이유). 사용자가 쓴 venue도 같은 선언으로 같은 답을 받는다.
- `JUDGMENT_CODES`에 코드를 더했고, `tests/characterization/refusal_codes.baseline.json`을 그 파일의 유일한
  writer(`regenerate`)로 다시 썼다 — diff는 새 코드 두 줄이다.

## 대안과 선택

- KRX가 차입 계좌에서 현금을 넘겨 체결하게 하기: KRX profile의 사실성 주장은 "현금으로 제한된 부분 체결"이고,
  신용 거래는 따로 모델링해야 한다(대출 한도 · 이자 · 반대매매). 모델링하지 않은 것을 켜지 않는다.
- run 도중에 알리기: 모순은 두 선언 사이에 있고 run 전에 답할 수 있다. 판단은 `check`와 `run`이 같은 문을 지난다.

## 검증

- 새 `tests/cli/test_check.py::test_a_borrowing_account_on_a_cash_limited_venue_is_refused`: KRX 위의 차입
  long-only 계좌는 `weights.cash_conflict` 하나(source `runs.x.initial_account.cash_mode`), academic 위의 같은
  계좌는 거절 없음.
- `uv run python -m pytest tests/cli/test_check.py tests/characterization -q`: 128 passed, 1 skipped.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
