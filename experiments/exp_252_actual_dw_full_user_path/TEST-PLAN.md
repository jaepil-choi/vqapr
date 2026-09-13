# Fixed test plan — actual DW full user path

Frozen: 2026-09-12 KST. Do not change the period, universe, fields, cadence, ranking, or strategy
count after baseline timing starts. A necessary correction that changes economic meaning creates
a new experiment ID.

## Reality contract

- Source files are the user's actual `/Users/jason/qlibx/DW` files, never generated market data.
- Use the maximum common 2018-01-02 through 2026-07-20 period.
- Keep all source rows during normalization. Filter the model's economic universe only by the
  supplied historical KOSPI 200 membership, retaining all 309 names ever observed there.
- DataModel fires daily and physically materializes reusable factor rows.
- Five strategies consume that registered result and fire on the last session of every week.
- Each strategy selects its eligible cross-section, buys the top 30, and sells the bottom 30.
- No artificial CPU loop, sleep, duplicated row, duplicated day, or enlarged synthetic universe.
- A full path longer than ten minutes is preferred, but an honest shorter maximum is accepted.
- Preparation is not allowed to dominate silently. Factor/model arithmetic must exceed 50% of
  the measured first full journey to earn a `high` reality grade.

## Inputs and meanings used for the benchmark

- Price close is stamped 15:30 Asia/Seoul on its trading date.
- Same-day volume, turnover, and share count are stamped 18:00 Asia/Seoul.
- Daily valuation and consensus are stamped 18:00 Asia/Seoul.
- Membership is treated as known at 08:00 on the supplied effective date.
- Strategy decision is 08:30; execution is the same session's 15:30 close.
- Consumer runs begin one day after the producer period begins, so the first 08:30 decision can
  read the prior 18:30 materialized row. No source day is removed from the producer.
- These are explicit benchmark assumptions, not facts proven by the files. In particular, the
  vendor dates do not prove original publication or revision times. The final report must state
  that investment-valid point-in-time semantics remain unverified.

## Fixed physical datasets

1. `prices`: close, volume, turnover from `fng_stock_daily_prices.csv`.
2. `shares`: listed and free-float-like share counts from
   `fng_daily_indicator_share_counts.csv`.
3. `valuation`: beta, forward PER, PBR, EV/EBITDA and forward profit fields from
   `dw_fng_mirror/dw_fng_valuation.parquet`.
4. `consensus`: sales, operating profit, net debt, and owner profit from
   `dw_fng_mirror/dw_fng_daily_consensus.parquet`.
5. `membership`: historical KOSPI 200 membership and supplied index weight from
   `fng_k200_members.csv`.
6. `execution`: same actual close and an explicit tradability approximation from the price file.

## Fixed model calculation

- Recent returns: 5, 10, 20, and 31 sessions.
- Stability: 31-session return standard deviation and downside share.
- Liquidity: recent volume and turnover change.
- Value: inverse forward PER, inverse PBR, inverse EV/EBITDA.
- Expectations: changes in forward EPS, sales, operating profit, owner profit, and net debt.
- Size: price times listed shares.
- Eligibility: historical membership, finite inputs, positive close, and usable execution row.
- Each daily cross-section is clipped at the 2nd and 98th percentiles, ranked, centered, and
  combined into five fixed scores: momentum, balanced, value-quality, low-vol-momentum, and
  earnings-momentum.
- DataModel writes the five scores plus eligibility. Strategies do no raw-table joins.

## Exact local SQL boundary

The preparation and SQL-comparison variant use only ephemeral DuckDB connections and write below
this experiment. No persistent or external database is accessed. The executable script must keep
the following logical query shapes unchanged:

```sql
COPY (
  SELECT timezone('Asia/Seoul', strptime(CAST(거래일자 AS VARCHAR), '%Y%m%d')
                  + INTERVAL '15 hours 30 minutes') AS available_at,
         종목약코드 AS instrument,
         TRY_CAST(종가 AS DOUBLE) AS close,
         TRY_CAST(거래량 AS DOUBLE) AS volume,
         TRY_CAST(거래대금 AS DOUBLE) AS turnover
  FROM read_csv_auto(<actual price csv>, header=true)
  WHERE 거래일자 BETWEEN 20180102 AND 20260720
) TO <experiment prices parquet> (FORMAT PARQUET, COMPRESSION ZSTD);
```

```sql
COPY (
  SELECT timezone('Asia/Seoul', strptime(일자, '%Y%m%d') + INTERVAL '18 hours') AS available_at,
         기업코드 AS instrument,
         결산년월,
         AVG(TRY_CAST(매출액 AS DOUBLE)) AS sales,
         AVG(TRY_CAST(영업이익 AS DOUBLE)) AS operating_profit,
         AVG(TRY_CAST(순부채 AS DOUBLE)) AS net_debt,
         AVG(TRY_CAST(지배주주순이익 AS DOUBLE)) AS owner_profit
  FROM read_parquet(<actual consensus parquet>)
  WHERE 일자 BETWEEN '20180102' AND '20260720'
  GROUP BY available_at, instrument, 결산년월
  QUALIFY 결산년월 = MAX(결산년월) OVER (PARTITION BY available_at, instrument)
) TO <experiment consensus parquet> (FORMAT PARQUET, COMPRESSION ZSTD);
```

- Equivalent fixed projections are used for shares, valuation, membership, and execution.
- Duplicate consensus rows are collapsed by the stated average and latest fiscal period. This is
  a declared normalization needed to create one instrument-day fact; it is identical for every
  compared version.
- The direct-SQL variant computes the same formulas from these canonical Parquet files and writes
  the same declared factor schema. Its values must pass the same equality tolerance; otherwise it
  is rejected as a different calculation.

## Variants fixed before measurement

- `B0`: untouched v0.15.0, daily DataModel materialization, then five strategies.
- `C1`: candidate engine, exactly the same DataModel and strategies.
- `A1 direct`: five strategies each recompute the raw factors; tests repeated work without a
  reusable materialized result.
- `A2 materialized`: one DataModel materialization followed by five consumers; this is the main
  public two-stage path.
- `A3 SQL`: ephemeral DuckDB computes the identical daily factor table once; the five public
  strategy runs consume the registered table.
- `A4 incremental`: preserve the prior materialized factor partition and compute only a fixed
  final 20-session extension. Compare with full rematerialization for that same extended end.
- A persistent server database is assessed but not installed unless baseline profiling shows
  source scanning/joining is the largest stage. Otherwise its setup would test a new deployment,
  not the measured bottleneck.

## Measurements

- Hash every source and canonical input.
- Record dependency versions and machine CPU/RAM.
- Measure each public command separately: new/scaffold, prepare, register, check, producer run,
  dataset list/show, consumer register/check, one consumer, five serial, five `--jobs 4`, result
  list/show/export.
- Record first run and two repeat runs; compare medians only for repeated measurements.
- External sampler: wall time, user/system CPU, maximum process-tree RSS every 100 ms.
- Internal/profiler categories: source scan, panel construction, data access, join/alignment,
  factor arithmetic, ranking, plan, exchange, account/valuation, record writing, export.
- Keep raw JSON, stdout, profiles, manifests, and parity results in `outputs/`.

## Pass, reject, and reporting rules

- Do not delete a slow or failed run from the report.
- Do not compare a warm candidate with a cold baseline as if it were an engine gain.
- Do not use registration or preparation speed to claim a strategy-compute improvement.
- A candidate is accepted only with full output equality and the thresholds in the ExecPlan.
- Parallel RSS is a process-tree sum and can double-count shared mapped pages; label it clearly.
- Final report must distinguish measured facts, source assumptions, and projections.
