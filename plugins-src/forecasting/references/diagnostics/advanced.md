# Diagnostics: advanced methods

Checks for `forecast-advanced`. Severity as in `baselines.md`.
Book: FPP3 chapter 12 (sections checked 2026-10-22).

## The standard model was tried first

**Why**: the book keeps ETS, ARIMA and dynamic regression as the comparison.
**Test**: is a standard model and a benchmark scored on the same test data?
**Severity**: serious. **Fix**: add them.

## Multiple seasonal periods

**Why**: every period present must be modelled.
**Test**: ACF spikes at each period; residual ACF after the fit.
**Severity**: serious if a period is left in the residuals.
**Fix**: add it to `MSTL(season_length=[...])` or add a Fourier set for it.

## Prophet residuals and intervals

**Why**: Prophet does not model autocorrelation, so its residuals usually fail the
white noise test and its intervals are not calibrated.
**Test**: `residual_check(resid, m=7, name="prophet")`; coverage in cross-validation.
**Severity**: serious. **Fix**: report point accuracy only, or use dynamic regression.

## VAR

**Why**: VAR needs stationary series and enough data for k squared times p coefficients.
**Test**: `ndiffs` per series; lag order by BIC (`VAR(df).select_order(maxlags).selected_orders["bic"]`); residual check per equation.
**Severity**: serious if non-stationary or residuals fail.
**Fix**: difference; lower the lag order; use dynamic regression when there is no feedback.

## NNAR approximation

**Why**: one network is unstable; intervals need simulation.
**Test**: number of networks averaged; how intervals were produced.
**Severity**: serious if intervals come from a normal formula.
**Fix**: average 20 or more networks; simulate paths with resampled errors, or give no interval.

## Bagging

**Why**: too few bootstrap series or blocks shorter than the dependence give little gain.
**Test**: number of series (the book uses many; 30 in the template to keep it short) and block size.
**Severity**: minor. **Fix**: more series; block size at least 2m.
