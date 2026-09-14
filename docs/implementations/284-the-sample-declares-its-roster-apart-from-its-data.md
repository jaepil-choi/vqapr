# 284 — 샘플은 명단을 데이터와 따로 선언한다: `instruments.yaml`과 `sample.yaml`

| | |
|---|---|
| **작성 시각** | 2026-09-14 KST (+09:00) |
| **캠페인** | 등록 정리 (`redesign/registration-cleanup`), M3c — 계획 `.agent/plans/active/registration-cleanup-campaign.md` |
| **앞선 기록** | `283` |
| **계기** | 오너가 stepper ①의 "종목 명단부터" 프레임을 보고 물었다: "instrument 선언 안하면 데이터 등록이 안돼? 데이터 등록 선언과 instrument 등록 선언은 별도여야 해." 코드는 이미 별도였다(데이터만 적은 YAML은 명단 없이 등록된다). 헷갈림은 `vqapr new sample`이 명단 · 데이터 · 부품 · run을 `sample.yaml` 한 장에 적었기 때문이다. 오너: "모두 고치고 develop에 merge 해" |
| **깨지는 변화** | 샘플의 모양만. `vqapr new sample`이 쓰는 `sample.yaml`에는 이제 `instruments:`가 없고, `instruments.yaml`을 먼저 등록해야 `check`가 통과한다. envelope의 `next`가 그 순서를 말한다. 패키지 API · 등록 규칙은 그대로 |

---

## 왜 이 변경이 있는가

샘플은 사용자가 처음 보는 선언이고, skill은 "`sample.yaml`을 복사해 첫 선언을 쓰라"고 권한다. 그 한 장에
명단이 데이터와 섞여 있으면, 데이터를 등록하려면 명단이 필요하다고 읽힌다 — 오너가 stepper에서 정확히 그렇게
읽었다. 규칙은 반대다. 데이터는 명단 없이 등록되고, 데이터의 종목이 모두 명단에 있을 필요도 없으며, 명단은 전략이
주문할 수 있는 종목만 정한다(명단 밖 주문은 run 전체 실패, 명단이 없으면 strategy run은 `check`에서 거절 —
오너 확인 2026-09-14).

## 무엇이 어떻게 바뀌었는가

- `agent/sample/materialize.py`: 두 문서를 쓴다. `instruments.yaml`(`roster_declaration`: 내보낸 명단 표를
  가리킨다)과 `sample.yaml`(`declaration`: dataset 둘 · 부품 둘 · run). `Materialized.roster`가 명단 선언의
  경로다. 샘플 README는 네 명령(명단 → 샘플 → check → run)과, 명단이 따로인 이유를 적는다.
- `cli/new.py::_sample`: envelope에 `instruments`를 더하고, `next`는 명단 등록부터 시작한다.
- 문서: introduce-vqapr skill과 그 `sample-journey.md`(명령 다섯, 명단 단계의 설명), 샘플 패키지 README,
  report-issue-dev의 재현 템플릿, architecture §14.1(등록 흐름: `read_declaration` → `apply` →
  `stage_measured`, 기록 280-281 반영 포함).
- 테스트: 샘플을 설치하는 여정(`tests/sample/journey.py`)과 샘플을 등록하는 CLI 테스트 셋이 명단을 먼저 등록한다.

## 대안과 선택

- 샘플은 한 장 그대로, 설명만 보강: 복사해 쓰라고 권하는 문서가 규칙과 반대 모양을 보이는 것이 문제의 뿌리다.
- 네 장(명단 · 데이터 · 부품 · run)으로 쪼개기: 오너의 규칙은 데이터와 명단의 분리다. 나머지를 쪼개면 명령만
  늘고 새로 알리는 것이 없다.

## 검증

- `uv run python -m pytest tests/ -q`: 1778 passed, 1 skipped.
- 새 `tests/cli/test_new_sample.py::test_the_roster_is_its_own_declaration`: `sample.yaml`에 `instruments`
  섹션이 없고, 그것만 등록하면 `check`가 `roster.absent` 하나로 거절하며, `instruments.yaml`을 등록한 뒤 통과한다.
- `test_new_sample_writes_a_registrable_journey_that_check_accepts`: envelope의 `instruments`와 `next`의 순서.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 오류 0. 샘플 여정 전체(`slow`)는 M5의 `test_all`에서.
