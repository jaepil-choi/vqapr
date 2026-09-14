# 281 — dataset은 문 하나로 들어온다: `stage_measured`, 그리고 source 불일치는 규칙 하나 · status 하나

| | |
|---|---|
| **작성 시각** | 2026-09-14 KST (+09:00) |
| **캠페인** | 등록 정리 (`redesign/registration-cleanup`), M2 — 계획 `.agent/plans/active/registration-cleanup-campaign.md` |
| **앞선 기록** | `280` |
| **깨지는 변화** | 아니오. `dataset.source_mismatch`가 `Transaction.register_dataset` 경로에서 409 대신 400으로 나간다 |

---

## 왜 이 변경이 있는가

2026-09-13 등록 흐름을 따라가며 두 가지 겹침이 보였다.

1. **"재고 담기" 세 줄이 세 곳에 있었다.** `verify_source` → `raise_if_failed` → `transaction.register_dataset(measured, …)`.
   `workspace/registration.py::register_dataset`(Python 표면), 선언의 `datasets:` 섹션, `run/engine/output.py::RunOutput.register`
   (run이 낸 출력)가 각자 썼다. 네 번째 호출자가 측정하지 않은 카드를 담는 것을 막을 문이 없었다.
2. **같은 규칙이 두 곳에서 다른 status로 나갔다.** "등록 카드와 파일 위치가 서로 다른 source를 가리킨다"를
   `data/verification.py::verify_source`는 400(`INVALID`)으로, `workspace/merge.py::_merge_dataset`은 409(`CONFLICT`)로 거절했다.
   두 코드는 같았다(`dataset.source_mismatch`). 이것은 건넨 쌍이 스스로 어긋난 것(400)이지, 장부에 이미 있는 것과의
   충돌(409)이 아니다.

## 무엇이 어떻게 바뀌었는가

- `workspace/registration.py::stage_measured(transaction, registration, source) -> (measured, changed)`: 검수대에서 재고,
  실패면 raise하고, **잰 카드**를 담는다. 세 호출자가 모두 이것을 부른다.
- `data/verification.py::mismatched_source(registration, spec) -> Failure | None`: 규칙 하나. `verify_source`와
  `_merge_dataset`이 모두 이것을 묻는다. merge는 그 `Failure`를 담아 raise한다(status 400).
- `run/engine/output.py`는 `verify_source`를 직접 import하지 않는다.
- 거절 코드 기준표(`tests/characterization/refusal_codes.baseline.json`)를 의도적으로 다시 썼다: 409 칸에서
  `dataset.source_mismatch`가 빠졌다(400 칸에는 원래 있었다). 다른 변화 없음.

`RunOutput.register`는 이제 트랜잭션을 연 뒤에 잰다. 트랜잭션은 commit 때 잠금 안에서 장부를 다시 읽으므로
순서가 결과를 바꾸지 않고, 검수가 실패하면 `with`가 commit하지 않는다.

## 검증

- `uv run python -m pytest tests/ -q`: 1772 passed, 1 skipped, 29 deselected (269.6 s).
- `uv run ruff check src/`: 통과. `uv run python -m pyright`: 오류 0.
- `python -m tests.characterization.refusal_codes`: 기준표 diff는 한 줄(409의 `dataset.source_mismatch` 삭제).
