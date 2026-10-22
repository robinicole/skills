# Chapter 3: Time series decomposition

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `decomposition.html`, `transformations.html`,
`components.html`, `moving-averages.html`, `classical-decomposition.html`,
`methods-used-by-official-statistics-agencies.html`, `stl.html`,
`decomposition-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `03-decomposition.html`, same section anchors.

## Key concepts and decision rules

- Adjustments first: calendar (days per month), population (per capita), inflation
  (deflate to one price level), currency. Removing known sources of variation makes
  the series simpler before any model is fitted.
- Mathematical transformations: log, power, Box-Cox with parameter lambda. Lambda 0
  is the log; lambda 1 is no change. Decision rule: use a transformation when the
  size of the seasonal swings grows or shrinks with the level of the series. Choose
  lambda so that the seasonal swing looks constant across the time plot, and round
  it to a readable value. The book picks lambda with the Guerrero method, and says a
  low lambda can give very wide prediction intervals.
- Back-transformed point forecasts are medians, not means. When means are needed
  (sums, budgets) apply the bias adjustment (covered in chapter 5).
- Components: trend-cycle, seasonal, remainder. Additive when the seasonal swing is
  constant; multiplicative when it scales with the level. A log transform turns a
  multiplicative pattern into an additive one.
- Seasonally adjusted series = data minus the seasonal component (or divided by it).
  It still contains the remainder, so it is noisy; use the trend-cycle to look for
  turning points, and the seasonally adjusted series when the seasonal pattern is
  not of interest.
- Moving averages smooth the series; a centred 2 x m moving average estimates the
  trend-cycle for a period m. Classical decomposition is built on this.
- Classical decomposition is simple and dated: the seasonal component cannot
  change, the first and last observations lose their trend estimate, and it is not
  robust to unusual values.
- X-11, SEATS (X-13ARIMA-SEATS) are what official statistics agencies use for
  monthly and quarterly data; they handle trading days and holidays and let the
  seasonal pattern evolve.
- STL: works for any period, lets the seasonal component change over time at a rate
  the user controls, can be robust to outliers, estimates the trend to the ends of
  the series. It is additive only (transform first for multiplicative) and does not
  handle trading-day or calendar effects. Two main settings: the trend window and
  the seasonal window (a larger seasonal window means a slower-changing seasonal
  pattern; "periodic" fixes it).

## Model diagnostics the book recommends

Inspect the decomposition plot: the remainder should look like noise; a seasonal
window that is too small lets the seasonal component absorb noise.

## Evaluation guidance

None in this chapter.

## R functions and Python equivalents

| R | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `box_cox()`, `features(y, guerrero)` | `coreforecast.scalers.boxcox_lambda(y, method="guerrero", season_length=m)` then `boxcox(y, lam)`; `method="loglik"` for non-seasonal data; also: `scipy.stats.boxcox` (maximum-likelihood lambda, not Guerrero) |
| `model(STL(y ~ trend(window=) + season(window=)))` | `statsmodels.tsa.seasonal.STL(endog, period, seasonal, trend, robust)`; `statsforecast.models.MSTL` for forecasting |
| `model(classical_decomposition(y, type=))` | `statsmodels.tsa.seasonal.seasonal_decompose(model="additive"/"multiplicative")` |
| `X_13ARIMA_SEATS()` | `statsmodels.tsa.x13` needs the external X-13 binary; no pure-Python equivalent (not in the Python edition: X-11 and SEATS are described, not run) |
| `components()`, `autoplot(components)` | result attributes `.trend`, `.seasonal`, `.resid` put in a DataFrame and drawn with `plot_series`; also: `.plot()` |

## Common mistakes the book warns about

- Forecasting the seasonally adjusted series when the seasonal pattern is what the
  user cares about.
- Using classical decomposition where the seasonal pattern changes.
- Reading the seasonally adjusted series for turning points (use trend-cycle).
