<!-- Copy of kaist-thesis/vqapr-scenario-testbed/FINDINGS.md at the end of run 4 (2026-09-14), with the evaluator's triage appended. The testbed's own copy is gitignored. -->

# FINDINGS.md — vqapr-scenario-testbed

| | |
|---|---|
| **Wheel** | `vqapr-0.16.0-py3-none-any.whl` — built 2026-09-14 from `vqapr@v0.16.0@3a52646d` (tag archive; sha256 `b0ed0b27…c1e6`) |
| **Skill** | 10 skills under `.agents/skills/vqapr-*/`, mirrored in `.claude/skills/vqapr-*/`, installed by `vqapr skill install --into .` |
| **CLI verbs** | `new` · `register` · `check` · `run` · `list` · `show` · `export` · `rm` · `skill` (9) |
| **Scenario** | `SCENARIO.md` |

## Known issues

- **023** — A digest describes a file that can change under it. The docs half is closed; the code half (`show run` reading `matches`/`differs`) is held.
  - *This run:* it cost a check cycle, and the refusal did its job. After the answers came back I rewrote `workspace/prepared/prices.parquet` (new column `ret_close`) and `book_equity.parquet` (new `nci` and `book_equity` columns) under datasets registered on the old bytes. `vqapr check km-s1` refused with `dataset.source_changed` (412), naming both digests and the fix. `vqapr check ff-s1` reported the same condition only as a `blocked` judgment whose cause is a full Python traceback (see F-014).
- **report 2026-09-11, factor return series** — Following the skills, agents concluded a factor return series cannot be built through vqapr and computed it in pandas. The skills were revised before this wheel; the owner has not closed it.
  - *This run:* no cost. `introduce-vqapr` and `make-strategy` sent me straight to six value-weighted legs plus a market leg, and `vqapr export` NAVs gave the factor arithmetic. The seven runs took about 35 s in total.
- **report 2026-09-11, smaller model** — A smaller model did not finish the framework path and reported that it had. Held; the proposals (a progress display, a started state in `list runs`, a shorter path for a factor leg) are open.

## Findings

### F-001 — The testbed root holds an empty nested `vqapr-scenario-testbed/` copy of its own layout

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** No — it is testbed setup, not anything the package emitted.
**Resolved by:** surface (listed it, found only empty `data/*` and `paper/` directories, ignored it)
**Where:** `ls` of the working directory
**What I was trying to say:** "which `data/` is the real one?"
**What happened:** `vqapr-scenario-testbed/vqapr-scenario-testbed/{data/{ecos,fng,kimchi-factor,korean_equity},paper}` exists, all empty.
**What would have told me directly:** not having it there. (The evaluator confirmed a setup error and removed the directory.)

### F-002 — `help()` on the dataset-registration API is in Korean and cites documents the wheel does not ship

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Yes — the docstring is the package's own public surface, and it points the reader at files a wheel user cannot open.
**Resolved by:** surface (I read Korean; the gist was recoverable)
**Where:** `vqapr.public.DatasetRegistration.__doc__`, `vqapr.public.register_dataset.__doc__`
**What I was trying to say:** "can I declare 'three months after fiscal year end' at registration, or must I compute the column?"
**What happened:** every other docstring and every skill is English; these two are Korean and say, e.g., "`docs/issues/049`의 ruling", "(PRD §4.0)", "(`docs/issues/038`)". None of those documents exist for a consumer of the wheel.
**What would have told me directly:** an English docstring that states the rule without citing internal issue numbers.

Same pattern, seen later in the run: `Rebalance.__doc__` tells a direct-constructor user to "quantise and settle through `vqapr.portfolio.weights.rescale` on the canonical grid `vqapr.portfolio.optimize.QUANTUM`", which are non-public module paths, although `rescale` and `QUANTUM` are both exported from `vqapr.public`. `PanelWindow`, `CalendarLookback` and `Hold` docstrings cite `docs/issues/033`, `/061`, `/072`, `/096` and "record `125`"/"record `184`".

### F-003 — The skills describe the 3-month statement lag as something "written once, at registration"; registration actually takes only a precomputed column

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Yes — the wording in two skills reads as a declarable lag rule; the docstring (F-002) says the opposite.
**Resolved by:** surface (`DatasetRegistration.__doc__`: "`available_at`은 컬럼 이름이지 규칙이 아니다" — available_at is a column name, not a rule)
**Where:** `vqapr-introduce-vqapr/SKILL.md` ("financials are known three months after the fiscal year ends — is written once, at registration"), `vqapr-make-strategy/references/factor-portfolios.md` ("written once as a registration fact instead of a merge nobody checks"); the dataset template shows only `available_at: <column>`
**What I was trying to say:** "financial statements become usable three months after the fiscal period end", as a declaration.
**What happened:** I looked through `vqapr new dataset` for a lag/offset key and through `dir(vqapr.public)` (found `declare_local_instant`, which is about DST, not lags) before the docstring settled that I compute `available_at` myself while preparing the parquet.
**What would have told me directly:** one line in the skill: "you compute `available_at = period_end + 3 months` while preparing the file; registration records it, it does not derive it."

### F-004 — The emitted sample strategy imports from a private module and cites an unshipped document

**Severity:** papercut
**Kind:** code
**Attributable to vqapr?** Yes — `vqapr new sample` output is the file the skills tell me to copy, and it reaches past `vqapr.public`.
**Resolved by:** surface (`Budget` and `PortfolioDirection` are both in `dir(vqapr.public)`, so I will import them from there)
**Where:** `vqapr new sample` → `reversal_5d.py`
**What I was trying to say:** "copy the sample's shape for my own legs, using only the public surface"
**What happened:** `from vqapr.domain.intent import Budget, PortfolioDirection`; the module docstring cites `docs/implementations/013-halted-names-do-not-stop-a-rebalance.md`. It also builds `Rebalance(target_weights=..., cash_weight=..., budget=...)` directly while every skill shows `Rebalance.of(...)` / `Rebalance.signed(...)`, a second path with no word on which to prefer.
**What would have told me directly:** the sample importing only from `vqapr.public`, and using the constructor the skills teach.

### F-005 — Two ways to list a venue's instruments, and the scaffold shows the one that does not scale

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Yes — two surface paths for one thing, nothing says which to use when the universe is ~3,000 names.
**Resolved by:** guess (I took the sample's `config: {instruments: [...]}` constructor-argument pattern)
**Where:** `vqapr new exchange ff-venue --profile academic --instruments ...` vs `vqapr new sample` → `exchange.py`
**What I was trying to say:** "every common stock in the price table is listed, divisible, long-only"
**What happened:** the exchange scaffold writes each id as a literal inside `Venue.__init__` (`"A005930": _rule("A005930"),`), fed by `--instruments` on the command line; the sample instead takes `instruments` as a constructor argument filled from the YAML's `config:`. For a whole-market universe the first means a command line of thousands of ids or a generated .py; neither the scaffold comment nor the make-exchange skill mentions the `config:` route for listings (the skill shows `config:` only for rates).
**What would have told me directly:** a line in the scaffold: "for a large universe, take `instruments` as a constructor argument and list them under `config:`".

### F-006 — Registration says a model sees rows with `available_at <= t`; the run declaration says rows "knowable before each instant"

**Severity:** papercut
**Kind:** message
**Attributable to vqapr?** Yes — two envelopes from the same package state the boundary two ways, and the difference is exactly the case a close-stamped row meets.
**Resolved by:** unresolved (I avoided it by deciding at 16:00, half an hour after the 15:30 stamps)
**Where:** `vqapr register workspace/ff/ff.yaml` (`spoken`) vs `vqapr register workspace/ff/runs.yaml` (`spoken`)
**What I was trying to say:** "at a decision on June's last session, the market cap stamped at that session's 15:30 close is visible"
**What happened:** datasets: "a model reading it at instant t sees rows with available_at <= t". Runs: "sees only rows knowable before each instant". Is a row stamped 15:30 visible to a 15:30 decision? One sentence says yes, the other says no.
**What would have told me directly:** the same inequality, written the same way, in both.

### F-007 — The Fama-French June formation cannot be said: "sort on June's last close and hold from that close"

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** Yes — a decision I had already made (the scenario's own rule) cannot be expressed; the package forbids it by design, and the skill already concedes the gap.
**Resolved by:** asked (which of the two expressible approximations the user accepts; see F-011)
**Where:** run `schedule`/`execution.fill`; `vqapr-make-exchange/references/fill-timing.md`; `vqapr-make-strategy/references/factor-portfolios.md` "What it cannot express exactly"
**What I was trying to say:** "Size and eligibility are measured at June's last close; the book is bought at that close; its first return is June-last-close → July-first-close." That is the Fama-French and Ken French Library convention the scenario names.
**What happened:** a fill is strictly after the decision, and fill-timing.md says "trading at the close on close data is forward-looking. This is settled and will not be reopened... do not offer it as an option." The two expressible variants each move one thing by a session: (A) decide at 16:00 on June's last session, fill at July's first close, so July's first session still earns last year's book; (B) decide at 15:29 on June's last session from the previous session's caps and halts, fill at June's last close. factor-portfolios.md measured (A) at 6 and 5 bp² of daily MSE; (B) "has not been measured".
**What would have told me directly:** nothing will make it expressible, by the package's own ruling. What would have saved time is the factor recipe saying up front that the choice between (A) and (B) is the user's, with both schedules written out, instead of one of them buried under "cannot express exactly".

### F-008 — A leg cannot redeploy money stuck in a delisted or halted holding, so each June its new book is under-bought, and nothing in the declaration can say otherwise

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** Yes — the decision "at each formation, value what cannot be sold at its last price and reinvest the whole leg" (the Fama-French buy-and-hold definition) has no channel; the behaviour is documented, but it changes the result and cannot be switched off.
**Resolved by:** asked (whether to accept the account's treatment; see F-011) — and measured
**Where:** `vqapr run ff-s1 ...` → `vqapr.fill` rows `reason: absent | nontradable | no_trade`; `vqapr-introduce-vqapr/SKILL.md` "What it does not do"
**What I was trying to say:** "Buy the leg at value weights every June with all of the leg's money; a name that stopped trading during the year is worth its last price and that value goes into the new book."
**What happened:** a held name with no row at the fill (`absent`, delisted) or halted (`nontradable`) cannot be sold; it stays in the book at its last price for the rest of the run, and its money cannot fund the new book, so the smallest buys are cut to zero (`no_trade`: `requested_quantity 0` with `sized_quantity` > 0). Measured on my six legs (timing A): money stuck in names the new target did not ask for, right after the fill, reached 5.8% of NAV (S1, 2025), 4.6% (S2, 2026), 3.6% (S3), 3.5% (B1), 0.7% (B2), 1.7% (B3). Against a pandas rebuild of the same membership that liquidates at last price and reinvests fully, the daily leg returns correlate at 0.9998 or higher, but the vqapr legs earn 0.35% to 0.66% a year less (S1 −0.66%, S2 −0.45%, B1 −0.36%, S3 −0.23%, B3 −0.17%, B2 −0.04%), with a daily MSE of 0.4 to 33 bp². The stuck capital also accumulates from year to year, because a delisted name is never removed.
**What would have told me directly:** the drag is documented ("a few percent of such dead capital"). What is missing is a way to *declare* a delisting treatment (for example "a name absent from the execution table is settled at its last price at the next fill"), or at least a run-level number in the envelope, such as dead capital as a share of NAV per rebalance. I had to reconstruct that from `holdings.csv` and `weights.csv`. `no_trade` also names neither the missing cash nor the funding order that caused it.
**Final runs (answers applied):** the most NAV stuck right after a fill, per leg: scenario 1 S1 5.4%, S2 4.7%, S3 3.8%, B1 3.4%, B3 1.9%, B2 0.6%; scenario 2 S1 5.6%, S2 5.3%, S3 3.4%, B1 2.8%, B2 1.6%, B3 1.0%. At factor level, vqapr − pandas rebuild: scenario 1 SMB −0.23%/yr, HML +0.30%/yr (corr 0.9996 / 0.9995, TE 0.45% / 0.49%); scenario 2 SMB −0.28%/yr, HML +0.38%/yr (TE 0.47% / 0.50%).
**Scenario 3 — the same mechanism decided a pre-registered test.** A052670, a separate-statement S1 name (S1 in every formation 2018–2023), was halted at 2,080 KRW through the 2024-07-01 and 2025-07-01 fills. The S1 leg could not sell it either time, so it stayed in the book while the pandas rebuild (and, by its S1 return, kimchi) had dropped it. On 2026-02-09 it resumed at 625,000 KRW (F-021), and the vqapr S1 leg returned +26.4% that day against +3.4% for the pandas rebuild and kimchi. At the 2026-07-01 fill 17.0% of S1's NAV was stuck, 13.0% of it in this one delisted name. For the whole run, vqapr vs pandas fell to SMB corr 0.982 / TE 2.95% and HML 0.959 / TE 4.39% (scenario 2: 0.9996). That single day turned both factor conditions of `SCENARIO-kimchi-sep.md`'s criterion from pass to fail: excluding it (diagnostic only), SMB 0.9947 / 1.61% and HML 0.9872 / 2.39% vs kimchi, both better than scenario 2. The account's treatment is documented, but here it meant a portfolio "held a year at a time" held a name for 2.6 years it was never asked to hold.

### F-009 — Which "book equity" the scenario means, when the statement file has two candidates and one does not cover FY2017

**Severity:** slowed
**Kind:** docs
**Attributable to vqapr?** No — the vendor extract has no account-code dictionary, and the scenario's words fit two lines. That is data and scenario, not package.
**Resolved by:** asked
**Where:** `data/korean_equity/fng_statement_facts/` (253 FnGuide account codes, no labels)
**What I was trying to say:** "B/M = consolidated book equity of the fiscal year ending in t−1 / December t−1 market cap"
**What happened:** I identified the codes from Samsung Electronics' published FY2018 balance sheet (thousand KRW): `4001110000` total assets 339.36조, `4001140000` total liabilities 91.60조, `4001160000` total equity 247.75조, `4001160050` equity attributable to owners of the parent 240.07조. `4001160000` is absent for every firm in FY2016–2017, but assets − liabilities reproduces it to within 1 (thousand KRW) on all but 3 of ~12,700 FY2018+ rows, so FY2017 total equity is recoverable. `4001160050` covers only 223 firms in FY2017 and 297 in FY2018, so a parent-equity definition cannot form the 2018 and 2019 portfolios. Settlement types `4` and `D` agree on both equity codes; `D` sits at each firm's fiscal-year-end month. I proceeded provisionally with total equity.
**Answer (2026-09-14):** book equity = total equity − non-controlling interest, with NCI = 0 when absent; FY2016–17 total equity = total assets − total liabilities (a proxy that affects only the 2018 formation). `SCENARIO-kimchi.md` names the NCI code, `4001167500`. I verified it on Samsung FY2018: 7.684e9 thousand KRW = 247.75 − 240.07조. It is absent for every firm in FY2016–17 and present for 1,144–1,419 firms a year from FY2018. total equity − NCI misses the parent-equity line by more than 1 (thousand KRW) on 8 of ~10,200 rows where both exist.
**What would have told me directly:** an account-code dictionary with the data.

### F-010 — The listing snapshot changes definition in December 2025, and the statements cover almost no financial firms

**Severity:** slowed
**Kind:** docs
**Attributable to vqapr?** No — both are properties of the vendor files. The scenario says to ask rather than adapt silently.
**Resolved by:** asked
**Where:** `data/fng/fgsc_market_rebalance_snapshots_201801_202606.csv`, `fng_statement_facts`
**What I was trying to say:** "the universe is every KOSPI/KOSDAQ common stock at formation, minus SPACs and names halted that day; financials stay in"
**What happened:** (1) The snapshot is the only source of market membership, and it holds only common stocks (every code ends in 0). By row counts, `시` = 1 is KOSPI (~800 names) and `시` = 2 is KOSDAQ (~1,400); `SP` = 1 appears only under `시` = 2. (2) The June snapshots for 2018–2025 contain **no** SPACs and **no** admin-issue (관리종목) names, although 48–119 admin-issue common stocks are priced each June. From 2025-12-30 the snapshot adds 225 names: 81 SPACs flagged `SP` = 1, plus 144 others, 94 of them admin-issue. The June-2026 snapshot therefore contains 103 admin-issue names that no earlier June did. (3) Financial firms (FGSC 40) carry a single account code per period (e.g. KB금융 `4002460100`), so only 7–11 of 70–102 financials (22 of 182 in 2026) have book equity. The rest leave the sort, and financials are 6–12% of big-cap market cap. Overall, 22% of each June universe has no annual consolidated statement. I proceeded provisionally: exclude `SP` = 1, keep 2026 admin-issue names, and let names without book equity drop out.
**Answer (2026-09-14):** `시` 1 = KOSPI, 2 = KOSDAQ, confirmed. From December 2025, exclude SPACs, keep admin-issue names, and note the coverage change in the results. **The user changed the rule: financials (FGSC.40) are now excluded**, and `SCENARIO.md` was updated.
**What would have told me directly:** a data note on the snapshot's inclusion rules, and financial-company statements.

### F-011 — Three conventions the scenario leaves open once vqapr's limits are known: formation timing, delisted holdings, the daily CD rate

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** No — each is the user's call. vqapr's part in the first two is filed separately (F-007, F-008).
**Resolved by:** asked
**Where:** `SCENARIO.md` rules vs `workspace/ff/runs.yaml`
**What I was trying to say:** the scenario's rules, exactly
**What happened:** (a) Timing: variant A (decide 16:00 on June's last session, fill at July's first close) or B (decide 15:29 on the previous session's data, fill at June's last close); I ran A provisionally. (b) Delisted and halted holdings: accept the account's treatment (F-008), or report something else as the main series? (c) "일별 환산값" of CD91: (1 + CD/100)^(1/252) − 1 on the same day reproduces kimchi's RF to 1e-17, while CD/100/365 is off by 2.7e-5 a day; I used the former provisionally.
**Answer (2026-09-14):** (a) variant A, with the results marking that July's first session earns the previous portfolio's return; (b) vqapr's result is the main series, and the pandas rebuild (liquidate at last price, reinvest everything) is also compared with kimchi, with the gap shown; (c) (1 + y/100)^(1/252) − 1 on the same day. The four choices I made myself stand.
**What would have told me directly:** n/a (scenario questions)

### F-012 — `AcademicExchange` is documented as "full-fill", yet 2,500+ buys dealt zero; the funding rule that explains it is documented only for `krx`

**Severity:** urge
**Kind:** docs
**Attributable to vqapr?** Yes — the only statement of how buys are funded and cut ("largest money delta first") sits under the `krx` profile, and the academic profile's own docstring says "full-fill".
**Resolved by:** guess (inferred from the `krx` text plus `requested_quantity 0` / `sized_quantity > 0` in `fills.csv`)
**Where:** `vqapr.public.AcademicExchange.__doc__` ("Zero-friction, full-fill execution"); `vqapr-make-exchange/references/execution-profiles.md` (funding order described under `krx`); `fills.csv` `reason: no_trade`
**What I was trying to say:** "is `no_trade` on a frictionless divisible venue a cash shortfall or a venue refusal?"
**What happened:** I wanted to open the academic execution code to confirm the funding and cut rule. I did not. I reasoned from the `krx` description and from the stuck-capital numbers (the weight gap after each fill equals the stuck share to 4 digits) that it is the same cash-first rule. I still have not verified whether academic funds largest-first. Later I found in `vqapr-analyze-result/references/panels-from-tables.md` that `reason` can also be `unfunded`, and that "On KRX the order is already cut to the cash". On this academic venue the cut buys come out as `no_trade` (requested 0), not `unfunded`, so the same shortfall carries a different reason code per profile, and only one of them is described.
**What would have told me directly:** the funding/cut rule stated once for both profiles, and `no_trade` carrying `unfunded` or the cash shortfall.

### F-013 — The skill says re-registering a dataset "replaces it in place, with no flag"; the package refuses a changed dataset declaration with 409

**Severity:** slowed
**Kind:** docs
**Attributable to vqapr?** Yes — `register-dataset/SKILL.md` and `references/correcting-a-registration.md` both state the replace-in-place loop for declarations, and the package's own dataset template says the opposite ("Registrations are immutable").
**Resolved by:** surface — `vqapr rm dataset ff-book-equity` was accepted, even though registered runs name components that read it, and then the whole document registered. I had half expected the rm to be refused ("Refused while a registered run still names it").
**Where:** `vqapr register workspace/ff/ff.yaml` after adding two fields (`nci`, `book_equity`) to `ff-book-equity`
**What I was trying to say:** "same dataset, corrected: it now also exposes book equity net of NCI"
**What happened:** `[409 dataset.registered] dataset_id 'ff-book-equity' must keep its existing declaration or use a new identity`; `fix`: "keep the registered declaration for 'ff-book-equity' unchanged, or choose a new dataset_id". The document was refused whole (`mutation: false`), so `ff-prices`, whose declaration had not changed but whose file had, was not re-measured either. The skill says: "Registering the same id again replaces it in place, with no flag; there is no `register --force`. A `runs:` declaration is the exception." correcting-a-registration.md says: "It replaces the registration in place ... The success payload then carries `replaced: {fingerprint: <the old one>}`".
**What would have told me directly:** the skill naming datasets as a second exception beside `runs:`, with the route (a new id, or `vqapr rm dataset <id>` first, if that is permitted).

### F-014 — `vqapr check` reports a changed source file as a `blocked` judgment carrying a raw Python traceback

**Severity:** papercut
**Kind:** message
**Attributable to vqapr?** Yes — the same condition reaches `km-s1` as a structured `dataset.source_changed` failure with a `fix`, and reaches `ff-s1` as a blocked phase whose cause is a traceback through package internals.
**Resolved by:** surface (the km-s1 envelope named the fix)
**Where:** `vqapr check ff-s1` after rewriting `prices.parquet` under the registered `ff-prices`
**What I was trying to say:** "is this run ready?"
**What happened:** `blocked: [{cause: {message: "freeze: 1 failure(s) [412 dataset.source_changed] ...", traceback: "Traceback (most recent call last): File ...\\.venv\\Lib\\site-packages\\vqapr\\run\\preflight\\checks.py ..."}}]`. No `fix` field, no `observed` digests. The envelope put package file paths and line numbers in front of me. I did not open them.
**What would have told me directly:** the structured `dataset.source_changed` failure `km-s1` got: "register dataset 'ff-book-equity' again so its facts are measured on the file as it is now".
Same pattern in scenario 3: `vqapr check ks-s1`, run before the run was registered, returned a well-formed `run.unregistered` (404) with a good `fix`. Its `cause`, though, held `type: "KeyError"`, `message: "'ks-s1'"` and a traceback through `vqapr\workspace\references.py`.

### F-015 — `vqapr rm run` deletes the record but leaves the run's `writes` dataset naming it, so the next `check` is refused as stale

**Severity:** papercut
**Kind:** code
**Attributable to vqapr?** Yes — the package let me remove the record that an output's provenance still names; the refusal that followed is clear, but the dangling state came from `rm`.
**Resolved by:** surface (`fix`: "vqapr run ff-s1 --force to rewrite it from the current component")
**Where:** `vqapr rm run ff-s1` (provisional records), then `vqapr check ff-s1`
**What I was trying to say:** "throw away the provisional records so the next run leaves one clean record per leg"
**What happened:** `rm run` answered `removed: ["ff-s1@c9855fa5", "record.json"]` and said nothing about `ff-s1-weights`. Then `check`: `[412 run.output_stale] 'ff-s1-weights' was written by record 'ff-s1@c9855fa5'; the registered component is 'ff-s1@3e05e371'`. That names a record that no longer exists. `rm --help` mentions only the materialized datasets of *datamodels* under `--cascade`.
**What would have told me directly:** `rm run` either removing or naming the `writes` dataset it leaves behind ("ff-s1-weights still carries rows from this record; the next run needs --force").

### F-016 — The `fix` that `check` gives for a stale run output (`vqapr run <id> --force`) is itself refused with 409

**Severity:** slowed
**Kind:** code
**Attributable to vqapr?** Yes — a documented verb and option, named in the package's own `fix`, did not do what its help says ("--force: replace this run's record ... and the dataset it published").
**Resolved by:** guess (`vqapr rm dataset ff-<leg>-weights` for each of the six, then a plain `vqapr run`, the same route that worked in F-013)
**Where:** `vqapr run ff-s1 ... ff-b3 km-s1 ... km-b3 --jobs 4 --force`
**What I was trying to say:** "rewrite the six scenario-1 legs from the current components", exactly what `check` told me to run
**What happened:** the six km runs (new ids) completed. Every ff run failed at `stage: register`: `[409 dataset.registered] dataset_id 'ff-s1-weights' must keep its existing declaration or use a new identity`, `fix`: "keep the registered declaration ... or choose a new dataset_id". I cannot change a `writes` dataset's declaration; the run derives it. `check` had passed `preflight` and reported only `run.output_stale` with `fix: "vqapr run ff-s1 --force"`, so the check promised a run that the run then refused.
**What would have told me directly:** `--force` replacing the published dataset, as its help says; or the `check` fix naming `vqapr rm dataset ff-s1-weights` when the output's declaration will change.

### F-017 — A run that reported `ok: false` had already written a `completed` record, so the plain retry was refused with `record.exists`

**Severity:** papercut
**Kind:** code
**Attributable to vqapr?** Yes — a failed run left durable state that `vqapr list strategies` shows as `completed`, and neither the failing envelope nor its `fix` said so.
**Resolved by:** surface (the `record.exists` refusal named `vqapr run ff-s1 --force`, which then worked)
**Where:** the `--force` batch in F-016, then `vqapr run ff-s1 ... ff-b3 --jobs 3` after withdrawing the six `ff-*-weights` datasets
**What I was trying to say:** "the failed batch did nothing; run it again"
**What happened:** the failing envelope was `ok: false`, `stage: register`, with only the 409 on `ff-s1-weights`. After that, `vqapr list strategies --run ff-s1` showed `ff-s1@3e05e371`, `status: completed`, `account_version: 9`, while `vqapr list datasets --id ff-s1-weights` showed nothing. The plain retry: `[409 record.exists] a strategy record is written once per run and fingerprint`. Three rounds (`--force`, `rm dataset` × 6 then plain, then `--force` again) to rewrite six legs.
**What would have told me directly:** the failing envelope saying "the record ff-s1@3e05e371 was written; its output dataset was not published", or the run publishing and recording all-or-nothing.

### F-018 — Kimchi's weighting, "each day by the previous session's market cap", cannot be said; a leg can only buy at formation weights and drift with its own prices

**Severity:** papercut
**Kind:** code
**Attributable to vqapr?** Yes — a decision the second scenario states outright has no channel: a held book drifts with the execution price only, and a daily re-weighting would fill one session after it was decided.
**Resolved by:** unresolved in vqapr (built as buy-and-hold from formation market cap; the stated weighting was computed in pandas as a diagnostic)
**Where:** `SCENARIO-kimchi.md` data table ("VW 가중치: 직전 거래일 시가총액"); run `schedule`/`fill`
**What I was trying to say:** "the bucket's return on day t is the average of its members' returns weighted by their market cap on day t−1", so that share issuance and buybacks move the weights as well as prices
**What happened:** the account holds shares bought at formation, and nothing between two decisions can re-weight it. `every: 1d` with a decision after the close fills at the next close, so the weights of day t would be those of t−1's decision: a session late and a full rebalance every day. Measured in pandas on the same membership: vqapr vs the lagged-market-cap series, SMB corr 0.9991, TE 0.68%/yr; HML corr 0.9987, +0.73%/yr, TE 0.80%/yr. Against kimchi, the lagged-market-cap series is no closer than the vqapr one (SMB 0.991 both, HML 0.980 both).
**What would have told me directly:** a sentence in `factor-portfolios.md` that a factor leg is buy-and-hold by shares, so a "lagged market-cap" definition, whose weights also move with share counts, is not expressible and differs by the share-count changes.

### F-019 — Nothing says which price field values the book when an execution table carries more than one

**Severity:** papercut
**Kind:** docs
**Attributable to vqapr?** Yes — the template says an execution table's numeric fields "are the prices a run may choose from" for fills; how held names are marked between fills is not stated anywhere I could reach.
**Resolved by:** guess (avoided). I registered the Kimchi price series as its own dataset, `km-prices`, on the same parquet, with `close: ret_close` as its only price, rather than adding `ret_close` to `ff-prices` and choosing it with `trade_price`.
**Where:** `vqapr new dataset` template (`execution:` comment), `run-declaration.md`, `panels-from-tables.md` (`price_fields`, `fill.trade_price`)
**What I was trying to say:** "fill and value the scenario-2 legs at the `return`-compounded price, and the scenario-1 legs at the adjusted close, from one table"
**What happened:** the docs describe the fill price (`trade_price`) and say "the book is valued at every instant of the market clock", but not at which field. With two numeric price fields in one table, a leg could fill at one and be marked at the other without any message.
**What would have told me directly:** "holdings are marked at the run's `trade_price` field" (or whichever rule holds), in the run template.

### F-020 — My scenario-3 book-equity file stamped every row 2017-03-31 (a pandas index misalignment), caught by my own key assertion

**Severity:** papercut
**Kind:** code
**Attributable to vqapr?** No — pandas and my own preparation code; vqapr never saw the file.
**Resolved by:** guess (debug print, then localize on the frame's own index with `Series.dt.tz_localize`, plus a Samsung FY2018 round-trip assertion)
**Where:** `workspace/prepare_ks_book_equity.py`
**What I was trying to say:** "available_at = 00:00 KST on the last day of the 3rd month after the period end", as in scenario 2
**What happened:** `be.insert(0, "available_at", <Series with a fresh RangeIndex>)` aligned on index labels, and after filtering and concatenation `be`'s labels were not 0..n. The result: 12,373 rows sharing (`available_at`, instrument), all at 2017-03-31. My `assert not be.duplicated([...])` stopped it. Registration would have refused the duplicate key too, but a misalignment that happened to stay unique would have registered and passed every check: the look-ahead the register-dataset skill warns about, produced by a pandas idiom.
**What would have told me directly:** n/a (my code). The skill's timezone round-trip on one known row, which I had skipped in this second preparation script, would have caught it.

### F-021 — The price file carries an unadjusted capital reduction: A052670 `return` = +299.48 (+29,948%) on 2026-02-09

**Severity:** slowed
**Kind:** docs
**Attributable to vqapr?** No — a vendor-data defect. vqapr cannot know that a 300× session is not a real price move; its part (it kept holding the name) is F-008.
**Resolved by:** unresolved (left in the data: `SCENARIO-kimchi-sep.md` fixes the rules before results, and the scenario prescribes the file's `return` column)
**Where:** `data/korean_equity/adjusted_prices.parquet`, ticker A052670
**What I was trying to say:** "the stock's return on the day it resumed trading"
**What happened:** after a halt at 2,080 KRW (622 halted sessions), 2026-02-09 shows `종가` 625,000, `전일종가` 2,080, `adjustment_multiplier` 1.0, `return` 299.480769, `adj_close` 625,000. `market_cap` falls from 60.6B to 12.1B KRW, so the share count fell about 1,500×, which is not reflected in the adjustment. The name delisted on 2026-02-20. It reached the results only because the vqapr S1 leg was still holding it (F-008). It cost the diagnosis of why scenario 3's factor metrics worsened while its stock counts matched.
**What would have told me directly:** a corporate-action flag in the price file, or an adjustment factor on the resumption day.

## Where I stopped

- **Scenario 3 (`SCENARIO-kimchi-sep.md`) — done.** `ks-book-equity` (consolidated, else separate: 18,637 consolidated rows identical to scenario 2, plus 264–666 separate firm-years a year), six `ks-*` legs registered, checked, run `completed` (envelope in `workspace/logs/ks_run.json`), series built into `outputs/kimchi-matched-sep/`, compared, and the pre-registered criterion applied as written.
  - **Verdict: criterion not met.** S3's mean stock count stays 6.2% below kimchi (the other five buckets are within 3.6%), and the vqapr factor correlation and TE vs kimchi are worse than scenario 2 (SMB 0.980 / 3.16% vs 0.991 / 2.06%; HML 0.951 / 4.77% vs 0.980 / 2.99%).
  - The counts nonetheless close from about −20% to about −2.5% per formation year (−9.2% in 2026). The factor failure comes from a single day, F-008 × F-021.
  - No new package friction in scenario 3 beyond the F-014 addendum. My own mistakes: F-020, and running `compare_sep.py` from the wrong directory (a relative-path error that wrote nothing).
  - `outputs/kimchi-matched-sep/SUMMARY.md` was not written (harness restriction on `.md` report files); the text went back in my report.
- **Logs:** an earlier cleanup, before I was asked to keep `workspace/logs/`, had already deleted `trial_run.json/.err` and `legs_run.json/.err` (the provisional scenario-1 runs behind F-008's first numbers and F-012). `final_run_ff.json` was overwritten by the successful `--force` rerun, so the failing `record.exists` envelope behind F-017 is not preserved. The F-016 envelope is intact in `final_run.json`.
- **Asked for:** (1) `SCENARIO.md`: daily Korean FF3 (RMRF, SMB, HML) and the six 2×3 portfolios from the June-2018 formation to the last data day, built with vqapr and compared with kimchi, with a one-page summary in `outputs/`. (2) `SCENARIO-kimchi.md`: the same factors matched to the Kimchi methodology and data definitions in `outputs/kimchi-matched/`, with bucket-level (`n_stocks`) and three-way comparisons.
- **Done, both scenarios, with the 2026-09-14 answers:** timing A with `prior_book_day` marked; book equity = total equity − NCI; financials excluded; SPACs excluded and admin-issue names kept from 2025-12; CD compounded over 252 days; price returns. Twelve stock legs and one market leg are registered, checked and `completed`. Each scenario's series come from `vqapr export` NAVs, with a pandas rebuild (liquidate at last price, reinvest) and, for scenario 2, a lagged-market-cap diagnostic. Comparison CSVs are written.
- **Headline:** scenario 1 vs kimchi: SMB corr 0.966, HML 0.870, RMRF 1.000. Scenario 2 vs kimchi: SMB 0.991, HML 0.980. Matching the B/M denominator (June ME) moves B3 from 0.890 to 0.994. What remains is data-side (price vs total return; 15–25% fewer names per bucket, because ~22% of each June universe has no annual consolidated statement in the file) plus the account's stuck capital (F-008).
- **Not written:** the one-page `outputs/SUMMARY.md` and `outputs/kimchi-matched/SUMMARY.md`. The session's file tool refused `.md` report files from a subagent. This is a harness restriction, not vqapr; the content went back in my final report for the main session to write.
- **Cost of the step-2 rerun:** F-013 → F-017: a changed dataset declaration refused although the skill says it replaces; the `check` fix (`run --force`) refused; a failed run left a completed record. Three rounds of rm/rerun to rewrite six legs.
- **Cleaned up:** `workspace/exports/` (881 MB of leg exports), provisional results, scratch, sample and scaffold copies, superseded scripts. Kept: `workspace/prepared/` (the registered sources), `workspace/ff/` (generator, legs, declarations, build and compare scripts), `.vqapr/` (records), `workspace/logs/` (final run envelopes).

---

## Evaluator triage (2026-09-14)

**Wheel.** `vqapr-0.16.0` built from tag `v0.16.0` (`3a52646d`).

**Scenarios.** Three, all run by one agent session with no prior vqapr context. Each builds daily
Korean FF3 factors with vqapr:

1. Canonical Fama-French rules.
2. Matched to the Kimchi Factor methodology.
3. As 2, plus a separate-statement fallback for book equity.

**How the findings were verified.** Every `Yes` finding was re-checked against the public surface
of the wheel. Three verifier sessions did this in scratch workspaces with synthetic data and read
no package source. Every report below is in `docs/issues/report-2026-09-14-*.md`, marked
`UNTRIAGED`.

| finding | verdict | filed as (`report-2026-09-14-…`) |
|---|---|---|
| F-002 | confirmed, and broader: 54 of 239 public docstrings cite internal documents or non-public module paths; 8 are in Korean | `public-docstrings-cite-internal-documents-the-wheel-does-not-ship`, `registration-and-error-docstrings-are-in-korean` |
| F-003 | confirmed | `skills-say-a-statement-lag-is-declared-at-registration-but-registration-takes-only-a-column` |
| F-004 | partial: the private import is confirmed; "no word on which constructor" did not reproduce | `sample-strategy-imports-from-private-vqapr-domain-intent` |
| F-005 | confirmed | `exchange-scaffold-inlines-listings-with-no-documented-route-for-a-large-universe` |
| F-006 | confirmed: a row stamped at the decision instant is read by that decision, so the run sentence is the wrong one | `run-register-says-rows-before-each-instant-but-a-row-stamped-at-the-instant-is-read` |
| F-007 | not filed: ruled WON'T FIX in `archive/064` | — |
| F-008 | confirmed; scenario 3 evidence added | `money-in-a-delisted-or-halted-holding-cannot-fund-the-next-book` |
| F-012 | partial: "full-fill" vs cut buys is confirmed; the per-profile reason code did not reproduce (both profiles record `no_trade`) | `academic-exchange-documented-as-full-fill-cuts-buys-to-zero` |
| F-013 | confirmed | `register-refuses-changed-dataset-declaration-skill-says-replaces` |
| F-014 | partial: the trigger is a stale **execution** dataset, not which run is checked | `stale-execution-dataset-reported-as-raw-traceback` |
| F-015 | partial: `rm run` leaves dangling provenance and says nothing; the `output_stale` refusal comes from the component edit | `rm-run-leaves-output-naming-removed-record` |
| F-016 | confirmed, only inside a `--jobs` batch | `run-force-in-a-jobs-batch-refused-with-409-dataset-registered` |
| F-017 | confirmed | `failed-run-leaves-completed-record-so-retry-refused` |
| F-018 | not filed: the "previous-session market cap" rule came from the evaluator's own scenario wording, and buy-and-hold differs from it only by share-count changes | — |
| F-019 | confirmed as a documentation gap; observed behaviour is marking at `trade_price` | `docs-never-say-which-price-field-marks-held-names` |
| F-001, F-009–F-011, F-020, F-021 | `No`: testbed setup, vendor data, scenario questions, the agent's own error, and an unadjusted capital reduction in the vendor price file | — |

**Found during verification and filed**, each reproduced at least twice:

- `deliberate-refusals-label-the-vqapr-launcher-as-user-code`
- `rm-dataset-accepted-while-a-registered-runs-strategy-reads-it`
- `check-repeats-unregistered-input-as-raw-keyerror-traceback`
- `check-reports-only-one-changed-source-file-per-call`
- `academic-rebalance-proceeds-when-a-name-has-no-row-at-the-fill-though-the-skill-says-it-is-refused-whole`
- `new-out-resolves-against-the-current-directory-while-its-envelope-pairs-the-relative-path-with-workspace-root`
- `unknown-key-fix-suggests-a-key-the-declaration-already-has-and-carries-a-package-traceback`
- `krx-scaffold-points-at-price-fields-which-registration-refuses`

**Seen, not filed:**

- An absent held name and a halted one lead to different buy sizing. One verifier saw this once
  per profile; it was not reproduced independently.
- The same retry state is answered `run.output_registered` in a single process and `record.exists`
  inside `--jobs` workers. Both fixes work.
- `KrxExchange` defaults `price_limits` to `None` and its docstring says "off by default",
  while `krx_listings` and `krx_rules` default it to `True`.

**Log caveat.** Before the evaluator asked it to keep logs, the testbed agent deleted
`trial_run.json` and `legs_run.json` and overwrote `final_run_ff.json`. So these rest on
`FINDINGS.md` plus the verifiers' reproductions:

- F-008's first numbers
- F-012's original envelope
- F-017's failing envelope
