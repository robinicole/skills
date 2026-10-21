# Chapter 4: Time series features

## Section URLs

R edition [unverified]: `features.html`, `some-simple-statistics.html`,
`acf-features.html`, `stlfeatures.html`, `other-features.html`,
`exploring-australian-tourism-data.html`, `features-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed.

## Key concepts and decision rules

- A feature is one number computed from a series (mean, quantiles, autocorrelation
  at lag 1, trend strength). With many series, features replace plots: compute a
  table of features and look at the table or scatter the features.
- ACF features: autocorrelations of the series, of the differenced series, of the
  twice-differenced series, and at the seasonal lag; sums of squares of the first
  ten autocorrelations.
- STL features: trend strength and seasonal strength, each between 0 and 1,
  computed from the variance of the remainder relative to the variance of
  remainder plus component. A value near 1 means the component dominates. Also the
  timing of the seasonal peak and trough, and the spikiness, linearity and
  curvature of the trend.
- Decision use: seasonal strength sorts series into those needing a seasonal model
  and those that do not; trend strength sorts those needing a trend. Series with
  strong seasonality and strong trend behave differently from noisy ones, so one
  model per group is often better than one model per series.
- Other features: Box-Cox lambda estimate, unit root statistics (KPSS, Phillips
  Perron), number of differences needed (`unitroot_ndiffs`, `unitroot_nsdiffs`),
  Hurst, spectral entropy (low entropy means more forecastable), longest flat
  spot, shift features (level, variance, KL shift), crossing points.
- Use of PCA on the feature table to find unusual series and groups of similar
  series.

## Model diagnostics the book recommends

None; features are exploratory.

## Evaluation guidance

None in this chapter.

## R functions and Python equivalents

| R (feasts) | Python [unverified] |
|---|---|
| `features(y, feat_stl)` | `statsmodels STL` then compute strengths by hand; the `tsfeatures` package computes the same set at scale |
| `features(y, feat_acf)` | `statsmodels.tsa.stattools.acf` |
| `features(y, unitroot_kpss)` | `statsmodels.tsa.stattools.kpss` |
| `features(y, unitroot_ndiffs/nsdiffs)` | `statsforecast.arima.ndiffs`, `nsdiffs` |
| `features(y, feature_set(pkgs="feasts"))` | `tsfeatures.tsfeatures` |

## Common mistakes the book warns about

- Fitting one model per series when series are too short or too many; group them by
  features first.
- Reading trend strength from a series without removing seasonality (compute both
  from STL).
