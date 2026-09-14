# An academic rebalance goes ahead when a name has no row at the fill instant, though `execution-profiles.md` says a missing exact-time price refuses it whole

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** `report-2026-09-14-money-in-a-delisted-or-halted-holding-cannot-fund-the-next-book.md` (what an absent held name then costs); the traceback inside the `check` envelope is the shape in `report-2026-09-14-stale-execution-dataset-reported-as-raw-traceback.md`.

## What I was doing

Verifying a finding about delisted holdings in the Korean Fama-French legs, on a synthetic
workspace. In that repro a held name had no row in the execution table at two later fills. Both
rebalances went ahead and recorded the name `absent`. That contradicts the skill's description of
the academic profile, so the evaluator built a smaller repro covering three shapes of "missing
exact-time price".

## What I expected

`vqapr-make-exchange/references/execution-profiles.md`, lines 24–25, under "`academic`":

> A rebalance is refused **whole, before any mutation**, if any of these is missing: a listing, an
> exact-time price, positive NAV, a compatible signed state transition, or a supported quantity rule.

`vqapr-register-dataset/references/universe-and-tradability.md`, lines 67–68:

> If there is no observation at all for a name and instant, that is a **coverage** problem, not a
> value problem, and the operation that required it fails before computing.

The same file, lines 38–39, says the opposite for names the strategy did not know were
untradable: "orders are generated for names that cannot trade and are recorded unfilled with a
reason. That is a normal result".

So I expected a fill instant where an ordered name has no row to refuse the rebalance whole. The
narrower reading was also tested: that the rule covers only names the target buys, not a held name
it sells.

## What happened

Three runs on one workspace. Each decides daily at 16:00 and fills at the next session's 15:30
close on an academic, divisible, long-only venue. The targets are scripted by date. In `ab-px`,
A's last row is 2024-01-17. In `ab-px-null`, A has a row every day, but its `close` is NULL on
2024-01-19 with `is_tradable` true.

| run | A at the 2024-01-19 15:30 fill | what the target asks of A | outcome |
|---|---|---|---|
| `ab-held-absent` | held (4504.50), **no row** | sell to 0 (target {B}) | rebalance goes ahead; A `absent`, requested `0E-24`, sized null; B `no_trade` |
| `ab-buy-absent` | not held, **no row** | **buy** 0.5 of NAV from cash | rebalance goes ahead; A `absent`, requested `0`, sized null; B bought 500,000; `never_filled: [A, absent]`; cash stays 500,000 of NAV 1,000,000 |
| `ab-buy-null` | row present, `close` NULL | buy 0.5 | **the whole run is refused at `check`**: `execution.price_not_positive` (412), no record written |

    $ vqapr --project-root <dir> register <dir>/data.yaml
    {"ok": true, "registered": {"components": ["ab-venue", "held-drop", "buy-ab"], "datasets": ["ab-px", "ab-px-null"], "instruments": [{"by_kind": {"stock": 2}, "digest": "c1116d15c4744de916fb1a2e4e5e2690b187bd879111aa71ecb7862eed5249cd", "instruments": 2}]}, "spoken": ["dataset 'ab-px': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t", "dataset 'ab-px-null': a row is knowable at its 'available_at' value and never earlier; a model reading it at instant t sees rows with available_at <= t"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> register <dir>/runs.yaml
    {"ok": true, "registered": {"runs": ["ab-held-absent", "ab-buy-absent", "ab-buy-null"]}, "spoken": ["run 'ab-held-absent' fills against dataset 'ab-px': the first execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'close' price", "run 'ab-held-absent': the model is called every 1d at 16:00:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant", "run 'ab-buy-absent' fills against dataset 'ab-px': the first execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'close' price", "run 'ab-buy-absent': the model is called every 1d at 16:00:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant", "run 'ab-buy-null' fills against dataset 'ab-px-null': the first execution instant after the decision, at 15:30:00 Asia/Seoul, at its 'close' price", "run 'ab-buy-null': the model is called every 1d at 16:00:00 Asia/Seoul, over the days its execution table has rows for, and sees only rows knowable before each instant; the book fills later, at the execution dataset's own instant"], "stage": "workspace.register", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> check ab-held-absent
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "ok": true, "passed": ["workspace", "run", "judgments", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> run ab-held-absent
    {"ok": true, "roster": {"by_kind": {"stock": 2}, "digest": "c1116d15c4744de916fb1a2e4e5e2690b187bd879111aa71ecb7862eed5249cd", "instruments": 2, "known": true, "tables": ["stock"]}, "run_id": "ab-held-absent", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1\\.vqapr", "strategies": {"held-drop": {"account_version": 2, "contract": {"accepted_intents": 2}, "events": 11, "fills": {"dealt": 2, "never_filled": [], "orders": 4, "partial": 0, "reasons": {"absent": 1, "no_trade": 1}, "zero_dealt": 2}, "fingerprint": "c1fdb0eb6cff08c7d46d41130347a7d07938eb6fd2990b70ace8dc9e0bc4a68c", "record": "held-drop@c1fdb0eb", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.001177, "due": 0.01332, "simulation.due.account_commit": 0.000345, "simulation.due.account_mark": 0.001622, "simulation.due.account_preparation": 0.000187, "simulation.due.exchange_execution": 8.2e-05, "simulation.due.feedback_candidate": 1.1e-05, "simulation.due.feedback_publication": 2.4e-05, "simulation.due.instrument_declaration": 1.6e-05, "simulation.due.order_planning": 0.000132, "simulation.due.snapshot": 0.010471, "simulation.due.valuation_mark": 1.9e-05, "simulation.due.valuation_selection": 3.4e-05, "total": 0.02059}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1", "writes": "ab-held-absent-weights"}

    $ vqapr --project-root <dir> show strategy ab-held-absent/held-drop --table vqapr.fill --limit 20
    {"items": [{"account_version": 1, "cash_delta": "-500000.0000000000000000000001", "commission": "0E-22", "dealt_quantity": "4504.504504504504504504504505", "event_time": "2024-01-17 15:30:00+09:00", "instrument": "A", "kind": "stock", "price": "111.0", "producer_id": "held-drop", "reason": null, "requested_quantity": "4504.504504504504504504504505", "run_id": "0546e24b07c18a5b10f0976098185ab5fdf12118748f2ca693daf656557c418c", "sequence": 4, "sized_quantity": "4504.504504504504504504504505", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 1, "cash_delta": "-499999.9999999999999999999999", "commission": "0E-22", "dealt_quantity": "8196.721311475409836065573769", "event_time": "2024-01-17 15:30:00+09:00", "instrument": "B", "kind": "stock", "price": "61.0", "producer_id": "held-drop", "reason": null, "requested_quantity": "8196.721311475409836065573769", "run_id": "0546e24b07c18a5b10f0976098185ab5fdf12118748f2ca693daf656557c418c", "sequence": 5, "sized_quantity": "8196.721311475409836065573770", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}, {"account_version": 2, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-01-19 15:30:00+09:00", "instrument": "A", "kind": null, "price": null, "producer_id": "held-drop", "reason": "absent", "requested_quantity": "0E-24", "run_id": "0546e24b07c18a5b10f0976098185ab5fdf12118748f2ca693daf656557c418c", "sequence": 13, "sized_quantity": null, "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 2, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-01-19 15:30:00+09:00", "instrument": "B", "kind": null, "price": null, "producer_id": "held-drop", "reason": "no_trade", "requested_quantity": "0", "run_id": "0546e24b07c18a5b10f0976098185ab5fdf12118748f2ca693daf656557c418c", "sequence": 14, "sized_quantity": "0E-24", "stage": "STRATEGY_CALLBACK", "tax": "0"}], "matched": 4, "ok": true, "returned": 4, "rows_total": 4, "run_id": "ab-held-absent", "stage": "strategy.table", "strategy_ref": "held-drop@c1fdb0eb", "table": "vqapr.fill", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> check ab-buy-absent
    {"blocked": [], "checked": ["workspace", "run", "judgments", "preflight"], "ok": true, "passed": ["workspace", "run", "judgments", "preflight"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> run ab-buy-absent
    {"ok": true, "roster": {"by_kind": {"stock": 2}, "digest": "c1116d15c4744de916fb1a2e4e5e2690b187bd879111aa71ecb7862eed5249cd", "instruments": 2, "known": true, "tables": ["stock"]}, "run_id": "ab-buy-absent", "stage": "run.complete", "store_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1\\.vqapr", "strategies": {"buy-ab": {"account_version": 1, "contract": {"accepted_intents": 1}, "events": 11, "fills": {"dealt": 1, "never_filled": [{"dealt": 0, "instrument": "A", "orders": 1, "reason": "absent"}], "orders": 2, "partial": 0, "reasons": {"absent": 1}, "zero_dealt": 1}, "fingerprint": "b6330b6effc615dbb63a9b6e3febec700636421241fba9d72ebf88ee997d0ba5", "record": "buy-ab@b6330b6e", "status": "completed", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "timing": {"callback": 0.000889, "due": 0.012808, "simulation.due.account_commit": 0.000166, "simulation.due.account_mark": 0.001388, "simulation.due.account_preparation": 9.7e-05, "simulation.due.exchange_execution": 4.7e-05, "simulation.due.feedback_candidate": 6e-06, "simulation.due.feedback_publication": 1.2e-05, "simulation.due.instrument_declaration": 1.1e-05, "simulation.due.order_planning": 6.8e-05, "simulation.due.snapshot": 0.010668, "simulation.due.valuation_mark": 1.4e-05, "simulation.due.valuation_selection": 2.1e-05, "total": 0.020023}}}, "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1", "writes": "ab-buy-absent-weights"}

    $ vqapr --project-root <dir> show strategy ab-buy-absent/buy-ab --table vqapr.fill --limit 20
    {"items": [{"account_version": 1, "cash_delta": "0", "commission": "0", "dealt_quantity": "0", "event_time": "2024-01-19 15:30:00+09:00", "instrument": "A", "kind": null, "price": null, "producer_id": "buy-ab", "reason": "absent", "requested_quantity": "0", "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 6, "sized_quantity": null, "stage": "STRATEGY_CALLBACK", "tax": "0"}, {"account_version": 1, "cash_delta": "-500000.0000000000000000000000", "commission": "0E-22", "dealt_quantity": "7936.507936507936507936507937", "event_time": "2024-01-19 15:30:00+09:00", "instrument": "B", "kind": "stock", "price": "63.0", "producer_id": "buy-ab", "reason": null, "requested_quantity": "7936.507936507936507936507937", "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 7, "sized_quantity": "7936.507936507936507936507937", "stage": "STRATEGY_CALLBACK", "tax": "0E-22"}], "matched": 2, "ok": true, "returned": 2, "rows_total": 2, "run_id": "ab-buy-absent", "stage": "strategy.table", "strategy_ref": "buy-ab@b6330b6e", "table": "vqapr.fill", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> show strategy ab-buy-absent/buy-ab --table vqapr.account --instrument _ACCOUNT --limit 20
    {"items": [{"account_version": 0, "cash": "1000000", "event_time": "2024-01-15 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1000000", "observed_at": "2024-01-15 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 0, "stage": "VALUATION"}, {"account_version": 0, "cash": "1000000", "event_time": "2024-01-16 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1000000", "observed_at": "2024-01-16 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 1, "stage": "VALUATION"}, {"account_version": 0, "cash": "1000000", "event_time": "2024-01-17 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1000000", "observed_at": "2024-01-17 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 2, "stage": "VALUATION"}, {"account_version": 0, "cash": "1000000", "event_time": "2024-01-18 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1000000", "observed_at": "2024-01-18 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 3, "stage": "VALUATION"}, {"account_version": 1, "cash": "500000.0000000000000000000000", "event_time": "2024-01-19 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1000000.000000000000000000000", "observed_at": "2024-01-19 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 8, "stage": "VALUATION"}, {"account_version": 1, "cash": "500000.0000000000000000000000", "event_time": "2024-01-22 15:30:00+09:00", "instrument": "_ACCOUNT", "nav": "1007936.507936507936507936508", "observed_at": "2024-01-22 06:30:00+00:00", "price": null, "producer_id": "buy-ab", "quantity": null, "run_id": "941a4f9fb87898ea0e2eec3bf2dcfd0dcb334c1df658407d31bba4ecef5578f4", "sequence": 10, "stage": "VALUATION"}], "matched": 6, "ok": true, "returned": 6, "rows_total": 8, "run_id": "ab-buy-absent", "stage": "strategy.table", "strategy_ref": "buy-ab@b6330b6e", "table": "vqapr.account", "tables": ["vqapr.account", "vqapr.fill", "vqapr.weight"], "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> check ab-buy-null
    {"blocked": [{"cause": {"message": "freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 189, in judgments\n    found.extend(judge())\n                 ^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 165, in <lambda>\n    lambda: _judge_execution_ordering(definition, at, read),\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 343, in _judge_execution_ordering\n    table = facts.execution_table()\n            ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 285, in execution_table\n    return self._once(  # type: ignore[return-value]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 276, in _once\n    raise error\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 271, in _once\n    self._settled[key] = (read(), None)\n                          ^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 286, in <lambda>\n    \"execution_table\", lambda: bound_execution_table(self._workspace, self._definition)\n                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 190, in bound_execution_table\n    raise VqaprError(\nvqapr.domain.errors.VqaprError: freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset\n", "type": "VqaprError", "where": null}, "code": "judgment.blocked", "example_total": 0, "examples": [], "fix": "run `vqapr check ab-buy-null` to see the full report, then fix what stopped the judgment from answering; the exception is in `cause`", "observed": "execution_ordering could not answer: VqaprError: freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset", "requirement": "every judgment answers before a run is accepted", "source": {"file": null, "key_path": "runs.ab-buy-null", "line": null}, "status": 412}], "checked": ["workspace", "run", "judgments", "preflight"], "failures": [{"cause": {"message": null, "origin": "user", "traceback": null, "type": null, "where": "D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Scripts\\vqapr.exe\\__main__.py:10 (<module>)"}, "code": "execution.price_not_positive", "example_total": 0, "examples": [], "fix": "repair 'close' in the prepared source and register 'ab-px-null' again, or fill at one of the fields the table can offer", "observed": "trade_price 'close'; registration measured no field as positive on every tradable row of 'ab-px-null'", "requirement": "the run's trade_price must be finite and positive on every tradable row of the execution dataset", "source": {"file": null, "key_path": null, "line": null}, "status": 412}], "ok": false, "passed": ["workspace", "run"], "skipped": [], "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

    $ vqapr --project-root <dir> run ab-buy-null
    {"correlation_id": "dbdbd4e3cb074d2999af1e9ee59f4e1b", "error": "VqaprError: check: 1 failure(s)\n  [412 judgment.blocked] every judgment answers before a run is accepted", "failures": [{"cause": {"message": "freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset", "origin": null, "traceback": "Traceback (most recent call last):\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 189, in judgments\n    found.extend(judge())\n                 ^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 165, in <lambda>\n    lambda: _judge_execution_ordering(definition, at, read),\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py\", line 343, in _judge_execution_ordering\n    table = facts.execution_table()\n            ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 285, in execution_table\n    return self._once(  # type: ignore[return-value]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 276, in _once\n    raise error\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 271, in _once\n    self._settled[key] = (read(), None)\n                          ^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 286, in <lambda>\n    \"execution_table\", lambda: bound_execution_table(self._workspace, self._definition)\n                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"D:\\chljeffreyz\\DevProjects\\kaist-thesis\\vqapr-scenario-testbed\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\facts.py\", line 190, in bound_execution_table\n    raise VqaprError(\nvqapr.domain.errors.VqaprError: freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset\n", "type": "VqaprError", "where": null}, "code": "judgment.blocked", "example_total": 0, "examples": [], "fix": "run `vqapr check ab-buy-null` to see the full report, then fix what stopped the judgment from answering; the exception is in `cause`", "observed": "execution_ordering could not answer: VqaprError: freeze: 1 failure(s)\n  [412 execution.price_not_positive] the run's trade_price must be finite and positive on every tradable row of the execution dataset", "requirement": "every judgment answers before a run is accepted", "source": {"file": null, "key_path": "runs.ab-buy-null", "line": null}, "status": 412}], "mutation": false, "ok": false, "retry_precondition": null, "stage": "check", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v3\\absent-r1"}

(The traceback inside the `blocked` judgment is the shape already filed as testbed F-014. It is not
part of this report.)

Which parts of the skill sentence hold:

- **A missing row at the fill instant**, whether the name is held or the target buys it: not
  refused. The rebalance proceeds, the name is recorded `absent`, and the rest of the book fills.
  Both lines 24–25 of `execution-profiles.md` and lines 67–68 of `universe-and-tradability.md`
  say otherwise. Lines 38–39 of the latter describe what happens.
- **The narrower reading, "only names the target buys"**, does not explain it either. In
  `ab-buy-absent` the target buys A from cash, A is `absent`, and half of NAV stays in cash with
  nothing refused.
- **A row present at the fill instant with a NULL price** on a tradable row: refused before any
  mutation. That part matches, but it happens at `check`, for the whole run, as a property of the
  execution dataset (`execution.price_not_positive`), not per rebalance.

## Reproduction

This needs only the wheel, plus pandas and pyarrow. It reproduced 2 of 2 times, each from an empty
directory. The `vqapr.fill` rows of `ab-held-absent` and `ab-buy-absent` were identical apart from
`run_id`, and `ab-buy-null` was refused with the same codes both times. The same behaviour appeared
in a separate four-name repro, at two fills with a delisted held name.

1. Save the generator below as `make_absent.py` and run `uv run python make_absent.py <dir>`.
2. `uv run vqapr --project-root <dir> register <dir>/data.yaml`, then `... register <dir>/runs.yaml`.
3. For each of `ab-held-absent`, `ab-buy-absent` and `ab-buy-null`: `... check <run>`, then `... run <run>`.
4. `... show strategy ab-held-absent/held-drop --table vqapr.fill --limit 20` and
   `... show strategy ab-buy-absent/buy-ab --table vqapr.fill --limit 20`. **A is `absent` at
   2024-01-19, and the rebalance was not refused.**

```python
"""Academic venue: what happens when a name has no exact-time price at the fill instant.

Writes, into the directory given as argv[1] (default: this file's directory):
  px.parquet       execution table `ab-px`: A and B, one row per business day at 15:30
                   Asia/Seoul, 2024-01-02 .. 2024-01-31. A has NO row after 2024-01-17.
  px_null.parquet  execution table `ab-px-null`: the same, except A has a row every day and its
                   `close` is NULL on 2024-01-19 only (is_tradable True).
  instruments_stock.parquet, venue.py (academic, divisible, long-only), held_drop.py,
  buy_ab.py, data.yaml, runs.yaml

Three runs, each deciding daily at 16:00 and filling at the next session's 15:30 close:
  ab-held-absent  buys A and B at the 2024-01-17 fill; decides {B} on 2024-01-18, so the
                  2024-01-19 fill must sell A, which has no row then.
  ab-buy-absent   starts in cash; decides {A, B} on 2024-01-18, so the 2024-01-19 fill must
                  BUY A, which has no row then.
  ab-buy-null     the same decision as ab-buy-absent, against `ab-px-null`, where A's
                  2024-01-19 row exists but its close is NULL.
The strategies are scripted by date: every other decision is a Hold.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
TZ = "Asia/Seoul"
DAYS = pd.bdate_range("2024-01-02", "2024-01-31")


def table(a_last=None, a_null_on=None):
    rows = []
    for i, d in enumerate(DAYS):
        at = pd.Timestamp(f"{d:%Y-%m-%d} 15:30:00", tz=TZ)
        if a_last is None or d <= pd.Timestamp(a_last):
            null = a_null_on is not None and d == pd.Timestamp(a_null_on)
            rows.append({"instrument": "A", "available_at": at,
                         "close": None if null else 100.0 + i, "is_tradable": True})
        rows.append({"instrument": "B", "available_at": at, "close": 50.0 + i, "is_tradable": True})
    return pd.DataFrame(rows).astype({"close": "float64"})


table(a_last="2024-01-17").to_parquet(OUT / "px.parquet", index=False)
table(a_null_on="2024-01-19").to_parquet(OUT / "px_null.parquet", index=False)
pd.DataFrame({"instrument_id": ["A", "B"], "kind": "stock"}).to_parquet(
    OUT / "instruments_stock.parquet", index=False
)

(OUT / "venue.py").write_text(
    '''from decimal import Decimal
from vqapr.public import AcademicExchange, ListingAccess, TradeRule

STEP = Decimal("0.00000001")


class Venue(AcademicExchange):
    """Divisible, long-only, cost-free listings."""

    def __init__(self, instruments):
        super().__init__(
            {
                str(n): TradeRule(instrument_id=str(n), quantity_step=STEP, minimum_quantity=STEP,
                                  fractional_allowed=True, access=ListingAccess.LONG_ONLY)
                for n in instruments
            },
            exchange_id="ab-venue",
        )
''',
    encoding="utf-8",
)

STRATEGY = '''from zoneinfo import ZoneInfo

from vqapr import public as vq

TZ = ZoneInfo("Asia/Seoul")
TARGETS = {targets}


class {cls}(vq.StrategyModel):
    """Scripted targets by decision date; Hold on every other date."""

    def inputs(self):
        return {{"px": vq.DatasetInput(dataset_id="ab-px", fields=("close",),
                                      lookback=vq.CalendarLookback(days=5, timezone="Asia/Seoul"))}}

    def decide(self, call):
        target = TARGETS.get(call.at.astimezone(TZ).date().isoformat())
        if target is None:
            return vq.Hold(reason="no scripted target on this date")
        return vq.Rebalance.of(long=target, invested=1)
'''
(OUT / "held_drop.py").write_text(
    STRATEGY.format(targets='{"2024-01-16": {"A": 1, "B": 1}, "2024-01-18": {"B": 1}}', cls="HeldDrop"),
    encoding="utf-8",
)
(OUT / "buy_ab.py").write_text(
    STRATEGY.format(targets='{"2024-01-18": {"A": 1, "B": 1}}', cls="BuyAB"),
    encoding="utf-8",
)

DATASET = """  {id}:
    source_id: {id}-source
    path: {path}
    instrument_field: instrument
    available_at: available_at
    grain: instrument_instant
    key_fields: [available_at, instrument]
    fields: {{close: close, is_tradable: is_tradable}}
    field_types: {{close: DOUBLE, is_tradable: BOOLEAN}}
    execution:
      is_tradable: is_tradable
"""
(OUT / "data.yaml").write_text(
    "instruments:\n  tables:\n    stock: instruments_stock.parquet\ndatasets:\n"
    + DATASET.format(id="ab-px", path="px.parquet")
    + DATASET.format(id="ab-px-null", path="px_null.parquet")
    + """components:
  ab-venue:
    kind: exchange
    path: venue.py
    object_name: Venue
    config:
      instruments: [A, B]
  held-drop:
    kind: strategy
    path: held_drop.py
    object_name: HeldDrop
  buy-ab:
    kind: strategy
    path: buy_ab.py
    object_name: BuyAB
""",
    encoding="utf-8",
)

RUN = """  {run}:
    instruments: [A, B]
    start: '2024-01-15T00:00:00+09:00'
    end: '2024-01-22T15:30:01+09:00'
    timezone: Asia/Seoul
    schedule:
      every: 1d
      at: '16:00'
    exchange: ab-venue
    execution:
      dataset: {execution}
      trade_price: close
      fill:
        at: '15:30'
    initial_account:
      cash: '1000000'
      mode: LONG_ONLY
      positions: {{}}
    writes: {run}-weights
    strategy:
      component: {component}
"""
(OUT / "runs.yaml").write_text(
    "runs:\n"
    + RUN.format(run="ab-held-absent", execution="ab-px", component="held-drop")
    + RUN.format(run="ab-buy-absent", execution="ab-px", component="buy-ab")
    + RUN.format(run="ab-buy-null", execution="ab-px-null", component="buy-ab"),
    encoding="utf-8",
)
print("wrote", OUT.name)
```

## Impact

Nothing was blocked. The run-4 agent did not rely on this sentence; the evaluator found the
contradiction while verifying the delisted-holdings finding.

The cost is to anyone who believes the text. They expect a missing exact-time price to stop the
rebalance, so that a missing row can never silently change a result. What actually happens is
that the rebalance proceeds:
- A held name with no row stays in the book, and its money cannot fund the new book. In the Korean
  FF3 legs that was up to 5.8% of a leg's NAV after a fill. It is filed separately as "Money in a
  held name that is delisted, or halted at a rebalance, cannot fund the next book".
- A bought name with no row leaves its share of NAV in cash: 50% in `ab-buy-absent`.

Both are recorded in `vqapr.fill` with reason `absent`, so the facts are in the record. The text
that says they cannot happen is what is wrong.

## What would have prevented it

- Lines 24–25 of `execution-profiles.md` stating what the academic profile does. A name with no row
  at the fill instant is recorded `absent` and the rest of the rebalance proceeds. A NULL price on a
  tradable row refuses the whole run at `check` (`execution.price_not_positive`).
- Lines 67–68 of `universe-and-tradability.md` reconciled with lines 38–39 of the same file.
