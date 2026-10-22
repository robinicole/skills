# Method registry

One entry per method: when to use it, the Python function, the book's R function,
and the book sections. Book URLs follow the pattern `https://otexts.com/fpp3/<page>.html`
(R edition) and `https://otexts.com/fpppy/` (Python edition). Page names checked
2026-10-22; old section pages redirect to anchors on the chapter page.

## Benchmarks (mean, naive, seasonal naive, drift)

- **Use**: always, first. They are the bar every other model must clear.
- **Python**: `statsforecast.models.HistoricAverage`, `Naive`, `SeasonalNaive(season_length=m)`, `RandomWalkWithDrift` (column `RWD`).
- **R (book)**: `MEAN()`, `NAIVE()`, `SNAIVE()`, `RW(y ~ drift())`.
- **Book**: FPP3 5.2 (`simple-methods`).
- **Skill**: `forecast-baselines`. Diagnostics: `diagnostics/baselines.md`.

## Decomposition (STL, classical) and features

- **Use**: exploration; seasonal adjustment; forecasting the adjusted series with a non-seasonal model.
- **Python**: `statsmodels.tsa.seasonal.STL`, `seasonal_decompose`; `statsforecast.models.MSTL(season_length, trend_forecaster)` for forecasting.
- **R (book)**: `STL()`, `classical_decomposition()`, `decomposition_model()`, `feat_stl`.
- **Book**: FPP3 3.4 to 3.6, 4.3, 5.7.
- **Skill**: `forecast-explore`. Diagnostics: `diagnostics/explore.md`.

## Linear regression

- **Use**: predictors with known or forecastable future values, and residuals that are not autocorrelated; trend and season dummies; Fourier terms.
- **Python**: `statsmodels.api.OLS` with `statsmodels.tsa.deterministic.DeterministicProcess` and `Fourier`.
- **R (book)**: `TSLM()`, `trend()`, `season()`, `fourier()`.
- **Book**: FPP3 chapter 7.
- **Skill**: `forecast-regression`. Diagnostics: `diagnostics/regression.md`.

## Exponential smoothing (ETS)

- **Use**: trend and seasonality without drivers; multiplicative seasonality; damped trend for long forecast horizons. Strong default for many series.
- **Python**: `statsforecast.models.AutoETS(season_length=m, model="ZZZ", damped=None)`.
- **R (book)**: `ETS(y ~ error() + trend() + season())`.
- **Book**: FPP3 chapter 8.
- **Skill**: `forecast-ets`. Diagnostics: `diagnostics/ets.md`.

## ARIMA

- **Use**: autocorrelation that ETS does not capture; cycles; stationary series after differencing.
- **Python**: `statsforecast.models.AutoARIMA(season_length=m)`, `ARIMA(order, seasonal_order, season_length)`; `statsforecast.arima.ndiffs`, `nsdiffs`; `statsmodels.tsa.stattools.kpss`.
- **R (book)**: `ARIMA(y ~ pdq() + PDQ())`, `unitroot_kpss`, `unitroot_ndiffs`, `unitroot_nsdiffs`.
- **Book**: FPP3 chapter 9.
- **Skill**: `forecast-arima`. Diagnostics: `diagnostics/arima.md`.

## Dynamic regression (regression with ARIMA errors)

- **Use**: predictors plus autocorrelated errors; long or non-integer seasonal periods (Fourier terms); lagged effects; scenarios.
- **Python**: `AutoARIMA` / `ARIMA` with predictors in `X` (model API) or extra columns plus `X_df` (`StatsForecast` API).
- **R (book)**: `ARIMA(y ~ x + fourier(K = k) + PDQ(0, 0, 0))`.
- **Book**: FPP3 chapter 10.
- **Skill**: `forecast-regression`. Diagnostics: `diagnostics/dynamic-regression.md`.

## Hierarchical and grouped reconciliation

- **Use**: series that add up; coherent forecasts at every level.
- **Python**: `hierarchicalforecast.utils.aggregate`; `HierarchicalReconciliation` with `BottomUp`, `TopDown(method)`, `MiddleOut(middle_level, top_down_method)`, `MinTrace(method)`.
- **R (book)**: `aggregate_key()`, `reconcile()`, `bottom_up()`, `top_down()`, `middle_out()`, `min_trace()`.
- **Book**: FPP3 chapter 11.
- **Skill**: `forecast-hierarchical`. Diagnostics: `diagnostics/hierarchical.md`.

## Multiple seasonality, Prophet, VAR, neural networks, bagging

- **Use**: only when ETS, ARIMA or dynamic regression miss a specific feature; keep them in the comparison.
- **Python**: `MSTL(season_length=[m1, m2])`; Fourier terms with `AutoARIMA`; `prophet.Prophet`; `statsmodels.tsa.api.VAR`; `mlforecast.MLForecast` with `sklearn.neural_network.MLPRegressor` (Not from the book: approximation of NNAR); bagging by hand (see `advanced.py`).
- **R (book)**: `STL()` with several `season()`, `prophet()`, `VAR()`, `NNETAR()`, `generate(bootstrap = TRUE)`.
- **Book**: FPP3 chapter 12.
- **Skill**: `forecast-advanced`. Diagnostics: `diagnostics/advanced.md`.

## Practical cases

- **Use**: counts and intermittent demand, bounded values, combinations, aggregates, backcasting, short and long series, missing values, outliers.
- **Python**: `CrostonClassic`, `CrostonSBA`, `TSB`; scaled logit by hand; `statsmodels` `ETSModel.simulate` for sample paths; `SARIMAX` for gaps; robust `STL` for outliers.
- **R (book)**: `CROSTON()`, `new_transformation()`, `generate()`, `interpolate()`.
- **Book**: FPP3 chapter 13.
- **Skill**: `forecast-practical`. Diagnostics: `diagnostics/practical.md`.

## Judgmental forecasting

- **Use**: no data, or information the model cannot see.
- **Python**: none. Use `templates/adjustment-log.md`.
- **Book**: FPP3 chapter 6.
- **Skill**: `forecast-judgmental`.
