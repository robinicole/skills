# ETS: Australian quarterly gas production, 8 quarters ahead

Data: `aus_production`, column `Gas` (PJ), 1956 Q1 to 2010 Q2, n = 218, no gaps, all > 0.
Forecast: 2010 Q3 to 2012 Q2 (8 quarters), 80% and 95% intervals. Feeds a capacity planning decision.
Code: `analysis/ets_gas.py` (full-history candidates and CV), `ets_gas_window.py` (window check),
`ets_gas_final.py` (final model). Logs: `run.log`, `window.log`, `final.log`. Outputs: `analysis/out/`.

No plan, explore.md or baselines.md existed, and I did not stop to ask. Choices I made and state here:
m = 4; benchmark = seasonal naive; cross-validation h = 8 quarters, 12 origins (2002 Q4 to 2008 Q2, step 2 quarters);
no transformation (multiplicative ETS handles the growing swing).

## Candidates (full history, AICc, same data and family)

| Form | AICc | alpha | beta | gamma | phi |
|---|---|---|---|---|---|
| ETS(M,A,M) = auto choice | 1689.8 | 0.83 | 0.05 | 0.08 | |
| ETS(M,N,M) | 1720.1 | 1.00 | | 0.00 | |
| ETS(M,Ad,M) | 1720.6 | 0.97 | 0.05 | 0.00 | 0.80 |
| ETS(A,A,A) | 1839.3 | 0.58 | 0.016 | 0.35 | |
| ETS(A,Ad,A) | 1844.0 | 0.57 | 0.03 | 0.35 | 0.98 |

A,M-season forms were not requested (unstable). Positivity holds, so M components are allowed.

**SERIOUS: residual autocorrelation (full-history ETS(M,A,M))**
Ljung-Box lag 8: stat 43.8, p < 0.001. Same failure for ETS(M,Ad,M) (p < 0.001, mean also off); ETS(A,A,A) borderline (p = 0.049).
The residual plot shows relative errors far larger before about 1975 than after, so one error variance fits neither period.
Why it matters: intervals built from that variance were far too wide in the recent period (cross-validated coverage 99% at the 80% level, 100% at the 95% level).
Choosing by AICc alone also picked a form with worse cross-validated error than ETS(A,A,A): AICc is in-sample.

## Robustness: training window (same CV origins; window.log)

| Training from | Auto form | Ljung-Box p | ETS(A,A,A) RMSE | 80% / 95% coverage of ETS(A,A,A) |
|---|---|---|---|---|
| 1956 | M,A,M | < 0.001 | 9.51 | 0.68 / 0.88 |
| 1970 | M,A,M | 0.071 | 9.02 | 0.72 / 0.94 |
| 1980 | A,A,A | 0.393 | 8.78 | 0.76 / 0.98 |
| 1990 | A,A,A | 0.211 | 8.92 | 0.75 / 0.95 |

Seasonal naive RMSE is 10.91 in every row. From 1980 the automatic search itself chooses ETS(A,A,A).

## Chosen model: ETS(A,A,A), trained on 1980 Q1 to 2010 Q2 (n = 122)

- AICc 1016.2. Automatic search on this window returns the same form. Damped version ETS(A,Ad,A): AICc 1020.2, phi = 0.98.
- alpha = 0.58: the level follows recent data fairly closely.
- beta = 0.0001: the slope barely changes (a fixed trend rate over the window).
- gamma = 0.26: the seasonal pattern drifts slowly rather than staying fixed.
- No phi (undamped). I also fitted the damped trend, as the skill asks for long horizons. Phi = 0.98 is near 1, and cross-validation prefers the undamped form (pooled RMSE 8.78 vs 9.34), so I kept it. Because beta is near 0, the slope is small and the horizon is only 8 quarters, so over-forecasting from the trend is limited here.
- Residual check: Ljung-Box lag 8, stat 8.43, p = 0.393, mean -0.004 (within 2 se). Passes.

## Cross-validated accuracy (12 origins, h = 1 to 8, training from 1980)

Skill = 1 - score / seasonal naive score (positive = better than the benchmark).

| h | MASE ETS(A,A,A) | MASE seasonal naive | MASE skill | RMSE ETS(A,A,A) | RMSE seasonal naive | RMSE skill |
|---|---|---|---|---|---|---|
| 1 | 0.711 | 0.867 | 0.18 | 5.85 | 7.82 | 0.25 |
| 2 | 0.863 | 1.068 | 0.19 | 8.09 | 9.47 | 0.15 |
| 3 | 0.701 | 0.827 | 0.15 | 6.66 | 7.64 | 0.13 |
| 4 | 1.075 | 1.169 | 0.08 | 8.74 | 9.82 | 0.11 |
| 5 | 1.077 | 1.413 | 0.24 | 9.82 | 12.89 | 0.24 |
| 6 | 0.909 | 1.293 | 0.30 | 9.71 | 12.54 | 0.23 |
| 7 | 1.237 | 1.465 | 0.16 | 10.39 | 13.12 | 0.21 |
| 8 | 1.056 | 1.251 | 0.16 | 9.85 | 12.30 | 0.20 |

Pooled: RMSE 8.78 vs 10.91 (skill 0.20), MAE 7.01 vs 8.59. ETS beats the benchmark at every horizon, but the margin at h = 4 is small (8%).
The damped version has lower skill at most horizons and is not better at any long one by MASE.

## Interval coverage (pooled over 96 forecasts)

| Level | ETS(A,A,A) | Seasonal naive |
|---|---|---|
| 80% | 0.76 | 0.77 |
| 95% | 0.98 | 0.95 |

**MINOR: 80% intervals slightly narrow**
Coverage 0.76 against 0.80 nominal, with 12 overlapping origins (a few forecasts per horizon, so noisy; per-horizon values range 0.67 to 0.83).
The 95% interval is at or above nominal. I did not apply conformal intervals: on the full-history model they under-covered badly (0.59 / 0.71), and I did not re-run them on the 1980 window. If this matters, run that step.

## Forecast (PJ)

| Quarter | Point | 80% interval | 95% interval |
|---|---|---|---|
| 2010 Q3 | 253.8 | 245.4 to 262.3 | 241.0 to 266.7 |
| 2010 Q4 | 211.8 | 202.4 to 221.2 | 197.4 to 226.2 |
| 2011 Q1 | 204.3 | 194.0 to 214.6 | 188.5 to 220.0 |
| 2011 Q2 | 242.1 | 231.0 to 253.2 | 225.1 to 259.1 |
| 2011 Q3 | 258.6 | 246.7 to 270.4 | 240.4 to 276.7 |
| 2011 Q4 | 216.6 | 204.0 to 229.2 | 197.3 to 235.8 |
| 2012 Q1 | 209.0 | 195.7 to 222.3 | 188.7 to 229.3 |
| 2012 Q2 | 246.8 | 232.9 to 260.7 | 225.5 to 268.1 |

Files: `analysis/out/final_forecast.csv`, `analysis/out/final_forecast.png`.
Pattern: Q3 is the peak each year and Q1 the trough. The trend adds little over two years (point forecasts sit close to seasonal naive, within about 7 PJ), so the gain over the benchmark is mostly in how the seasonal shape and level are updated.

## Caveats for the capacity decision

- **Window choice was made after looking at cross-validation.** I tried four start years on the same origins and picked 1980, so the reported skill is somewhat optimistic. The 1970, 1980 and 1990 windows all beat seasonal naive, so the conclusion does not depend on the exact year.
- **The data end in 2010 Q2.** The forecast covers 2010 Q3 to 2012 Q2. If you need the next 8 quarters from today, newer data are needed.
- Intervals cover forecast uncertainty from the model only: they assume the 1980+ pattern continues, with no supply shocks, new fields or demand shifts.
- For capacity, the upper end matters: plan against the 95% upper bound (for example 266.7 in 2010 Q3, 276.7 in 2011 Q3, 268.1 in 2012 Q2) if shortfall is costly. The 80% interval is a little narrow in cross-validation.
- Not compared with ARIMA. Do that by cross-validation (`/forecasting:forecast-arima`), never by AICc.

## Verification gate

- [x] Scripts ran without errors (`run.log`, `window.log`, `final.log`).
- [x] Model and parameters quoted: ETS(A,A,A), alpha 0.58, beta 0.0001, gamma 0.26.
- [x] Cross-validated accuracy per horizon quoted with the seasonal naive row.
- [x] Residual check quoted: lag 8, p = 0.393.
- [x] Coverage quoted: 0.76 (80%), 0.98 (95%).

Next: `/forecasting:forecast-auditor`.
