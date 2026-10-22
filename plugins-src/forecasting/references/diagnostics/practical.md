# Diagnostics: practical issues

Checks for `forecast-practical`. Severity as in `baselines.md`.
Book: FPP3 chapter 13 (sections checked 2026-10-22).

## Intermittent demand scored correctly

**Why**: MAPE is undefined at zero; a Croston forecast is a rate.
**Test**: metric used; how the forecast is described.
**Severity**: serious. **Fix**: MAE or MASE; describe it as average demand per period.

## Series still alive

**Why**: a series that ended in zeros needs a retirement decision, not a model.
**Test**: zeros in the last two seasons.
**Severity**: serious. **Fix**: confirm with the data owner; drop or flag it.

## Bounds respected

**Why**: forecasts below zero or above a capacity are impossible values.
**Test**: `(fc[cols] < a).any()` or above b.
**Severity**: serious. **Fix**: log or scaled logit transform, then back-transform.

## Aggregate intervals

**Why**: errors at different forecast horizons are correlated; summed interval ends are wrong.
**Test**: was an interval for a total made by adding interval ends?
**Severity**: serious. **Fix**: simulate sample paths, sum per path, take quantiles (`practical.py` section 7).

## Combination

**Why**: averaging point forecasts gives no valid interval.
**Test**: is an interval reported for a combination?
**Severity**: serious if made by averaging interval ends. **Fix**: pool simulated paths, or report the point only.

## Missing values

**Why**: a gap may carry information (a closed shop).
**Test**: ask why the values are missing.
**Severity**: serious if informative gaps were interpolated.
**Fix**: dummies in a dynamic regression; otherwise state-space interpolation (SARIMAX accepts NaN).

## Outliers

**Why**: replacing a real value removes information about the future.
**Test**: robust STL remainder beyond 3 IQR; ask whether the value is an error or will recur.
**Severity**: minor. **Fix**: keep with a dummy; replace only errors.

## Short series

**Why**: there is no minimum length, but every parameter needs data.
**Test**: observations against parameters; full seasons available.
**Severity**: serious if a seasonal model has fewer than two seasons.
**Fix**: non-seasonal model or benchmark; let AICc choose.

## Weekly data

**Why**: m = 52 drifts off the calendar: a 53-week year comes about once every five to six years, and the true period is 365.25 / 7 = 52.18.
**Test**: seasonal period used.
**Severity**: serious. **Fix**: Fourier terms with period 365.25 / 7.
