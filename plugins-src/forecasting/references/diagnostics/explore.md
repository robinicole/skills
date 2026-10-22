# Diagnostics: exploration, transformation, decomposition, features

Checks for `forecast-explore`. Severity as in `baselines.md`.
Book: FPP3 chapters 2, 3, 4 (sections checked 2026-10-22).

## Regular time index, gaps explicit

**Why**: every method assumes one observation per period.

```python
full = pd.date_range(df["ds"].min(), df["ds"].max(), freq=FREQ)
gaps = full.difference(pd.DatetimeIndex(df["ds"]))
```

**Failure**: missing periods not listed, duplicate dates. **Severity**: serious.
**Fix**: add the missing rows as NaN and handle them (`forecast-practical`).

## Seasonal period identified

**Why**: the seasonal period m sets the benchmark, the model and the lag rule.
**Test**: seasonal plot, subseries plot, ACF spikes at multiples of m.
**Failure**: m taken from the calendar without checking the data; weekly data with
m = 52 when the period is 52.18. **Severity**: serious.
**Fix**: confirm on the plots; for non-integer or long periods use Fourier terms.

## Additive or multiplicative

**Why**: decides the transformation and the ETS season type.
**Test**: does the seasonal swing grow with the level on the time plot?
**Severity**: minor. **Fix**: log or Box-Cox, then additive.

## Decomposition fit

**Why**: a seasonal window that is too short lets the seasonal component absorb
noise; one that is too long hides a changing season.

```python
from statsmodels.tsa.seasonal import STL
res = STL(y, period=m, seasonal=13, robust=True).fit()
```

**Failure**: remainder with structure; seasonal component that wiggles every year.
**Severity**: minor. **Fix**: change `seasonal` (odd number, larger = smoother).
Avoid classical decomposition for forecasting work.

## Outliers and breaks

**Why**: they distort parameters and residual checks.
**Test**: robust STL remainder beyond 3 IQR of the middle half (`explore.py`
section 5); time plot for level shifts.
**Severity**: serious when a break is not handled.
**Fix**: keep the outlier with a dummy, or replace it only if it is an error;
start the training data after a break.

## White noise

**Why**: a white noise series has nothing to forecast beyond its mean.
**Test**: Ljung-Box on the series; ACF inside about 2 divided by the square root of T.
**Severity**: none. **Fix**: use the mean or naive and say so.

## Many series

**Why**: one model per series overfits when series are short or many.
**Test**: trend and seasonal strength per series (`explore.py`, `strengths()`).
**Severity**: minor. **Fix**: group series by features; one model per group.
