# R to Python map

R column: fable 0.5.0, feasts 0.5.0, fabletools, tsibble 1.2.0 (installed from
conda-forge, R 4.4.3). Python column: statsforecast 2.1.1, mlforecast 1.1.0,
hierarchicalforecast 1.5.3, utilsforecast 0.2.17, coreforecast 0.0.19,
statsmodels 0.15.0. Signatures were read from the installed packages with
`inspect.signature` and `ls("package:...")` on 2026-10-21.

**Not checked against the Python edition.** The Python edition could not be
fetched, so the "Python" column is the closest installed API, not necessarily what
the Python edition uses. Rows marked `Not from the book` are my choice.

Status: `equivalent` = same method and same defaults to my knowledge;
`partial` = same idea, different defaults or missing options;
`none` = no equivalent; closest option named.

| R function | Python function | Library | Status |
|---|---|---|---|
| `as_tsibble(index=, key=)` | long frame `unique_id, ds, y` | pandas | equivalent |
| `autoplot()` | `StatsForecast.plot()` / matplotlib | statsforecast | partial |
| `gg_season()`, `gg_subseries()` | pandas pivot + matplotlib | pandas | none (manual) |
| `gg_lag()` | `pandas.plotting.lag_plot` | pandas | partial (one lag per call) |
| `ACF()`, `PACF()` | `acf`, `pacf`, `plot_acf`, `plot_pacf` | statsmodels | equivalent |
| `gg_tsdisplay()`, `gg_tsresiduals()` | three matplotlib panels | statsmodels | none (manual) |
| `ljung_box(lag=, dof=)` | `acorr_ljungbox(x, lags=, model_df=)` | statsmodels | equivalent |
| `box_pierce()` | `acorr_ljungbox(boxpierce=True)` | statsmodels | equivalent |
| `guerrero()` | `coreforecast.scalers.boxcox_lambda(method="guerrero")` [check arg] ; `scipy.stats.boxcox` is ML | coreforecast | partial |
| `box_cox()`, `inv_box_cox()` | `coreforecast.scalers.boxcox`, `inv_boxcox`; `scipy.special.inv_boxcox` | coreforecast / scipy | equivalent |
| `STL()` | `STL(endog, period, seasonal, trend, robust)` | statsmodels | partial (window defaults differ) |
| `STL()` with two `season()` | `MSTL(endog, periods=)` | statsmodels | partial |
| `classical_decomposition()` | `seasonal_decompose()` | statsmodels | equivalent |
| `X_13ARIMA_SEATS()` | `x13_arima_analysis()` (needs external binary) | statsmodels | partial |
| `feat_stl` | STL strengths by hand; `tsfeatures` (Not from the book) | statsmodels | partial |
| `feat_acf`, `feat_spectral`, shift features | `tsfeatures` (Not from the book) | tsfeatures | partial |
| `unitroot_kpss` | `kpss()` | statsmodels | equivalent |
| `unitroot_ndiffs`, `unitroot_nsdiffs` | `statsforecast.arima.ndiffs`, `nsdiffs` [check exported] | statsforecast | equivalent |
| `MEAN()` | `HistoricAverage()` | statsforecast | equivalent |
| `NAIVE()` | `Naive()` | statsforecast | equivalent |
| `SNAIVE()` | `SeasonalNaive(season_length=)` | statsforecast | equivalent |
| `RW(y ~ drift())` | `RandomWalkWithDrift()` | statsforecast | equivalent |
| `TSLM(y ~ trend() + season())` | `ols` + `DeterministicProcess` | statsmodels | partial (no AICc/CV in `glance`) |
| `fourier(K=)` | `Fourier(period=, order=)` | statsmodels | equivalent |
| `ETS()` | `AutoETS(season_length=, model="ZZZ", damped=)` | statsforecast | equivalent |
| `ARIMA()` | `AutoARIMA(season_length=, stepwise=, approximation=)` | statsforecast | equivalent |
| `ARIMA(y ~ pdq() + PDQ())` | `ARIMA(order=, seasonal_order=, season_length=)` | statsforecast | equivalent |
| `ARIMA(y ~ x)` | `AutoARIMA` with exog columns + `X_df=` | statsforecast | equivalent |
| `decomposition_model(STL, ...)` | `MSTL(season_length=, trend_forecaster=)` | statsforecast | partial |
| `THETA()` | `Theta()` | statsforecast | equivalent |
| `CROSTON()` | `CrostonClassic`, `CrostonSBA`, `CrostonOptimized`, `TSB` | statsforecast | equivalent |
| `VAR()` | `VAR`, `select_order(ic="bic")` | statsmodels | equivalent |
| `NNETAR()` | lags into `MLForecast` with `sklearn.neural_network.MLPRegressor` | mlforecast | partial (no NNAR defaults, no averaging over starts) |
| `prophet()` (fable.prophet) | `prophet.Prophet` | prophet | equivalent |
| TBATS (forecast pkg, not fable) | `AutoTBATS(season_length=)` | statsforecast | Not from the book's code |
| `forecast(h=, bootstrap=TRUE)` | `ConformalIntervals(h=, n_windows=)` | statsforecast | none (different method) |
| `generate(h=, times=)` | `simulate()` on statsmodels `ETSModel`/`SARIMAX` results | statsmodels | partial |
| `hilo()` | `level=[80, 95]` columns | statsforecast | equivalent |
| `augment()` | `forecast(fitted=True)` + `forecast_fitted_values()` | statsforecast | equivalent |
| `report()`, `tidy()`, `glance()` | `sf.fitted_[i, j].model_` dict [check keys] | statsforecast | partial |
| `accuracy()` | `evaluate(df, metrics=, train_df=, level=)` | utilsforecast | equivalent |
| MAE, RMSE, MAPE, MASE, RMSSE | `mae`, `rmse`, `mape`, `mase`, `rmsse` | utilsforecast | equivalent |
| `quantile_score`, `winkler_score`, `CRPS` | `quantile_loss`, `winkler_score`, `scaled_crps` | utilsforecast | partial (CRPS is scaled) |
| `skill_score()` | by hand: 1 - score / benchmark score | pandas | partial |
| `stretch_tsibble(.init, .step)` | `cross_validation(h=, n_windows=, step_size=, input_size=)` | statsforecast | equivalent |
| `aggregate_key()` | `aggregate(df, spec)` | hierarchicalforecast | equivalent |
| `bottom_up()` | `BottomUp()` | hierarchicalforecast | equivalent |
| `top_down(method=)` | `TopDown(method=)` | hierarchicalforecast | equivalent |
| `middle_out()` | `MiddleOut(middle_level=, top_down_method=)` | hierarchicalforecast | equivalent |
| `min_trace(method=)` | `MinTrace(method=)` | hierarchicalforecast | equivalent |
| `combination_ensemble()` / mable arithmetic | mean of forecast columns | pandas | partial (no distribution) |
| `interpolate()` with ARIMA | `SARIMAX` accepts NaN; Kalman smoother | statsmodels | partial |
