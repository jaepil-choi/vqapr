"""Five weekly long-short consumers of the materialized actual-DW factors."""

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

SELECTED = 30
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
    (destination / f"strategy-{os.getpid()}.json").write_text(
        json.dumps({"seconds": _TOTALS, "calls": _CALLS}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


atexit.register(_flush)


class MaterializedFactorStrategy(va.StrategyModel):
    score_field = "balanced_score"

    def inputs(self):
        return {
            "factors": va.DatasetInput(
                dataset_id="actual_daily_factors",
                fields=(self.score_field, "eligible"),
                lookback=va.RowsLookback(rows=1),
            )
        }

    def decide(self, context):
        with stage("strategy.read"):
            window = context.read("factors", self.score_field)
            score = window.matrix()[-1]
            eligible_value = context.read("factors", "eligible").matrix()[-1]
        with stage("strategy.plan"):
            names = np.asarray(window.instruments)
            eligible = np.flatnonzero(
                np.isfinite(score) & np.isfinite(eligible_value) & (eligible_value > 0)
            )
            if len(eligible) < SELECTED * 2:
                return va.Hold(reason="fewer than sixty eligible actual members")
            order = eligible[np.lexsort((names[eligible], score[eligible]))]
            short = {str(name): 1.0 for name in names[order[:SELECTED]]}
            long = {str(name): 1.0 for name in names[order[-SELECTED:]]}
            return va.Rebalance.of(long=long, short=short, invested="1.0")


class SixWeekMomentum(MaterializedFactorStrategy):
    score_field = "momentum_score"


class BalancedFactors(MaterializedFactorStrategy):
    score_field = "balanced_score"


class ValueQuality(MaterializedFactorStrategy):
    score_field = "value_quality_score"


class LowVolMomentum(MaterializedFactorStrategy):
    score_field = "low_vol_momentum_score"


class EarningsMomentum(MaterializedFactorStrategy):
    score_field = "earnings_momentum_score"
