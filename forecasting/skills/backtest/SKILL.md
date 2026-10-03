---
name: backtest
description: Backtest time series forecasts and select a model, using rolling-origin cross-validation scored per horizon against seasonal naive. Use when the user wants to evaluate forecasting models, choose between them, check prediction intervals, pick a forecast metric (MASE, RMSE, MAPE, CRPS), or when the forecast skill reaches evaluation.
---

# Backtest

A backtest scores forecasts on data the model never saw, at every horizon that will ship, from many origins, against **the bar**: seasonal naive (naive for non-seasonal data). Training-set fit is never evidence of accuracy; it rewards every extra parameter and only covers one step ahead.

The second threat is **leakage**: any information from after the forecast origin reaching the model. A leaked backtest looks better than production will ever be.

Work the seven steps in order. A model moves to the next step only when the current criterion holds.

## Steps

1. **Fix the score before seeing results.** Choose one primary point metric and one distributional metric from how the forecast will be used ([METRICS.md](METRICS.md) maps decisions to metrics), plus the horizons and interval levels that ship. Done when all four are written down with a one-line reason, before any model is scored.

2. **White residuals.** Every candidate except the benchmarks passes the residual check in [MODELS.md](../forecast/MODELS.md#residuals-and-intervals) (step 4 of `forecasting:forecast` already runs it). Done when each candidate has a recorded pass; the benchmarks carry straight through as the yardstick.

3. **Seal against leakage.** Done when every item below is checked for every candidate:
   - Transform parameters (Box-Cox lambda, scaling) are estimated inside each training window.
   - Features use only values at or before the origin: lags, rolling windows, target encodings.
   - Regressors are scored ex ante, with forecasts of their future values. Ex-post scores (actual future values) are labelled as such and used only to isolate model error.
   - Hyperparameters, the model list and ensemble weights were chosen on earlier data than the final test origins.
   - If data arrives late in production, the backtest skips the same gap: score from horizon latency + 1.
   - Data revisions: the backtest uses the values that were known at each origin when they differ from today's.

4. **Set the rolling origins.** Expanding window by default; sliding window (`input_size`) when old data describes a different process. Done when there are at least 10 origins spanning every season, the first training window holds at least two full seasons, and each window's horizon covers the longest one that ships.

5. **Score per horizon.** Score each model at each h separately, from every origin. Done when there is a table model × h with the bar as a row, for the primary point metric, the distributional metric, and coverage at every shipped level. Coverage should sit within a few points of nominal. Under-coverage means intervals are too narrow: switch that model to conformal intervals and score it again on the same origins.

6. **Select.** Apply the selection rules below. Done when the report names one winner (a model or a combination) with positive skill against the bar at every shipped horizon, or names the bar as the winner and sends the work back to exploration (step 3 of `forecasting:forecast`).

7. **Report.** Done when the deliverable holds: the step 1 choices with reasons, the leakage checklist, the per-horizon table with skill against the bar, the winner and why, and a plot of the winner's forecasts against actuals from a few origins.

## Selection rules

- **Skill**: skill = (score_bar - score_model) / score_bar on the primary metric, per horizon.
- **AICc only inside one family.** AICc compares models fitted to the same data with the same transform and the same differencing, such as ETS variants or ARIMA orders with fixed d and D. Between families (ETS against ARIMA), between transforms or between differencing orders, only backtest scores count.
- **Ties.** For two close models, take the per-origin difference in score. If its mean is within about two standard errors of zero, call it a tie; the Diebold-Mariano test is the formal version, and it corrects for the overlap between multi-step errors. On a tie, ship the simpler model or the mean of the tied models.
- **Many series.** Report the mean and the median of the scaled score, and the share of series where each model beats the bar. A mean carried by a handful of series is not a general win.
- **Selection is itself fitted.** Choosing the best of many models per series overfits the choice, most of all on short histories. Prefer one model for a whole group of similar series, or a combination, unless per-series winners hold up on later origins.
- **Refit to ship.** The winner is refit on all the data before forecasting.

## Code

```python
import pandas as pd
from functools import partial
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mae, rmse, mase, rmsse, coverage, scaled_crps

# step 4: expanding window; input_size=N for sliding; refit=k refits every k windows to save time
cv = sf.cross_validation(df=df, h=h, step_size=3, n_windows=12, level=[80, 95])
cv["h"] = cv.groupby(["unique_id", "cutoff"]).cumcount() + 1

# step 5: keep the cutoff column so MASE is scaled with training data up to each cutoff only
metrics = [mae, rmse, partial(mase, seasonality=m), partial(rmsse, seasonality=m),
           coverage, scaled_crps]
scores = evaluate(cv.drop(columns="h"), metrics=metrics, train_df=df, level=[80, 95])
overall = scores.groupby("metric").mean(numeric_only=True)

by_h = pd.concat(
    evaluate(g.drop(columns="h"), metrics=[partial(mase, seasonality=m)], train_df=df).assign(h=k)
    for k, g in cv.groupby("h")
).groupby("h").mean(numeric_only=True)

# step 6: skill per horizon, and the tie check between two models
skill = 1 - by_h.drop(columns="SeasonalNaive").div(by_h["SeasonalNaive"], axis=0)

per_origin = scores[scores["metric"] == "mase"].groupby("cutoff")[["AutoETS", "AutoARIMA"]].mean()
diff = per_origin["AutoETS"] - per_origin["AutoARIMA"]
tie = abs(diff.mean()) < 2 * diff.std(ddof=1) / len(diff) ** 0.5

# many series: mean, median, share beating the bar
mase_rows = scores[scores["metric"] == "mase"]
summary = mase_rows.drop(columns=["unique_id", "cutoff", "metric"]).agg(["mean", "median"])
beats_bar = (mase_rows.drop(columns=["unique_id", "cutoff", "metric"])
               .lt(mase_rows["SeasonalNaive"], axis=0).mean())
```
