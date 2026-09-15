# No record, envelope or public attribute names the vqapr version that wrote a run, so records from 0.16.0 and 0.16.1 of the same strategy file cannot be told apart

**Status: RECEIVED 2026-09-15 (접수) — reproduced by the evaluator on the 0.16.1 wheel (triage: `docs/handoff/2026-09-15-scenario-testbed-run-5-findings.md`); fix plan with the owner.**

| | |
|---|---|
| vqapr version | `0.16.1` |
| installed from | `../../vqapr/dist/vqapr-0.16.1-py3-none-any.whl` (files match a `v0.16.1@9c54f211` tag build except line endings) |
| reported | 2026-09-15 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 5 (scenario 4, SMB book rebalancing), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

## What I was doing

The testbed workspace was upgraded from the 0.16.0 wheel to 0.16.1 between scenario 3 and scenario 4.
It still held the records of 57 runs written by 0.16.0. Before running scenario 4, the agent wanted to
know what 0.16.1 changed, and which of the existing records the old package had written.

## What I expected

`vqapr-introduce-vqapr/SKILL.md:31`: "Every run freezes its declaration, the digests of the data it
read and the fingerprint of the code. `vqapr show run` answers months later." The package is part of
the code that produced a number, so I expected a record, `--version` or `vqapr.__version__` to name it.

## What happened

    $ uv run --no-sync python -c "import vqapr, importlib.metadata as m; print(repr(getattr(vqapr,'__version__','<missing>')), m.version('vqapr'))"
    '<missing>' 0.16.1

    $ uv run --no-sync vqapr --version
    {"correlation_id": null, "error": "UsageError: the following arguments are required: COMMAND", "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "usage.rejected", "example_total": 0, "examples": [], "fix": "the form it accepts is `vqapr [-h] [--project-root PROJECT_ROOT] COMMAND ...`; run `vqapr --help` to see what each argument means", "observed": "vqapr --version", "requirement": "the following arguments are required: COMMAND", "source": {"file": null, "key_path": null, "line": null}, "status": 400}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "usage"}

- `vqapr show strategy bd-b/bd-book@78d0fe87` (a 0.16.1 record): the only `version` in the payload
  is the account version (`1962`). There is no package version. The record's identity is
  `<component>@<fp8>`, and the fingerprint is the strategy file's.
- The `--jobs` batch envelope (`runs.<id>.strategies.<component>`) carries `account_version` and
  `timing`, and no package version.
- The only place the version appears is `vqapr skill list` (`"package_version": "0.16.1"`) and the
  installed `.vqapr-skill.json`. Every skill reports `state: current`, and none says what changed
  since 0.16.0.

## Reproduction

1. Install any vqapr wheel. Run `python -c "import vqapr; print(vqapr.__version__)"`. It raises
   `AttributeError`.
2. `vqapr --version` returns the 400 above.
3. Run any strategy, then `vqapr show strategy <run>/<component>@<fp8>`. No field names the package
   version.

Reproduced 1 of 1 attempts. Deterministic.

## Impact

Slowed, not blocked. The agent reread about twenty skill files looking for a difference it could not
recognise without the old text. It then removed every old record (the scenario also asked for a clean
start). For research use, where a result must be traceable to the code that computed it, the record
alone cannot say which package version computed it. According to the agent (not re-verified here),
`records-and-tweaks.md` says running the same strategy file again is refused as the same fingerprint
unless `--force` overwrites it. So a record from before the upgrade and one from after it share one
identity.

## What would have prevented it

A `package_version` field in each strategy record (and `show strategy`), plus `vqapr --version` or
`vqapr.__version__`. A short "changed in this version" note installed with the skills would have
answered the first question.
