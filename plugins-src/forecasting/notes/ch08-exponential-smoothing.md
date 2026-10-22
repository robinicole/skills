# Chapter 8: Exponential smoothing

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `expsmooth.html`, `ses.html`, `holt.html`, `holt-winters.html`, `taxonomy.html`,
`ets.html`, `exponential-smoothing.html#sec-ets-estimation`, `ets-forecasting.html`,
`expsmooth-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `08-exponential-smoothing.html`, same section anchors.

## Key concepts and decision rules

- Forecasts are weighted averages of past observations with weights decaying
  geometrically. Simple exponential smoothing (no trend, no seasonality): one
  smoothing parameter alpha; alpha near 1 reacts fast, near 0 averages far back.
  Its forecast is flat.
- Holt's linear trend adds a slope with parameter beta; the forecast is a straight
  line, which over-forecasts at long horizons. Damped trend adds phi (between 0.8
  and 0.98 in practice) so the slope flattens; the book calls this the most popular
  automatic choice for many series, and lets the information criterion decide.
- Holt-Winters adds seasonality with parameter gamma, additive (constant swing) or
  multiplicative (swing scales with level). Damped versions of both exist.
- Taxonomy: Error (A or M) x Trend (N, A, Ad) x Season (N, A, M). Fifteen
  combinations after the unstable ones are excluded: multiplicative error needs
  strictly positive data; additive error with multiplicative season (A,N,M; A,A,M;
  A,Ad,M) is numerically unstable and the automatic search skips it.
- Each combination is a state space model with a level, trend and seasonal state
  updated each period. Additive and multiplicative error versions give the same
  point forecasts but different prediction intervals.
- Estimation by maximum likelihood (or least squares for additive error). Model
  selection by AICc among ETS models fitted to the same data. The AICc of an ETS
  model cannot be compared with the AICc of an ARIMA model.
- Prediction intervals: closed forms for the linear (additive) models; simulation
  for the others. Intervals widen with the horizon except for the flat methods
  where growth is slower.
- Parameter reading: alpha near 1 means the level chases the latest value; gamma
  near 0 means a fixed seasonal pattern; a damping parameter near 1 is almost
  Holt's method.

## Model diagnostics the book recommends

Residual checks as in chapter 5; inspect the component plot (level, slope,
season) to see whether the fitted states make sense.

## Evaluation guidance

AICc within the ETS family; held-out accuracy or cross-validation against the
benchmarks and against other families.

## R functions and Python equivalents

| R (fable) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `ETS(y)` (automatic) | `statsforecast.models.AutoETS(season_length=)` |
| `ETS(y ~ error("A") + trend("Ad") + season("M"))` | `statsforecast.models.AutoETS(season_length=, model="AAM", damped=True)`; a full model string fixes the form, `phi=` fixes the damping |
| `report()`, `tidy()`, `components()` | `sf.fitted_[i, j].model_` dict: `"method"`, `"fit"].x` (parameters), `"par"`, `"components"`, `"states"`, `"residuals"`, `"actual_residuals"` |
| `forecast(h=)` | `sf.forecast(h=, level=)` |
| `glance()` AICc | `model_["aicc"]` [check] (not in the Python edition) |
| `statsmodels.tsa.holtwinters.ExponentialSmoothing` / `ETSModel` | alternative with full state space output (not in the Python edition) |

## Common mistakes the book warns about

- Comparing ETS and ARIMA by AICc.
- Requesting an unstable combination (additive error with multiplicative season).
- Using Holt's undamped trend for long horizons.
- Using multiplicative components on data with zeros or negatives.
