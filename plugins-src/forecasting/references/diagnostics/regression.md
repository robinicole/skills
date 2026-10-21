# Diagnostics: linear regression

Checks for `forecast-regression`. Severity as in `baselines.md`.
Book: FPP3 7.3 to 7.9 [unverified sections].

## Residuals uncorrelated

**Why**: autocorrelated residuals make the standard errors and intervals wrong and
may signal a spurious regression.

```python
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from fc_checks import residual_check
r = residual_check(fit.resid, m=m, dof=len(fit.params), name="regression")
bg_p = acorr_breusch_godfrey(fit, nlags=2 * m)[1]
```

**Failure**: Ljung-Box or Breusch-Godfrey p below 0.05. **Severity**: serious.
**Fix**: move to regression with ARIMA errors (`forecast-dynamic-regression`).

## Spurious regression

**Why**: two trending series regress on each other with a high R squared and no
real link.
**Test**: high R squared together with strongly autocorrelated residuals.
**Severity**: fatal. **Fix**: difference both series or model the errors as ARIMA.

## Residual patterns against predictors and fitted values

**Why**: a pattern means a missing term, a nonlinear effect, or changing variance.
**Test**: scatter plots saved by `regression.py` section 5.
**Severity**: serious. **Fix**: add the term, transform, or use a piecewise trend.

## Predictor selection

**Why**: R squared always rises; p-values do not measure forecast value.
**Test**: was selection by AICc, BIC or leave-one-out CV?
**Severity**: serious if by R squared or p-values. **Fix**: all-subsets by AICc
(`regression.py` section 4).

## Dummy trap

**Why**: m season dummies plus an intercept are perfectly collinear.
**Test**: count season dummies; with an intercept there must be m - 1.
**Severity**: serious. **Fix**: `DeterministicProcess(..., seasonal=True, drop=True)`.

## Extrapolation

**Why**: future predictor values outside the training range give unreliable
forecasts, and cubic splines explode at the ends.
**Severity**: serious. **Fix**: piecewise linear trend with knots; scenarios inside the observed range.

## Ex-ante versus ex-post

**Why**: ex-post accuracy uses the actual predictors and overstates real accuracy.
**Test**: how were future predictor values obtained?
**Severity**: serious if ex-post is reported as the accuracy. **Fix**: forecast the
predictors and report ex-ante accuracy.
