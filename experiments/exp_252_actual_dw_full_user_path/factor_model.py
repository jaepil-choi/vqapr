"""Daily reusable factors from five actual DW tables through the public authoring API."""

from __future__ import annotations

import atexit
import json
import os
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from vqapr import authoring as va

LOOKBACK = 31
_TOTALS = defaultdict(float)
_CALLS = defaultdict(int)


@contextmanager
def stage(name):
    started = time.perf_counter()
    try:
        yield
    finally:
        _TOTALS[name] += time.perf_counter() - started
        _CALLS[name] += 1


def _flush():
    root = os.environ.get("VQAPR_BENCH_TIMINGS")
    if not root or not _TOTALS:
        return
    destination = Path(root)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"datamodel-{os.getpid()}.json").write_text(
        json.dumps({"seconds": _TOTALS, "calls": _CALLS}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


atexit.register(_flush)


def _last_finite(values: np.ndarray) -> np.ndarray:
    valid = np.isfinite(values)
    positions = np.where(valid, np.arange(values.shape[0])[:, None], -1).max(axis=0)
    columns = np.arange(values.shape[1])
    result = np.full(values.shape[1], np.nan)
    present = positions >= 0
    result[present] = values[positions[present], columns[present]]
    return result


def _change(values: np.ndarray) -> np.ndarray:
    first = np.full(values.shape[1], np.nan)
    last = _last_finite(values)
    valid = np.isfinite(values)
    positions = np.where(valid, np.arange(values.shape[0])[:, None], values.shape[0]).min(axis=0)
    columns = np.arange(values.shape[1])
    present = positions < values.shape[0]
    first[present] = values[positions[present], columns[present]]
    with np.errstate(divide="ignore", invalid="ignore"):
        return last / first - 1.0


def _return(values: np.ndarray, sessions: int) -> np.ndarray:
    if values.shape[0] <= sessions:
        return np.full(values.shape[1], np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        return values[-1] / values[-1 - sessions] - 1.0


def _rank(values: np.ndarray, eligible: np.ndarray) -> np.ndarray:
    result = np.full(values.shape, np.nan)
    where = np.flatnonzero(eligible & np.isfinite(values))
    if not len(where):
        return result
    clipped = values.copy()
    low, high = np.nanquantile(values[where], (0.02, 0.98))
    clipped[where] = np.clip(values[where], low, high)
    order = where[np.lexsort((where, clipped[where]))]
    result[order] = np.arange(len(order), dtype=float) / max(len(order) - 1, 1) - 0.5
    return result


def _blend(signals: tuple[np.ndarray, ...], weights: tuple[float, ...]) -> np.ndarray:
    values = np.vstack(signals)
    weight = np.asarray(weights)[:, None]
    present = np.isfinite(values)
    numerator = np.nansum(values * weight, axis=0)
    denominator = np.sum(present * np.abs(weight), axis=0)
    return np.divide(
        numerator,
        denominator,
        out=np.full(values.shape[1], np.nan),
        where=denominator > 0,
    )


class ActualDailyFactors(va.DataModel):
    def inputs(self):
        return {
            "prices": va.DatasetInput(
                dataset_id="prices",
                fields=("close", "volume", "turnover"),
                lookback=va.RowsLookback(rows=LOOKBACK),
            ),
            "shares": va.DatasetInput(
                dataset_id="shares",
                fields=("listed_shares", "investable_shares"),
                lookback=va.RowsLookback(rows=2),
            ),
            "valuation": va.DatasetInput(
                dataset_id="valuation",
                fields=("beta", "forward_eps", "forward_per", "pbr", "ev_ebitda", "profit_12m"),
                lookback=va.RowsLookback(rows=LOOKBACK),
            ),
            "consensus": va.DatasetInput(
                dataset_id="consensus",
                fields=("sales", "operating_profit", "net_debt", "owner_profit"),
                lookback=va.RowsLookback(rows=LOOKBACK),
            ),
            "membership": va.DatasetInput(
                dataset_id="membership",
                fields=("member", "index_weight"),
                lookback=va.RowsLookback(rows=1),
            ),
        }

    def compute(self, context):
        with stage("datamodel.read"):
            price_window = context.read("prices", "close")
            close = price_window.matrix()
            volume = context.read("prices", "volume").matrix()
            turnover = context.read("prices", "turnover").matrix()
            listed = context.read("shares", "listed_shares").matrix()
            investable = context.read("shares", "investable_shares").matrix()
            beta = context.read("valuation", "beta").matrix()
            forward_eps = context.read("valuation", "forward_eps").matrix()
            forward_per = context.read("valuation", "forward_per").matrix()
            pbr = context.read("valuation", "pbr").matrix()
            ev_ebitda = context.read("valuation", "ev_ebitda").matrix()
            profit_12m = context.read("valuation", "profit_12m").matrix()
            sales = context.read("consensus", "sales").matrix()
            operating = context.read("consensus", "operating_profit").matrix()
            net_debt = context.read("consensus", "net_debt").matrix()
            owner_profit = context.read("consensus", "owner_profit").matrix()
            member = context.read("membership", "member").matrix()
            index_weight = context.read("membership", "index_weight").matrix()

        with stage("datamodel.align"):
            current_close = _last_finite(close)
            current_listed = _last_finite(listed)
            current_member = np.nan_to_num(_last_finite(member), nan=0.0)
            eligible = (
                (current_member > 0)
                & np.isfinite(current_close)
                & (current_close > 0)
                & np.isfinite(current_listed)
                & (current_listed > 0)
            )

        with stage("datamodel.indicator"):
            daily = close[1:] / close[:-1] - 1.0 if close.shape[0] > 1 else close[:0]
            momentum_raw = (
                0.15 * _return(close, 5)
                + 0.20 * _return(close, 10)
                + 0.30 * _return(close, 20)
                + 0.35 * _return(close, 30)
            )
            volatility_raw = -np.nanstd(daily, axis=0) if len(daily) else current_close * np.nan
            downside_raw = -np.nanmean(daily < 0, axis=0) if len(daily) else current_close * np.nan
            liquidity_raw = np.log1p(np.nanmean(turnover[-20:], axis=0))
            volume_change_raw = _change(volume[-20:])
            value_raw = _blend(
                (
                    -np.log1p(np.abs(_last_finite(forward_per))),
                    -np.log1p(np.abs(_last_finite(pbr))),
                    -np.log1p(np.abs(_last_finite(ev_ebitda))),
                ),
                (1.0, 1.0, 1.0),
            )
            sales_last = _last_finite(sales)
            quality_raw = _blend(
                (
                    _last_finite(operating) / np.maximum(np.abs(sales_last), 1.0),
                    _last_finite(owner_profit) / np.maximum(np.abs(sales_last), 1.0),
                    -_last_finite(net_debt) / np.maximum(np.abs(sales_last), 1.0),
                    -np.abs(_last_finite(beta) - 1.0),
                ),
                (1.0, 1.0, 0.5, 0.25),
            )
            expectations_raw = _blend(
                (_change(forward_eps), _change(profit_12m), _change(sales), _change(operating)),
                (1.0, 1.0, 0.5, 0.75),
            )
            size_raw = -np.log1p(current_close * current_listed)
            investable_raw = np.log1p(np.maximum(_last_finite(investable), 0.0))
            benchmark_raw = np.nan_to_num(_last_finite(index_weight), nan=0.0)

        with stage("datamodel.rank"):
            momentum = _rank(momentum_raw, eligible)
            stability = _blend(
                (_rank(volatility_raw, eligible), _rank(downside_raw, eligible)), (1.0, 1.0)
            )
            liquidity = _blend(
                (_rank(liquidity_raw, eligible), _rank(volume_change_raw, eligible)), (1.0, 0.5)
            )
            value = _rank(value_raw, eligible)
            quality = _rank(quality_raw, eligible)
            earnings = _rank(expectations_raw, eligible)
            size = _blend((_rank(size_raw, eligible), _rank(investable_raw, eligible)), (1.0, 0.25))
            benchmark = _rank(benchmark_raw, eligible)
            scores = {
                "momentum_score": _blend((momentum, stability, liquidity), (1.7, 0.4, 0.2)),
                "balanced_score": _blend(
                    (momentum, stability, liquidity, value, quality, earnings, size),
                    (1.0, 0.6, 0.3, 0.8, 0.8, 0.7, 0.2),
                ),
                "value_quality_score": _blend(
                    (value, quality, earnings, size), (1.2, 1.0, 0.4, 0.2)
                ),
                "low_vol_momentum_score": _blend(
                    (momentum, stability, liquidity, benchmark), (1.0, 1.4, 0.3, 0.1)
                ),
                "earnings_momentum_score": _blend(
                    (momentum, earnings, quality, value), (0.5, 1.6, 0.8, 0.2)
                ),
            }

        with stage("datamodel.output"):
            names = np.asarray(price_window.instruments)
            chosen = np.flatnonzero(eligible)
            return tuple(
                {
                    "instrument": str(names[position]),
                    **{field: float(values[position]) for field, values in scores.items()},
                    "eligible": 1.0,
                }
                for position in chosen
                if all(np.isfinite(values[position]) for values in scores.values())
            )
