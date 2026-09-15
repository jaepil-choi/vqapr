<!-- Evaluator's triage of kaist-thesis/vqapr-scenario-testbed FINDINGS.md entries F-022 to F-032 (2026-09-15). The testbed's own FINDINGS.md is gitignored; the entries are copied verbatim at the end. -->

# Scenario testbed run 5 — triage of F-022 to F-032

**Status: for the owner to check. The reports below are `UNTRIAGED`.**

## What ran

| part | wheel | findings |
|---|---|---|
| Corrected-price rerun of scenarios 1–3 (the vendor price file's adjustment defects fixed; a universe rule added) | `0.16.0` (`v0.16.0@3a52646d`) | F-022 |
| Scenario 4: one SMB long-short component on a SIGNED academic venue, three runs that differ only in schedule. Book A resets long = short = NAV each June, B every session, C each month end. The six 2×3 legs ran alongside. | `0.16.1` (`vqapr-0.16.1-py3-none-any.whl`, files match a `v0.16.1@9c54f211` tag build except line endings) | F-023–F-032 |

Scenario 4's result, which is about factor construction rather than vqapr: A tracks the annual SMB
(corr 0.999, TE 0.57%/yr) but is not dollar neutral during the year (net exposure up to 6–17%). B tracks
the daily SMB (corr 0.9992) and C the monthly SMB (corr 0.998). Annual turnover is 12.6–17.7× for B,
1.9–5.2× for C and 0.8–2.1× for A.

## How it was verified

The evaluator reproduced each filed finding on the 0.16.1 wheel's public surface. The package source
was not read.

- F-023: interpreter, CLI and `show strategy`.
- F-026: the two batch envelopes.
- F-028: the testbed's `bd-a` record.
- F-032: a fresh `vqapr new sample` workspace.

No separate verifier sessions ran this time.

## Triage

| finding | agent said | verdict | filed as (`report-2026-09-15-…`) |
|---|---|---|---|
| F-022 | Unsure | Not filed; question for the owner. Does a run's `instruments:` limit what a strategy *reads*, or only what it trades? If it limits reads, a security-level universe rule could live in the run and not in 18 copies of the leg. Either way, one sentence in `run-declaration.md` would settle it. | — |
| F-023 | Yes | Confirmed. `vqapr.__version__` is missing, `vqapr --version` is a 400, and no record field names the package version. | `no-record-or-public-surface-names-the-vqapr-version-that-wrote-a-run` |
| F-024 | No | Agent's own slip. | — |
| F-025 | Yes (code) | **Reclassified to docs, lower severity.** A weight target is a money amount at the fill, so the weight-only design is not the defect; a quantity-scaling order would differ by one session of drift. What cost time is the undocumented fixed point: a decision right after a fill reads the previous target. | `docs-do-not-say-a-decision-right-after-a-fill-reads-the-previous-target` |
| F-026 | Yes | Confirmed from the envelopes: there is no batch elapsed time, and about 144–154 s of 483–516 s is outside every `timing.total`. | `batch-envelope-has-no-batch-elapsed-and-timing-total-is-undocumented` |
| F-027 | No | The agent ran `--jobs 9` without measuring one full run first, which the skill says to do. | — |
| F-028 | Yes | Confirmed: `builtins.ValueError: nav[1943] must be positive to define a return`. | `strategy-report-raises-bare-valueerror-when-nav-goes-nonpositive` |
| F-029 | Unsure | Not filed; question for the owner. Develop's record 288 (`85e03ec5`) now stops an order plan at NAV ≤ 0 with a reason. Book A made no decision during its 38 sessions at NAV ≤ 0, so a run can still end `completed` with a negative NAV and no word. Should the envelope flag it? | — |
| F-030 | No | The agent's own rule. It is the evidence behind the F-025 docs report. | — |
| F-031 | Unsure | Not filed; question for the owner. After each fill, the long and short sides of the in-membership book land equal (within 1e-4) but at 0.978–1.002 × the fill NAV, while names that cannot trade hold 3.0% long and 1.0–1.1% short. The level may come from the funded account's cut of buys to cash (record 288 describes that path). The question: which NAV a signed rebalance sizes against when held names cannot trade. | — |
| F-032 | Yes | Confirmed and narrowed. Only the YAML declaration route omits `replaced`; `register strategy <id> <file>` returns it. | `yaml-re-register-of-a-changed-strategy-omits-the-replaced-fingerprint` |

## Known issues: cost in this run

- **023** (a digest over a file that can change): no cost. The one new file was registered once.
- **report 2026-09-11, factor return series**: no cost. `factor-portfolios.md`'s "Why six long-only legs, not one
  signed book" described in advance the drift scenario 4 measured.
- **F-008** (`money-in-a-delisted-or-halted-holding-cannot-fund-the-next-book`): it still applies to
  the signed books. Stuck names keep long ≠ short ≠ NAV by 1–4%.

## Seen, not filed

- `vqapr list strategies --run bd-b`, while the run was running, showed `"fingerprint": null` next to a
  `strategy_ref` that names the fingerprint. Seen once.
- `vqapr export bd-b/bd-book` took 614–631 s for 4.15 M fills (2.6 GB of CSV), longer than the run
  itself (339–362 s). Nothing lets an export skip `weights.csv` (0.66 GB). A performance observation,
  not a defect.

---

## FINDINGS.md entries F-022 to F-032 and scenario 4's "Where I stopped", verbatim

### F-022 — One universe rule for every leg had no channel but the legs themselves: 18 new strategy files, 18 component ids, 19 runs

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Unsure — "one strategy is one file, there is no config channel" is documented design. But the run declaration already carries a universe (`instruments:`), and nothing says whether it limits what a strategy *reads* or only what it *trades*, so I could not use it for a security-level exclusion with confidence.
**Resolved by:** surface plus my own tooling: a new `u-listing` dataset carrying a `kr_common` flag, generator patches onto the 18 rendered legs under `u-` ids, and 19 `u-` runs
**Where:** SCENARIO-rerun.md 2-1 (domestic common shares only), applied to scenarios 1–3
**What I was trying to say:** "from now on, every leg excludes securities that are not KRX common shares (ISIN not KR7, and A155900 / A088980 / A152550)"
**What happened:** the rule is a new input, so each leg must read a new field. Adding it to `ff-listing` would change a registered declaration (409, F-013). Editing the 18 legs in place would record as *tuning* of scenarios 1–3 and collide with their records and `writes` (F-015–F-017). So the rule became a second dataset, 18 new files and 19 new run definitions: about 20 minutes, most of it in my generator. The rule is time-invariant per security, so dropping 24 ids from each run's `instruments:` list might have given the same memberships with no new components. The run template calls that list "the universe every strategy trades", and I did not test whether it also bounds `call.read(...)`.
**What would have told me directly:** one line in `run-declaration.md` on whether `instruments:` bounds a strategy's reads, or a skill note that a methodology-wide filter belongs in a shared base installed on `PYTHONPATH` (mentioned in make-strategy for "code several strategies share").

### F-023 — After the 0.16.0 → 0.16.1 upgrade nothing on the surface says what changed, and no record says which version wrote it

**Severity:** slowed
**Kind:** docs
**Attributable to vqapr?** Yes — "every run freezes ... the fingerprint of the code" is the package's provenance claim, but the package's own version is in no record, `vqapr.__version__` is `None`, and the CLI has no `--version`.
**Resolved by:** unresolved (what changed); surface (the installed version: `vqapr skill list` → `package_version: "0.16.1"`)
**Where:** `vqapr --help`, `import vqapr; vqapr.__version__`, `vqapr show strategy u-ks-s1/u-ks-s1`, `vqapr check u-ks-s1`, `.agents/skills/.vqapr-skill.json`
**What I was trying to say:** "what does 0.16.1 change for the scenario-3 workspace I inherited, and which of these records were written by the old package?"
**What happened:** (1) Nothing on the public surface lists changes: no changelog in the skills, no `--version`, `vqapr.__version__` is `None`. Only `vqapr skill list` and `.vqapr-skill.json` name `0.16.1`, and every skill reports `state: current`, so the skills cannot tell me what moved either. I reread `introduce-vqapr`, `make-strategy` (+ `factor-portfolios`, `rebalance`, `composition-and-budget`, `memory-and-payload`, `reading-inputs`), `run-backtest` (+ `run-declaration`, `records-and-tweaks`, `watching-and-failures`), `inspect-workspace` (+ `deleting`), `make-exchange` (+ `access-and-account`, `fill-timing`, `execution-profiles`) and `analyze-result` (+ `panels-from-tables`) looking for a difference I could not recognise without the old text. I wanted to diff the skills against their 0.16.0 copies through git. That would have meant reading the repository outside this directory, so I did not. (2) The upgrade cost this workspace nothing mechanical: every registration survived, and `vqapr check u-ks-s1` returned `ok: true` with the 0.16.0 record still in place. (3) That is also the gap. `show strategy` on the old record has `timing`, `fingerprint`, `period` and `account.version`, but no package version, and the record identity is `<component>@<fp8>` of the strategy file only. So a record written by 0.16.0 and one written by 0.16.1 from the same file are indistinguishable in `list strategies`. Per `records-and-tweaks.md`, running it again on the new package is refused as the same fingerprint unless `--force` overwrites it. I avoided the question by removing every record first, as the scenario asked.
**What would have told me directly:** a `vqapr --version` (or `__version__`), a "changed in this version" section the skills install with, and the package version in each record (`show strategy` → `package_version`).

### F-024 — My own double removal: `rm run ff-b1` a second time in the cleanup loop

**Severity:** papercut
**Kind:** message
**Attributable to vqapr?** No — I had already removed `ff-b1`'s records while probing F-015, then looped over every run id `list runs` returned (definitions, not records).
**Resolved by:** surface (the refusal named the cause and listed the ids that do have records)
**Where:** `vqapr rm run ff-b1` inside `workspace/logs/bookdrift_cleanup.jsonl`
**What I was trying to say:** "remove every run's records"
**What happened:** `[400 argument.value_invalid] rm run requires the id of a run this store holds records for`, with `observed` listing the 56 others. Harmless. `list runs` lists definitions, with records beside them under `recorded`; I looped over the wrong key.
**What would have told me directly:** n/a (it did)

### F-025 — "Scale each bucket's current holdings by k" cannot be said; a target is a weight of the NAV at the fill, so every rebalance also resets the bucket to the previous close's proportions

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** Yes — the scenario's rule is a relative-quantity order ("multiply every holding in bucket b by the same factor"), and the only order a strategy can return is a weight vector, so a decision the user made cannot be expressed. The design reason is documented; the gap is still the package's.
**Resolved by:** guess (approximated: within-bucket weights = each name's share of the bucket's marked value at the decision, applied by the account at the next close)
**Where:** `Rebalance.signed` / `PortfolioTarget.__doc__` ("A target is a weight and never a quantity. The callback cannot see the execution price or NAV, so a quantity it named would have to be derived from an earlier price"); `StrategyCall.account` (`EconomicAccountView.values`: "what it sees is the previous valuation's marks")
**What I was trying to say:** "at every rebalance, set long = NAV and short = NAV, 1/3 per bucket, by multiplying each bucket's existing share counts by one factor; do not re-pick names, do not touch within-bucket proportions." That is `SCENARIO-bookdrift-rerun.md` §2.
**What happened:** a strategy can read its own book (`call.account.values`, marked at the decision session's close) and return weights; the account converts them into quantities at the next session's close, at that close's NAV and prices. So the decided within-bucket proportions are the decision-day close's, and the fill imposes them on the fill-day prices. Each rebalance undoes one session of within-bucket drift, instead of preserving it. Book B rebalances daily, so its within-bucket weights are always one session stale. Dollar neutrality, by contrast, is exact at the fill for every name that trades, so the "gap caused by filling after the decision" appears as a composition gap, not as net exposure. With a quantity-scaling order the two would swap: proportions kept exactly, net exposure off by the fill day's move. Neither channel lets me choose which gap to accept. Measured sizes are under this entry's *Measured* line (added after the runs).
**Measured, smoke run** (`bd-smoke`: the book-B rule, 2018-06-01 to 2018-09-28, removed afterwards): after every daily fill, long and short were each within 4e-4 of NAV. The only residual came from orders that dealt nothing (259 `nontradable`, 6 `absent`); right after the 2018 formation fill B1 was short 0.33314 NAV, not 0.33333, because a halted name could not be shorted. The within-bucket composition, compared with "scale the previous close's share counts by one factor per bucket" at the fill prices, was off by a half-L1 of 0.58–1.02% of the bucket per daily rebalance (bucket means; max 1.6%).
**Measured, full runs, and worse than "one session stale":** on a daily schedule the reset compounds. A decision at 16:00 reads the book the 15:30 fill has just set, which already carries the previous target's proportions. So a rule that reads "current holdings" from `call.account` returns the previous target, and the previous target returned the one before it. My first book B therefore held **June's formation weights inside every bucket all year**: half-L1 against the me_june weights was ≤ 0.6% at year end, against 6–17% for books A and C. At return level it tracked the pandas **W3** SMB (June weights restored daily; corr 0.9993, −0.24%/yr) and not the W1 buy-and-hold SMB (+2.67%/yr, TE 1.79%). "Scale the current holdings" became "reset to June every day", the one thing `SCENARIO-bookdrift-rerun.md` §2 rules out. Nothing in the package or the record says so; I found it from a persistent +2.7%/yr gap. The expressible version of the user's rule is to compute the within-bucket proportions a uniform share scaling would have, me_june × P(t) / P(first fill), from prices at the decision. It is still one session stale at the fill (F-030 records the rule I used first, and why). The v1 records' tables are kept in `outputs/bookdrift/diagnostic_v1_account_rule/`.
**Measured, corrected rule (final records `bd-book@78d0fe87`):** at month ends, within-bucket half-L1 against buy-and-hold proportions averaged 0.76–1.18% (B) and 0.72–1.31% (C) per holding year, the one-session lag, not accumulating. A was ≤ 0.12% (untradable names only). Book B then tracks the daily W1 SMB at corr 0.9992, −0.63%/yr, TE 0.53% (to 2025-06), and no longer tracks W3 (0.991). So the price-based rule recovers the user's book to within one session, and the lag itself is worth about −0.6%/yr for a daily book here.
**What would have told me directly (F-025):** a rebalance form that scales held quantities per group ("scale these names' current quantities so their marked value at the fill is w × NAV"). Or, failing that, one sentence in `rebalance.md`: "a weight target resets within-group proportions to the decision's marks; there is no way to scale existing holdings".

### F-026 — The batch envelope times each strategy but not the batch; the per-run totals miss about 150 s of a 516 s batch

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Yes — the scenario's "wall time per book and for the batch" had to come from my own clock around the command. The envelope's per-strategy `timing.total` is not documented as covering the whole run, and it evidently does not cover the batch's shared work.
**Resolved by:** guess (timed the command myself: `workspace/logs/bookdrift_batch_wall.txt`)
**Where:** `vqapr run bd-a bd-b bd-c u-ks-s1 ... u-ks-b3 --jobs 9` → `workspace/logs/bookdrift_batch.json`
**What I was trying to say:** "how long did each book take, and the whole batch?"
**What happened:** the batch envelope has `jobs: 9`, `ok`, `stage` and, per strategy, `timing` (`total`, `callback`, `due` and `simulation.due.*`). It has no batch elapsed time and no per-run start/end instants. My clock gave 516 s for the batch. The longest run, `bd-b`, reports `timing.total` 362.5 s, and the other eight 16.5–86.2 s. So about 154 s of the wall time (cube baking, which `run-backtest` says happens "before the workers start", plus process start and record folding) is in no record, and nothing says what `total` includes. `vqapr list strategies --run bd-b` while running also showed `"fingerprint": null` next to `"strategy_ref": "bd-book@ac96cd8f"`, which names the fingerprint. The corrected three-book batch (`--jobs 3`) repeated the pattern: 483 s on my clock, `bd-b` `timing.total` 339 s, so 144 s in no record. Exporting the records also cost more than running them: `vqapr export bd-b/bd-book` took 614–631 s for 4.15 M fills (2.6 GB of CSV), against 339–362 s for the run, and nothing lets an export skip `weights.csv` (0.66 GB), which I did not need.
**What would have told me directly:** a batch-level `elapsed` (and the bake time) in the envelope, plus one line in `watching-and-failures.md` on what `timing.total` covers.

### F-027 — I ran `--jobs 9` with about 1 GB of RAM free; the machine hit 100% and the batch completed only by paging

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** No — `run-backtest` says to "measure one run alone and size `--jobs` by that, not by core count", and I measured only a 3-month smoke run of the daily book (19 s), not a full one, before launching nine.
**Resolved by:** surface (nothing failed; every run `completed`)
**Where:** `vqapr run ... --jobs 9`; my sampler `workspace/logs/bookdrift_batch_mem.csv` (104 samples, 5 s apart)
**What I was trying to say:** "run the three books and the six legs concurrently", as `SCENARIO-bookdrift-rerun.md` §3 asks
**What happened:** available memory fell from about 1–2 GB to 0.004 GB (100% used) during the batch. There was no refusal, OOM kill or 503. The batch's wall time (516 s, F-026) therefore includes paging and is not a clean measure of the package's speed. The 16.8 GB machine had other processes holding about 15 GB before the batch started.
**What would have told me directly:** n/a — the skill says it; I chose to follow the scenario's "all nine in one batch" over measuring first.

### F-028 — `strategy_report` on a book whose NAV went below zero raises a bare `ValueError`, so the whole report is lost, not just the return section

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** Yes — `analyze-result/SKILL.md` says each of the six sections "is `None` with a reason in `omitted` when the record cannot give it". Here one undefined quantity (a return off a non-positive NAV) took down `book`, `trading`, `attribution` and `intent` too, through an exception that is neither a `VqaprError` nor carries a `fix`.
**Resolved by:** unresolved in vqapr (every number I report for the books is computed from `vqapr export` CSVs in pandas/duckdb)
**Where:** `strategy_report(Path(".vqapr"), "bd-a")`; `vqapr export bd-a/bd-book` wrote `nav.csv`, `holdings.csv`, `fills.csv`, `weights.csv` and `tables/`, but no `report.json` (bd-c's export has one)
**What I was trying to say:** "give me book A's report: turnover, exposure, attribution, and returns where they are defined"
**What happened:** `ValueError: nav[1943] must be positive to define a return`. Book A (SMB long/short set once a year, never re-set) is short the big buckets through 2025-07..2026-06, when this data's KOSPI goes from 3,072 to 8,476 and the B buckets return +64% to +235%. Its NAV crossed zero on 2026-05-06 and stayed ≤ 0 for 38 sessions, reaching −0.648 × C. A return off that NAV is undefined, and the refusal is correct for `performance`. But `book`, `trading` (turnover) and `attribution` are sums of positions and fills that do not need a positive NAV, and they were lost with it. I had not yet captured the export envelope in full (my own log truncated it). Re-exported: `vqapr export bd-a/bd-book` is `ok: true` with `omitted: {"report.json": "nav[1943] must be positive to define a return"}`, so the export names the omission. It still drops the whole report for one undefined section, and the Python call raises.
**What would have told me directly:** `performance: None`, `omitted: {"performance": "nav ≤ 0 at 2026-05-06 … 2026-06-30: returns undefined"}` and the other sections intact. Failing that, a `VqaprError` with that sentence as its `fix`.

### F-029 — A SIGNED account ran 38 sessions with NAV ≤ 0 and the run reported `ok`/`completed` without a word

**Severity:** papercut
**Kind:** message
**Attributable to vqapr?** Unsure — margin, collateral and borrow are documented as not modelled on `academic` (`make-exchange`, `execution-profiles.md`), so an insolvent book continuing is within the stated limits. But the package refuses a NAV of exactly zero where a weight is derived (`EconomicAccountView.weight`: "a weight against no NAV is not a small number, it is an undefined one"), and let a negative one pass through a whole run and its envelope. I cannot tell whether that is intended.
**Resolved by:** unresolved (found it myself from `nav.csv`, after F-028)
**Where:** `vqapr run bd-a ...` → `workspace/logs/bookdrift_batch.json` (`bd-a: status completed`, no warning); `workspace/exports/bookdrift/bd-a/nav.csv`
**What I was trying to say:** "run the book the user described (no margin, short proceeds as idle cash) and tell me if it ever stopped being a book"
**What happened:** nothing flagged it. Book A made no decision while its NAV was negative (its next formation, 2026-06-30, is outside the period), so no weight was ever derived from a negative NAV. Had it decided, `Rebalance.signed(..., gross=2)` of a negative NAV would have sized positions in the opposite direction, and I do not know whether the account would refuse that. I did not test it.
**What would have told me directly (F-029):** an envelope line such as `nav_nonpositive: {first: 2026-05-06, sessions: 38}`, or a sentence in `access-and-account.md` saying what a SIGNED account does when its NAV reaches zero.

### F-030 — My first book rule read "current holdings" from the account, which on a daily schedule meant "restore June's weights every day"

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** No — the rule was mine. The package's part (weights only, filled a session later, F-025) made the natural reading of "scale current holdings" wrong, but I should have seen the fixed point before running: a decision taken right after a fill reads the previous target.
**Resolved by:** guess (found from the data, then rewrote the rule; the first three book records were removed and the books rerun)
**Where:** `workspace/bookdrift/bd_book_v1.py` (the rule as first run), `workspace/bookdrift/bd_book.py` (corrected)
**What I was trying to say:** "at each rebalance, keep each bucket's names and within-bucket proportions, and scale the bucket to NAV/3"
**What happened:** v1 set within-bucket weights to each name's share of the bucket's marked value in `call.account.values`. The smoke run (3 months) showed about 0.7% of each bucket moving back per day, and I read that as a one-session lag. Over a year it never accumulated, because each day undid the day before. Book B was a fixed-weight (W3) book; C lost one session of drift a month (11 a year); A was unaffected. I caught it only because B beat the daily W1 SMB by 1–8% in every holding year. The corrected rule computes the within-bucket weights of the uniformly scaled book from prices (me_june × P(t)/P(first fill after formation), last price for a delisted name). Only the book-level scale uses the account (its NAV, through the weights).
**What would have told me directly:** n/a (my logic). A check I now run for every book: within-bucket half-L1 against buy-and-hold proportions at each fill (`outputs/bookdrift/drift_fidelity*.csv`).

### F-031 — After a fill, each side of the signed book is k × NAV with k drifting from 1.002 to 0.971; the weight-to-quantity rule is stated nowhere I could reach

**Severity:** urge
**Kind:** docs
**Attributable to vqapr?** Unsure — `PortfolioTarget.__doc__` says a target is "a fraction of execution-time NAV", and the realised sides are not that fraction of the NAV at the fill. Stuck positions (names the book cannot trade) or my own weights may explain the gap, but I could not find how the account converts weights into quantities when some held names cannot trade.
**Resolved by:** unresolved (measured and reported as part of "net exposure right after a rebalance")
**Where:** first `bd-b` records (v1 rule, since removed; export analysed before removal), then the final records (`outputs/bookdrift/post_rebalance_exposure*.csv`, `live_*` columns)
**What I was trying to say:** "each rebalance sets long = NAV and short = NAV, 1/3 per bucket". The weights I passed do that exactly: the last decision's weights sum to +1.000000 / −1.000000, ±0.333333 per bucket, and weight 0 for the 98 held names outside the membership.
**What happened:** right after the fill, the names inside the membership hold, as a share of the NAV marked at that fill:

| fill | live long | live short | stuck long | stuck short | NAV(t−1)/NAV(t) |
|---|---|---|---|---|---|
| 2019-01-03 | 1.00184 | 1.00183 | 0 | 0 | 1.00088 |
| 2019-12-02 | 0.99769 | 0.99768 | 0.0198 | 0.0021 | 1.00333 |
| 2021-10-01 | 0.99273 | 0.99275 | 0.0340 | 0.0063 | 1.00717 |
| 2023-08-01 | 0.99036 | 0.99035 | 0.0472 | 0.0091 | 1.00460 |
| 2025-12-01 | 0.98459 | 0.98461 | 0.0802 | 0.0241 | 0.99374 |
| 2026-06-26 | 0.97056 | 0.97082 | 0.1048 | 0.0455 | 0.98694 |

Long and short land equal to about 1e-4, so sizing is at the fill's prices. Their common level is neither the fill NAV (k = 1), nor the previous NAV, nor 1 − (stuck net)/2, nor the gross less stuck. I wanted to open the account's order-planning code to see which NAV it scales targets against when positions cannot move, and whether `absent` names are marked at their last price in that NAV. I did not open it. `fill-timing.md`'s "Order conversion" table (intended → requested → dealt → committed) and `execution-profiles.md`'s KRX sizing steps are the only statements, and neither covers a signed academic book with untradable holdings.
**Final records (corrected rule, same account behaviour):** across all 2,062 fills of the three books, live long right after the fill averaged 0.995 of NAV (min 0.978, max 1.002), live short matched it to within 1.4% of NAV (mean |live net| 0.05–0.11%), and stuck names held a further 3.0% long and 1.0–1.1% short on average (`post_rebalance_exposure_summary.csv`).
**What would have told me directly:** one sentence on which NAV a signed rebalance sizes against, and how held names that cannot trade enter it. Or `sized_quantity` beside a `sizing_nav` column in `vqapr.fill`.

### F-032 — Re-registering an edited strategy through its YAML declaration returned no `replaced` fingerprint, which the skill says the payload carries

**Severity:** papercut
**Kind:** message
**Attributable to vqapr?** Yes — `correcting-a-registration.md`: "The success payload then carries `replaced: {fingerprint: <the old one>}`, and says nothing about it when the id was new or the bytes unchanged." The bytes changed and the payload said nothing.
**Resolved by:** surface (`vqapr list components --id bd-book` showed the new fingerprint `78d0fe87…`, and the rerun's records are `bd-book@78d0fe87`)
**Where:** `vqapr register workspace/bookdrift/bd.yaml` after editing `bd_book.py` (log: `workspace/logs/bookdrift_rerun_prep.jsonl`)
**What I was trying to say:** "this is the corrected rule; confirm the component's fingerprint moved"
**What happened:** `{"ok": true, "registered": {"components": ["bd-venue", "bd-book"], "datasets": ["bd-membership"]}, "spoken": [...]}`, the same shape as the first registration. `bd-venue` and `bd-membership` were unchanged; `bd-book` went from `ac96cd8f` to `78d0fe87` without a word. The skill's example uses `vqapr register <kind> <id> <file.py>` and I used the declaration route, so the promise may hold only for the three-argument form. Nothing says the two routes answer differently.
**What would have told me directly:** `replaced: {"bd-book": {"fingerprint": "ac96cd8f…"}}` in the declaration route's payload, as documented.

### Where I stopped (scenario 4 and the corrected-price rerun)

- **Scenario 4 (`SCENARIO-bookdrift.md` + `SCENARIO-bookdrift-rerun.md`, vqapr 0.16.1): done, with the limits below.**
  - **Clean start:** I removed the records of all 57 earlier runs and their 57 `writes` datasets (`workspace/logs/bookdrift_cleanup.jsonl`; F-015 unchanged, F-024 was my own slip). Source datasets, components and run definitions were kept. The upgrade invalidated nothing, and nothing said what it changed (F-023).
  - **Legs:** `u-ks-s1 … u-ks-b3` rerun unchanged on 0.16.1. Their formation tables equal `outputs/rerun-corrected-prices/s3/formation_membership.csv` exactly, and their daily returns equal scenario 3's 0.16.0 series to ≤ 5e-11 (`legs_check.csv`).
  - **Books:** one component (`bd-book`, `workspace/bookdrift/bd_book.py`) on a SIGNED divisible venue (`bd-venue`), three runs differing only in schedule: `bd-a` each June's last session, `bd-b` every session, `bd-c` each month's last session. All decide at 16:00 and fill at the next 15:30 close on `km-prices`, 2018-06-01 to 2026-06-30. Membership is scenario 3's, registered as `bd-membership` and stamped 15:30 on each formation session.
  - **Batches:** batch 1 was the three books under my first rule plus the six legs (`--jobs 9`, 516 s, `workspace/logs/bookdrift_batch.json`). That rule turned out to restore June's weights daily in book B (F-025, F-030), so its three book records were removed and the books rerun under the corrected rule as batch 2 (`--jobs 3`, 483 s, `bookdrift_batch2.json`). Records in force: the legs from batch 1 and the books from batch 2 (`bd-book@78d0fe87`). The first rule's tables are kept in `outputs/bookdrift/diagnostic_v1_account_rule/`. A 3-month smoke run was made and removed.
  - **Outputs:** `outputs/bookdrift/*.csv` (paths, daily and monthly returns, book vs pandas, per-year returns, net exposure daily and by year, post-rebalance exposure, beta, turnover, rebalance counts, composition gap, drift fidelity, legs check, wall time), built by `workspace/bookdrift/analyze_bookdrift.py` from `vqapr export` CSVs. The `SUMMARY.md` text went back in my final report (harness restriction on `.md` files).
  - **Headline:** in 2018–2025 the annual book A tracks the annual SMB (pandas annual book, corr 0.999, TE 0.57%/yr), and it stays within 6.2 pp a year of compounded daily or monthly SMB. In 2025-26 the big buckets returned +64% to +235% (KOSPI +176%); A lost 162.5% of its formation NAV (NAV ≤ 0 for 38 sessions) against −65.9% for daily SMB. The daily book B reproduces daily SMB (corr 0.9992, −0.63%/yr) and the monthly book C reproduces monthly SMB (monthly corr 0.998, −0.07%/yr), at turnover of 12.6–17.7× and 1.9–5.2× a year against A's 0.8–2.1×.
  - **What stood in the way:** the rule "scale each bucket's holdings" cannot be expressed; I approximated it one session stale (F-025). My first rule was wrong (F-030). Stuck delisted names on both sides keep long ≠ short ≠ NAV by 1–4% (F-008 addendum). The sizing level after a fill is unexplained (F-031). Book A's negative NAV cost its `strategy_report` (F-028) and passed silently (F-029). Timing needed my own clock (F-026), and my `--jobs 9` ran the machine out of memory (F-027).
  - **Not done:** the optional HML books (`SCENARIO-bookdrift.md` "시간이 되면"; not in the rerun file).
  - **Not verified:** the rule behind F-031; what a SIGNED account does if a rebalance is decided while NAV < 0 (book A never decided then); whether `vqapr register strategy <id> <file>` reports `replaced` where the YAML route did not (F-032).
  - **Cleaned up:** `workspace/exports/` (4.1 GB, regenerable with `vqapr export` plus the analysis script) and my throwaway scripts. Kept: `workspace/bookdrift/` (declarations, venue, the rule as run, the first rule `bd_book_v1.py`, preparation and analysis scripts), `workspace/prepared/bd_membership.parquet`, and every envelope and memory log under `workspace/logs/`.
- **Corrected-price rerun (`SCENARIO-rerun.md`, including 2-1) — done.**
  - **Setup:** `workspace/prepared/` was rebuilt from the replaced price file (only `prices.parquet` changed) and `ff-prices`/`km-prices` were re-registered. The universe rule was added as `u-listing` plus 18 `u-` components (F-022). Nineteen `u-` runs completed (`workspace/logs/rerun_u.json`). The pre-rule corrected-price runs (`r-`, `workspace/logs/rerun.json`) and every earlier record are kept.
  - **Outputs:** `outputs/rerun-corrected-prices/{s1,s2,s3,weighting}/` and `universe_rule_removals.csv`. The rule removed 0 eligible names in 2018–2025 and 20 / 20 / 21 in 2026 (scenarios 1 / 2 / 3); A155900, flagged in 2021–2023, was never eligible.
  - **Results vs kimchi (SMB / HML corr):** scenario 1: 0.966 / 0.870; scenario 2: 0.991 / 0.980 (both essentially unchanged from the first runs); scenario 3: 0.997 / 0.992 (was 0.980 / 0.951).
  - **Scenario 3 criterion, re-applied as written:** all four factor conditions now pass, but S3's mean stock count is still 6.2% below kimchi, so the criterion is **not met**.
  - **Weighting (standard timing, pandas):** W1 buy-and-hold and W2 previous-day market cap are both close to kimchi (scenario 3: SMB 0.9985 / 0.9982, HML 0.9942 / 0.9934), with W1 marginally closer. W3 fixed weights is clearly further (0.979 / 0.963).
  - SUMMARY `.md` files were again not written (harness restriction); the texts went back in my report.
