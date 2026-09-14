# 282 — rows grain의 키는 세고 거절하지 않는다: 반복 · null은 영수증에, 읽기는 모든 필드로 순서를 정한다

| | |
|---|---|
| **작성 시각** | 2026-09-14 KST (+09:00) |
| **캠페인** | 등록 정리 (`redesign/registration-cleanup`), M3 — 계획 `.agent/plans/active/registration-cleanup-campaign.md` |
| **앞선 기록** | `281` |
| **계기** | 오너가 0.16.0 stepper를 읽다가: panel이라고 주장하지 않은 dataset이 키 중복으로 거절된다. 제안(2026-09-14) "grain이 panel 여부를 선언한다 — `rows`는 반복 · null을 세어 영수증에 적고, 읽기는 결정적인 순서로" — 오너 승인: "지금 브랜치에서 M3와 함께 고쳐" |
| **깨지는 변화** | 아니오. 거절이 줄었다: `rows`의 `dataset.key_duplicate` · `dataset.key_null`. panel grain은 그대로 거절한다 |

---

## 왜 이 변경이 있는가

`grain`은 이미 "이 표로 panel을 만들 수 있는가"를 선언한다. `instrument_instant`와 `instant`는 한 칸
(시각 × 종목, 또는 시각)에 값이 하나여야 panel이 되므로, 그 축의 반복이나 null은 결함이다. `rows`는
panel을 만들지 않는다고 선언한 벤더의 긴 표 — 종목 · 날짜마다 여러 행 — 인데, 등록은 여기서도 저자의
`key_fields`가 유일하기를 요구해 그런 표를 거절했다. 저자는 가짜 키 열을 만들거나 행을 버려야 했다.

## 무엇이 어떻게 바뀌었는가

- `data/verification.py::check_key`: panel grain은 그대로 증명한다(거절). `rows`는 같은 스캔
  (`scan.key_check`)으로 **세기만** 하고, `(Diagnosis, KeyCheck | None)`을 돌려준다.
- `DatasetRegistration.key_repeats` · `key_nulls`: `rows`의 잰 값. `verify_source`가 `with_key_counts`로
  붙인다. `compare=False`이고 장부에 저장하지 않는다 — 이 수에 기대는 읽기가 없고, 파일과 함께 움직인
  수가 같은 선언을 "바뀐 선언"으로 보이게 하면 안 되므로.
- `spoken()`: `rows`면 한 줄 더 — 몇 개 키 그룹이 한 행보다 많고 몇 개에 null이 있는지, 읽기는
  `available_at`, 키, 모든 필드 순으로 정렬한다는 것.
- `data/scan.py::_observation_query`: 행 단위 읽기의 `ORDER BY`에 노출 필드 전부를 키 뒤에 붙였다. 키가
  반복되면 두 행의 순서가 run마다 바뀔 수 있었다. panel grain은 키가 유일하므로 결과 순서가 같다.
- 문구: `Grain.ROWS` · `key_axis` docstring, grain 거절 문구(`workspace/registration.py`), `vqapr new
  dataset` 템플릿 주석, register-dataset skill의 `grain-and-cost.md`, architecture의 "grain은 선언이다".

## 대안과 선택

- 수를 장부에 저장(측정값 `span`처럼): 읽는 곳이 없고, merge의 "측정값만 바뀜" 규칙에 필드를 더해야
  한다. 등록 영수증에 한 번 말하는 것으로 충분하다.
- `rows` 읽기에서 중복 제거: 벤더 표의 각 행은 저마다 사실이다. 한 종목 · 날짜의 여러 행 중 무엇을
  뜻하는지는 연구 결정이고, 그 접기는 DataModel에 둔다(`grain-and-cost.md`).

## 검증

- `uv run python -m pytest tests/ -q`: 1772 passed, 1 failed. 실패는 실데이터 테스트
  `test_dev_dataset_rejects_a_weak_key` — 이 기록이 뒤집은 전제(rows의 약한 키는 거절)를 검사했다.
  `test_dev_dataset_counts_a_weak_rows_key`(반복 그룹 5000개 초과를 세고 등록)로 바꾼 뒤
  `tests/data/test_datasets.py` · `test_grain.py` · `tests/boundaries/test_public.py` 53 passed.
- 거절을 검사하던 rows 테스트 둘은 같은 파일을 panel grain으로 선언해 거절을 계속 검사하고,
  `test_a_rows_key_is_counted_not_refused`가 `rows`의 셈과 그 수가 동등 비교 밖에 있음을 검사한다.
- 거절 코드 기준표 변화 없음(characterization 통과 — 두 코드는 panel grain 경로에서 여전히 나온다).
- `uv run ruff check src/` 통과, `uv run python -m pyright` 오류 0.
