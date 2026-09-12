# 280 — Panel evidence is lazy and execution reads are wider

| | |
|---|---|
| **작성 시각** | 2026-09-12 KST (+09:00) |
| **기준** | `develop` `v0.15.0`, commit `8e0045f3` |
| **실험** | `experiments/exp_251_v015_realistic_user_journey/` |
| **브랜치** | `codex/v015-performance-harness` |

## 왜 이 변경이 있는가

`v0.15.0`의 Panel은 이미 숫자 자료를 한 행렬로 한 번만 들고 `matrix()`로 잘라 준다. 그러나
8년·1,800종목·13개 입력 필드·주간 판단 408회의 실제 사용자 실행을 프로파일하니, 행렬 자체가
아닌 두 bookkeeping 작업이 판단 구간을 지배했다.

- 필드 하나를 읽을 때마다 같은 1,800개 종목을 SHA-256에 다시 넣어 Panel identity를 만들었다.
  5,317회 호출에서 문자열 encode/update가 각각 약 960만 회였다.
- 읽은 필드마다 1,800개 종목의 non-null 행 수를 중첩 dict로 즉시 만들고 callback evidence가
  실행 끝까지 보관했다. 모델과 보통의 record writer는 이 dict를 읽지 않는다.
- 일별 execution table은 약 20만 행씩 18번 읽었다. 프로파일에서 이 scan만 4.47초였고 run
  timing의 snapshot 구간은 비프로파일 실행에서 약 2.9초였다.

## 무엇이 어떻게 바뀌었는가

### 이미 있는 Panel을 먼저 찾음

`DuckDbObservationStore`가 `(dataset id, declared fields)`라는 작은 모양으로 이미 만든 Panel
후보를 먼저 찾는다. source digest, instruments, bounds가 같은 후보가 있으면 그대로 사용한다.
모든 이름을 bytes로 바꾸어 해시하는 `panel_identity`는 실제 cache miss에서만 계산한다.

Content identity의 뜻과 Panel의 공개 값은 바뀌지 않았다. 같은 run 안의 동일한 읽기가 content
identity를 다시 만드는 일만 없어졌다.

### 종목별 행 수는 요청될 때 계산함

Panel read의 `AccessRecord.actual_rows`는 여전히 `Mapping[str, Mapping[str, int]]`이다. 다만
`_PanelActualRows`가 PanelWindow를 가리키고 있다가 진단 코드가 해당 mapping을 읽을 때 validity
행렬에서 계산한다. equality, iteration, indexing의 기존 mapping 계약은 유지된다.

### 체결 자료를 더 큰 묶음으로 읽음

`ExecutionSnapshots`의 목표 묶음을 20만 행에서 100만 행으로 늘렸다. 메모리 상한은 여전히
행 수로 정해지고 한 번에 현재 묶음 하나만 보관한다. 1,800종목 일별 시험에서 18회 읽기가
4회로 줄었다.

## 바꾸지 않은 것

- 공개 CLI와 Python API
- Panel identity의 계산식과 source digest 검증
- point-in-time cutoff와 lookback
- `AccessRecord.actual_rows`의 관찰 가능한 mapping 내용
- 주문, 체결, 계좌 평가, 기록 표의 모양
- batch cube의 생성·mmap·삭제 규칙

## 측정 결과

입력은 DW에서 고정한 3,533,400행, 1,963거래일, 1,800종목이다. 다섯 개 물리 자료 묶음의
13개 숫자 필드를 읽어 16개 신호를 만들고, 매주 상위 30개 long·하위 30개 short를 408회
결정했다. 설치된 wheel의 `register -> check -> run -> list/show/export` 경로로 측정했다.

| 조건 | v0.15.0 | 변경 후 | 변화 |
|---|---:|---:|---:|
| 단일 전략 wall 중앙값 | 14.73 s | 9.27 s | -37.1% |
| 단일 전략 callback | 약 7.1 s | 약 4.2 s | 약 -41% |
| 단일 전략 snapshot | 약 2.9 s | 약 1.24 s | 약 -57% |
| 5개 전략 직렬 | 68.02 s | 43.99 s | -35.3% |
| 5개 전략 `--jobs 4` | 33.62 s | 18.85 s | -43.9% |
| 단일 전략 peak RSS 중앙값 | 2.43 GB | 1.52 GB | -37.4% |
| 5개 전략 직렬 peak RSS | 3.36 GB | 1.88 GB | -43.9% |
| 5개 전략 병렬 peak RSS 합계 | 5.93 GB | 2.93 GB | -50.5% |

`panel_identity`는 프로파일에서 5,317회에서 5회로, execution window scan은 18회에서 4회로
줄었다. 기준판과 변경판의 account/fill/weight 15개 parquet, 합계 879,745행은 Arrow table
equality와 파일 SHA-256이 모두 같았다.

## 검증

| 검사 | 결과 |
|---|---|
| `tests/data/test_panel.py` | 13 passed |
| lazy actual_rows 계약 | 즉시 `counts()` 호출 없음, 기존 dict와 equality 동일 |
| Panel cache identity 시험 | 세 cutoff·두 field 읽기에서 identity 1회 |
| 5개 전략 결과 전수 비교 | 15/15 tables, 879,745 rows, byte-identical |
| 후보 wheel 공개 journey | register, check, run, list, show, export 모두 exit 0 |
| `ruff` 변경 파일 | clean |
| `pyright` 전체 | 0 errors |
| `ruff check src/` | clean |
| 전체 적용 가능 검사 | 1,791 passed, 7 skipped, 3 deselected |
| `uv build` | sdist와 wheel 성공 |

전체 실행에서는 원본 `v0.15.0`에서도 동일하게 실패하는 운영체제별 고정 문구 검사와 강제
종료 경쟁 검사를 분리했다. Showcase 1개는 작업 공간에 필요한
`data/DW/fng_k200_members.csv`가 없어 제외했다. 변경과 연결된 나머지 전체 검사는 통과했다.

## 실제 DW 전체 경로 재확인

`exp_252`에서 `/Users/jason/qlibx/DW`의 실제 자료, 최대 공통 2018-01-02~2026-07-20,
KOSPI200 이력 전체 309종목으로 다시 확인했다. 기준판의 DataModel 반복 실행 중앙값
15.936초·1.929GB가 이 변경 뒤 12.028초·516MB가 되었다. 이어 record 281의 출력 스키마
검증 캐시까지 적용한 최종 후보는 9.722초·507MB였다. 동일한 프로젝트 위치에서 다시 만든
DataModel 419,686행과 다섯 전략의 account/fill/weight 15개 표는 기준판과 파일 SHA-256까지
같았다. 최종 실제 자료 보고서는
`experiments/exp_252_actual_dw_full_user_path/outputs/PERFORMANCE-REPORT.md`에 있다.

## 현재 develop 이식

- 측정값은 조건을 고정한 `v0.15.0` 시험 결과로 유지함
- 변경 코드는 `develop`의 `v0.16.0` 구조에 병합함
- 실행 자료 경로 변경을 따라 `src/vqapr/data/execution_table.py`에 적용함
- Panel 계약 집중 검사와 현재 전체 검사를 다시 실행해 호환성을 확인함
