"""Normalize the fixed actual-DW inputs into vqapr's typed parquet contract."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "outputs" / "inputs"
DW = Path("/Users/jason/qlibx/DW")
START = "20180102"
END = "20260720"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def quoted(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def finite(column: str, alias: str | None = None) -> str:
    name = alias or column
    value = f'TRY_CAST("{column}" AS DOUBLE)'
    return f"CASE WHEN isfinite({value}) THEN {value} END AS {name}"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_paths = {
        "price": DW / "fng_stock_daily_prices.csv",
        "shares": DW / "fng_daily_indicator_share_counts.csv",
        "valuation": DW / "dw_fng_mirror" / "dw_fng_valuation.parquet",
        "consensus": DW / "dw_fng_mirror" / "dw_fng_daily_consensus.parquet",
        "membership": DW / "fng_k200_members.csv",
    }
    for path in source_paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)

    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET preserve_insertion_order=false")
    timings: dict[str, float] = {}

    queries = {
        "prices.parquet": f"""
            COPY (
              SELECT timezone('Asia/Seoul', strptime(CAST(거래일자 AS VARCHAR), '%Y%m%d')
                              + INTERVAL '15 hours 30 minutes') AS available_at,
                     종목약코드 AS instrument,
                     {finite("종가", "close")},
                     {finite("거래량", "volume")},
                     {finite("거래대금", "turnover")},
                     CAST(COALESCE(거래량, 0) > 0 AND COALESCE(거래정지구분, 0) = 0
                          AS BOOLEAN) AS is_tradable
              FROM read_csv_auto('{quoted(source_paths["price"])}', header=true)
              WHERE 거래일자 BETWEEN {START} AND {END}
            ) TO '{{output}}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """,
        "shares.parquet": f"""
            COPY (
              SELECT timezone('Asia/Seoul', strptime(CAST(거래일자 AS VARCHAR), '%Y%m%d')
                              + INTERVAL '18 hours') AS available_at,
                     종목약코드 AS instrument,
                     {finite("기말보통주주식수", "listed_shares")},
                     CASE
                       WHEN isfinite(TRY_CAST(기말보통주주식수 AS DOUBLE))
                        AND isfinite(TRY_CAST(기말보통주자기주식수 AS DOUBLE))
                       THEN TRY_CAST(기말보통주주식수 AS DOUBLE)
                            - TRY_CAST(기말보통주자기주식수 AS DOUBLE)
                     END AS investable_shares
              FROM read_csv_auto('{quoted(source_paths["shares"])}', header=true)
              WHERE 거래일자 BETWEEN {START} AND {END}
            ) TO '{{output}}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """,
        "valuation.parquet": f"""
            COPY (
              SELECT timezone('Asia/Seoul', strptime(일자, '%Y%m%d')
                              + INTERVAL '18 hours') AS available_at,
                     종목약코드 AS instrument,
                     {finite("베타", "beta")},
                     {finite("FORWARD_EPS", "forward_eps")},
                     {finite("FORWARD_PER", "forward_per")},
                     {finite("PBR", "pbr")},
                     {finite("EV_EBITDA", "ev_ebitda")},
                     {finite("순이익12MFWD", "profit_12m")}
              FROM read_parquet('{quoted(source_paths["valuation"])}')
              WHERE 일자 BETWEEN '{START}' AND '{END}'
            ) TO '{{output}}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """,
        "consensus.parquet": f"""
            COPY (
              WITH grouped AS (
                SELECT timezone('Asia/Seoul', strptime(일자, '%Y%m%d')
                                + INTERVAL '18 hours') AS available_at,
                       기업코드 AS instrument,
                       결산년월 AS fiscal_period,
                       AVG(TRY_CAST(매출액 AS DOUBLE)) AS sales,
                       AVG(TRY_CAST(영업이익 AS DOUBLE)) AS operating_profit,
                       AVG(TRY_CAST(순부채 AS DOUBLE)) AS net_debt,
                       AVG(TRY_CAST(지배주주순이익 AS DOUBLE)) AS owner_profit
                FROM read_parquet('{quoted(source_paths["consensus"])}')
                WHERE 일자 BETWEEN '{START}' AND '{END}'
                GROUP BY available_at, instrument, fiscal_period
              ), latest AS (
                SELECT *, ROW_NUMBER() OVER (
                  PARTITION BY available_at, instrument
                  ORDER BY fiscal_period DESC NULLS LAST
                ) AS choice
                FROM grouped
              )
              SELECT available_at, instrument,
                     CASE WHEN isfinite(sales) THEN sales END AS sales,
                     CASE WHEN isfinite(operating_profit) THEN operating_profit END
                       AS operating_profit,
                     CASE WHEN isfinite(net_debt) THEN net_debt END AS net_debt,
                     CASE WHEN isfinite(owner_profit) THEN owner_profit END AS owner_profit
              FROM latest
              WHERE choice = 1
            ) TO '{{output}}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """,
        "membership.parquet": f"""
            COPY (
              SELECT timezone('Asia/Seoul', strptime(CAST(일자 AS VARCHAR), '%Y%m%d')
                              + INTERVAL '8 hours') AS available_at,
                     종목코드2 AS instrument,
                     1.0::DOUBLE AS member,
                     {finite("지수내비중", "index_weight")}
              FROM read_csv_auto('{quoted(source_paths["membership"])}', header=true)
              WHERE 일자 BETWEEN {START} AND {END}
            ) TO '{{output}}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 250000)
        """,
    }

    for name, template in queries.items():
        destination = OUTPUT / name
        started = time.perf_counter()
        con.execute(template.format(output=quoted(destination)))
        timings[name] = round(time.perf_counter() - started, 6)

    # The historical membership table is the economic universe. No observed member is dropped.
    universe = [
        row[0]
        for row in con.execute(
            f"SELECT DISTINCT 종목코드2 FROM read_csv_auto('{quoted(source_paths['membership'])}', "
            "header=true) ORDER BY 종목코드2"
        ).fetchall()
    ]
    (OUTPUT / "universe.json").write_text(
        json.dumps(universe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    con.close()

    files = {}
    for path in sorted(OUTPUT.glob("*.parquet")):
        metadata = pq.ParquetFile(path).metadata
        files[path.name] = {
            "rows": metadata.num_rows,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    manifest = {
        "contract": {
            "start": START,
            "end": END,
            "universe": len(universe),
            "sampling": "none",
        },
        "sources": {
            key: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for key, path in source_paths.items()
        },
        "outputs": files,
        "stage_wall_s": timings,
        "machine": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "logical_cpu": os.cpu_count(),
            "ram_bytes": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
        },
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
