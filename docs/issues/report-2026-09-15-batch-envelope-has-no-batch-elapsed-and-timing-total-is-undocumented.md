# A `--jobs` batch envelope has no batch elapsed time, and per-strategy `timing.total` misses about 30% of the wall time without saying what it covers

**Status: RECEIVED 2026-09-15 (접수) — reproduced by the evaluator on the 0.16.1 wheel (triage: `docs/handoff/2026-09-15-scenario-testbed-run-5-findings.md`); fix plan with the owner.**

| | |
|---|---|
| vqapr version | `0.16.1` |
| installed from | `../../vqapr/dist/vqapr-0.16.1-py3-none-any.whl` (files match a `v0.16.1@9c54f211` tag build except line endings) |
| reported | 2026-09-15 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 5 (scenario 4, SMB book rebalancing), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

## What I was doing

Scenario 4 ran three SMB long-short books in one batch. They were identical except for the schedule:
annual, every session and month end. The Korean equity universe was about 2,500 names over
2018-06..2026-06. The scenario asked for the wall time of each book and of the whole batch.

## What I expected

`vqapr-run-backtest/SKILL.md:123`: "A batch reads each panel-grain dataset once: before the workers
start it bakes every field …". `:133`: "Measure one run alone and size `--jobs` by that, not by core
count." Both treat time as something the user measures and acts on. So I expected the envelope to
carry the batch's elapsed time, and a documented meaning for `timing.total`.

## What happened

The batch envelope's keys are, at the top, `jobs`, `ok`, `runs`, `stage`, `store_root` and
`workspace_root`. Per run they are `ok`, `run_id` and `strategies`. Per strategy they are
`account_version` and `timing` (`total`, `callback`, `due`, `simulation.due.*`). There is no batch
elapsed time and no per-run start or end instant.

| batch | wall clock (agent's own timer) | longest `timing.total` | not in any record |
|---|---|---|---|
| `vqapr run bd-a bd-b bd-c u-ks-s1 … u-ks-b3 --jobs 9` | 516 s | `bd-b` 362.5 s (others 16.5–86.2 s) | ≈ 154 s |
| `vqapr run bd-a bd-b bd-c --jobs 3` | 483 s | `bd-b` 339.4 s (A 59.2 s, C 79.7 s) | ≈ 144 s |

The missing time is presumably the bake, process start and record folding, but the envelope cannot
confirm that. Caveat: memory reached 99–100% during both batches (other processes held most of the
16.8 GB machine), so paging may have inflated the gap. Its presence does not depend on that.

## Reproduction

1. Any `vqapr run <a> <b> <c> --jobs 3` over a panel-grain dataset.
2. Time the command externally, and compare with `max(runs.*.strategies.*.timing.total)`.

Reproduced 2 of 2 batches (the envelopes are `workspace/logs/bookdrift_batch.json` and
`bookdrift_batch2.json` in the testbed).

## Impact

Worked around with an external timer. The cost is small, but "size `--jobs` by one run's time" cannot
be done from the package's own output when a third of the wall time is outside every `timing`.

## What would have prevented it

A batch-level `elapsed` (with the bake time) in the envelope, and one line in
`references/watching-and-failures.md` saying what `timing.total` covers.
