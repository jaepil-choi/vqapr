# 283 — 명단 거절은 있는 길을 가리키고, `check`는 한 번만 말하고, `--out`은 스크립트를 가리킨다

| | |
|---|---|
| **작성 시각** | 2026-09-14 KST (+09:00) |
| **캠페인** | 등록 정리 (`redesign/registration-cleanup`), M3b — 계획 `.agent/plans/active/registration-cleanup-campaign.md` |
| **앞선 기록** | `282` |
| **계기** | 오너가 stepper의 "종목 명단부터" 프레임을 묻고, 명단 규칙을 확인했다(명단 밖 주문은 run 전체 실패, 명단 0개면 strategy run은 못 돈다 — 둘 다 이미 그대로였다). 그 실측에서 세 결함이 나왔고, 오너: "지금 브랜치에서 M3와 함께 고쳐. 모두 고치고 develop에 merge 해" |
| **깨지는 변화** | 아니오. `vqapr new <kind> --out X.yaml`(또는 `.yml`)은 이제 400으로 거절된다 — 전에는 성공했지만 스크립트가 사라져 있었다 |

---

## 왜 이 변경이 있는가

1. **거절이 없는 길을 가리켰다.** `roster.absent`의 `fix`는 "`vqapr new instruments <ids...>`가 표와 선언을
   쓴다"고 했다. 그 명령은 id를 `--instruments`로 받고, 표를 내보내는 **스크립트**(`instruments.py`)와 선언을
   쓴다. 표는 스크립트를 실행해야 생긴다.
2. **`--out`이 YAML 이름이면 선언이 스크립트를 덮어썼다.** 스크립트와 선언을 함께 쓰는 kind는 선언을
   `target.with_suffix(".yaml")`에 쓴다. `vqapr new instruments --out instruments.yaml`은 두 경로를 하나로
   만들어, 스크립트 없이 선언만 남았다 — 선언은 영영 생기지 않을 표를 가리킨다. develop `58a398a9`의 skill
   문구가 바로 이 형태를 권했다.
3. **`check`가 `roster.absent`를 두 번 보였다.** 한 번은 `roster` 판정, 한 번은 얼리기의
   `require_declared_roster`. record `171`이 "한 사실, 두 문"으로 둔 것인데, record `240` 이후 모든 문(check ·
   run · Python `freeze` · `--jobs` 작업자)이 얼리기 전에 판정하므로 두 번째는 같은 말의 반복이다.

## 무엇이 어떻게 바뀌었는가

- `run/preflight/checks.py::absent_roster_failure`의 `fix`: `vqapr new instruments --instruments <ids...>`가
  instruments.py(실행하면 표를 내보낸다)와 instruments.yaml을 쓰고 `vqapr register instruments.yaml` — 또는
  Python에서 `vqapr.public.register_instruments(project_root, {id: kind})` 한 번.
- `run/preflight/freeze.py`는 명단이 있는지 묻지 않는다. 부르는 곳이 없어진 `require_declared_roster`는
  지웠다. `check`는 `roster.absent`를 한 번 말하고, `run`은 여전히 판정의 거절로 멈춘다.
- `cli/new.py::_script_target`: 스크립트와 선언을 함께 쓰는 kind(strategy · datamodel · compliance ·
  exchange · instruments)의 `--out`이 `.yaml`/`.yml`이면 400 `argument.value_invalid`, 고칠 이름
  (`<name>.py`)을 말한다. 그 밖의 이름은 그대로 스크립트의 이름이다.
- skill: run-backtest의 0단계와 `references/run-declaration.md`의 `--out instruments.yaml`을
  `--instruments <ids...>`로 고쳤다.

## 대안과 선택

- `check`에서 `(code, observed)`가 같은 실패를 한 번만 보이기: 두 번 묻는 구조가 남는다. 묻는 곳을 하나로 했다.
- `--out`은 `.py`만: 첫 시도였고, 테스트들이 쓰는 `x.out` 같은 이름까지 막았다(아래 검증). 결함은 YAML
  이름뿐이라 그것만 거절한다.
- YAML `--out`을 선언 경로로 읽고 스크립트를 `.py`로 옮기기: 추측이다. 거절하고 고칠 이름을 말한다.

## 검증

- `uv run python -m pytest tests/ -q`: 9 failed, 1768 passed — `.py`만 받던 첫 규칙이 `--out <kind>.out`을
  쓰는 테스트 아홉을 막았다. YAML 이름만 거절하도록 좁힌 뒤, 그 두 모듈과 새 테스트 · 명단 테스트 · `check` ·
  preflight 테스트 73 passed.
- `tests/cli/test_commands.py`: `check`의 `roster.absent`가 한 번.
- 새 `tests/cli/test_new_out_names_the_script.py`: instruments · exchange · compliance에 `--out written.yaml`
  → 400, 아무 파일도 쓰지 않음, fix는 `--out written.py`; `--instruments A B --out roster.py` → 스크립트에 A와 B.
- `tests/run/test_an_order_names_a_declared_instrument.py`: 거절의 fix가 `--instruments`와
  `register_instruments`를 말한다.
- 거절 코드 기준표 변화 없음. `uv run ruff check src/` 통과, `uv run python -m pyright` 오류 0.
