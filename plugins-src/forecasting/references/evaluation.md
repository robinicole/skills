# Evaluation

How to score forecasts. `forecast-baselines` owns this file; every other skill
points here. Book: FPP3 5.8 to 5.10 [unverified sections].

## Rules

1. Score forecasts, not fits. Fitted values are one-step predictions from a model
   that saw the data. They serve the residual check only.
2. Score every forecast horizon the decision uses, separately.
3. Score from many forecast origins (time series cross-validation), not from one
   test set, when the series is long enough.
4. Compare every model with the benchmarks on the same origins.
5. Choose the metric before you look at the results.

## Test set

Hold out the end of the series. Make it at least as long as the largest forecast
horizon. About 20% of the data is a common size. Fit on the training set only;
that includes the transformation lambda and any scaling.

## Time series cross-validation

For origins t1 < t2 < ... < tk: fit on data up to each origin, forecast h steps,
score. Expanding window by default. Use a sliding window (`input_size=`) when old
data describe a different process.

Checks before you trust the result:

- Enough origins (10 or more where the data allow) spread over the seasons.
- First training window at least two full seasons long.
- Test rows always after their origin.
- Predictors: ex-ante (forecast) values for the headline score; ex-post only to
  isolate model error, labelled as such.

```python
cv = sf.cross_validation(df=df, h=h, n_windows=10, step_size=1, level=[80, 95])
from fc_checks import score_cv
by_h = score_cv(cv, train_df=df, m=m, levels=[80, 95])            # per forecast horizon
overall = score_cv(cv, train_df=df, m=m, levels=[80, 95], by_h=False)
```

For a model outside statsforecast use `fc_checks.rolling_origin(df, h, n_windows,
step_size, fit_forecast)`; it returns the same frame shape.

## Point accuracy measures

In words; e is the forecast error (actual minus forecast).

| Measure | Definition | Best forecast for it | Use |
|---|---|---|---|
| MAE | mean of the absolute errors | median | one series, its own units |
| RMSE | square root of the mean squared error | mean | one series, forecasts that will be summed |
| MAPE | mean of 100 times absolute error divided by the actual | | only for positive data with a true zero; never with zeros |
| MASE | MAE divided by the mean absolute one-step seasonal naive error on the training data | median | across series; below 1 beats one-step seasonal naive in-sample |
| RMSSE | RMSE divided by the root mean squared one-step seasonal naive error on the training data | mean | across series |

Use MASE or RMSSE whenever you average across series. Average squared errors
before taking the square root. sMAPE is not recommended.

## Distribution accuracy measures

| Measure | Definition | Use |
|---|---|---|
| Quantile score at p | for a quantile forecast q: weight p on misses above, weight 1 - p on misses below | one quantile (a stock level at service level p) |
| Winkler score | interval width plus 2/alpha times the distance by which the actual falls outside | a prediction interval |
| CRPS | the quantile score averaged over all p | the whole forecast distribution; in units of the data, like MAE |
| Coverage | share of actuals inside the interval | calibration check only, never a score on its own |
| Skill score | 1 minus model score over benchmark score | compare against the benchmark; positive is better |

`fc_checks.crps_from_intervals` approximates CRPS from interval columns (Not from
the book; pass many levels for a close value).

## Matching the measure to the decision

| The forecast is used as | Primary measure |
|---|---|
| A total to be summed (budget, capacity) | RMSE or RMSSE; bias-adjust back-transformed forecasts first |
| A typical value | MAE or MASE |
| A stock level at service level p | quantile score at p |
| A range or risk | CRPS or Winkler, with coverage |

## Comparing models

- Inside one family fitted to the same data: AICc is fine.
- Across families, transformations or differencing orders: cross-validation only.
- Many series: report mean and median of the scaled measure, and the share of
  series where each model beats the benchmark.
