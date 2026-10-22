# Chapter 13: Some practical forecasting issues

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `practical.html`, `weekly.html`, `counts.html`,
`practical.html#sec-limits`, `combinations.html`, `aggregates.html`, `backcasting.html`,
`long-short-ts.html`, `training-test.html`, `missing-outliers.html`.
Python edition (checked 2026-10-22): one page per chapter, `13-practical.html`, same section anchors. No sections on aggregate intervals or training and test sets, so 13.5 is backcasting and 13.7 outliers and missing values.

## Key concepts and decision rules

- Weekly data: period about 52.18, not an integer, and long. Use STL on the log or
  Box-Cox scale with a non-seasonal model on the adjusted series, or dynamic
  harmonic regression with Fourier terms; choose K by AICc (K = 6 for the
  US gasoline example in both editions).
- Daily and sub-daily data: several seasonal periods; moving holidays need dummy
  predictors in a dynamic regression; STL with several periods, or Fourier terms
  per period.
- Counts: for large counts, treat as continuous. For small counts and intermittent
  demand, Croston's method: separate exponential smoothing of the non-zero demand
  sizes and of the intervals between demands, forecast as the ratio (a demand
  rate). Croston gives no proper prediction intervals in its original form and is
  biased; variants correct this. A demand rate, not a count, is the output.
- Bounded forecasts: positive only: model the log and back-transform. Between a
  and b: scaled logit transform log((y - a)/(b - y)), forecast, back-transform.
  Both keep the point forecast and the interval inside the bounds.
- Forecast combinations: averaging several good models (ETS, STL-ETS, ARIMA, NNAR)
  usually beats each member; equal weights are hard to beat. Combining gives
  no automatic distribution: simulate from each member and pool the paths, or
  report the point combination only.
- Prediction intervals for aggregates (a sum of forecasts over several horizons):
  the point forecasts add, intervals do not, because errors across horizons are
  correlated. Simulate future sample paths, sum within each path, take quantiles.
- Backcasting: reverse the series, forecast, reverse the forecasts.
- Very long series: parameters that were constant long ago may not be now; use only
  the recent part or a model that lets parameters evolve.
- Very short series: the only hard constraint is more observations than
  parameters; there is no magic minimum such as 30 observations; AICc will choose
  simple models on short data. Seasonal models need at least a few full seasons.
- Forecasting on training and test sets (the book's "beware of overfitting" point):
  one-step forecasts on the test set with parameters frozen let training and test
  residuals be compared on an equal footing.
- Missing values: ask whether the gap carries information (a closed store). If
  not random, model the cause with dummies. If random, interpolate with a model
  fitted to the series (ARIMA interpolation) or use only the data after the last
  gap. Some methods tolerate gaps; others need a complete series.
- Outliers: find them with a robust STL remainder (beyond about 3 IQR of the
  middle half). Replace by interpolation only when the value is an error or will
  not recur; otherwise keep it, perhaps with a dummy for that date.

## Model diagnostics the book recommends

Residual checks per model; for combinations, check the members individually.

## Evaluation guidance

Cross-validation as before; for counts, evaluate the demand rate with scale-free
measures; for aggregates, compare simulated intervals with empirical coverage.

## R functions and Python equivalents

| R (fable) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `CROSTON(y)` | `statsforecast.models.CrostonClassic`, `CrostonOptimized`, `CrostonSBA`; also: `TSB`, `ADIDA`, `IMAPA` |
| `log(y)` in model formula | `np.log` on the frame before `forecast`, `np.exp` on point and interval columns after; also: `inv_boxcox` |
| scaled logit via `new_transformation()` | functions by hand |
| `(ets + arima + stl) / 3` combination in a mable | average columns of the forecast frame after back-transforming each member; intervals from quantiles of validation residuals of the average |
| `generate(h=, times=)` sample paths | `statsforecast` has no sample-path generator; statsmodels `simulate()` on a fitted model, or bootstrap by hand (not in the Python edition) |
| `ARIMA(y)` interpolation, `interpolate()` | `pandas.Series.interpolate()` (StatsForecast rejects NaN); also: statsmodels SARIMAX handles NaN |
| `STL(... robust=TRUE)` remainder for outliers | `statsforecast.models.MSTL(season_length=m, stl_kwargs={"robust": True})`, flag remainders beyond 3 IQR; also: `statsmodels STL(robust=True)` |

## Common mistakes the book warns about

- Fitting seasonal ARIMA to weekly data with m = 52.
- Treating a Croston forecast as a count or an expected integer.
- Adding prediction intervals across horizons.
- Refusing to forecast short series because of a minimum-length myth.
- Replacing informative missing values by interpolation.
