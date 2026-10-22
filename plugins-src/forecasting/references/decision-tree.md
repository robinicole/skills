# Decision tree: from the problem and the data to a method

`forecast-planner` walks this tree. Method skills use it to suggest a fallback.
Book URLs checked 2026-10-22.

## Q1. Is the target forecastable?

Ask: does the forecast change the outcome (prices in an open market, a stock)? Is
there any relevant history?

- Forecast feeds back on the outcome: say so. Offer naive with a wide prediction
  interval, and stop. Book: FPP3 1.1.
- No relevant history (new product, new market): go to `forecast-judgmental`.
- Otherwise: Q2.

## Q2. Is the question about forecasting or about cause?

"Did the promotion increase sales?", "What would sales have been without the
policy?", "What is the effect of X?": this is causal inference, not forecasting.
Say so and stop. A forecasting model cannot answer it (FPP3 7.x, correlation is
not causation). Otherwise: Q3.

## Q3. Do the series add up?

Products into categories, stores into regions, a total that is the sum of parts:
plan base forecasts for every level, then `forecast-hierarchical`. Continue with
Q4 for the base model.

## Q4. What does the data look like? (`forecast-explore`)

| Data property | Go to |
|---|---|
| Fewer observations than parameters of any seasonal model | Non-seasonal ETS or a benchmark; `forecast-practical` (very short series) |
| Mostly zeros, small counts | `forecast-practical` (Croston family) |
| Must stay positive or inside [a, b] | Transform first; `forecast-practical` (bounded forecasts) |
| Weekly, daily or sub-daily; period long or not an integer | `forecast-regression` (Fourier terms) or `forecast-advanced` (multiple seasonal periods) |
| Monthly, quarterly or yearly, one seasonal period | Q5 |

## Q5. Are there known drivers?

- Drivers whose future values are known or can be forecast better than the target
  (calendar, price plans, temperature forecasts): `forecast-regression`. It starts
  with a linear regression and moves to ARIMA errors when the residuals are
  autocorrelated.
- Several series that drive each other: `forecast-advanced` (VAR).
- No drivers: Q6.

## Q6. Univariate model

Fit both, compare by time series cross-validation (never by AICc across them):

- `forecast-ets`: trend and season visible, multiplicative season, damping.
- `forecast-arima`: autocorrelation beyond trend and season, cycles.

Both must beat the benchmarks from `forecast-baselines`. If neither does, ship the
best benchmark and say so.

## Q7. After the model

- Several models close in accuracy: average them (`forecast-practical`, combinations).
- A person wants to change the numbers: `forecast-judgmental` (adjustment log).
- Before shipping: `forecast-auditor`. Then `forecast-report`.

## Terminal table

| Situation | Skill | Template |
|---|---|---|
| Any series, first step | `forecast-baselines` | `baselines.py` |
| Trend and season, no drivers | `forecast-ets`, `forecast-arima` | `ets.py`, `arima.py` |
| Drivers | `forecast-regression` | `regression.py`, then `dynamic_regression.py` if residuals are autocorrelated |
| Hierarchy or groups | `forecast-hierarchical` | `hierarchical.py` |
| Several seasonal periods, nonlinear, VAR | `forecast-advanced` | `advanced.py` |
| Intermittent, bounded, gaps, outliers | `forecast-practical` | `practical.py` |
| No usable data | `forecast-judgmental` | `adjustment-log.md` |
