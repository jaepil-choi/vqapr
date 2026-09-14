# exp_282 -- the eight scenes traced on the registration cleanup (f862c147)

`docs/walkthroughs/2026-09-14-scenario-stepper-registration-cleanup.html` is the 0.16.0 stepper
re-traced on `redesign/registration-cleanup` at `f862c147`: develop `f639add0` plus records `280`
(the declaration reader lives in `workspace/registration.py`, `apply` is one function) and `281`
(every dataset enters by `stage_measured`; `mismatched_source` is one rule, 400). The same sixteen
commands on the sample door, one per process, never a reading of the code.

The owner asked (2026-09-14) for the stepper again on the new structure. Plan M4 also asked for a
command badge on every frame, scene 2 split in two, and plain notation instead of `list[1]`.

| file | what it is |
| --- | --- |
| `run_traces.sh` | the sixteen commands, fresh project under the scratch dir given, exp_280's declarations |
| `trace_io.py` | exp_280's tracer unchanged, except containers are described as they look: `[x]`, `[a, … 12개]`, `(a, b)`, `{k: v, … 5개}` |
| `want.json` | which calls get inputs and outputs recorded: the 0.16.0 page's WANT, renamed where record 280 renamed, plus the one-door calls on every command that registers a dataset |
| `scenes.py` | the eight scenes. exp_280's frames moved by the k-th call of the same qualname; the frames records 280-281 changed rewritten and tagged `[280]` / `[281]`. The table's evidence uses `h(trace, idx, label)`, which refuses a wrong label; outcomes come from the run envelopes |
| `explain.py` | exp_280's plain-words → / ← lines, minus `read_yaml_mapping` and `_apply`, plus `read_declaration`, `stage_measured`, `mismatched_source`, `Transaction.register_dataset` |
| `render.py` | exp_280's renderer pointed at this directory's map and lines, plus the command badge (`02 · vqapr register bad.yaml`, from the trace's argv) |
| `src_map.json` | exp_280's map with the seven touched files' line counts taken from `f862c147` and their prose corrected (reader moved, one door, one rule) |

## Regenerating

```bash
S=/path/to/scratch
bash experiments/exp_282_the_scenario_trace_registration_cleanup/run_traces.sh "$S" \
    experiments/exp_282_the_scenario_trace_registration_cleanup/want.json
uv run python experiments/exp_282_the_scenario_trace_registration_cleanup/render.py \
    experiments/exp_282_the_scenario_trace_registration_cleanup/scenes.py "$S/traces" \
    docs/walkthroughs/2026-09-14-scenario-stepper-registration-cleanup.html
```

The renderer prints every frame's trace / index / qualname / ms beside its title; all 62 agree, and
every call a frame's stack shows has its inputs and outputs recorded. The traces are not committed.

## Moving the old frames

The 0.16.0 page's traces (second pass, 2026-09-14) were kept. For each of the 213 indices its scenes
cite, the old call's qualname and its occurrence k were looked up and the k-th call of the same
qualname taken in the new trace (`read_yaml_mapping` → `read_declaration`, `_apply` → `apply`).
None was missing and no qualname's count changed. 48 indices moved, all in commands that register a
dataset, by +1 to +19.

## What the traces showed

| command | calls 0.16.0 → f862c147 | why |
| --- | ---: | --- |
| register sample.yaml | 980 → 989 | `stage_measured` and `mismatched_source` (in the bench and in the merge), per dataset |
| register bad.yaml (exit 1) | 431 → 434 | the refusal now passes the door: `stage_measured` → `verify_source` → `raise_if_failed` |
| check (file rewritten, exit 1) | 49,807 → 49,807 | untouched |
| register sample.yaml again | 1,304 → 1,313 | as the first register |
| register features / factor / stoploss / enhanced | +1 each | |
| run features / factor / enhanced | +4 / +4 / +2 | `RunOutput.register` now opens the transaction, then `stage_measured` |
| run stop-loss, worker | +4 / +4 | |
| list, show, `--jobs` driver | 0 | |

Outcomes equal the 0.16.0 page's, read from the envelopes: factor 73 orders / 54 fills / v10,
stop-loss 111 / 59 / v34, enhanced 81 / 41 / v9; component fingerprints `sample-factor@0696c8f4`,
`sample-features@4327b244`, `sample-stoploss@6db3d49b`, `sample-enhanced@371d7e0c`. The quoted
digests (`18bb7017`, `49e4b4ab`, `34c1d63c`) appear in the new traces.

Scene 3 still shows `dataset.source_changed` refusing a rewritten file (held; owner ruling
2026-09-13, memory `data-digest-is-a-receipt`).
