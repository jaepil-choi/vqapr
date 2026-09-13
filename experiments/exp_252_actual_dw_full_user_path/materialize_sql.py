# ruff: noqa: E501
"""Attempt the fixed daily factor calculation as one local DuckDB SQL statement."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import duckdb


def quoted(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    source = args.input.resolve()
    destination = quoted(args.output)
    con = duckdb.connect()
    con.execute("SET TimeZone='Asia/Seoul'")
    con.execute("SET threads=8")
    for name in ("prices", "shares", "valuation", "consensus", "membership"):
        con.execute(
            f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{quoted(source / f'{name}.parquet')}')"
        )

    query = r"""
    WITH
    instruments AS (SELECT DISTINCT instrument FROM membership),
    days AS (SELECT DISTINCT available_at AS price_at FROM prices),
    grid AS (
      SELECT d.price_at, i.instrument
      FROM days d CROSS JOIN instruments i
    ),
    joined AS (
      SELECT g.*,
        p.close, p.volume, p.turnover,
        s.listed_shares, s.investable_shares,
        v.beta, v.forward_eps, v.forward_per, v.pbr, v.ev_ebitda, v.profit_12m,
        c.sales, c.operating_profit, c.net_debt, c.owner_profit,
        m.member, m.index_weight
      FROM grid g
      LEFT JOIN prices p ON p.available_at = g.price_at AND p.instrument = g.instrument
      LEFT JOIN shares s ON s.available_at = g.price_at + INTERVAL '2 hours 30 minutes'
                        AND s.instrument = g.instrument
      LEFT JOIN valuation v ON v.available_at = g.price_at + INTERVAL '2 hours 30 minutes'
                           AND v.instrument = g.instrument
      LEFT JOIN consensus c ON c.available_at = g.price_at + INTERVAL '2 hours 30 minutes'
                           AND c.instrument = g.instrument
      LEFT JOIN membership m ON m.available_at = g.price_at - INTERVAL '7 hours 30 minutes'
                            AND m.instrument = g.instrument
    ),
    windows AS (
      SELECT *,
        lag(close, 1) OVER w AS close_1,
        lag(close, 5) OVER w AS close_5,
        lag(close, 10) OVER w AS close_10,
        lag(close, 20) OVER w AS close_20,
        lag(close, 30) OVER w AS close_30,
        last_value(listed_shares IGNORE NULLS) OVER w2 AS listed_last,
        last_value(investable_shares IGNORE NULLS) OVER w2 AS investable_last,
        last_value(member IGNORE NULLS) OVER w1 AS member_last,
        last_value(index_weight IGNORE NULLS) OVER w1 AS index_weight_last,
        last_value(beta IGNORE NULLS) OVER w31 AS beta_last,
        last_value(forward_eps IGNORE NULLS) OVER w31 AS eps_last,
        first_value(forward_eps IGNORE NULLS) OVER w31 AS eps_first,
        last_value(forward_per IGNORE NULLS) OVER w31 AS per_last,
        last_value(pbr IGNORE NULLS) OVER w31 AS pbr_last,
        last_value(ev_ebitda IGNORE NULLS) OVER w31 AS ev_last,
        last_value(profit_12m IGNORE NULLS) OVER w31 AS profit_last,
        first_value(profit_12m IGNORE NULLS) OVER w31 AS profit_first,
        last_value(sales IGNORE NULLS) OVER w31 AS sales_last,
        first_value(sales IGNORE NULLS) OVER w31 AS sales_first,
        last_value(operating_profit IGNORE NULLS) OVER w31 AS operating_last,
        first_value(operating_profit IGNORE NULLS) OVER w31 AS operating_first,
        last_value(net_debt IGNORE NULLS) OVER w31 AS debt_last,
        last_value(owner_profit IGNORE NULLS) OVER w31 AS owner_last,
        avg(turnover) OVER w20 AS turnover_mean,
        last_value(volume IGNORE NULLS) OVER w20 AS volume_last,
        first_value(volume IGNORE NULLS) OVER w20 AS volume_first
      FROM joined
      WINDOW
        w AS (PARTITION BY instrument ORDER BY price_at),
        w1 AS (PARTITION BY instrument ORDER BY price_at ROWS BETWEEN CURRENT ROW AND CURRENT ROW),
        w2 AS (PARTITION BY instrument ORDER BY price_at ROWS BETWEEN 1 PRECEDING AND CURRENT ROW),
        w20 AS (PARTITION BY instrument ORDER BY price_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w31 AS (PARTITION BY instrument ORDER BY price_at ROWS BETWEEN 30 PRECEDING AND CURRENT ROW)
    ),
    daily AS (
      SELECT *, close / close_1 - 1.0 AS daily_return
      FROM windows
    ),
    raw AS (
      SELECT *,
        0.15*(close/close_5-1) + 0.20*(close/close_10-1)
          + 0.30*(close/close_20-1) + 0.35*(close/close_30-1) AS momentum_raw,
        -stddev_pop(daily_return) OVER w30 AS volatility_raw,
        -avg(CASE WHEN daily_return < 0 THEN 1.0 ELSE 0.0 END) OVER w30 AS downside_raw,
        ln(1 + turnover_mean) AS liquidity_raw,
        volume_last / volume_first - 1.0 AS volume_change_raw,
        (-ln(1+abs(per_last)) - ln(1+abs(pbr_last)) - ln(1+abs(ev_last))) / 3 AS value_raw,
        ((operating_last/greatest(abs(sales_last),1.0))
          + (owner_last/greatest(abs(sales_last),1.0))
          + 0.5*(-debt_last/greatest(abs(sales_last),1.0))
          + 0.25*(-abs(beta_last-1.0))) / 2.75 AS quality_raw,
        ((eps_last/eps_first-1.0) + (profit_last/profit_first-1.0)
          + 0.5*(sales_last/sales_first-1.0)
          + 0.75*(operating_last/operating_first-1.0)) / 3.25 AS expectations_raw,
        -ln(1 + close*listed_last) AS size_raw,
        ln(1 + greatest(investable_last,0.0)) AS investable_raw,
        coalesce(index_weight_last,0.0) AS benchmark_raw,
        member_last > 0 AND close > 0 AND listed_last > 0 AS eligible
      FROM daily
      WINDOW w30 AS (PARTITION BY instrument ORDER BY price_at ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
    ),
    quantiles AS (
      SELECT *,
        quantile_cont(momentum_raw, [0.02,0.98]) FILTER (eligible AND isfinite(momentum_raw)) OVER (PARTITION BY price_at) AS q_momentum,
        quantile_cont(volatility_raw, [0.02,0.98]) FILTER (eligible AND isfinite(volatility_raw)) OVER (PARTITION BY price_at) AS q_volatility,
        quantile_cont(downside_raw, [0.02,0.98]) FILTER (eligible AND isfinite(downside_raw)) OVER (PARTITION BY price_at) AS q_downside,
        quantile_cont(liquidity_raw, [0.02,0.98]) FILTER (eligible AND isfinite(liquidity_raw)) OVER (PARTITION BY price_at) AS q_liquidity,
        quantile_cont(volume_change_raw, [0.02,0.98]) FILTER (eligible AND isfinite(volume_change_raw)) OVER (PARTITION BY price_at) AS q_volume,
        quantile_cont(value_raw, [0.02,0.98]) FILTER (eligible AND isfinite(value_raw)) OVER (PARTITION BY price_at) AS q_value,
        quantile_cont(quality_raw, [0.02,0.98]) FILTER (eligible AND isfinite(quality_raw)) OVER (PARTITION BY price_at) AS q_quality,
        quantile_cont(expectations_raw, [0.02,0.98]) FILTER (eligible AND isfinite(expectations_raw)) OVER (PARTITION BY price_at) AS q_earnings,
        quantile_cont(size_raw, [0.02,0.98]) FILTER (eligible AND isfinite(size_raw)) OVER (PARTITION BY price_at) AS q_size,
        quantile_cont(investable_raw, [0.02,0.98]) FILTER (eligible AND isfinite(investable_raw)) OVER (PARTITION BY price_at) AS q_investable,
        quantile_cont(benchmark_raw, [0.02,0.98]) FILTER (eligible AND isfinite(benchmark_raw)) OVER (PARTITION BY price_at) AS q_benchmark
      FROM raw
    ),
    complete AS (
      SELECT * FROM quantiles
      WHERE eligible
        AND isfinite(momentum_raw) AND isfinite(volatility_raw)
        AND isfinite(downside_raw) AND isfinite(liquidity_raw)
        AND isfinite(volume_change_raw) AND isfinite(value_raw)
        AND isfinite(quality_raw) AND isfinite(expectations_raw)
        AND isfinite(size_raw) AND isfinite(investable_raw)
        AND isfinite(benchmark_raw)
    ),
    ranks AS (
      SELECT *,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_momentum[1],least(q_momentum[2],momentum_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS momentum,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_volatility[1],least(q_volatility[2],volatility_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS volatility,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_downside[1],least(q_downside[2],downside_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS downside,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_liquidity[1],least(q_liquidity[2],liquidity_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS liquidity,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_volume[1],least(q_volume[2],volume_change_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS volume_change,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_value[1],least(q_value[2],value_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS value_rank,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_quality[1],least(q_quality[2],quality_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS quality,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_earnings[1],least(q_earnings[2],expectations_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS earnings,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_size[1],least(q_size[2],size_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS size_rank,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_investable[1],least(q_investable[2],investable_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS investable_rank,
        (row_number() OVER (PARTITION BY price_at ORDER BY greatest(q_benchmark[1],least(q_benchmark[2],benchmark_raw)), instrument)
          - 1.0) / greatest(count(*) OVER (PARTITION BY price_at)-1,1) - 0.5 AS benchmark
      FROM complete
    ),
    blended AS (
      SELECT *,
        (volatility+downside)/2 AS stability,
        (liquidity+0.5*volume_change)/1.5 AS liquidity_mix,
        (size_rank+0.25*investable_rank)/1.25 AS size_mix
      FROM ranks
    )
    SELECT price_at + INTERVAL '3 hours' AS available_at, instrument,
      (1.7*momentum+0.4*stability+0.2*liquidity_mix)/2.3 AS momentum_score,
      (momentum+0.6*stability+0.3*liquidity_mix+0.8*value_rank+0.8*quality+0.7*earnings+0.2*size_mix)/4.4 AS balanced_score,
      (1.2*value_rank+quality+0.4*earnings+0.2*size_mix)/2.8 AS value_quality_score,
      (momentum+1.4*stability+0.3*liquidity_mix+0.1*benchmark)/2.8 AS low_vol_momentum_score,
      (0.5*momentum+1.6*earnings+0.8*quality+0.2*value_rank)/3.1 AS earnings_momentum_score,
      1.0::DOUBLE AS eligible
    FROM blended
    WHERE eligible
      AND isfinite(momentum_score) AND isfinite(balanced_score)
      AND isfinite(value_quality_score) AND isfinite(low_vol_momentum_score)
      AND isfinite(earnings_momentum_score)
    ORDER BY available_at, instrument
    """
    started = time.perf_counter()
    con.execute(f"COPY ({query}) TO '{destination}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    elapsed = time.perf_counter() - started
    row_count = con.execute(f"SELECT count(*) FROM read_parquet('{destination}')").fetchone()[0]
    print(json.dumps({"wall_s": elapsed, "rows": row_count, "output": str(args.output)}))


if __name__ == "__main__":
    main()
