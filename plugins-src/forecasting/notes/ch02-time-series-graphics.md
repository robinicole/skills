# Chapter 2: Time series graphics

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `graphics.html`, `tsibbles.html`, `time-plots.html`,
`tspatterns.html`, `seasonal-plots.html`, `subseries.html`, `scatterplots.html`,
`lag-plots.html`, `acf.html`, `wn.html`, `graphics-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `02-graphics.html`, same section anchors.

## Key concepts and decision rules

- Data structure: one row per time point per series. In R a `tsibble` has an
  index (time) and keys (series identifiers). In Python the Nixtla long format is
  `unique_id, ds, y`; the Python edition uses these names (checked 2026-10-22), and
  `plot_series` takes `id_col`, `time_col`, `target_col` for other names.
- Patterns to name on every series: trend (long-run rise or fall, not necessarily
  linear), seasonality (fixed and known period, calendar driven), cycle (rises and
  falls with no fixed period, usually longer than two years, economic). Cycles and
  seasonality are different things and need different models.
- Plot types and what each decides:
  - Time plot: level, trend, breaks, outliers, whether variance grows with the
    level (this decides additive versus multiplicative seasonality and whether a
    transformation is needed).
  - Seasonal plot (one line per season cycle): the shape of the seasonal pattern
    and whether it changes over the years.
  - Seasonal subseries plot (one panel per season, points over years): which
    seasons drift and the mean of each season.
  - Scatterplot matrix: relationships between series or with predictors.
  - Lag plot: y against lagged y, one panel per lag, to see which lags carry
    signal.
  - ACF plot (correlogram): autocorrelation at each lag.
- Reading an ACF: trend gives large positive values that decay slowly; seasonality
  gives spikes at multiples of the period; both together give a slowly decaying
  scalloped shape.
- White noise: a series with no autocorrelation. The ACF of white noise should
  stay inside bounds of about plus or minus 2 divided by the square root of the
  sample size (the book uses 1.96). Expect about 5 percent of spikes outside by
  chance; many more than that means the series is not white noise.

## Model diagnostics the book recommends

The ACF and the white noise bounds are the basis of the residual checks later in
the book.

## Evaluation guidance

None in this chapter.

## R functions and Python equivalents

| R (tsibble, feasts, ggplot2) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `as_tsibble(index=, key=)` | pandas long frame with `unique_id, ds, y` |
| `autoplot()` time plot | `utilsforecast.plotting.plot_series` (the book calls it through `fpppy.utils.plot_series`); also: `StatsForecast.plot()` |
| `gg_season()` | `seaborn.lineplot(x=month, y=, hue=year)` on pandas date parts (no direct equivalent) |
| `gg_subseries()` | matplotlib `subplots(1, m)`, one panel per season with an `axhline` at its mean (no direct equivalent) |
| `gg_lag()` | `Series.shift(k)` + `seaborn.scatterplot` in a grid of lags; also: `pandas.plotting.lag_plot` for one lag |
| `ACF()` + `autoplot()` | `statsmodels.api.tsa.acf`, `statsmodels.graphics.tsaplots.plot_acf` |

## Common mistakes the book warns about

- Calling a cycle "seasonality" or the reverse.
- Reading autocorrelation into an ACF whose spikes are inside the noise bounds.
- Not plotting the data before modelling.
