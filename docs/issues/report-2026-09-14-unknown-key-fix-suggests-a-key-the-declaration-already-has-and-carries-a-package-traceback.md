# An unknown dataset key is refused with a `fix` that says to rename it to a key the declaration already has, and the refusal carries a traceback through package files

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-skills-say-a-statement-lag-is-declared-at-registration-but-registration-takes-only-a-column.md` (why a user writes a lag key), and `report-2026-09-14-krx-scaffold-points-at-price-fields-which-registration-refuses.md` (the same `fix` on `price_fields`).

## What I was doing

Run 4 builds Korean Fama-French factors. Book equity is usable three months after the fiscal year
ends, and two skills describe that lag as something "written once, at registration" (filed
separately). While verifying that report, I declared the lag as a dataset key,
`available_after: 3M`, next to the existing `available_at` column, to see what registration says.

## What I expected

`vqapr-make-exchange/SKILL.md:155-156`, like the other skills, tells the reader to trust the
refusal: "A refusal carries its own status, stage and cause, plus `fix`, `requirement`, `observed`
and `source` — read it rather than looking for it here." So I expected a `fix` that can be applied
as written.

For `cause`, I expected what other refusals from the same package carry. A mistyped command
(`usage.rejected`, 400) and a preflight refusal (`execution.requirement_missing`, 404) both carry
`"traceback": null`. I expected a 400 for a mistake in my own YAML to look the same.

## What happened

    $ uv run vqapr --project-root . register lag.yaml
    {"correlation_id": "5ccfb85fc2764774ac474a8e3438b9d6", "error": "VqaprError: register: 1 failure(s)\n  [400 declaration.key_unknown] datasets.lagged-prices may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "failures": [{"cause": {"message": "1 validation error for DatasetDeclaration\navailable_after\n  Extra inputs are not permitted [type=extra_forbidden, input_value='3M', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registration.py\", line 329, in declared\n    return model.model_validate(body)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 732, in model_validate\n    return cls.__pydantic_validator__.validate_python(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\npydantic_core._pydantic_core.ValidationError: 1 validation error for DatasetDeclaration\navailable_after\n  Extra inputs are not permitted [type=extra_forbidden, input_value='3M', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden\n", "type": "ValidationError", "where": null}, "code": "declaration.key_unknown", "example_total": 1, "examples": ["available_after"], "fix": "rename datasets.lagged-prices.available_after to 'available_at', which is the closest permitted value to 'available_after'", "observed": "datasets.lagged-prices declares 'available_after', which is not one of them", "requirement": "datasets.lagged-prices may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "source": {"file": "lag.yaml", "key_path": "datasets.lagged-prices.available_after", "line": null}, "status": 400}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\lag-1"}

Two things are wrong with this refusal. The refusal itself is correct, and nothing was written:
`mutation: false`, and no `.vqapr/` was created.

**1. The `fix` names a key the declaration already has.** `lag.yaml` already declares
`available_at: available_at`. Renaming `available_after` to `available_at`, as the fix says,
produces a mapping with that key twice. Or, if the user replaces the existing line, it loses the
real column. Either way the lag the user was trying to state is gone, and nothing tells them it
was never declarable.

The same pattern appears with other unknown keys. Each fix names a key that is already declared:

| unknown key | `fix` says rename it to | already declared in the same dataset? |
|---|---|---|
| `available_after` | `available_at` | yes |
| `availability_lag` | `available_at` | yes |
| `price_fields` | `key_fields` | yes |
| `execution_prices` | `execution` | yes |

Two contrasts show the fix is not always like this:

- **When `available_at` is actually missing,** the same rename appears beside a separate
  `declaration.key_missing` failure ("add available_at under datasets.lagged-prices"). There the
  rename would be right.
- **Inside the `execution:` sub-mapping,** an unknown key gets a different fix: "remove
  'price_fields' at datasets.exec-pf.execution.price_fields, or replace it with one of:
  is_tradable". That form offers removal as an option.

**2. `cause.traceback` carries a traceback through package files.** It names
`vqapr\workspace\registration.py", line 329, in declared` and `pydantic\main.py", line 732`,
followed by pydantic's own message and help URL. `cause.origin` and `cause.where` are both `null`,
so the envelope does not say whose mistake this was. The actionable parts (`observed`,
`requirement`, `source.key_path`) are all present and correct; the traceback adds package
internals to a refusal of user input.

## Reproduction

This needs only the `vqapr new sample` data.

1. `uv run vqapr --project-root . new sample --out ./sample`
2. Write `lag.yaml` beside `sample/`:

   ```yaml
   datasets:
     lagged-prices:
       source_id: lagged-prices-source
       path: sample/observations.parquet
       instrument_field: instrument
       available_at: available_at
       available_after: 3M
       grain: instrument_instant
       key_fields: [available_at, instrument]
       fields: {close: close}
       field_types: {close: DOUBLE}
   ```

3. `uv run vqapr --project-root . register lag.yaml`. It fails here, with the `fix` and
   `cause.traceback` shown above.
4. Variants:
   - Replace `available_after` with `availability_lag`: the fix is again "rename … to
     'available_at'".
   - Delete the `available_at` line: `declaration.key_missing` appears beside the same rename.
   - A dataset declaring `price_fields: [close]` next to `key_fields`: the fix is "rename … to
     'key_fields'".

Reproduced 3 of 3 attempts for step 3: two fresh workspaces plus one scratch workspace. The
`correlation_id` differs each time; everything else is identical.

## Impact

Worked around; a papercut. The agent read `requirement` and ignored the `fix`. A user who follows
the `fix`, as the skills say to, damages a declaration that was otherwise correct. They also learn
nothing about the real answer, which is that the lag is computed into the `available_at` column
before registration. The traceback costs attention: it puts package file paths and line numbers in
front of a user whose only mistake was an extra YAML key.

## What would have prevented it

A correct `fix` would have to account for these facts:

- **The suggested key may already be declared in the same mapping.** Here it was, in every case
  tried. When it is, "rename to X" is not a fix. Removing the unknown key is the only edit that
  leaves a valid declaration.
- **The unknown key may be a concept the package does not have** (a lag rule), not a misspelling.
  "Closest permitted value" by spelling cannot tell those apart, so the fix should at least not
  assert a rename when the target already exists.

For the cause: a `declaration.key_unknown` refusal carrying no traceback, like the other user-input
refusals in the same package.
