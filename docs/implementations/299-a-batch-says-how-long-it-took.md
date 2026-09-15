# 299 — 배치가 걸린 시간과 그중 bake를 말하고, skill이 `timing.total`의 범위를 말한다

| | |
|---|---|
| **작성 시각** | 2026-09-15 KST (+09:00) |
| **캠페인** | 보고서 절과 등록 창구 (`redesign/sections-and-one-register`), M4 — 설계 `docs/design/2026-09-15-sections-and-one-register.md` §3 |
| **앞선 기록** | `298` |
| **계기** | `docs/issues/report-2026-09-15-batch-envelope-has-no-batch-elapsed-and-timing-total-is-undocumented.md` — 516 s 배치에서 가장 긴 run의 `timing.total`이 362.5 s였고, 약 150 s가 어느 기록에도 없었다. `total`이 무엇을 재는지 쓴 곳도 없었다 |
| **깨지는 변화** | 없음. 여러 run의 envelope에 키가 늘었다. run 하나의 envelope과 record는 그대로다 |

---

## 무엇이 어떻게 바뀌었는가

- `cli/run.py::run`: 대상이 둘 이상이면 명령의 벽시계를 잰다. `_runs_envelope`가 `elapsed`(초, 소수 셋째 자리)를 싣는다.
- `cli/run.py::_run_each_in_workers`: `batch_cubes`가 들어가는 순간(워커가 뜨기 전 panel을 굽는 곳)을 재서
  `bake`로 싣는다. 순차 배치는 굽지 않으므로 `bake`가 없다.
- skill `run-backtest/references/watching-and-failures.md`: 전략마다의 `timing`은 그 전략의 이벤트 루프라는 것(콜백과
  due 단계, `simulation.due.*`), run을 불러오고 판정하고 panel을 만들고 기록을 쓰는 시간은 들지 않는다는 것, 그리고
  `elapsed` · `bake`가 무엇인지.

## 대안과 선택

- run마다의 `elapsed`: 풀 안의 run은 그 worker 안에서 재야 하고, 그러면 `in_workers`가 돌려주는 모양이 바뀐다.
  보고가 청한 것은 배치 시간 · bake · `total`의 뜻이라서 하지 않았다.
- run 하나의 envelope에도 `elapsed`: 테스트가 봉투를 바이트 단위로 대조하는 곳이 있어, 벽시계를 넣으면 결정적이지
  않게 된다. 한 run의 시간은 명령을 밖에서 재면 된다(`--jobs`를 정하는 기준이 그것이다).

## 검증

- 새 `tests/cli/test_a_batch_says_how_long_it_took.py`(3): `--jobs 2`의 datamodel run 둘은 `elapsed > 0`과
  `0 <= bake <= elapsed`, 순차 배치는 `elapsed`만, run 하나는 둘 다 없다.
- 이 테스트와 기존 배치 CLI 테스트(`test_a_datamodel_run_through_the_cli.py`, `test_commands.py`): 33 passed.
  fast set(`uv run python -m pytest tests/ -q`): 1798 passed, 6 skipped.
- `uv run ruff check src/` 통과, `uv run python -m pyright` 0 errors.
