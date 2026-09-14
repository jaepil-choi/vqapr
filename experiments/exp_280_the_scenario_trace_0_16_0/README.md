# exp_280 -- the seven scenarios traced on 0.16.0, told as one warehouse

`docs/walkthroughs/2026-09-14-scenario-stepper-0.16.0.html` is built from `sys.setprofile` traces
of sixteen real commands on the sample door (`vqapr new sample`: ten names, 2022-01-03 ~
2024-12-30), never from a reading of the code. The seven scenarios are exp_235's.

Why this directory exists: a 0.16.0 stepper was published on 2026-09-12 as an artifact only; its
scenes, its tracer changes and its declarations were never committed and are gone. The owner asked
(2026-09-14) for the current version's stepper, re-traced, and written the way the registration
explanation of 2026-09-13 was: one analogy (a warehouse) carried through every frame, and what each
step does to the files on disk.

| file | what it is |
| --- | --- |
| `declarations/` | exp_235's declarations moved to the 0.16.0 author surface: `from vqapr import public as vq`, `schedule:` for `agenda:`, `call.at` for `call.evaluation_time`, `vq.Budget` for the retired `vqapr.portfolio.budgets`. Committed byte-for-byte as traced (E501 exempt in `pyproject.toml`) |
| `trace_worker.py` | exp_238's worker tracer on the 0.16.0 tree (`run/batch.py`, `run/assemble.py`, `workspace/registry.py`) |
| `probe_panel.py`, `probe_cubes.py` | exp_238's probes on the 0.16.0 tree: the scan bounds, the panel shapes and the cube files the page quotes |
| `render_0_16_0.py` | exp_230's renderer reused whole, plus the shelf (per scene), the chronicle (all sixteen commands), the file card and the src/ map |
| `scenes_0_16_0.py` | the curated scenes. Every call in a folded chain is written `c(trace, idx, label)`, which reads its milliseconds from the trace and refuses a label that is not the qualname at that index |
| `trace_io.py` | the page's tracer since 2026-09-14: exp_230's trace, plus `args` and `ret` (a short description of each value's shape) for the calls the page shows |
| `wanted.py` | which calls the page shows: executes the scenes against the traces and records every index they read; writes the WANT file `trace_io.py` takes |
| `probe_data.py`, `data_previews.json` | a few real rows of each file a frame opens (the roster, the prices, the record tables, the cube files), for the table beside the frame |
| `src_map.json` | the 2026-09-12 page's description of all 199 files under `src/vqapr/`, parsed out of the published page and checked against `26726b1f`: every path exists, 197 line counts match, the two parquet files have none |

## What is new on this page

- **The warehouse.** A table near the top maps each picture to its code: the declaration is the
  delivery note, `data/verification.py` the inspection bench, the digest the seal number,
  `Transaction` the intake cart, `.vqapr/workspace.yaml` the ledger, `preflight` the pre-dispatch
  check, `FrozenRun` the work kit, the record writer's Arrow buffer the workbench, the run record
  the work log, `.running` the "in progress" sign, `strategy.json` the closing stamp, a published
  dataset the part the factory puts back on the shelf.
- **The shelf and the chronicle.** What each command left on disk is computed from the traces'
  own `files_after` (diffed against the previous command) and from the ledger-write calls the trace
  recorded. Nothing about files is typed by hand except the two notes for what no trace can list:
  the rewrite of `execution.parquet` before `03`, and the cube directory `15` bakes and removes.
- **Seven frames where a file comes into being**: the ledger written by temp-file-and-replace
  (`01 #967`), `run.json` first (`06 #2119`), the run directory and its `.running` claim
  (`06 #2167`, `08 #2567`), rows held in memory (`08 #3823`), the tables sealed and then the
  closing stamp (`08 #24218`, `06 #8026`).

## The tree the traces were taken on

`develop` at `26726b1f` (0.16.0), clean apart from the untracked `.claude/agents/` and this
directory. Local disk, cold file cache: the registration's first duckdb scan (`check_span`) took
the most time of the first command; the second table's same stage took a few ms. Compare pages by
call counts and by which calls exist, never by milliseconds.

## Regenerating the traces

The sixteen commands of `exp_246/README.md`, with this directory's declarations and tracer, one
command per process, `PYTHONUTF8=1`, the project path passed unresolved:

```bash
S=/path/to/scratch; P=$S/sample; T=$S/traces
uv run vqapr --project-root "$P" new sample --out "$P"
cp experiments/exp_280_the_scenario_trace_0_16_0/declarations/* "$P"/
X="uv run python experiments/exp_230_the_spine_trace/trace.py"
$X "$T/01_register.json"          --project "$P" -- --project-root "$P" register "$P/sample.yaml"
$X "$T/02_register_bad.json"      --project "$P" -- --project-root "$P" register "$P/bad.yaml"     # exit 1
# rewrite execution.parquet without its last day (duckdb COPY ... WHERE trade_at < max), then:
$X "$T/03_check_changed.json"     --project "$P" -- --project-root "$P" check sample-run           # source_changed
$X "$T/04_register_again.json"    --project "$P" -- --project-root "$P" register "$P/sample.yaml"
# restore the original bytes and register once more (untraced), then 05-14 as in exp_246:
#   register features.yaml / run sample-features-run / register factor.yaml / run sample-factor-run
#   register stoploss.yaml / run sample-stoploss-run / register enhanced.yaml / run sample-enhanced-run
#   list datasets / show run sample-enhanced-run
$X "$T/15_run_batch.json"         --project "$P" -- --project-root "$P" run sample-factor-run sample-stoploss-run --jobs 2 --force
uv run python experiments/exp_280_the_scenario_trace_0_16_0/trace_worker.py "$T/16_worker_factor.json" \
    --project "$P" --run sample-factor-run --with sample-stoploss-run
```

The traces are not committed (several MB each). Keep a copy of `.vqapr/runs/` before the probes:
`probe_panel.py` re-runs each run with `--force`.

## Rendering the page

```bash
uv run python experiments/exp_280_the_scenario_trace_0_16_0/render_0_16_0.py \
    experiments/exp_280_the_scenario_trace_0_16_0/scenes_0_16_0.py "$T" \
    docs/walkthroughs/2026-09-14-scenario-stepper-0.16.0.html
```

The renderer prints every frame's trace / index / qualname / ms beside its title; all 60 agree.

## Inputs and outputs (second pass, 2026-09-14)

The owner asked to see, beside the call stack, what each call receives and returns, and the actual
rows behind "opens the roster". The page is now rendered from a second pass of the same sixteen
commands under `trace_io.py` (a fresh project; `wanted.py` picks the qualnames first), and each
frame draws its chain as a nested call stack with `→ args` and `← return`, plus `probe_data.py`'s
rows where the frame opens a file.

Between the two passes the call counts are equal except `12` (27,993, one more progress checkpoint:
timing), and a few order-planning calls change places (`OrderRequest` / `ZeroDeltaDiagnostic`
construction follows a set's iteration order, which string hashing randomises per process). The
fills, accounts and records are identical. One scene index moved (`12 #27420` -> `#27422`); the
renderer's label check found it.

## What the traces showed

| command | calls | ms | 2026-09-12 page |
| --- | ---: | ---: | ---: |
| register sample.yaml | 980 | 1,516 | 980 |
| register bad.yaml (exit 1) | 431 | 49 | 431 |
| check sample-run (file rewritten, exit 1) | 49,807 | 1,914 | 49,807 |
| register sample.yaml again | 1,304 | 596 | 1,304 |
| register features.yaml / run sample-features-run | 653 / 8,169 | 54 / 1,086 | 653 / 8,171 |
| register factor.yaml / run sample-factor-run | 1,069 / 24,985 | 80 / 1,613 | 1,069 / 24,985 |
| register stoploss.yaml / run sample-stoploss-run | 1,124 / 62,541 | 81 / 3,529 | 1,124 / 62,541 |
| register enhanced.yaml / run sample-enhanced-run | 1,329 / 27,991 | 91 / 1,674 | 1,329 / 27,993 |
| list datasets / show run | 1,093 / 35 | 57 / 10 | 1,093 / 35 |
| run a b --jobs 2 --force (driver) / worker | 3,512 / 23,963 | 1,467 / 1,184 | 3,512 / 23,963 |

Outcomes, read back from the records: factor 73 orders / 54 fills / account v10, first day
K000003 +23, K000008 +8, K000009 +94, K000004 -55, K000005 -19, K000006 -12, cash 99,463,501.24;
stop-loss 111 / 59 / v34, the last name (K000008, -52 at 1,441,901.11) sold on 2022-02-23, cash
84,184,068.92; enhanced 81 / 41 / v9. Component fingerprints `sample-factor@0696c8f4`,
`sample-features@4327b244` and `sample-enhanced@371d7e0c` equal the 2026-09-12 page's;
`sample-stoploss@6db3d49b` differs because this migration of `stoploss.py` takes `Budget` from
`vq` rather than importing it on its own line.

One correction to the 2026-09-12 page: its enhanced-index frame said the 01-13 09:00 decision
tilted by the factor weights of 01-12 (long K000003/8/9). The alpha window's newest row at 09:00
is the factor run's 01-13 08:00 decision -- long K000002/3/8, short K000004/5/9 -- and the
enhanced run's published weights (0.1944 / 0.0278 / 0.1111) confirm it.

Scene 2 still shows `dataset.source_changed` refusing a rewritten file, because that is what
`26726b1f` does. The page marks it as due to change: the owner ruled on 2026-09-13 that a changed
file is measured again by the registration's criteria rather than refused; where the re-measured
facts are kept is held.
