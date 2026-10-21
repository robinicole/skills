# Forecast audit: 2026-10-21-tourism-hierarchy
**Date**: 2026-10-21  **Method audited**: AutoETS (m=4) base forecasts, grouped structure, MinT-OLS reconciliation with non-negative constraint, normality intervals
**Verdict**: Red (one fatal finding for the stated decision)

## Summary
The forecast is coherent and, in a backtest, beats seasonal naive at every level. However, the data end in 2017 Q4 and the forecast covers 2018 Q1 to 2019 Q4, which is already past, so it cannot allocate a budget from today. Separately, the intervals for the exact configuration shipped (non-negative OLS) were never back-tested, and my re-run shows they cover far less than nominal. Treat the state shares as accurate to roughly ±1.5 percentage points, not to 0.1.

Checks run in code: `check_horizon`, `check_baseline`, `check_cv_design`, `check_metric_scale`, `check_calibration`, `check_break` from `audit_checks.py`. `check_skill` was replaced by a manual per-level MASE comparison against seasonal naive. `check_residuals` was not run, because no fitted-model residuals were saved; this is a finding below. I re-ran the 6-origin backtest (same origins as `hier_origins.py`) with seasonal naive and non-negative OLS added. The script is `scratchpad/aud/aud.py`.

## Findings

### FATAL: Forecast period is in the past; the data are 9 years old
**Category**: 1 Problem fit (and 2 Data)
**Evidence**: `plan.md`: "1998 Q1 to 2017 Q4 ... Horizon: 8 quarters (2018 Q1 to 2019 Q4)". Today is 2026-10-21. `check_horizon`: no gap in length (8 = 8), but the dates do not match the decision. A budget made now needs 2026 Q4 to 2028 Q3. The history also has no 2020 to 2021 collapse and recovery, so the pattern it assumes has already broken once.
**Why it matters**: Shares by state for 2018 to 2019 say nothing about where visitors will go in the next 8 quarters. The state mix has probably moved, and a 9-year extrapolation is outside any evaluated horizon.
**Fix**: If this is a real allocation, refresh the data to the latest quarter, set the horizon from that origin, re-run the pipeline, and decide how to treat 2020 to 2022 (outliers or a break). If it is only a method demonstration, label it as one and do not pass the shares to the budget.
**Owner**: /forecasting:forecast-planner (data, horizon), then /forecasting:forecast-explore (the 2020 to 2022 break), /forecasting:forecast-practical (outliers)

### SERIOUS: Interval coverage of the shipped configuration was never tested, and is poor
**Category**: 5 Uncertainty
**Evidence**: The coverage table in `hierarchical.md` comes from `hier_origins.py`, which uses `MinTrace(method="ols")` without `nonnegative`. `hier_final.py` uses `nonnegative=True`. Re-running the backtest with `nonnegative=True` and applying `check_calibration` to the 6 origins and 8 horizons: State, OLS 80% covers 47% and 95% covers 69% (n=384); the doc reports 73% and 87% for State. Total: 80% covers 23% and 95% covers 33% (n=48); the doc reports 48% and 65%. Base ETS: State 65% and 84%, Total 62% and 83%. In `hier_forecast_final.csv`, the OLS 80% band for Total in 2018 Q1 is 28,421 to 29,586 (width 1,165), against 27,995 to 30,164 for base ETS (width 2,168).
**Why it matters**: The report says OLS "has the best interval coverage". For the final configuration it is the worst of the three. Any budget margin or risk range from these bands is overconfident, by a factor of two or more at the Total.
**Fix**: Back-test coverage with `nonnegative=True`. Try bootstrap or conformal intervals, or use base ETS intervals scaled to coverage. Correct the coverage claim in `hierarchical.md`. Do not publish the reconciled bands until coverage is tested for the final configuration.
**Owner**: /forecasting:forecast-hierarchical (intervals), /forecasting:forecast-baselines (coverage)

### SERIOUS: State shares are shown to 0.1 points, but the method barely moves them and backtest error is about 1.5 points
**Category**: 4 Evaluation (decision link)
**Evidence**: The allocation is by state, but no run scored the shares. My re-run computes the summed absolute share error over 8 quarters (sum of |forecast share − actual share| / 2, in points) across 6 origins: OLS 1.52, base ETS 1.63, seasonal naive 1.68. By origin, OLS ranges from 0.61 to 3.43. The doc's own note says OLS and base shares differ by at most 0.4 points. The NT share is 2.1% against 1.7% for base.
**Why it matters**: A choice between the three methods changes the allocation less than the forecast error does. The one-decimal shares suggest precision the backtest does not support, and small states (NT 2.1%, ACT 2.9%, Tasmania 3.3%) carry large relative errors.
**Fix**: Report shares with the backtest error range next to them (about ±1.5 points; up to 3.4 in a bad window). Show the state-level share error as a standing metric. Rank methods on it, not only on MASE.
**Owner**: /forecasting:forecast-report (caveat), /forecasting:forecast-baselines (share-error metric)

### SERIOUS: Model never checked; verification gate unmet
**Category**: 3 Model
**Evidence**: `plan.md` says explore.md and baselines.md were not produced. `hierarchical.md` says "no residual (Ljung-Box) check". No Ljung-Box output is saved, and `fc_checks.py` residual output is not in `outputs/`. `check_break` on log Total: p=0.0015 (CUSUM rejects a stable linear trend), which is only a prompt, and I did not see a time plot of any series. 304 untuned AutoETS fits include some unstable forms, but none are inspected.
**Why it matters**: Autocorrelated residuals mean missed structure and intervals that are too narrow (consistent with the coverage failure above). Seasonal strength, trend and zeros in small regions are unexamined.
**Fix**: Explore the series (time plots at State level, seasonality, zeros and outliers). Run Ljung-Box with the correct dof on the base ETS fits at the Total, State and a sample of bottom series. Report the share failing. Re-run the audit afterwards.
**Owner**: /forecasting:forecast-explore, /forecasting:forecast-ets

### SERIOUS: Method choice and its evaluation use the same six overlapping origins
**Category**: 4 Evaluation
**Evidence**: `hier_origins.py` evaluates 5 methods on 6 origins, one year apart, each with an 8-quarter test window, so adjacent windows overlap by 4 quarters. OLS beats base ETS at State in 4/6 origins (1.270 vs 1.356 mean MASE). Overall MASE for OLS is 0.979, worse than base ETS (0.960) and shrink (0.931). The recommendation rests on the State, Purpose and Region columns only.
**Why it matters**: The margins at State (0.09 MASE) are small, the windows are not independent, and the winner is picked from the same windows used to report it, so the reported gain is optimistic. The best method at the Total (base ETS) differs from the chosen one.
**Fix**: Report OLS, base ETS and seasonal naive on the same origins and say plainly that the OLS advantage is small. Add earlier origins if the data allow (the first window has far more than two seasons, so more origins are available). Consider a held-out final year for the choice.
**Owner**: /forecasting:forecast-baselines (evaluation design), /forecasting:forecast-hierarchical

### MINOR: Benchmark missing from the multi-origin result (resolved by this audit)
**Category**: 4 Evaluation
**Evidence**: `hier_origins.py` fits only AutoETS, and the table in `hierarchical.md` has no seasonal naive row. `check_baseline` found it in my re-run. Mean MASE over 6 origins, seasonal naive vs OLS (non-negative): Total 1.826 vs 1.692, State 1.431 vs 1.270, Purpose 1.533 vs 1.349, State x Purpose 1.239 vs 1.101, Region 1.129 vs 0.959, Bottom 1.076 vs 0.953. OLS beats the benchmark at every level, so this is not fatal.
**Why it matters**: The doc cannot show skill over a benchmark without that row, but the audit confirms the skill exists.
**Fix**: Add the seasonal naive row to the accuracy table in `hierarchical.md` and `hier_origins.py`.
**Owner**: /forecasting:forecast-baselines

### MINOR: Non-negative option not back-tested, but the check came out close
**Category**: 3 Model
**Evidence**: `hierarchical.md`: "That option was not back-tested." My re-run with `nonnegative=True`: MASE Total 1.692, State 1.270, Purpose 1.349, Region 0.959, Bottom 0.953 (vs 0.956 without the constraint). The backtest raised "Replacing negative forecasts with zero" warnings. Without the constraint OLS had 50 negative point forecasts in the backtest, the most of any method.
**Why it matters**: Accuracy is effectively unchanged, but the constraint is what causes the interval problem above.
**Fix**: Keep the constraint and add its back-test and coverage to the doc.
**Owner**: /forecasting:forecast-hierarchical

### MINOR: Accuracy averaged over h=1 to 8; no interval for 8-quarter totals
**Category**: 5 Uncertainty (and 4 Evaluation)
**Evidence**: MASE tables pool all 8 horizons. State-level mean absolute percentage error by horizon, OLS: 7.8, 9.8, 6.8, 9.7, 9.8, 11.3, 10.0, 13.2% (h=1 to 8). The shares use sums over 8 quarters (`hier_state_8q_totals_shares.csv`), but there is no interval for those sums.
**Why it matters**: Error grows by about 5 points from h=1 to h=8, and the budget uses the sum. A sum's interval is not the sum of interval ends.
**Fix**: Report accuracy by horizon, and give an interval for each state's 8-quarter total from simulated or bootstrapped paths.
**Owner**: /forecasting:forecast-practical, /forecasting:forecast-report

### MINOR: `check_cv_design` leakage flag is a false alarm
**Category**: 2 Data
**Evidence**: `check_cv_design` reported "Some test rows are at or before their cutoff". My frame stored the first test date as `cutoff`. In `hier_origins.py`, `tr = ds < cut` and `te = ds >= cut`, so training and test windows do not overlap. No leakage in the origin construction. The model, lambda and reconciliation are fitted only on `tr` at each origin.
**Why it matters**: None, but noted so the flag is not read as a real fatal.
**Fix**: None.
**Owner**: none

## Not found
No leakage, no accuracy from fitted values, no scale-dependent measure averaged across series (MASE is used), the coherence gap is 0.0, and the series count matches the structure (304 bottom, 425 in total). Disclosed weaknesses (Total reconciled worse than base in 0/6 origins; bottom-up much worse at the Total) are stated honestly in `hierarchical.md`.

## Handoff order
1. forecast-planner: refresh the data and horizon, which decides whether the rest matters.
2. forecast-explore and forecast-ets: time plots, break and outlier handling, residual checks.
3. forecast-hierarchical and forecast-baselines: re-run with the benchmark, `nonnegative` coverage, a share-error metric, and a better interval method.
4. forecast-report: state the share error and the interval caveats beside the numbers.
Then run the audit again.
