# Diagnostics: ARIMA

Checks for `forecast-arima`. Severity as in `baselines.md`.
Book: FPP3 9.1, 9.7 to 9.10 [unverified sections].

## Variance stable before differencing

**Why**: differencing does not fix a variance that grows with the level.
**Test**: time plot; Guerrero lambda (`boxcox_lambda(y, method="guerrero", season_length=m)`).
**Severity**: serious. **Fix**: log or Box-Cox first.

## Differencing order

**Why**: too little leaves a unit root; too much adds a moving average and inflates
the intervals.

```python
from statsforecast.arima import ndiffs, nsdiffs
D = nsdiffs(y, period=m)
d = ndiffs(y[m:] - y[:-m] if D else y, test="kpss")
```

**Failure**: d + D above 2; lag-1 autocorrelation near -0.5 after differencing
(over-differenced). **Severity**: serious. **Fix**: drop one difference.

## Residuals are white noise

**Why**: the ARMA orders should leave no autocorrelation.

```python
p, q, P, Q, m, d, D = model.model_["arma"]
r = residual_check(model.model_["residuals"], m=m, dof=p + q + P + Q, name="ARIMA")
```

**Failure**: Ljung-Box p below 0.05. **Severity**: serious.
**Fix**: wider search (`AutoARIMA(stepwise=False, approximation=False)`), or other orders read from ACF/PACF.

## AICc comparisons

**Why**: differencing changes the data the likelihood is computed on.
**Test**: do the compared models share d and D? Is ETS in the comparison?
**Severity**: serious. **Fix**: AICc inside one (d, D) group; cross-validation across.

## Constant and long-run behaviour

**Why**: with d = 2 a constant implies a quadratic trend; with d = 1 a constant is
a drift that never stops.
**Test**: `model.model_["coef"]` has `drift` or `intercept`; check d.
**Severity**: serious for d = 2 with a constant; minor otherwise.
**Fix**: remove the constant, or prefer a damped ETS for long forecast horizons.

## Roots near the unit circle

**Why**: AR or MA roots near 1 make the model unstable or close to over-differenced.
**Test**: `statsmodels` `ARIMA(...).fit().arroots` and `.maroots`; moduli close to 1.
**Severity**: minor. **Fix**: change d, or reduce the order.
