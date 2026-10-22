# Chapter 5: The forecaster's toolbox

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `toolbox.html`, `toolbox.html#a-tidy-forecasting-workflow`, `simple-methods.html`,
`ftransformations.html`, `residuals.html`, `toolbox.html#sec-prediction-intervals`,
`prediction-intervals.html`, `forecasting-decomposition.html`, `accuracy.html`,
`distaccuracy.html`, `tscv.html`, `toolbox-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `05-toolbox.html`, same section anchors.

## Key concepts and decision rules

- Workflow in code: tidy, visualise, specify, estimate, evaluate, forecast. A model
  table holds one fitted model per series per method, so many series and many
  methods are handled in one call.
- Four benchmark methods, always fitted first: mean, naive (last value), seasonal
  naive (value from one season ago), drift (last value plus the average historical
  change, a line from first to last observation). Naive is the right benchmark for
  random-walk-like series; seasonal naive for seasonal series. Every proposed model
  must beat the relevant benchmark on held-out data or it does not ship.
- Fitted values are one-step forecasts made with the parameters estimated on all
  the data, so they are not true forecasts and understate the error at longer
  horizons. Residuals are observations minus fitted values; after a transformation,
  innovation residuals live on the transformed scale and are the ones to check.
- Residual diagnostics. Essential: residuals uncorrelated, mean zero. Useful but
  not essential: constant variance, normal distribution (needed only for the
  default interval formulas). A failing check means the model is missing
  structure. The portmanteau tests: Box-Pierce and Ljung-Box, with the lag count
  set to 10 for non-seasonal data and 2 x period for seasonal data, and the
  degrees of freedom reduced by the number of estimated parameters for ARIMA and
  regression models. A small p-value means the residuals are not white noise.
- Forecast distributions and prediction intervals. The one-step interval is the
  point forecast plus or minus a multiplier times the residual standard deviation
  (1.28 for 80 percent, 1.96 for 95 percent under normality). Multi-step intervals
  widen with the horizon for every method except the mean: naive grows with the
  square root of h, drift faster, seasonal naive in steps once per season. Bootstrap
  intervals drop the normality assumption by simulating future sample paths from
  resampled residuals; they need the residuals to be uncorrelated and homoscedastic.
- Transformations and forecasts: back-transformed point forecasts are medians.
  Bias adjustment turns them into means, using the forecast variance on the
  transformed scale; apply it when forecasts will be summed. Prediction intervals
  back-transform directly and become asymmetric, with no adjustment.
- Forecasting with decomposition: forecast the seasonally adjusted series with a
  non-seasonal method and the seasonal component with seasonal naive, then add. A
  cheap, strong approach.
- Training and test sets: hold out the end of the series, typically about 20
  percent or at least as long as the forecast horizon. Fit on the training data
  only. Fit quality on training data (R squared, residual size) is not evidence of
  forecast accuracy: more parameters always improve the fit and can worsen the
  forecasts.
- Point accuracy measures: MAE (minimised by the median), RMSE (minimised by the
  mean), MAPE (needs a meaningful zero, undefined at zero, penalises positive
  errors more), sMAPE (not recommended), MASE and RMSSE (scale-free; errors divided
  by the in-sample one-step naive or seasonal naive MAE or MSE from the training
  data; these are the default for comparing across series).
- Distributional accuracy: quantile score (pinball loss), Winkler score for an
  interval (width plus a penalty proportional to the miss distance), CRPS (the
  quantile score averaged over all probabilities; it generalises MAE to a whole
  distribution), and skill scores (relative improvement over a benchmark).
- Time series cross-validation (evaluation on a rolling forecasting origin): many
  training sets, each ending one observation later, each scored on the next h
  observations. Report accuracy per horizon. This is the main tool for model
  selection; it uses the data far better than one train/test split.

## Model diagnostics the book recommends

Time plot of residuals, ACF of residuals, histogram of residuals, Ljung-Box test
with the lag rule above. Innovation residuals, not response residuals, after a
transformation.

## Evaluation guidance

Train/test split with the test set at least as long as the horizon; time series
cross-validation for the final choice; MASE/RMSSE across series; CRPS and Winkler
for distributions; accuracy per horizon.

## R functions and Python equivalents

| R (fable, feasts) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `MEAN()`, `NAIVE()`, `SNAIVE()`, `RW(y ~ drift())` | `statsforecast.models.HistoricAverage`, `Naive`, `SeasonalNaive`, `RandomWalkWithDrift` |
| `augment()` (fitted, residuals) | `StatsForecast.forecast_fitted_values()` after `forecast(fitted=True)` |
| `gg_tsresiduals()` | a `plot_diagnostics()` helper written in the chapter: matplotlib time plot + `plot_acf` + histogram |
| `features(.innov, ljung_box, lag=, dof=)` | `statsmodels.stats.diagnostic.acorr_ljungbox(x, lags=, model_df=)`; `boxpierce=True` adds Box-Pierce |
| `forecast(h=, bootstrap=TRUE)` | bootstrap by hand: resample residuals from `forecast_fitted_values()` with `numpy.random.choice`, cumulate into paths, take quantiles; also: `ConformalIntervals` via `prediction_intervals=` (conformal, not bootstrap; the book describes conformal intervals in text only) |
| `hilo()` | `level=[80, 95]` columns in the forecast frame |
| `accuracy()` | `utilsforecast.evaluation.evaluate(fc, train_df=, metrics=[rmse, mae, mape, partial(mase, seasonality=m)])`; CRPS as 2 x `mqloss` over many levels |
| `stretch_tsibble(.init=, .step=)` | `StatsForecast.cross_validation(h=, step_size=, test_size=)` or `n_windows=` |
| `decomposition_model(STL, ...)` | statsmodels `STL`, then `Naive` on the adjusted series and `SeasonalNaive` on the seasonal part, forecast columns added; also: `statsforecast.models.MSTL(trend_forecaster=)` |

## Common mistakes the book warns about

- Judging models by training fit instead of test accuracy.
- Using MAPE when the data have zeros or no natural zero.
- Comparing MAE or RMSE across series of different scales.
- Estimating the test error from one small test set when cross-validation is
  possible.
- Forgetting that intervals get wider with the horizon.
