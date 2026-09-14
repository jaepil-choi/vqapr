# The `krx` exchange scaffold says to add the base price to the execution table's `price_fields`, but registration refuses `price_fields`; the working route is a field named `base`, and only preflight names it

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-unknown-key-fix-suggests-a-key-the-declaration-already-has-and-carries-a-package-traceback.md` (the `fix` this refusal gives).

## What I was doing

While verifying run 4's exchange findings, I emitted the `krx` exchange scaffold and followed its
comment for switching on KRX's daily price band (`price_limits=True`) over the sample data.

## What I expected

The scaffold (`vqapr new exchange krx-venue --profile krx --instruments … --out krx_venue.py`),
lines 43–49:

> `price_limits=True` models KRX's daily band, computed from the session base price, and it
> REQUIRES your execution dataset to carry that price. Preflight refuses the run by name if it does
> not … The venue-table dataset a run fills against carries a trade price only by default, so this
> scaffold ships with the band off in order to run as emitted rather than refusing on first use. To
> switch it on: add the session base price to your execution table's `price_fields`, then set it
> to True.

I expected a `price_fields` key in the execution dataset's declaration.

## What happened

**`price_fields` is refused at dataset level:**

    $ uv run vqapr --project-root . register top.yaml
    {"correlation_id": "edf89583787b4f48ac0f720a39440046", "error": "VqaprError: register: 1 failure(s)\n  [400 declaration.key_unknown] datasets.exec-pf may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "failures": [{"cause": {"message": "1 validation error for DatasetDeclaration\nprice_fields\n  Extra inputs are not permitted [type=extra_forbidden, input_value=['close'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registration.py\", line 329, in declared\n    return model.model_validate(body)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 732, in model_validate\n    return cls.__pydantic_validator__.validate_python(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\npydantic_core._pydantic_core.ValidationError: 1 validation error for DatasetDeclaration\nprice_fields\n  Extra inputs are not permitted [type=extra_forbidden, input_value=['close'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden\n", "type": "ValidationError", "where": null}, "code": "declaration.key_unknown", "example_total": 1, "examples": ["price_fields"], "fix": "rename datasets.exec-pf.price_fields to 'key_fields', which is the closest permitted value to 'price_fields'", "observed": "datasets.exec-pf declares 'price_fields', which is not one of them", "requirement": "datasets.exec-pf may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "source": {"file": "top.yaml", "key_path": "datasets.exec-pf.price_fields", "line": null}, "status": 400}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\pf-1"}

**It is refused inside the `execution:` role too**, which accepts only `is_tradable`:

    $ uv run vqapr --project-root . register inexec.yaml
    {"correlation_id": "690fd8c5ab4b4ae2954b35fb524f9ee4", "error": "VqaprError: register: 1 failure(s)\n  [400 declaration.key_unknown] datasets.exec-pf.execution may declare: is_tradable", "failures": [{"cause": {"message": "1 validation error for DatasetDeclaration\nexecution.price_fields\n  Extra inputs are not permitted [type=extra_forbidden, input_value=['close'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registration.py\", line 329, in declared\n    return model.model_validate(body)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 732, in model_validate\n    return cls.__pydantic_validator__.validate_python(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\npydantic_core._pydantic_core.ValidationError: 1 validation error for DatasetDeclaration\nexecution.price_fields\n  Extra inputs are not permitted [type=extra_forbidden, input_value=['close'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden\n", "type": "ValidationError", "where": null}, "code": "declaration.key_unknown", "example_total": 1, "examples": ["price_fields"], "fix": "remove 'price_fields' at datasets.exec-pf.execution.price_fields, or replace it with one of: is_tradable", "observed": "datasets.exec-pf.execution declares 'price_fields', which is not one of them", "requirement": "datasets.exec-pf.execution may declare: is_tradable", "source": {"file": "inexec.yaml", "key_path": "datasets.exec-pf.execution.price_fields", "line": null}, "status": 400}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\pf-1"}

**Other places I looked for a way to set `price_fields`:**

- **The `vqapr new dataset` template** has no `price_fields` key. Its `execution:` comment says the
  table's "numeric fields are the prices a run may choose from".
- **`vqapr show run <id>`** has `execution.price_fields`, but it is a read-only map derived from the
  dataset's numeric fields: `"price_fields": {"base": "close", "close": "close"}`.
- **`vqapr-analyze-result/references/panels-from-tables.md:203` and `:221`** only read
  `run["execution"]["price_fields"]` back from a record.
- **`inspect.signature(vqapr.public.DatasetRegistration)`** has a Python-level
  `execution_prices: tuple[str, ...] | None = None` parameter. No docstring or skill mentions it,
  and as a YAML key it is refused: `declaration.key_unknown`, with the fix "rename
  datasets.exec-ep.execution_prices to 'execution'".
- **`vqapr.public.ExecutionRole.__doc__`** says a venue table's "numeric fields are the prices it
  published".
- **`KrxExchange.__init__.__doc__`** says only "the daily band on or off per ``price_limits``, off
  by default".
- **`krx_rules.__doc__`** says "``price_limits=False`` switches off the limit-up/limit-down regime,
  which is how a user whose execution table carries only a trade price still runs here".

None of these names the field the band needs.

**Preflight names it.** This is the scaffold with `price_limits=True` over the sample's execution
table:

    $ uv run vqapr --project-root . check krx-limits-run
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "execution.requirement_missing", "example_total": 0, "examples": [], "fix": "register the missing price fields on the execution dataset, or construct the Exchange with the features that need them disabled", "observed": "price_limit needs price 'base'", "requirement": "the execution dataset must declare every price the Exchange requires, or the feature that needs it must be switched off", "source": {"file": null, "key_path": null, "line": null}, "status": 404}], "ok": false, "passed": ["workspace", "run", "judgments"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\pl-1"}

`vqapr run krx-limits-run` refuses the same way, at `stage: freeze`.

**The working route is an ordinary field named `base`.** Adding `base` under `fields` (here as
`base: close`, only to prove the route) with `base: DOUBLE` under `field_types` makes `check`
return `ok: true`. The run then completes, and the strategy record shows
`"settings": {…, "price_limits": true, "profile": "krx", …}`.

So the scaffold's pointer names a key that registration refuses in both places it could go. The
name that works, `base`, appears only in a preflight refusal's `observed` text. The preflight
`fix` ("register the missing price fields on the execution dataset") does not say that means a
field called `base` under `fields`.

## Reproduction

This needs only the `vqapr new sample` data.

1. `uv run vqapr --project-root . new sample --out ./sample`
2. `uv run vqapr --project-root . new exchange krx-venue --profile krx --instruments K000001 K000002 K000003 K000004 --out krx_venue.py`.
   Read lines 43–49.
3. Add `price_fields: [close]` to an execution dataset, then register it. It is refused
   (`declaration.key_unknown`). Moving it into `execution:` is also refused.
4. Copy `krx_venue.py` to `krx_venue_pl.py` with `price_limits=False` changed to `True`. Register it
   with the sample's execution table (`fields: {close: close, is_tradable: is_tradable}`) and a
   one-name buy-and-hold strategy, then run `uv run vqapr check <run>`. It fails with
   `execution.requirement_missing`: "price_limit needs price 'base'".
5. On a fresh workspace, declare `fields: {close: close, base: close, is_tradable: is_tradable}`
   and `field_types: {close: DOUBLE, base: DOUBLE, is_tradable: BOOLEAN}`. `check` returns
   `ok: true` and `run` completes.

Each result reproduced 2 of 2 attempts on fresh workspaces: step 3 (both placements), step 4 and
step 5.

## Impact

Not hit during run 4, whose legs ran on the academic venue, so no result was affected. A user who
follows the scaffold comment lands on a registration refusal, and the refusal's `fix` sends them
further off ("rename … to 'key_fields'"). Only by switching the band on and reading preflight's
`observed` text do they learn that the price must be a field named `base`.

## What would have prevented it

The scaffold comment naming the actual route: "add the session base price to your execution
dataset's `fields` under the name `base`", plus the same line in `vqapr-make-exchange`.
