# Diagnostics: benchmarks, residuals, transformations, evaluation

Checks for `forecast-baselines`. Severity: **fatal** = do not use the forecast;
**serious** = use only with the caveat stated; **minor** = note it.
Book: FPP3 5.4, 5.5, 5.8 to 5.10 (sections checked 2026-10-22).

## Residuals uncorrelated

**Why**: autocorrelated residuals mean the model left usable information behind,
and its prediction intervals are too narrow.

```python
from fc_checks import residual_check
r = residual_check(resid, m=m, dof=0, name="SeasonalNaive")   # dof = 0 for benchmarks
```

**Failure**: Ljung-Box p below 0.05 at lag 2m (seasonal) or 10, capped at T/5.
**Severity**: serious for a model you plan to ship; expected for benchmarks.
**Fix**: add the missing structure (season, trend, transformation) or move to a
method skill.

## Residual mean zero

**Why**: a non-zero mean is bias; every forecast is off by about that amount.
**Test**: `r["mean_within_2se"]` from `residual_check`.
**Severity**: minor. **Fix**: add the mean to the forecasts, or fix the model.

## Constant variance, normal shape

**Why**: only the default interval formula needs them. Point forecasts do not.
**Test**: residual time plot and histogram saved by `residual_check`.
**Severity**: minor. **Fix**: transform, or use conformal intervals
(`statsforecast.utils.ConformalIntervals(h=h, n_windows=5)`).

## Transformation chosen on the data

**Why**: the transformation should make the seasonal swing constant. A lambda at
the search bound usually means no transformation is needed.

```python
from coreforecast.scalers import boxcox_lambda
lam = boxcox_lambda(train_y, method="guerrero", season_length=m)
```

**Failure**: lambda at -0.9 or 2 (the bounds), or a transformation on a series whose
swing does not grow with the level. **Severity**: minor. **Fix**: check the time
plot; round lambda; drop the transformation when it is not needed.

## Back-transformed point is a median

**Why**: after a transformation the back-transformed point forecast is a median.
Sums of medians are not medians of sums.
**Test**: are the forecasts summed (budget, capacity, hierarchy)?
**Severity**: serious when forecasts are summed. **Fix**: bias-adjust (see
`baselines.py`, section 5).

## Evaluation design

**Why**: training fit rewards every extra parameter.
**Test**: `audit_checks.check_cv_design(cv, train_df, m)` and
`check_horizon(decision_h, evaluated_h, forecast_h)`.
**Failure**: accuracy from fitted values; one short test set; forecast horizon
shorter than the decision; fewer than 5 origins.
**Severity**: fatal when accuracy comes from fitted values; serious otherwise.
**Fix**: time series cross-validation per `references/evaluation.md`.
