"""Five realistic weekly factor mixes over several registered input tables."""

from __future__ import annotations

import numpy as np

from vqapr.authoring import DatasetInput, Hold, Rebalance, RowsLookback, StrategyModel

LOOKBACK = 31
SELECTED = 30


def _last(matrix: np.ndarray) -> np.ndarray:
    return matrix[-1]


def _change(matrix: np.ndarray, old: int) -> np.ndarray:
    return matrix[-1] / matrix[old] - 1.0


def _rank(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Stable percentile ranks; invalid cells remain NaN."""
    result = np.full(values.shape, np.nan)
    where = np.flatnonzero(valid & np.isfinite(values))
    if not len(where):
        return result
    order = where[np.argsort(values[where], kind="stable")]
    result[order] = np.arange(len(order), dtype=float) / max(len(order) - 1, 1)
    return result


class FactorStrategy(StrategyModel):
    weights = np.array([1.0, 0.4, 0.3, 0.3, 0.2, 0.3, 0.2, 0.2])

    def inputs(self):
        return {
            "prices": DatasetInput(
                dataset_id="prices",
                fields=("close", "volume", "turnover_value"),
                lookback=RowsLookback(rows=LOOKBACK),
            ),
            "valuation": DatasetInput(
                dataset_id="valuation",
                fields=("beta", "forward_per", "pbr", "ev_ebitda"),
                lookback=RowsLookback(rows=LOOKBACK),
            ),
            "consensus": DatasetInput(
                dataset_id="consensus",
                fields=(
                    "forward_net_income",
                    "consensus_sales",
                    "consensus_operating_income",
                    "consensus_net_income",
                ),
                lookback=RowsLookback(rows=LOOKBACK),
            ),
            "shares": DatasetInput(
                dataset_id="shares", fields=("shares",), lookback=RowsLookback(rows=1)
            ),
            "membership": DatasetInput(
                dataset_id="membership",
                fields=("k200_weight",),
                lookback=RowsLookback(rows=1),
            ),
        }

    def decide(self, call):
        price_window = call.read("prices", "close")
        close = price_window.matrix()
        volume = call.read("prices", "volume").matrix()
        turnover = call.read("prices", "turnover_value").matrix()
        beta = call.read("valuation", "beta").matrix()
        per = call.read("valuation", "forward_per").matrix()
        pbr = call.read("valuation", "pbr").matrix()
        ev = call.read("valuation", "ev_ebitda").matrix()
        income = call.read("consensus", "forward_net_income").matrix()
        sales = call.read("consensus", "consensus_sales").matrix()
        operating = call.read("consensus", "consensus_operating_income").matrix()
        net = call.read("consensus", "consensus_net_income").matrix()
        shares = call.read("shares", "shares").matrix()
        member = call.read("membership", "k200_weight").matrix()
        if close.shape[0] != LOOKBACK:
            return Hold(reason="incomplete-lookback")

        valid = np.isfinite(close[[0, -6, -1]]).all(axis=0)
        valid &= np.isfinite(_last(shares)) & (_last(shares) > 0)
        member_score = np.nan_to_num(_last(member), nan=0.0)
        daily = close[1:] / close[:-1] - 1.0
        signals = (
            _change(close, 0),
            _change(close, -6),
            -np.nanstd(daily, axis=0),
            np.log1p(np.nanmean(turnover[-21:], axis=0)),
            -np.log1p(np.abs(_last(per))),
            -np.log1p(np.abs(_last(pbr))),
            income[-1] / np.maximum(np.abs(income[0]), 1.0) - 1.0,
            operating[-1] / np.maximum(np.abs(sales[-1]), 1.0),
        )
        score = np.zeros(close.shape[1])
        for weight, signal in zip(self.weights, signals, strict=True):
            score += weight * (_rank(signal, valid) - 0.5)
        # Exercise the remaining declared financial inputs without changing their scale wildly.
        score += 0.05 * (_rank(-np.abs(_last(beta) - 1.0), valid) - 0.5)
        score += 0.05 * (_rank(-np.abs(_last(ev)), valid) - 0.5)
        score += 0.05 * (_rank(net[-1] / np.maximum(np.abs(sales[-1]), 1.0), valid) - 0.5)
        score += 0.05 * (_rank(np.nanmean(volume[-5:], axis=0), valid) - 0.5)
        score += 0.05 * (_rank(member_score, valid) - 0.5)

        names = np.asarray(price_window.instruments)
        eligible = np.flatnonzero(valid & np.isfinite(score))
        if len(eligible) < SELECTED * 2:
            return Hold(reason="too-few-names")
        order = eligible[np.lexsort((names[eligible], score[eligible]))]
        short = sorted(names[order[:SELECTED]].tolist())
        long = sorted(names[order[-SELECTED:]].tolist())
        return Rebalance.of(
            long={name: 1 for name in long},
            short={name: 1 for name in short},
            invested="1.0",
        )


class SixWeekMomentum(FactorStrategy):
    weights = np.array([1.8, 0.5, 0.2, 0.1, 0.0, 0.0, 0.1, 0.0])


class BalancedFactors(FactorStrategy):
    weights = np.array([1.0, 0.3, 0.4, 0.3, 0.5, 0.5, 0.4, 0.4])


class ValueQuality(FactorStrategy):
    weights = np.array([0.2, 0.0, 0.2, 0.2, 1.0, 1.0, 0.5, 0.8])


class LowVolMomentum(FactorStrategy):
    weights = np.array([1.0, 0.5, 1.4, 0.3, 0.1, 0.1, 0.2, 0.1])


class EarningsMomentum(FactorStrategy):
    weights = np.array([0.5, 0.2, 0.3, 0.2, 0.2, 0.2, 1.7, 1.0])
