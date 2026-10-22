# Diagnostics: exponential smoothing (ETS)

Checks for `forecast-ets`. Severity as in `baselines.md`.
Book: FPP3 8.4 to 8.7 (sections checked 2026-10-22).

## Innovation residuals are white noise

**Why**: autocorrelation left in the residuals means a missing component.

```python
from fc_checks import residual_check
r = residual_check(model.model_["residuals"], m=m, dof=0, name="ETS")
```

For multiplicative error models these residuals are relative errors.
**Failure**: Ljung-Box p below 0.05. **Severity**: serious.
**Fix**: try a different season type or a transformation; compare with ARIMA.

## Model form matches the data

**Why**: multiplicative components need strictly positive data; additive error with
multiplicative season is unstable.
**Test**: `(y > 0).all()` before any M component; the chosen method string
`model.model_["method"]`.
**Failure**: zeros or negatives with an M component; A error with M season requested.
**Severity**: fatal. **Fix**: additive components, or transform first.

## Parameters at a bound

**Why**: alpha, beta or gamma near 0 or 1, or phi at 0.8 or 0.98, means the search
hit a limit or a component is not needed.

```python
alpha, beta, gamma, phi = model.model_["par"][:4]
```

**Severity**: minor. **Fix**: read it (gamma near 0 = fixed season); try the
simpler form without that component.

## Long forecast horizon with an undamped trend

**Why**: a straight-line trend over-forecasts far ahead.
**Test**: trend type A with a forecast horizon of several seasons or more.
**Severity**: serious. **Fix**: compare with the damped trend (`damped=True`) by cross-validation.

## AICc used across families

**Why**: ETS and ARIMA likelihoods differ.
**Severity**: serious. **Fix**: compare by time series cross-validation.

## Intervals

**Why**: ETS intervals assume the model is right and errors are uncorrelated.
**Test**: coverage in cross-validation (`audit_checks.check_calibration`).
**Severity**: serious when coverage is clearly below nominal.
**Fix**: conformal intervals, or fix the residuals first.
