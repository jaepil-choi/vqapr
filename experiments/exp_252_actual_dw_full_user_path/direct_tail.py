# ruff: noqa: F821
# Appended to factor_model.py so the public component remains one self-contained file.
class DirectFactorStrategy(va.StrategyModel):
    score_field = "balanced_score"

    def inputs(self):
        return ActualDailyFactors.inputs(self)

    def decide(self, context):
        with stage("direct.factor"):
            rows = ActualDailyFactors.compute(self, context)
        with stage("direct.plan"):
            if len(rows) < 60:
                return va.Hold(reason="fewer than sixty eligible actual members")
            ranked = sorted(rows, key=lambda row: (row[self.score_field], row["instrument"]))
            short = {row["instrument"]: 1.0 for row in ranked[:30]}
            long = {row["instrument"]: 1.0 for row in ranked[-30:]}
            return va.Rebalance.of(long=long, short=short, invested="1.0")


class DirectSixWeekMomentum(DirectFactorStrategy):
    score_field = "momentum_score"


class DirectBalancedFactors(DirectFactorStrategy):
    score_field = "balanced_score"


class DirectValueQuality(DirectFactorStrategy):
    score_field = "value_quality_score"


class DirectLowVolMomentum(DirectFactorStrategy):
    score_field = "low_vol_momentum_score"


class DirectEarningsMomentum(DirectFactorStrategy):
    score_field = "earnings_momentum_score"
