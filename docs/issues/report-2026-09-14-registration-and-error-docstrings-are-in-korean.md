# `help()` on `DatasetRegistration`, `SourceSpec`, `register_dataset` and `VqaprError` is in Korean, while the rest of the public surface is in English

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-public-docstrings-cite-internal-documents-the-wheel-does-not-ship.md` (the same pages, citations), and `report-2026-09-14-skills-say-a-statement-lag-is-declared-at-registration-but-registration-takes-only-a-column.md` (the rule the Korean docstring states).

## What I was doing

Run 4 builds Korean Fama-French factors. Book equity has to be registered with an availability
time three months after the fiscal year end. The skills were ambiguous about whether that lag is
declared or computed (filed separately), so the agent read `help(vqapr.public.DatasetRegistration)`
and `help(vqapr.public.register_dataset)`.

## What I expected

I expected English. `vqapr-make-strategy/SKILL.md:125` sends readers to `vqapr.public`. Of the 239
public docstrings (the names in `__all__` plus the public methods defined on them), 231 are in
English. So are all 56 shipped skill files, except one line in a skill script (below).

## What happened

The original run (`FINDINGS.md`, F-002): "every other docstring and every skill is English; these
two are Korean". The agent reads Korean, so it recovered the rule.

I checked this again on 0.16.0. Eight docstrings contain Hangul, not two:

- `DatasetRegistration`: "소비자가 `dataset_id`와 framework 이름으로 읽게 만드는 선언. … `available_at`은
  컬럼 이름이지 규칙이 아니다. user가 준비 단계에서 계산해 넣은 값이며 (PRD §4.0), 우리는 그것이
  tz-aware인지만 본다." In English: "`available_at` is a column name, not a rule; the user computes
  it at preparation; we only check it is tz-aware." That is the answer the agent was looking for.
- `DatasetRegistration.with_aggregation`, `.with_span` and `.declared_columns`: Korean throughout.
- `register_dataset`: "준비된 parquet을 검증하고 project workspace에 등록한다. 새 등록이면 ``True``,
  디스크에 이미 같은 선언이 있으면 ``False``다. …"
- `SourceSpec`: Korean for the parameters ("path 단일 parquet 파일 또는 디렉터리(하위 전부)",
  "hive_partitioned hive 레이아웃이면 True. **장식이 아니라 읽는 방법을 바꾼다** …"), then an
  English paragraph.
- `VqaprError`: "package가 내는 모든 실패의 뿌리. …" ("the root of every failure the package
  raises").
- `VqaprError.as_dict`: "agent가 읽는 형태. 사람이 읽는 것은 `str(err)`."

The shipped skill script `vqapr-register-dataset/scripts/profile_source.py:44` also quotes a
Korean line: "PRD §4.1's "낮은 카디널리티 문자열과 값의 쌍 -> field별 저장"".

## Reproduction

1. `uv run python -c "import re,sys,vqapr.public as p; sys.stdout.reconfigure(encoding='utf-8'); [print(n) for n in p.__all__ if isinstance(getattr(getattr(p,n),'__doc__',None),str) and re.search('[\uac00-\ud7a3]', getattr(p,n).__doc__)]"`
   prints `DatasetRegistration`, `SourceSpec`, `VqaprError` and `register_dataset`. The three
   `DatasetRegistration` methods and `VqaprError.as_dict` are Korean as well.
2. `uv run python -c "import vqapr.public as p; help(p.DatasetRegistration)"`

Reproduced 1 of 1 attempts. Deterministic.

## Impact

A papercut for this reporter, who reads Korean. For a reader who does not, the registration
rule (what `available_at` is) and the documentation of the error class every failure derives
from are unreadable. These are exactly the pages a first registration sends you to.

## What would have prevented it

English docstrings on these eight, matching the rest of the surface.
