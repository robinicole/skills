# Diagnostics: dynamic regression

Checks for `forecast-regression`. Severity as in `baselines.md`.
Book: FPP3 10.1 to 10.6 (sections checked 2026-10-22).

## Stationary variables

**Why**: non-stationary variables give inconsistent coefficients (unless the series
are cointegrated).

```python
from statsforecast.arima import ndiffs
print(ndiffs(y, test="kpss"), ndiffs(x, test="kpss"))
```

**Failure**: target differenced but predictors not, or the reverse. **Severity**: serious.
**Fix**: let the ARIMA error differencing apply to all variables (statsforecast
does this when d > 0 with predictors); or difference all by hand.

## Innovation residuals are white noise

**Why**: only the ARIMA errors should be white noise; regression residuals keep
the autocorrelation the ARIMA absorbs.

```python
p, q, P, Q, *_ = model.model_["arma"]
residual_check(model.model_["residuals"], m=m, dof=p + q + P + Q, name="dynreg")
```

**Failure**: Ljung-Box p below 0.05 on the innovation residuals; or the check was
run on the regression residuals. **Severity**: serious.
**Fix**: change the error order; check the residuals of the right kind.

## Future predictor values

**Why**: the forecast is only as good as the predictor values fed to it.
**Test**: how were they obtained: known (calendar), forecast, or scenario?
**Severity**: serious if the intervals are reported as if predictors were known.
**Fix**: say that intervals are conditional; report ex-ante accuracy.

## Fourier K

**Why**: K too small misses the seasonal shape; too large overfits.
**Test**: AICc over K with d fixed; is the best K the largest tried?
**Severity**: minor. **Fix**: extend the range or cap K by hand and say so.

## Lagged predictors on comparable rows

**Why**: AICc values from different row counts are not comparable.
**Test**: did every candidate drop the same first rows?
**Severity**: serious. **Fix**: drop max-lag rows for all, choose, then refit on all usable rows.

## Deterministic trend at long forecast horizons

**Why**: a trend in time assumes the slope never changes, so intervals are too narrow.
**Severity**: serious beyond a few periods. **Fix**: compare with a differenced model with drift.
