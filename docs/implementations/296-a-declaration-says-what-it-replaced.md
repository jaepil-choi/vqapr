# 296 — 선언으로 다시 등록해도 교체한 fingerprint를 말한다: 교체는 병합이 답한다

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 보고서 절과 등록 창구 (`redesign/sections-and-one-register`), M1 — 설계 `docs/design/2026-09-15-sections-and-one-register.md`, 계획 `.agent/plans/active/sections-and-one-register-campaign.md` |
| **앞선 기록** | `290`. `291`–`295`는 같은 날의 다른 캠페인(`redesign/strategy-budget`) 몫이다 |
| **계기** | `docs/issues/report-2026-09-15-yaml-re-register-of-a-changed-strategy-omits-the-replaced-fingerprint.md` — 선언 YAML로 편집한 전략을 다시 등록하면 fingerprint가 조용히 바뀌고, `replaced`는 세 인자 형식만 말했다 |
| **깨지는 변화** | 없음. 선언 형식의 응답에 `replaced`가 교체가 있을 때만 붙는다. 내부 API `Transaction.register_component`의 반환이 `bool`에서 교체한 `ComponentRef \| None`으로 바뀌었다(반환값을 읽던 곳은 테스트 하나) |

---

## 무엇이 어떻게 바뀌었는가

컴포넌트를 등록하는 길은 둘인데 옛 항목을 아는 곳은 병합 하나다. 세 인자 형식은 그 옆에서 같은 사실을 따로
읽어 `replaced`를 말했고, 선언 형식은 읽지 않았다. 이제 병합의 스테이징이 답하고 두 길이 그 답을 싣는다.

- `workspace/registry.py::Transaction.register_component`: 스테이징된 상태에서 그 id가 가졌던 참조를 읽고,
  fingerprint가 바뀌었으면 그 참조를, 새 id이거나 바이트가 같으면 `None`을 돌려준다.
- `workspace/registration.py::apply`: 컴포넌트마다 그 답을 `Registered.replaced[<id>] = {"fingerprint": <옛것>}`로
  모은다. `cli/register.py`는 비어 있지 않을 때만 `replaced`를 싣는다.
- `register_authored`: 따로 하던 `Workspace.create(...).components` 조회를 버리고 같은 답을 쓴다. 응답 모양
  (`replaced: {fingerprint}`)은 그대로다.
- exchange처럼 세 인자 형식이 없는 종류도 선언 형식으로 같은 답을 받는다.
- skill `register-dataset/references/correcting-a-registration.md`가 두 형식을 같이 말한다.

## 대안과 선택

- 선언 경로에서도 따로 조회하기: 문이 둘로 남고, 같은 사실을 세 번째로 읽는다.
- 선언 응답을 `replaced: {fingerprint}` 하나로: 한 문서가 여러 컴포넌트를 싣기 때문에 id별 매핑으로 했다.
- 데이터셋 재측정의 옛 digest를 같이 말하기: 이 보고의 범위 밖이다(설계 §4). 같은 문에 나중에 더할 수 있다.

## 검증

- 새 `tests/cli/test_a_declaration_says_what_it_replaced.py`(2): 선언으로 첫 등록하거나 같은 바이트를 다시
  등록하면 `replaced`가 없고, 편집 뒤에는 `{"cap20": {"fingerprint": <옛것>}}`이다. 두 형식을 섞어 써도 각자
  상대가 남긴 fingerprint를 말한다.
- 옛 `bool` 반환을 단언하던 네 곳을 새 답으로 고쳤다: 새 id와 같은 바이트는 `None`
  (`tests/test_workspace.py`, `tests/test_two_sections_carry_no_information.py`,
  `tests/test_workspace_remove_and_force.py`), 편집은 교체된 옛 참조.
- 등록 · skill · agent surface · workspace · boundaries 묶음: 180 passed. fast set
  (`uv run python -m pytest tests/ -q`): 1786 passed, 3 failed — 그 셋이 위의 `bool` 단언이었고, 고친 뒤 통과.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
