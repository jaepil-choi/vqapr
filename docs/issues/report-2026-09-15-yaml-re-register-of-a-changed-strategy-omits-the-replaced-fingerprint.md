# Re-registering a changed strategy through a YAML declaration replaces its fingerprint silently; only the three-argument form returns the `replaced` field the skill promises

**Status: CLOSED 2026-09-15 by record 296 (`redesign/sections-and-one-register`) — the merge answers `replaced` for both routes; a declaration says `replaced: {<id>: {fingerprint}}`.**

| | |
|---|---|
| vqapr version | `0.16.1` |
| installed from | `../../vqapr/dist/vqapr-0.16.1-py3-none-any.whl` (files match a `v0.16.1@9c54f211` tag build except line endings) |
| reported | 2026-09-15 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 5 (scenario 4, SMB book rebalancing), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

## What I was doing

The agent fixed a bug in its book strategy (`bd_book.py`), re-registered it through the scenario's
declaration (`vqapr register workspace/bookdrift/bd.yaml`), and wanted confirmation that the
component's fingerprint had moved before rerunning three books.

## What I expected

`vqapr-register-dataset/references/correcting-a-registration.md:19`: "The success payload then
carries `replaced: {fingerprint: <the old one>}`, and says nothing about it when the id was new or
the bytes unchanged." The bytes had changed, so I expected `replaced`.

## What happened

In the testbed, `bd-book` went from `ac96cd8f` to `78d0fe87`, and the payload had the same shape as a
first registration. The evaluator reproduced this in a fresh workspace from `vqapr new sample`:

    $ vqapr register repro/sample.yaml          # after appending a comment to repro/reversal_5d.py
    {"ok": true, "registered": {"components": ["sample-reversal-5d", "sample-exchange"], "datasets": ["sample-prices", "sample-execution"], "runs": ["sample-run"]}, "spoken": ["dataset 'sample-prices': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'sample-execution': a row is knowable at its 'trade_at' value and never earlier; a model reading it at instant t sees rows with trade_at <= t", "run 'sample-run' fills against dataset 'sample-execution': the first execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'close' price", "run 'sample-run': the model is called every 1d at 08:00:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\vqapr-f032"}

`vqapr list components --id sample-reversal-5d` confirms the change was applied: the fingerprint went
from `208ef40e…` to `10cbbb2f…` across one such re-registration.

The three-argument form does report it:

    $ vqapr register strategy sample-reversal-5d repro/reversal_5d.py   # after another edit
    {"component": {"id": "sample-reversal-5d", "kind": "strategy", "object": "SampleReversal5d", "source": "repro\\reversal_5d.py"}, "ok": true, "registered": {"components": ["sample-reversal-5d"]}, "replaced": {"fingerprint": "c464f1c2bf12c7e43e7bcff0662665b9a65dc23805330d4dfbdec6b095f750c8"}, "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\vqapr-f032"}

The same bytes again, in three-argument form, give no `replaced`, as documented.

## Reproduction

1. `vqapr new sample --out ./repro`
2. `vqapr register repro/instruments.yaml`, then `vqapr register repro/sample.yaml`
3. Append a comment line to `repro/reversal_5d.py`
4. `vqapr register repro/sample.yaml`: no `replaced`, although `list components` shows a new fingerprint
5. Append another line, then `vqapr register strategy sample-reversal-5d repro/reversal_5d.py`: `replaced` is present

Reproduced 3 of 3 attempts (the testbed run, plus two YAML re-registrations in the fresh workspace).
The three-argument form: 1 of 1.

## Impact

Papercut. The agent confirmed the new fingerprint with `vqapr list components`. The risk is the
reverse case: after editing a strategy, a user cannot tell from the YAML payload whether their edit
was picked up.

## What would have prevented it

The declaration route reporting `replaced` per component (for example
`replaced: {"sample-reversal-5d": {"fingerprint": "…"}}`). If that is not intended, the skill should
say that only the three-argument form reports it.
