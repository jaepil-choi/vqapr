# `vqapr new --out` resolves a relative path against the current directory, while its envelope prints that relative path beside a `workspace_root` it is not relative to

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-11-skill-install-writes-into-the-enclosing-repositorys-git-root-not-the-project-that-installed-vqapr.md` (another command whose output location `--project-root` does not steer).

## What I was doing

Emitting templates to learn the declaration surface while verifying findings in a scratch
workspace. Every command passed `--project-root <X>/ws` explicitly, from a shell whose current
directory was `<X>`. I ran `vqapr new dataset --out tpl/dataset.yaml`, then tried to read
`<X>/ws/tpl/dataset.yaml`. It did not exist: `cat: tpl/dataset.yaml: No such file or directory`.
The file was at `<X>/tpl/dataset.yaml`.

## What I expected

- `vqapr --help`, for `--project-root`: "workspace root: where `.vqapr/` is or will be (default:
  the current directory; refused when an ancestor directory already holds a workspace and this one
  does not, so a command run from a subdirectory cannot start a second workspace by accident --
  pass the ancestor, or this directory, explicitly)".
- `vqapr new --help`, for `--out`: "output path for the emitted file". It does not say relative to
  what.
- The envelope of `vqapr new` reports `"path": "tpl\\d.yaml"` and `"declaration": "tpl\\d.yaml"`
  in the same object as `"workspace_root": "<X>\\ws"`.
- `vqapr-analyze-result/references/panels-from-tables.md`, lines 204–205 and 222, reads the same
  two fields from a `vqapr show dataset` envelope and joins them:
  `source = (Path(shown["workspace_root"]) / shown["path"]).as_posix()`.

With an explicit `--project-root`, and a `path` printed beside `workspace_root`, I expected the
relative path to be under the workspace root, or at least the envelope to print a path that says
where the file is.

## What happened

The file is written relative to the current directory. The envelope prints the path exactly as
given, beside a `workspace_root` it is not relative to. Joining the two, as the skill recipe does
for `show dataset`, names a file that does not exist. Attempt 1, with current directory `<X>` =
`...\verify-v3\newout-r1`:

    $ vqapr --project-root <X>/ws new dataset --out tpl/d.yaml
    {"declaration": "tpl\\d.yaml", "kind": "dataset", "ok": true, "path": "tpl\\d.yaml", "stage": "template.new", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\newout-r1\\ws"}

    $ vqapr --project-root <X>/ws new run --out tpl/r.yaml
    {"declaration": "tpl\\r.yaml", "kind": "run", "ok": true, "path": "tpl\\r.yaml", "stage": "template.new", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\newout-r1\\ws"}

    $ vqapr --project-root <X>/ws new strategy s1 --dataset d1 --out tpl/s1.py
    {"declaration": "tpl\\s1.yaml", "id": "s1", "kind": "strategy_model", "object_name": "S1", "ok": true, "path": "tpl\\s1.py", "stage": "component.new", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\newout-r1\\ws"}

    $ vqapr --project-root <X>/ws new sample --out smp
    {"declaration": "smp\\sample.yaml", "kind": "sample", "next": ["vqapr register smp\\sample.yaml", "vqapr check sample-run", "vqapr run sample-run"], "ok": true, "path": "smp", "run_id": "sample-run", "stage": "template.new", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\newout-r1\\ws"}

Where the files are:

    -- files under cwd:
    ./smp/README.md
    ./smp/exchange.py
    ./smp/execution.parquet
    ./smp/instruments.csv
    ./smp/instruments_stock.parquet
    ./smp/observations.parquet
    ./smp/panel.json
    ./smp/reversal_5d.py
    ./smp/sample.yaml
    ./tpl/d.yaml
    ./tpl/r.yaml
    ./tpl/s1.py
    ./tpl/s1.yaml
    -- workspace_root/path joins exist?
    ws/tpl/d.yaml MISSING
    ./tpl/d.yaml exists
    ws/tpl/r.yaml MISSING
    ./tpl/r.yaml exists
    ws/tpl/s1.py MISSING
    ./tpl/s1.py exists
    ws/smp/sample.yaml MISSING
    ./smp/sample.yaml exists

The `next` lines of `new sample` (`vqapr register smp\\sample.yaml`, `vqapr check sample-run`, ...)
carry the cwd-relative path and no `--project-root`, although `--project-root` was given.

## Reproduction

No data is needed. It reproduced 2 of 2 times, from two fresh directories (`newout-r1`,
`newout-r2`), with identical envelopes apart from the directory name.

1. `mkdir -p X/ws && cd X`
2. `uv run vqapr --project-root "$PWD/ws" new dataset --out tpl/d.yaml`. The envelope says
   `"path": "tpl\\d.yaml"` and `"workspace_root": "...\\X\\ws"`.
3. `ls ws/tpl/d.yaml`: missing. **The file is at `X/tpl/d.yaml`.**
4. The same holds for `new run --out`, `new strategy ... --out`, and `new sample --out` (a directory).

## Impact

A papercut, but a real one. It cost one failed read and a search for where the template went.
Resolving against the current directory is a normal CLI convention, so the resolution itself may be
intended. The friction comes from two things:
- The envelope pairs a relative `path` with a `workspace_root` it is not relative to.
- The one place the skills combine those two fields (`panels-from-tables.md`, for
  `show dataset`) joins them.

A script or agent that follows that recipe on a `new` envelope gets a path to a file that does not
exist. Copying the `next` lines of `new sample` verbatim drops the `--project-root` the user gave.

## What would have prevented it

- The `new` envelope printing an absolute `path` and `declaration`.
- Or `--out` help saying "relative to the current directory, not to --project-root".
- The `next` lines of `new sample` carrying the `--project-root` the command was given.
