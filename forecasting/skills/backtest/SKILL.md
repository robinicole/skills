---
name: backtest
description: Backtest time series forecasts with rolling-origin cross-validation, scored per horizon against seasonal naive. Use when the user wants to evaluate, compare or validate forecasting models, check prediction intervals, pick a forecast metric (MASE, RMSE, MAPE, CRPS), or when the forecast skill reaches evaluation.
---

# Backtest

A backtest scores forecasts on data the model never saw, at every horizon that will ship, from many origins, against **the bar**: seasonal naive (naive for non-seasonal data). Training-set fit is never evidence of accuracy; it rewards every extra parameter and only covers one step ahead.

Work the six steps in order. A model moves to the next step only when the current criterion holds.

## Steps

1. **White residuals.** Compute one-step residuals on the training set (after a transform, test them on the transformed scale). Done when, per model: Ljung-Box p > 0.05 at 10 lags (non-seasonal) or 2m (seasonal), mean within ±2 standard errors of zero, variance flat on a time plot. A model that fails is misspecified; fix it or drop it before scoring.
2. **Sealed holdout.** Hold out at least the longest horizon you will report, more for seasonal data. Done when nothing computed on the holdout has fed back into the model: transform, hyperparameters, ensemble weights.
3. **Point scores per horizon.** Done when you have a table model × h with the bar as a row, on MAE and RMSE for one series or MASE across series. Each h scored separately.
4. **Interval scores.** Done when coverage is within a few points of nominal for every level that ships, and CRPS or Winkler is at least as good as the bar's. Under-coverage means intervals are too narrow: switch to conformal intervals and rescore.
5. **Rolling origin.** Repeat steps 2 to 4 from many origins, moving forward by a fixed step. Done when there are at least 10 origins spanning every season and scores are averaged per h.
6. **Skill.** skill = (score_bar - score_model) / score_bar. Done when the report names a winner with positive skill at every shipped horizon, or names the bar as the winner and sends the work back to exploration (step 3 of `forecasting:forecast`).

## Code

Tested with statsforecast 2.1 and utilsforecast 0.2.

```python
import numpy as np
import pandas as pd
from functools import partial
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mae, rmse, mase, rmsse, coverage, scaled_crps

# steps 2 and 5: refit=True re-estimates at each origin
cv = sf.cross_validation(df=df, h=h, step_size=3, n_windows=12, level=[80, 95], refit=True)
cv["h"] = cv.groupby(["unique_id", "cutoff"]).cumcount() + 1

# steps 3 and 4: one row per series × metric, one column per model
metrics = [mae, rmse, partial(mase, seasonality=m), partial(rmsse, seasonality=m),
           coverage, scaled_crps]
scores = evaluate(cv.drop(columns=["cutoff", "h"]), metrics=metrics,
                  train_df=df, level=[80, 95])
overall = scores.groupby("metric").mean(numeric_only=True)

# per horizon
by_h = pd.concat(
    evaluate(g.drop(columns=["cutoff", "h"]), metrics=[partial(mase, seasonality=m)],
             train_df=df).assign(h=k)
    for k, g in cv.groupby("h")
).groupby("h").mean(numeric_only=True)

# step 6
skill = 1 - by_h.drop(columns="SeasonalNaive").div(by_h["SeasonalNaive"], axis=0)

def winkler(y, lo, hi, alpha):
    width = hi - lo
    below = np.where(y < lo, 2 / alpha * (lo - y), 0.0)
    above = np.where(y > hi, 2 / alpha * (y - hi), 0.0)
    return (width + below + above).mean()
```

## Point metrics

| Metric | Definition | Optimal forecast | Use | Watch for |
| --- | --- | --- | --- | --- |
| MAE | mean abs error | Median | One series, own scale | Not comparable across series |
| RMSE | root mean squared error | Mean | Forecasts that will be summed | Outlier-sensitive |
| MASE | MAE / in-sample MAE of one-step seasonal naive | Median | Across series; the default | 1.0 means as good as naive on training data; denominator from training data only |
| RMSSE | RMSE scaled the same way | Mean | M5-style comparisons | Same denominator rule |
| MAPE | mean abs error / actual, % | | Business reporting only | Undefined at zero, needs a true zero (not temperature), penalises over-forecasts more |
| sMAPE | | | Legacy only | Unstable near zero and not symmetric; prefer MASE |

## Distributional metrics

A proper scoring rule is minimised only by the true distribution, so widening or narrowing intervals cannot game it. Coverage alone can be gamed; always pair it with one of these.

| Metric | Definition | Reads as |
| --- | --- | --- |
| Quantile (pinball) | p(y - q) if y ≥ q, else (1 - p)(q - y) | Absolute error tilted toward the side the quantile covers; p = 0.5 gives absolute error |
| Winkler | Width + 2/α × distance of any miss outside | Narrow and honest beats wide |
| CRPS | Quantile score averaged over all p | MAE of a whole distribution |
| Coverage | Share of actuals inside the interval | Calibration check, not a score |
