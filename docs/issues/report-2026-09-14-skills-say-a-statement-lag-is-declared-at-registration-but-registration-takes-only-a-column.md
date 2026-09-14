# Two skills say a fixed statement lag "is written once, at registration", but a dataset declaration accepts only a precomputed `available_at` column

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-registration-and-error-docstrings-are-in-korean.md` (the only place that states the rule is in Korean).

## What I was doing

Run 4 builds daily Korean Fama-French factors (RMRF, SMB, HML) with vqapr. Book equity comes from
annual consolidated statements, which the scenario treats as usable three months after the fiscal
year ends. Before preparing the statement parquet, the agent needed to know whether that lag is
declared to vqapr at registration, or computed into the file first.

## What I expected

Two shipped skills describe the lag as something declared at registration:

- `vqapr-introduce-vqapr/SKILL.md`, line 26: "Each dataset declares when its values became
  available — "financials are known three months after the fiscal year ends" is written once, at
  registration. Every read after that sees only what was available at that instant; there is no
  filter to forget."
- `vqapr-make-strategy/references/factor-portfolios.md`, lines 21–24: "An annual statement is known
  three months after its fiscal year ends — the usual availability rule, written once as a
  registration fact instead of a merge nobody checks."

Read literally, both say the rule itself is declared at registration. So I expected a declaration
key for a lag or offset.

## What happened

The original run (`FINDINGS.md`, F-003): "I looked through `vqapr new dataset` for a lag/offset
key and through `dir(vqapr.public)` (found `declare_local_instant`, which is about DST, not lags)
before the docstring settled that I compute `available_at` myself while preparing the parquet."

I checked this again on 0.16.0:

1. `vqapr new dataset --out ds/dataset.yaml` has one availability key, `available_at: timestamp`,
   with the comment "column that says WHEN this row could first have been known". Its TYPE note
   says: "the column must already be a TIMEZONE-AWARE timestamp in the parquet … Localize it while
   preparing the data; registration does not convert it for you." The template has no lag or
   offset key.
2. `inspect.signature(vqapr.public.DatasetRegistration)` has no lag parameter:
   `(dataset_id, source, instrument_field, available_at: 'str', key_fields, fields, grain=None,
   span=None, produced_by=None, produced_by_record=None, field_types=None, aggregated=False,
   execution=None, source_digest=None, execution_prices=None)`.
3. `vqapr.public.DatasetRegistration.__doc__` is in Korean and says the opposite of the two skill
   lines: "`available_at`은 컬럼 이름이지 규칙이 아니다. user가 준비 단계에서 계산해 넣은 값이며
   (PRD §4.0), 우리는 그것이 tz-aware인지만 본다." In English: "`available_at` is a column name,
   not a rule. It is a value the user computes and puts in at the preparation stage, and we only
   check that it is tz-aware." The language and citations of that docstring are filed separately.
4. A declaration that carries a lag key is refused:

       $ uv run vqapr --project-root . register lag.yaml
       {"correlation_id": "cf4656ec9476444fb16b524c94ff0617", "error": "VqaprError: register: 1 failure(s)\n  [400 declaration.key_unknown] datasets.lagged-prices may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "failures": [{"cause": {"message": "1 validation error for DatasetDeclaration\navailable_after\n  Extra inputs are not permitted [type=extra_forbidden, input_value='3M', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\workspace\\registration.py\", line 329, in declared\n    return model.model_validate(body)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 732, in model_validate\n    return cls.__pydantic_validator__.validate_python(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\npydantic_core._pydantic_core.ValidationError: 1 validation error for DatasetDeclaration\navailable_after\n  Extra inputs are not permitted [type=extra_forbidden, input_value='3M', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden\n", "type": "ValidationError", "where": null}, "code": "declaration.key_unknown", "example_total": 1, "examples": ["available_after"], "fix": "rename datasets.lagged-prices.available_after to 'available_at', which is the closest permitted value to 'available_after'", "observed": "datasets.lagged-prices declares 'available_after', which is not one of them", "requirement": "datasets.lagged-prices may declare: available_at, execution, field_types, fields, grain, hive_partitioned, instrument_field, key_fields, path, source_id", "source": {"file": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\f003\\lag.yaml", "key_path": "datasets.lagged-prices.available_after", "line": null}, "status": 400}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\f003"}

   None of the permitted keys is a lag. The `fix` suggests renaming the key to `available_at`,
   which this declaration already has; that is outside this report.

A successful registration's `spoken` line only restates the column: "dataset 'sample-prices': a
row is knowable at its 'available_at' value and never earlier; a model reading it at instant t
sees rows with available_at <= t".

`vqapr-register-dataset/references/point-in-time.md`, lines 38–42, treats a fixed lag as the user's
approximation ("If the user chooses a fixed lag, that choice belongs in the result's limitations").
It does not say where the lag is applied either.

## Reproduction

No data outside the package is needed.

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

3. `uv run vqapr --project-root . register lag.yaml`. It fails here with `400
   declaration.key_unknown`.
4. Compare with `vqapr-introduce-vqapr/SKILL.md:26` and
   `vqapr-make-strategy/references/factor-portfolios.md:21-24`.

Reproduced 1 of 1 attempts. Deterministic.

## Impact

Worked around; a papercut. The agent searched the dataset template and `dir(vqapr.public)` before
a Korean-language docstring settled the question. It then computed `available_at` = fiscal period
end + 3 months itself while preparing the parquet. No number changed.

The risk is a reader who takes the skill lines literally and believes the package applied a lag
that it did not. Nothing after registration would correct that belief.

## What would have prevented it

One sentence in both skills: "you compute `available_at` (for example, fiscal period end + 3
months) while preparing the file; registration records the column, it does not derive it."
