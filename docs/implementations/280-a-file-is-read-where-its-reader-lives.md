# 280 — 파일은 그 파일을 읽는 층에서 읽는다: 선언 읽기는 workspace로, 덮어쓰기 거절은 cli로, apply는 하나로

| | |
|---|---|
| **작성 시각** | 2026-09-14 KST (+09:00) |
| **캠페인** | 등록 정리 (`redesign/registration-cleanup`), M1 — 계획 `.agent/plans/active/registration-cleanup-campaign.md` |
| **계기** | 오너가 0.16.0 scenario stepper를 읽다가 물었다(2026-09-14): "pyyaml을 쓰는 게 맞아? 이게 왜 domain/errors.py에 들어가 있는지도 모르겠어", "registration에서는 왜 apply와 _apply가 나뉘는거야?" |
| **깨지는 변화** | 아니오. 공개 표면(`vqapr.public`)에는 두 이름 모두 없었다 |

---

## 왜 이 변경이 있는가

`domain/`은 고리가 주고받는 값과 규칙의 층이고, 파일을 열지 않는 층이다(`tests/boundaries/test_the_layers_hold.py`의
layer 0). 그런데 `domain/errors.py`에 파일 입출력 함수 둘이 있었다.

- `read_yaml_mapping(path, what=...)`: 선언 YAML을 PyYAML(YAML 1.2 불리언으로 좁힌 `SafeLoader`)로 읽는다. 부르는
  곳은 `cli/register.py` 하나이고 `what`은 늘 `"a declaration"`이었다.
- `refuse_existing(path, what=...)`: 경로가 있으면 덮어쓰지 않고 거절한다. 부르는 곳은 `cli/new.py` 하나다.

둘 다 거절 양식(`InputError`)을 쓰기 때문에 errors 옆에 붙었을 뿐, 하는 일은 파일을 여는 것이다.

`workspace/registration.py`의 `apply` / `_apply`는 둘로 나뉠 이유가 하나뿐이었다. `apply`가 "지금 읽는 선언 파일"을
`ContextVar`에 넣었다가 되돌리고, 일은 `_apply`가 했다. 함수 둘은 읽는 사람에게 "두 가지 일"로 보인다.

## 무엇이 어떻게 바뀌었는가

| 전 | 후 |
|---|---|
| `domain/errors.py::read_yaml_mapping(path, what=...)` + `_DeclarationLoader` | `workspace/registration.py::read_declaration(path)` + `_DeclarationLoader` |
| `domain/errors.py::refuse_existing` | `cli/new.py::refuse_existing` |
| `domain/errors.py`가 `yaml`, `re`를 import | import하지 않는다 |
| `apply`(ContextVar 설정) → `_apply`(일) | `apply` 하나. 설정은 `with _reading(declaration):` |

거절의 모양(code · status · requirement · fix)은 한 글자도 바뀌지 않았다. `cli/register.py`는 `workspace.registration`
에서 `apply`와 `read_declaration`을 함께 가져온다 — CLI가 읽어도 되는 층(`test_the_cli_reads_through_the_surfaces.py`)이다.

## 대안과 선택

- `read_declaration`을 `workspace/declarations.py`에 두기: 그 파일의 docstring이 "Nothing here opens a file"을
  약속한다. 선언의 모양(pydantic 모델)과 선언 파일 읽기는 다른 일이라 `registration.py`(선언 문서를 등록으로 바꾸는
  곳)에 두었다.
- `refuse_existing`을 `cli/envelope.py`에 두기: 부르는 곳이 `new` 하나라 공용 자리에 둘 이유가 없다.

## 검증

- `uv run python -m pytest tests/ -q`: 1772 passed, 1 skipped, 29 deselected (354.8 s).
- `uv run ruff check src/`: 통과. `uv run python -m pyright`: 오류 0.
- `tests/cli/test_an_unquoted_on_is_a_key.py`가 새 이름(`read_declaration`)으로 YAML 1.2 불리언을 계속 검증한다.
