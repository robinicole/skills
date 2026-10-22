# Chapter 7: Time series regression models

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `regression.html`, `regression-intro.html`,
`least-squares.html`, `useful-predictors.html`, `selecting-predictors.html`,
`forecasting-regression.html`, `nonlinear-regression.html`,
`regression.html#sec-causality`, `regression-matrices.html`,
`regression-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `07-regression.html`, same section anchors.

## Key concepts and decision rules

- Linear model: the target is a linear combination of predictors plus an error.
  Assumptions on the error: mean zero, not autocorrelated, unrelated to the
  predictors; normality only for the standard interval formulas. Predictors must not
  be random in the model's eyes, and must not be perfectly collinear.
- Least squares estimation; coefficients read as the change in the target per unit
  change in that predictor with the other predictors held fixed, which is not the
  same as a simple regression on one predictor.
- Goodness of fit: R squared always rises when predictors are added, so it is not a
  selection tool; the residual standard error is the one-step accuracy on the
  training data.
- Useful predictors that need no outside data: a linear trend on time; dummy
  variables for seasons (one fewer than the number of seasons; never a full set
  with an intercept); intervention dummies (a spike for a one-off event, a step for
  a permanent change, a ramp for a gradual change); trading-day counts; Easter and
  other moving holidays; Fourier terms for seasonality (K sine and cosine pairs;
  K = m/2 reproduces seasonal dummies; useful for long periods such as weekly data);
  distributed lags of an advertising-type predictor.
- Selecting predictors: use AICc (or AIC, BIC, or cross-validation, which all
  penalise extra parameters), not p-values or R squared. Fit all subsets when the
  number of predictors allows; otherwise backward stepwise. Adjusted R squared is
  allowed but tends to pick too many predictors. The chapter's leave-one-out CV
  statistic has a closed form from the hat matrix.
- Forecasting with regression: ex-ante forecasts use forecasts of the predictors;
  ex-post forecasts use their actual later values and serve only to isolate model
  error. Scenario-based forecasts fix the predictors at chosen values. Prediction
  intervals from the regression ignore the uncertainty in the predictor forecasts
  and are too narrow in ex-ante use. Intervals widen as the predictor moves away
  from its mean.
- Nonlinear regression: transform the target (log) or the predictor, or fit a
  piecewise linear trend with knots at known change points. Piecewise trends
  extrapolate; cubic splines must not be used to forecast because the last piece
  extrapolates a cubic.
- Correlation is not causation, and causation is not required to forecast. A
  confounder can make a predictor useful even with no causal link. Spurious
  regression: two trending series regress on each other with high R squared and
  highly autocorrelated residuals; a Durbin Watson statistic far from 2 or a
  residual ACF with slow decay reveals it. Multicollinearity makes coefficients
  unstable but barely hurts forecasts, as long as the future predictor values stay
  inside the range seen in training.
- Residual plots: residuals against time, against each predictor, against the
  fitted values. A pattern means a missing or nonlinear term or heteroscedasticity.

## Model diagnostics the book recommends

Residual time plot and ACF, Ljung-Box with degrees of freedom reduced by the
number of coefficients, residuals against predictors and fitted values, Breusch
Godfrey test for serial correlation in regression residuals, Durbin Watson for lag 1.

## Evaluation guidance

AICc, BIC, or leave-one-out CV for predictor selection; ex-ante versus ex-post
accuracy reported separately.

## R functions and Python equivalents

| R (fable) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `TSLM(y ~ trend() + season())` | `mlforecast.MLForecast(models=fpppy.models.LinearRegression())` with `utilsforecast.feature_engineering.trend` and `pandas.get_dummies(..., drop_first=True)`; also: `statsmodels.formula.api.ols` with `DeterministicProcess` |
| `fourier(K=)` | `utilsforecast.feature_engineering.fourier(df, freq=, season_length=, k=)`; also: `statsmodels.tsa.deterministic.Fourier(period, order)` |
| `glance()` (AICc, CV) | AIC, AICc, BIC and leave-one-out CV (hat-matrix shortcut) written as helper functions in the chapter; also: statsmodels `results.aic`, `results.bic` |
| `forecast(new_data=scenarios())` | `MLForecast.predict(h=, X_df=scenario_df)`, one call per scenario; intervals from `PredictionIntervals(n_windows=, h=)` at fit (conformal); also: statsmodels `results.get_prediction(exog=future_X)` |
| `gg_tsresiduals()`, `ljung_box` | `plot_diagnostics()` helper (time plot, `plot_acf`, histogram), `acorr_ljungbox(resid, lags=[10])` |
| `TSLM(y ~ trend(knots=))` | piecewise terms built by hand: `(trend - tau).clip(lower=0)` per knot |

## Common mistakes the book warns about

- Selecting predictors by p-value or R squared.
- Using a full set of seasonal dummies with an intercept.
- Extrapolating a cubic spline.
- Reading a coefficient as a causal effect.
- Ignoring autocorrelated residuals (spurious regression).
