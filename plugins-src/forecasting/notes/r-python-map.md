# R to Python map

R column: fable 0.5.0, feasts 0.5.0, fabletools, tsibble 1.2.0 (installed from
conda-forge, R 4.4.3). Python column: statsforecast 2.1.1, mlforecast 1.1.0,
hierarchicalforecast 1.5.3, utilsforecast 0.2.17, coreforecast 0.0.19,
statsmodels 0.15.0. Signatures were read from the installed packages with
`inspect.signature` and `ls("package:...")` on 2026-10-21.

**Checked against the Python edition 2026-10-22.** Where the Python edition uses
a different function, the "Python function" cell names it first and keeps the
earlier choice after "also:". Rows marked `not in the Python edition` have no code
there. Rows marked `Not from the book` are my choice.

Status: `equivalent` = same method and same defaults to my knowledge;
`partial` = same idea, different defaults or missing options;
`none` = no equivalent; closest option named.

| R function | Python function | Library | Status |
|---|---|---|---|
| `as_tsibble(index=, key=)` | long frame `unique_id, ds, y` | pandas | equivalent |
| `autoplot()` | `utilsforecast.plotting.plot_series` (book wrapper `fpppy.utils.plot_series`); also: `StatsForecast.plot()` | utilsforecast | partial |
| `gg_season()`, `gg_subseries()` | `seaborn.lineplot(hue=year)`; subseries as one matplotlib panel per season | pandas, seaborn | none (manual) |
| `gg_lag()` | `Series.shift(k)` + `seaborn.scatterplot`; also: `pandas.plotting.lag_plot` | pandas | partial (one lag per call) |
| `ACF()`, `PACF()` | `acf`, `pacf`, `plot_acf`, `plot_pacf` | statsmodels | equivalent |
| `gg_tsdisplay()`, `gg_tsresiduals()` | `plot_diagnostics()` helper written in the book: three matplotlib panels | statsmodels | none (manual) |
| `ljung_box(lag=, dof=)` | `acorr_ljungbox(x, lags=, model_df=)` | statsmodels | equivalent |
| `box_pierce()` | `acorr_ljungbox(boxpierce=True)` | statsmodels | equivalent |
| `guerrero()` | `coreforecast.scalers.boxcox_lambda(y, method="guerrero", season_length=m)`; `scipy.stats.boxcox` is ML | coreforecast | partial |
| `box_cox()`, `inv_box_cox()` | `coreforecast.scalers.boxcox`, `inv_boxcox`; `scipy.special.inv_boxcox` | coreforecast / scipy | equivalent |
| `STL()` | `STL(endog, period, seasonal, trend, robust)` | statsmodels | partial (window defaults differ) |
| `STL()` with two `season()` | `statsforecast.models.MSTL(season_length=[m1, m2])`; also: statsmodels `MSTL(endog, periods=)` | statsforecast | partial |
| `classical_decomposition()` | `seasonal_decompose()` | statsmodels | equivalent |
| `X_13ARIMA_SEATS()` | `x13_arima_analysis()` (needs external binary; not in the Python edition) | statsmodels | partial |
| `feat_stl` | `tsfeatures.tsfeatures(df, freq=m, features=[stl_features])`; also: STL strengths by hand | tsfeatures | partial |
| `feat_acf`, `feat_spectral`, shift features | `tsfeatures` (`acf_features`, `entropy`, `lumpiness`, ...) | tsfeatures | partial |
| `unitroot_kpss` | `kpss()` | statsmodels | equivalent |
| `unitroot_ndiffs`, `unitroot_nsdiffs` | `statsforecast.arima.ndiffs`, `nsdiffs` | statsforecast | equivalent |
| `MEAN()` | `HistoricAverage()` | statsforecast | equivalent |
| `NAIVE()` | `Naive()` | statsforecast | equivalent |
| `SNAIVE()` | `SeasonalNaive(season_length=)` | statsforecast | equivalent |
| `RW(y ~ drift())` | `RandomWalkWithDrift()` | statsforecast | equivalent |
| `TSLM(y ~ trend() + season())` | `MLForecast(models=fpppy.models.LinearRegression())` + `utilsforecast.feature_engineering.trend`, `pandas.get_dummies`; also: `ols` + `DeterministicProcess` | mlforecast | partial (no AICc/CV in `glance`) |
| `fourier(K=)` | `utilsforecast.feature_engineering.fourier(df, freq=, season_length=, k=)`; also: statsmodels `Fourier(period=, order=)` | utilsforecast | equivalent |
| `ETS()` | `AutoETS(season_length=, model="ZZZ", damped=)` | statsforecast | equivalent |
| `ARIMA()` | `AutoARIMA(season_length=, stepwise=, approximation=)` | statsforecast | equivalent |
| `ARIMA(y ~ pdq() + PDQ())` | `ARIMA(order=, seasonal_order=, season_length=)` | statsforecast | equivalent |
| `ARIMA(y ~ x)` | `AutoARIMA` with exog columns + `X_df=` | statsforecast | equivalent |
| `decomposition_model(STL, ...)` | statsmodels `STL`, then `Naive` and `SeasonalNaive` on the parts, summed; also: `MSTL(season_length=, trend_forecaster=)` | statsforecast | partial |
| `THETA()` | `Theta()` (not in the Python edition) | statsforecast | equivalent |
| `CROSTON()` | `CrostonClassic`, `CrostonOptimized`, `CrostonSBA`; also: `TSB` | statsforecast | equivalent |
| `VAR()` | `VAR(df).fit(ic="bic")`; also: `select_order()` | statsmodels | equivalent |
| `NNETAR()` | `neuralforecast.models.MLP(h=, input_size=)` (Python edition chapter 14); also: lags into `MLForecast` with `sklearn.neural_network.MLPRegressor` | neuralforecast | partial (no NNAR defaults, no averaging over starts) |
| `prophet()` (fable.prophet) | `prophet.Prophet`, `add_seasonality()`; also: `statsforecast.adapters.prophet.AutoARIMAProphet` | prophet | equivalent |
| TBATS (forecast pkg, not fable) | `AutoTBATS(season_length=)` (not in the Python edition) | statsforecast | Not from the book's code |
| `forecast(h=, bootstrap=TRUE)` | bootstrap by hand from `forecast_fitted_values()` residuals; also: `ConformalIntervals(h=, n_windows=)` | numpy | partial |
| `generate(h=, times=)` | `simulate()` on statsmodels `ETSModel`/`SARIMAX` results (not in the Python edition) | statsmodels | partial |
| `hilo()` | `level=[80, 95]` columns | statsforecast | equivalent |
| `augment()` | `forecast(fitted=True)` + `forecast_fitted_values()` | statsforecast | equivalent |
| `report()`, `tidy()`, `glance()` | `sf.fitted_[i, j].model_` dict (`aicc`, `fit`, `states`, `residuals`, ...); `statsforecast.arima.ARIMASummary` | statsforecast | partial |
| `accuracy()` | `evaluate(df, metrics=, train_df=, level=)` | utilsforecast | equivalent |
| MAE, RMSE, MAPE, MASE, RMSSE | `mae`, `rmse`, `mape`, `mase`; `rmsse` not in the Python edition | utilsforecast | equivalent |
| `quantile_score`, `winkler_score`, `CRPS` | book writes `quantile_score` and `winkler_score` helpers; CRPS as 2 x `mqloss` over many levels, `scaled_crps` in ch. 11; also: `quantile_loss`, `winkler_score` | utilsforecast | partial (CRPS is scaled) |
| `skill_score()` | by hand: 1 - score / benchmark score | pandas | partial |
| `stretch_tsibble(.init, .step)` | `cross_validation(h=, step_size=, test_size=)` or `n_windows=` | statsforecast | equivalent |
| `aggregate_key()` | `aggregate(df, spec)`; score with `hierarchicalforecast.evaluation.evaluate(tags=)` | hierarchicalforecast | equivalent |
| `bottom_up()` | `BottomUp()` | hierarchicalforecast | equivalent |
| `top_down(method=)` | `TopDown(method=)` | hierarchicalforecast | equivalent |
| `middle_out()` | `MiddleOut(middle_level=, top_down_method=)` | hierarchicalforecast | equivalent |
| `min_trace(method=)` | `MinTrace(method=)` | hierarchicalforecast | equivalent |
| `combination_ensemble()` / mable arithmetic | mean of forecast columns | pandas | partial (no distribution) |
| `interpolate()` with ARIMA | `pandas.Series.interpolate()`; also: `SARIMAX` accepts NaN, Kalman smoother | pandas | partial |
