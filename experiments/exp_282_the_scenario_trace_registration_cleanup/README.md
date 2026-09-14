# exp_282 -- the eight scenes traced on the registration cleanup (0.16.1)

`docs/walkthroughs/2026-09-14-scenario-stepper-registration-cleanup.html` is the 0.16.0 stepper
re-traced on `redesign/registration-cleanup`, released as 0.16.1: records `280` (the declaration
reader lives in `workspace/registration.py`, `apply` is one function), `281` (every dataset enters
by `stage_measured`; `mismatched_source` is one rule, 400), `282` (a `rows` key is counted, not
refused), `283` (the roster refusal names a road that exists; `check` says `roster.absent` once;
`new --out X.yaml` refused) and `284` (the sample declares its roster apart from its data). The same
commands on the sample door, one per process, never a reading of the code.

The owner asked (2026-09-14) for the stepper again on the new structure, then for everything fixed
and merged. Plan M4 also asked for a command badge on every frame, scene 2 split in two, and plain
notation instead of `list[1]`.

| file | what it is |
| --- | --- |
| `run_traces.sh` | the seventeen commands (`00_register_instruments` first, record `284`), fresh project under the scratch dir given, exp_280's declarations |
| `trace_io.py` | exp_280's tracer unchanged, except containers are described as they look: `[x]`, `[a, … 12개]`, `(a, b)`, `{k: v, … 5개}` |
| `want.json` | which calls get inputs and outputs recorded: the 0.16.0 page's WANT, renamed where record 280 renamed, plus the one-door calls on every command that registers a dataset, plus the roster command |
| `scenes.py` | the eight scenes. Frames moved by the k-th call of the same qualname; the frames records 280-284 changed rewritten and tagged. Chains use `c(trace, idx, label)` and the table `h(trace, idx, label)`, both refusing a wrong label; outcomes come from the run envelopes |
| `explain.py` | exp_280's plain-words → / ← lines, minus `read_yaml_mapping` and `_apply`, plus `read_declaration`, `stage_measured`, `mismatched_source`, `Transaction.register_dataset` |
| `render.py` | exp_280's renderer pointed at this directory's map and lines, plus the command badge (`02 · vqapr register bad.yaml`, from the trace's argv) |
| `src_map.json` | exp_280's map with every touched file's line count taken from the 0.16.1 tree and the prose corrected (reader moved, one door, one rule, rows counted, roster asked once, two sample declarations) |

## Regenerating

```bash
S=/path/to/scratch
bash experiments/exp_282_the_scenario_trace_registration_cleanup/run_traces.sh "$S" \
    experiments/exp_282_the_scenario_trace_registration_cleanup/want.json
uv run python experiments/exp_282_the_scenario_trace_registration_cleanup/render.py \
    experiments/exp_282_the_scenario_trace_registration_cleanup/scenes.py "$S/traces" \
    docs/walkthroughs/2026-09-14-scenario-stepper-registration-cleanup.html
```

The renderer prints every frame's trace / index / qualname / ms beside its title; all 64 agree, and
every call a frame's stack shows has its inputs and outputs recorded. The traces are not committed.

## Moving the frames, twice

Each pass kept the previous page's traces and moved every index its scenes cite to the k-th call of
the same qualname in the new trace.

- 0.16.0 → f862c147 (records 280-281): 213 indices, none missing (`read_yaml_mapping` →
  `read_declaration`, `_apply` → `apply`).
- f862c147 → 0.16.1 (records 282-284): 252 indices, six missing -- the roster calls (`_instruments`,
  `verify_roster`, `build_roster`, `_write_roster`) that record 284 moved from `01_register` to the
  new `00_register_instruments`. Scene ① was rewritten by hand around them.

## What the traces showed

| command | calls 0.16.0 → f862c147 → 0.16.1 | why |
| --- | ---: | --- |
| register instruments.yaml | — → — → 118 | the roster, its own declaration (284) |
| register sample.yaml | 980 → 989 → 957 | +9 the one door (281); the roster leaves for `00` (284) |
| register bad.yaml (exit 1) | 431 → 434 → 434 | the refusal passes the door (281) |
| check (file rewritten, exit 1) | 49,807 → 49,807 → 49,801 | the freeze no longer asks for a roster (283) |
| register sample.yaml again | 1,304 → 1,313 → 1,265 | the door (281); no roster section to re-register (284) |
| register features / factor / stoploss / enhanced | +1 each → unchanged | |
| run features | 8,169 → 8,173 → 8,173 | the output passes the door (281); a datamodel run is not asked for a roster |
| run factor / stop-loss / enhanced | +4 / +4 / +2 → −6 each | the door (281); the roster asked once (283) |
| list, show, `--jobs` driver | unchanged | |
| worker | 23,963 → 23,967 → 23,961 | as the runs |

Outcomes equal the 0.16.0 page's, read from the envelopes: factor 73 orders / 54 fills / v10,
stop-loss 111 / 59 / v34, enhanced 81 / 41 / v9; component fingerprints `sample-factor@0696c8f4`,
`sample-features@4327b244`, `sample-stoploss@6db3d49b`, `sample-enhanced@371d7e0c`.

Scene 3 still shows `dataset.source_changed` refusing a rewritten file (held; owner ruling
2026-09-13, memory `data-digest-is-a-receipt`).
