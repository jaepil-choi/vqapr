# 298 — 기록이 그것을 쓴 vqapr를 말한다: `package_version`, `vqapr.__version__`, `vqapr --version`

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 보고서 절과 등록 창구 (`redesign/sections-and-one-register`), M3 — 설계 `docs/design/2026-09-15-sections-and-one-register.md` §3 |
| **앞선 기록** | `297` |
| **계기** | `docs/issues/report-2026-09-15-no-record-or-public-surface-names-the-vqapr-version-that-wrote-a-run.md` — `vqapr.__version__`이 없고, `vqapr --version`은 usage 거절(400)이고, 어느 record도 버전을 말하지 않아 0.16.0과 0.16.1이 쓴 같은 전략의 기록을 가를 수 없었다 |
| **깨지는 변화** | 없음. `strategy.json`과 `datamodel.json`에 키 하나가 늘었다. 이전 기록에는 없고, 읽는 쪽은 `None`으로 본다. run identity와 showcase digest는 그대로다 |

---

## 무엇이 어떻게 바뀌었는가

- `vqapr/_internal/version.py::package_version()`: 버전의 답이 한 곳에 있다. 원래 `agent/skillset.py`에 있었는데,
  record에 도장을 찍는 run 층은 agent 층을 import할 수 없다. 표준 라이브러리만 쓰는 함수라 `_internal`의 세 번째
  shared primitive로 등록했다(`tests/boundaries/test_internal_holds_no_extension_authority.py`의
  `SHARED_PRIMITIVES`; 가져가는 두 곳 `run/recording.py`, `agent/skillset.py`는 `PERMITTED`에 이유와 함께).
  `vqapr.record`에 두면 `import vqapr`와 `vqapr skill`이 pyarrow를 끌어온다.
- `vqapr.__version__`: `vqapr/__init__.py`의 `__getattr__`가 capability와 같은 방식(`importlib.import_module`)으로
  푼다. `import vqapr`는 여전히 가볍고, 함수 안 import의 상한(7)은 그대로다.
- `vqapr --version`: 명령 없이 주어지면 `main`이 파싱 전에 답한다 — `{"ok": true, "stage": "version",
  "package_version": ...}`. 다른 답과 같은 봉투다. CLI는 surface를 통해서만 읽으므로 `agent.skillset`에서 가져온다.
- `StrategyRecord.package_version`, `DatamodelRecord.package_version`: `run/recording.py`가 기록을 얼릴 때 찍는다.
  `vqapr show strategy`는 모델의 필드 목록을 그대로 쓰므로 따로 고칠 것이 없었다. `run.json`에는 넣지 않았다:
  run의 전략들이 함께 쓰고 다시 쓰이는 파일이라, 나중에 쓴 버전이 먼저 쓴 전략의 것을 덮는다.
- `RunRecordExists.written_by`: 서 있는 기록이 말하는 버전. `record.exists` 거절의 `observed`가
  `..., written by vqapr X`로 끝난다. 필드가 생기기 전의 기록은 아무 말도 하지 않는다.
- `scripts/showcase_record_digest.py`: `package_version`을 `timing`처럼 뺀다. 릴리스마다 움직이는 값이지 run이
  계산한 것이 아니다.

## 대안과 선택

- 버전을 run identity에 넣기(오너 결정 2026-09-15: 넣지 않는다): 넣으면 업그레이드할 때마다 모든 기록이 다른 run이
  되고, "데이터 digest는 영수증" 판정과 어긋난다. 버전도 영수증이다.
- `vqapr --version`을 argparse의 `version` action으로: 봉투가 아닌 평문을 찍고 프로세스를 끝낸다. 다른 모든 답이
  JSON 봉투라서 그 모양을 따랐다.
- "이번 버전에서 바뀐 것"을 skill과 함께 설치하기: 오너 질문으로 남았다.

## 발견

- 같은 run을 다시 돌리면 먼저 `run.output_registered`(첫 run이 publish한 dataset)가 거절한다. 그래서
  `record.exists`의 새 문장은 dataset을 지운 뒤에 다시 돌린 경우처럼 좁은 길에서만 보인다. 테스트는 그 거절을 직접 묻는다.

## 검증

- 새 `tests/cli/test_a_record_names_the_vqapr_that_wrote_it.py`(3): `vqapr.__version__`과 `vqapr --version`이
  설치된 distribution의 버전이다. `r1`의 기록을 `show strategy`로 읽으면 `package_version`이 있다. 서 있는
  기록의 `RunRecordExists.written_by`와 `record.exists`의 `observed`가 그 버전을 말하고, 필드 없는 옛 기록은
  아무 말도 하지 않는다.
- boundaries · record · commands · skill 묶음: 152 passed. fast set(`uv run python -m pytest tests/ -q`):
  1794 passed, 1 failed — `tests/cli/test_show.py`가 두 기록의 필드 집합을 고정해 두었고, 거기에
  `package_version`을 더했다.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
