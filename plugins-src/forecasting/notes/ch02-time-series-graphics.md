# Chapter 2: Time series graphics

## Section URLs

R edition [unverified]: `graphics.html`, `tsibbles.html`, `time-plots.html`,
`tspatterns.html`, `seasonal-plots.html`, `subseries.html`, `scatterplots.html`,
`lag-plots.html`, `acf.html`, `wn.html`, `graphics-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed.

## Key concepts and decision rules

- Data structure: one row per time point per series. In R a `tsibble` has an
  index (time) and keys (series identifiers). In Python the Nixtla long format is
  `unique_id, ds, y` [unverified that the Python edition uses exactly these names;
  it is the Nixtla convention].
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

| R (tsibble, feasts, ggplot2) | Python [unverified] |
|---|---|
| `as_tsibble(index=, key=)` | pandas long frame with `unique_id, ds, y` |
| `autoplot()` time plot | `StatsForecast.plot()` or `utilsforecast.plotting.plot_series` |
| `gg_season()` | manual pandas pivot + matplotlib (no direct equivalent) |
| `gg_subseries()` | manual (no direct equivalent) |
| `gg_lag()` | `pandas.plotting.lag_plot` for one lag |
| `ACF()` + `autoplot()` | `statsmodels.tsa.stattools.acf`, `statsmodels.graphics.tsaplots.plot_acf` |

## Common mistakes the book warns about

- Calling a cycle "seasonality" or the reverse.
- Reading autocorrelation into an ACF whose spikes are inside the noise bounds.
- Not plotting the data before modelling.
