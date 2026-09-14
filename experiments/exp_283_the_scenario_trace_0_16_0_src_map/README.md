# exp_283 -- the seven scenarios traced on 0.16.0, and the src/ map

This directory was committed on 2026-09-12 as `exp_280_the_scenario_trace_0_16_0` on a local
`develop` that was not pushed. Meanwhile origin/develop re-created the same stepper under the same
name (it believed this source lost), and `exp_282` builds on that one. The 2026-09-14 merge kept
origin's `exp_280` in place and moved this directory here unchanged, except that paths now name
`exp_283`.

`docs/walkthroughs/2026-09-12-scenario-stepper-0.16.0.html` is built from `sys.setprofile` traces
of real commands on the sample door (`vqapr new sample`: ten names, 2022-01-03 ~ 2024-12-30),
never from a reading of the code. The scenarios, the commands and the tools are the 0.14.3 page's
(`exp_249`, `exp_246`, `exp_230`, `exp_238`); what 0.16.0 changed is where the code lives and what
it is called (the concept-tree campaign, records `268`-`279`), so every frame now stands in a file
of the new tree, and the frames where a name or a place changed are marked `[0.16.0]`.

The page adds two things the earlier steppers did not have, asked for with it (2026-09-12: explain
every folder and file under `src/`):

- a card under every frame's code window saying what that file is for;
- after the closing table, the src/ map: all 199 tracked files of `src/vqapr/` in 34 folders, each
  with its role, a plain explanation, its main names, who imports it, and the frames of the page
  that stand in it.

The map's prose is `src_map_0_16_0.json`. It was written by reading each file of the 0.16.0 tree,
one reader per package, with importers found by grep; it is a description of the code, not
something a trace measured. Its coverage was checked against `git ls-files src` (199 = 199, no
duplicates).

| file | what it is |
|---|---|
| `declarations/` | `exp_235`'s declarations migrated to 0.16.0: `agenda:` -> `schedule:`, `from vqapr import authoring as va` -> `from vqapr import public as vq`, `vqapr.portfolio.budgets` -> `vqapr.public`, `call.evaluation_time` -> `call.at` |
| `trace_worker.py` | `exp_238/trace_worker.py` on the new module paths (`run.assemble`, `run.batch`, `workspace.registry`) |
| `port_scenes.py` | moves a scenes file onto new traces: frame indices, `name(#idx, ms)` in the prose, source anchors |
| `scenes_0_16_0.py` | the curated frames; ported by `port_scenes.py`, then the prose rewritten by hand |
| `src_map_0_16_0.json` | the src/ map's prose |
| `render_0_16_0.py` | `exp_230/render.py`, then the file card and the src/ map; optionally an artifact copy without the document wrapper |

## The tree the traces were taken on

`develop` at `26726b1f` (0.16.0 stamped), clean, on a local disk with a cold file cache (the
registration's first duckdb scan, `check_span`, took 1,677 ms; the second table's 11 ms). Compare
pages by call counts and by which calls exist, never by milliseconds.

## Regenerating the traces

One command per process, so `#idx` restarts at zero. `PYTHONUTF8=1` throughout. The traces are
not committed (a run trace is several MB).

```bash
S=/path/to/scratch; P=$S/sample; T=$S/traces
uv run vqapr new sample --out "$P"
cp experiments/exp_283_the_scenario_trace_0_16_0_src_map/declarations/* "$P"/
X="uv run python experiments/exp_230_the_spine_trace/trace.py"
$X "$T/01_register.json"          --project "$P" -- --project-root "$P" register "$P/sample.yaml"
$X "$T/02_register_bad.json"      --project "$P" -- --project-root "$P" register "$P/bad.yaml"     # exit 1
# keep execution.parquet aside, rewrite it without its last trade_at (duckdb COPY ... WHERE trade_at < max), then:
$X "$T/03_check_changed.json"     --project "$P" -- --project-root "$P" check sample-run           # source_changed
$X "$T/04_register_again.json"    --project "$P" -- --project-root "$P" register "$P/sample.yaml"
# restore the original bytes and register once more (untraced), then:
$X "$T/05_register_features.json" --project "$P" -- --project-root "$P" register "$P/features.yaml"
$X "$T/06_run_features.json"      --project "$P" -- --project-root "$P" run sample-features-run
$X "$T/07_register_factor.json"   --project "$P" -- --project-root "$P" register "$P/factor.yaml"
$X "$T/08_run_factor.json"        --project "$P" -- --project-root "$P" run sample-factor-run
$X "$T/09_register_stoploss.json" --project "$P" -- --project-root "$P" register "$P/stoploss.yaml"
$X "$T/10_run_stoploss.json"      --project "$P" -- --project-root "$P" run sample-stoploss-run
$X "$T/11_register_enhanced.json" --project "$P" -- --project-root "$P" register "$P/enhanced.yaml"
$X "$T/12_run_enhanced.json"      --project "$P" -- --project-root "$P" run sample-enhanced-run
$X "$T/13_list_datasets.json"     --project "$P" -- --project-root "$P" list datasets
$X "$T/14_show_run_enhanced.json" --project "$P" -- --project-root "$P" show run sample-enhanced-run
$X "$T/15_run_batch.json"         --project "$P" -- --project-root "$P" run sample-factor-run sample-stoploss-run --jobs 2 --force
uv run python experiments/exp_283_the_scenario_trace_0_16_0_src_map/trace_worker.py "$T/16_worker_factor.json" \
    --project "$P" --run sample-factor-run --with sample-stoploss-run
```

## Porting the 0.14.3 frames

`port_scenes.py experiments/exp_249_the_scenario_trace_0_14_3/scenes_0_14_3.py "$T" scenes_0_16_0.py`
re-finds each frame by the function its prose names at that index, renamed where 0.16.0 renamed it
(`verify_run` -> `preflight`, `preflight_run` -> `freeze`, `RunFacts.agenda` -> `RunFacts.schedule`,
`derived_agenda` -> `derived_schedule`, `_freeze_agenda` -> `_freeze_schedule`), nearest by index;
does the same for every `<code>name</code>(#idx, ms)` in the prose; and re-finds every
`at("src/...", needle)` anchor by searching the needle in `src/vqapr/`.

Nearest-by-index is right for a call that happens once and wrong for one that repeats inside a long
loop: the stop-loss run has 882 more calls than on 0.14.3, spread unevenly over 37 days, so its last
two frames landed a day early (on 02-22 and 02-23 instead of 02-23 and 02-24). Every frame on a
repeated call was therefore checked against the event its `RunLoop.handle` was handling (the
`event` local: `ScheduledEvent(event_id='...schedule-2022-02-23T0800')`, `MarketEvent(...)`), and
those two were moved by hand. After that, every frame's qualname was printed beside its title and
every `name(#idx` in the prose was checked against the trace at that index: 53 frames, 0 mismatches.
The prose was then rewritten against the new traces.

## Rendering the page

```bash
uv run python experiments/exp_283_the_scenario_trace_0_16_0_src_map/render_0_16_0.py "$T" \
    docs/walkthroughs/2026-09-12-scenario-stepper-0.16.0.html
```

## What the traces showed (numbers the page quotes)

| command | calls | ms | 0.14.3 calls |
| --- | ---: | ---: | ---: |
| register sample.yaml | 980 | 2,818 | 973 |
| register bad.yaml | 431 | 69 | 427 |
| check sample-run (file rewritten) | 49,807 | 2,093 | 48,329 |
| register sample.yaml again | 1,304 | 1,113 | 1,294 |
| register features.yaml / run sample-features-run | 653 / 8,171 | 62 / 1,631 | 647 / 8,158 |
| register factor.yaml / run sample-factor-run | 1,069 / 24,985 | 100 / 1,850 | 1,058 / 24,374 |
| register stoploss.yaml / run sample-stoploss-run | 1,124 / 62,541 | 104 / 4,506 | 1,112 / 61,659 |
| register enhanced.yaml / run sample-enhanced-run | 1,329 / 27,993 | 108 / 2,683 | 1,315 / 27,311 |
| list datasets / show run | 1,093 / 35 | 75 / 19 | 1,081 / 32 |
| run a b --jobs 2 --force (driver) | 3,512 | 2,917 | 3,492 |
| worker (sample-factor-run, cubes baked) | 23,963 | 1,247 | 23,353 |

What the campaign kept: `_actual_source_refs` x10 / x37, `inputs()` x7, `_local_date` x12 / x18 /
x38 / x734, `heartbeat` x110 / x404 -- the 0.14.3 counts exactly. The computed numbers were read
back from the records the traced runs wrote and match the 0.14.3 page: factor 73 orders / 54 fills /
account v10, first-day +23 +8 +94 / -55 -19 -12, cash 99,463,501.24; stop-loss 111 / 59 / v34,
K000008 -52 on 02-23, cash 84,184,068.92; enhanced 81 / 41 / v9; features 108 rows; factor weights
60 rows. Only the component fingerprints changed (`sample-factor@9bba20c4` -> `@0696c8f4`,
`sample-features@20c2acad` -> `@4327b244`), because the author files' import line changed.

Why the call counts rose 1-3% is not answered here: the 0.14.3 traces were not committed, so the
calls cannot be compared function by function.
