# 54 public docstrings cite internal documents, record numbers and module paths outside `vqapr.public` that the wheel does not ship

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-registration-and-error-docstrings-are-in-korean.md` (the same pages, language). The sample strategy's citation of an unshipped document is included here.

## What I was doing

Run 4 builds daily Korean Fama-French factors with vqapr. `vqapr-make-strategy/SKILL.md:125` sends
the reader to `vqapr.public` ("exports about 160 names and **the CLI help does not list them**").
So the agent read `help()` on the names it needed: `DatasetRegistration`, `register_dataset`,
`Rebalance`, `PanelWindow`, `CalendarLookback` and `Hold`.

## What I expected

I expected docstrings that stand on their own, or that point only at things the installed
distribution carries. `importlib.metadata.files("vqapr")` for the 0.16.0 wheel lists 210 files.
Its only non-code documents are the skills (`vqapr/agent/skills/**`) and the sample
(`vqapr/agent/sample/**`). There is no `docs/` directory, no PRD, no design document and no record
store.

## What happened

The original run (`FINDINGS.md`, F-002) quoted "`docs/issues/049`의 ruling", "(PRD §4.0)" and
"(`docs/issues/038`)", and added: "`Rebalance.__doc__` tells a direct-constructor user to
"quantise and settle through `vqapr.portfolio.weights.rescale` on the canonical grid
`vqapr.portfolio.optimize.QUANTUM`", which are non-public module paths, although `rescale` and
`QUANTUM` are both exported from `vqapr.public`. `PanelWindow`, `CalendarLookback` and `Hold`
docstrings cite `docs/issues/033`, `/061`, `/072`, `/096` and "record `125`"/"record `184`"."

I checked this again on 0.16.0 and the scope is wider. I scanned the 239 docstrings reachable
through `__doc__`: the 154 names in `vqapr.public.__all__`, plus the public methods defined on
those classes. 54 of them cite `docs/…`, `record N`, `PRD §…`, or a `vqapr.*` path that is not
`vqapr.public`:

    $ uv run python scan_citations.py
    AcademicExchange: ['record `184`']
    AccountSnapshot.value: ['record `276`']
    Budget: ['docs/issues/archive/075']
    CalendarLookback: ['docs/issues/033']
    Call: ['record `278`']
    Compliance: ['PRD §6.8', 'docs/design/two-clocks-and-the-wiring-table.md', 'vqapr.portfolio.bounds']
    Compliance.observe: ['record `229`']
    ComplianceCall: ['record `229`', 'vqapr.run.engine.calls']
    ComplianceFinding: ['docs/implementations/086']
    Component: ['docs/code-review/2026-09-08-four-readers-one-loop-and-the-missing-shapes.md', 'docs/issues/archive/036', 'record `184`']
    Component.inputs: ['docs/issues/archive/065']
    CrossSection.elementwise: ['vqapr.portfolio.bounds.intersect']
    DataModelEntry: ['docs/design/two-clocks-and-the-wiring-table.md', 'record `148`']
    DataRequirement: ['docs/issues/046', 'docs/issues/049']
    DatasetRegistration: ['PRD §4.0', 'docs/issues/038', 'docs/issues/049']
    DatasetRegistration.with_producer: ['docs/issues/091']
    DatasetRegistration.spoken: ['docs/issues/027']
    ExecutionRole: ['record `185`']
    ExecutionTable.spoken: ['docs/issues/archive/027']
    FrozenRun.dispatch_order: ['record `148`']
    FrozenSchedule.encoded: ['record `148`', 'record `182`']
    Grain: ['docs/design/the-panel-the-surface-and-the-run.md']
    Hold: ['record `125`']
    InstantsLookback: ['docs/issues/053']
    ModelWindow.panel: ['record `137`']
    ModelWindow.declared: ['docs/issues/046']
    Observation: ['docs/issues/035', 'docs/issues/archive/054']
    ObservationBatch: ['docs/issues/031', 'docs/issues/038', 'docs/issues/049', 'docs/issues/088']
    PanelWindow: ['docs/issues/061', 'docs/issues/096']
    PanelWindow.matrix: ['docs/issues/096']
    PanelWindow.current: ['docs/issues/072']
    PanelWindow.latest: ['docs/issues/072']
    Rebalance: ['docs/issues/archive/075', 'vqapr.portfolio.optimize.QUANTUM', 'vqapr.portfolio.weights.rescale']
    RowsLookback: ['docs/issues/033']
    RunDefinition: ['docs/design/two-clocks-and-the-wiring-table.md', 'record `148`']
    RunDefinition.spoken: ['docs/issues/archive/027']
    RunFill: ['record `259`']
    RunRecordMissing: ['docs/issues/archive/057']
    RunResult: ['docs/issues/archive/073']
    RunSchedule: ['record `253`']
    SimulationFailure.as_dict: ['record `171`']
    SourceSpec: ['PRD §4.0']
    StrategyCall: ['record `125`', 'vqapr.portfolio.bounds']
    StrategyEntry: ['record `148`']
    StrategyModel: ['record `132`']
    StrategyModelContext: ['record `130`']
    StrategyOutcome: ['docs/issues/archive/073']
    freeze: ['docs/issues/archive/070', 'record `168`', 'record `240`']
    read_strategy_table: ['docs/issues/archive/057', 'record `146`']
    register_run: ['record `139`']
    requirements_for: ['docs/issues/archive/049']
    rescale: ['vqapr.portfolio.optimize.QUANTUM']
    run: ['docs/issues/archive/070', 'record `242`']
    run_ids: ['record `139`']

Verbatim examples:

- `Rebalance`: "anyone building this directly should quantise and settle through
  `vqapr.portfolio.weights.rescale` on the canonical grid `vqapr.portfolio.optimize.QUANTUM` rather
  than by hand (`docs/issues/archive/075`)." Both objects are public: `rescale` and `QUANTUM` are
  in `vqapr.public.__all__`, and `vqapr.public.QUANTUM` is `Decimal('1E-12')`.
- `CalendarLookback`: "until 2026-08-30 neither class had a docstring and neither was named in the
  skill (`docs/issues/033`)."
- `Hold`: "It absorbed `models.strategy_model.NoDecision` in record `125`".
- `AcademicExchange`: "A plain dataclass rather than a frozen one since record `184`".
- `StrategyCall`: "The box it builds inside is its own to compute (`vqapr.portfolio.bounds`, design
  §7.1)".

The same pattern shows up on other parts of the surface:

- The `vqapr new sample` strategy, `reversal_5d.py`, lines 3–5: "(see
  `docs/implementations/013-halted-names-do-not-stop-a-rebalance.md`)".
- The `vqapr new run` template header: "A run is configuration (record 139)".
- `vqapr run --help`: "(record 201: a run is one model)".
- The shipped skill script `vqapr-register-dataset/scripts/profile_source.py:44`: "PRD §4.1's …".

Two corrections to the original entry: `record 184` sits on `AcademicExchange` and `Component`,
not on `PanelWindow`, `CalendarLookback` or `Hold`; `Hold` cites `record 125`.

## Reproduction

1. Save `scan_citations.py`:

   ```python
   import inspect, re, sys
   import vqapr.public as p
   sys.stdout.reconfigure(encoding="utf-8")
   CITE = re.compile(r"docs/[\w/.\-]+|PRD\s*§[\d.]+|record `?\d+`?|vqapr\.(?!public)[a-z_]+\.[\w.]+")
   for n in sorted(p.__all__):
       o = getattr(p, n)
       docs = [(n, getattr(o, "__doc__", None))]
       if inspect.isclass(o):
           docs += [(f"{n}.{m}", v.__doc__) for m, v in vars(o).items()
                    if not m.startswith("_") and callable(v) and v.__doc__]
       for label, d in docs:
           if isinstance(d, str) and (c := sorted(set(CITE.findall(d)))):
               print(f"{label}: {c}")
   ```

2. `uv run python scan_citations.py`
3. `uv run python -c "import importlib.metadata as m; print([str(f) for f in m.files('vqapr') if 'docs' in str(f)])"`
   prints `[]`.
4. `uv run vqapr new sample --out ./sample`, `uv run vqapr new run --out runs.yaml` and
   `uv run vqapr run --help` show the same citations.

Reproduced 1 of 1 attempts. The output is deterministic.

## Impact

A papercut; no number changed. Each citation is a dead end for anyone installing the wheel.

`Rebalance`'s pointer sends a direct-constructor author to module paths outside `vqapr.public`,
even though public names exist for the same objects. An author who follows it imports from
internals. Change-history sentences (for example `CalendarLookback`'s "until 2026-08-30 …") add
reading without adding a rule.

## What would have prevented it

Docstrings that state the rule without internal issue, record, PRD or design numbers, and that
name objects by their `vqapr.public` path.
