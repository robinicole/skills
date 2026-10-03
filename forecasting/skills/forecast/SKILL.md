---
name: forecast
description: Build a time series forecast end to end, from problem framing to shipped intervals, following Hyndman and Athanasopoulos (FPP3) in Python. Use when the user wants to forecast a series over time, choose a forecasting model, or asks why a forecast is bad.
---

# Forecast

Every run walks the same seven steps. Two rules hold throughout:

- **The bar** is seasonal naive (plain naive for non-seasonal data). A model that cannot clear the bar does not ship.
- **White residuals.** Structure left in the residuals is signal the model missed.

The Python stack is Nixtla (`statsforecast`, `utilsforecast`, `hierarchicalforecast`) plus `statsmodels`. Data is a long frame with columns `unique_id, ds, y`. [PYTHON.md](PYTHON.md) maps the book's R functions to Python and holds the end-to-end script.

## 1. Frame the problem

Pin down the quantity, the granularity (SKU-week, store-day), the horizon, and who uses the numbers for what decision.

Done when you can write one sentence of the form "forecast X per Y, Z periods ahead, as a point plus an N% interval, used for W". Ask the user for any part you cannot fill.

## 2. Tidy the data

One series per `unique_id`, a regular `ds` index, gaps made explicit as rows. Apply the adjustments that remove variation unrelated to the target: days per month, per capita, inflation, one currency.

Done when every series has a constant frequency, missing periods are listed (count per series), and each adjustment is either applied or ruled out with a reason.

## 3. Explore

Plot and test until you can name each series' trend, seasonality (and period m), variance behaviour and outliers. Choose a transform and decide whether to decompose. Read [EXPLORE.md](EXPLORE.md) for the plots, the ACF reading guide, strength features, Box-Cox and STL.

Done when, for each series or each feature cluster of series, you have written down: m, trend yes/no, seasonality additive or multiplicative, transform (with lambda), and any breaks or outliers with dates.

## 4. Fit candidates

Fit the four benchmarks (mean, naive, seasonal naive, drift) and at least two real models chosen from what step 3 found. [MODELS.md](MODELS.md) covers benchmarks, ETS, ARIMA, dynamic regression, complex seasonality and the rest. For data with a special shape (intermittent, bounded, very short, weekly or finer) check [PRACTICAL.md](PRACTICAL.md) first.

When series add up through a hierarchy (SKU, store, region, total), use the `forecasting:reconcile` skill on top of this step.

Done when every candidate other than the benchmarks has passed the residual check in [MODELS.md](MODELS.md#residuals-and-intervals), or has been fixed or dropped. The benchmarks are the yardstick and skip the check.

## 5. Evaluate

Run the `forecasting:backtest` skill on all candidates and the bar at the horizons from step 1. It owns metric choice, leakage checks and model selection.

Done when backtest has produced its skill table and named a winner, or named the bar as the winner.

## 6. Forecast

Refit the winner on all the data and forecast with the interval levels from step 1, using conformal intervals if backtest switched to them. When several models are close, see Combining in [MODELS.md](MODELS.md#combining).

Done when the output has a point forecast and the agreed intervals for every series and every horizon, back-transformed to the original scale.

## 7. Plan monitoring

State how live accuracy will be tracked (the same metrics as backtest, against the bar) and when the model is refit.

Done when the refit schedule and the accuracy check are written into the deliverable.
