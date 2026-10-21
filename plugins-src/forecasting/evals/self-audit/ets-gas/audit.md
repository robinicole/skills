# Forecast audit: aus-gas (quarterly gas production, 8 quarters ahead)
**Date**: 2026-10-21  **Method audited**: ETS(A,A,A), trained 1980 Q1 to 2010 Q2 (n = 122), `ets.md`
**Verdict**: Red (a fatal finding)

## Summary
The model itself is reasonable: residuals are clean, it beats seasonal naive at every horizon in cross-validation, and the 8-quarter horizon was scored. But the forecast covers 2010 Q3 to 2012 Q2, and the data stop in 2010 Q2, so it cannot serve a capacity decision made today. The reported skill over the benchmark is also less certain than the write-up says: the training window was chosen on the same origins that score it, and the margin over seasonal naive is not clearly different from zero.

## Automated checks (run on this analysis)
I re-ran the 1980 Q1 window model and the 12-origin, h = 8 cross-validation (`audit_run.py` in the scratchpad), then ran `check_horizon`, `check_baseline`, `check_cv_design`, `check_skill`, `check_metric_scale`, `check_calibration`, `check_residuals` and `check_break`. Output of `report(findings)`:

```
Empty DataFrame
Columns: [category, check, severity, finding]
```

No automated finding. I verified the underlying numbers myself rather than relying on the write-up: Ljung-Box lag 8 p = 0.393 (matches `final.log`), pooled coverage 0.76 / 0.98, and the CV frame has 12 origins, h up to 8, SeasonalNaive present, and the first window has 82 points (over 8 seasons).
The automated checks cannot see the findings below. They need judgment, or extra code that I ran separately.

## Findings

### FATAL: Forecast period is in the past; the data do not reach the decision
**Category**: 1 Problem fit, 2 Data
**Evidence**: `ets.md`: data end 2010 Q2, forecast is 2010 Q3 to 2012 Q2. Today is 2026-10-21. An 8-quarter decision made now needs 2026 Q4 to 2028 Q3. The write-up notes this itself ("newer data are needed") but still issues the numbers as the forecast for the capacity decision.
**Why it matters**: The point forecasts and intervals (for example 253.8 PJ and a 266.7 upper bound for 2010 Q3) describe quarters that have already happened. Applied to 2026 to 2028 capacity they would be a 16-year extrapolation from a stale origin, with no check that the 1980 to 2010 pattern still holds. Nothing here says whether the decision is a historical exercise or a live one; if it is live, this forecast must not be used.
**Fix**: Confirm the decision date. If live, obtain data up to the latest quarter, re-explore (trend, season, any break since 2010), refit and re-evaluate with the same protocol. If this is a teaching or backtest example, label it that way in `ets.md` and drop the "feeds a capacity decision" claim.
**Owner**: /forecasting:forecast-planner (reframe), then /forecasting:forecast-explore and /forecasting:forecast-ets (refit)

### SERIOUS: Window and form chosen on the same origins that report the skill
**Category**: 4 Evaluation
**Evidence**: `ets_gas.py` scored six forms on 12 origins (2002 Q4 to 2008 Q2); `ets_gas_window.py` scored four start years on the same origins; 1980 was chosen. The reported RMSE 8.78 against 10.91 (skill 0.20) is the best of 4 windows on these origins (8.78 to 9.51 across them). The model was also selected after seeing the full-history CV (AICc picked M,A,M; CV preferred A,A,A). `ets.md` admits the window choice but calls the optimism "somewhat".
**Why it matters**: Headline accuracy is an in-sample-selected number. The stated 20% gain over seasonal naive is an upper estimate.
**Fix**: Fix the selection rule, then score on origins not used to select. For example: choose window and form on origins up to 2005, report on later origins; or report the range across windows (0.17 to 0.20 RMSE skill for the 1970, 1980 and 1990 windows) rather than the best one.
**Owner**: /forecasting:forecast-baselines (evaluation design), /forecasting:forecast-ets

### SERIOUS: The gain over seasonal naive is not clearly different from zero
**Category**: 4 Evaluation
**Evidence**: Per-origin MAE over the 8-quarter block: ETS beats seasonal naive at 7 of 12 origins. Mean MAE difference 1.58 PJ; origin bootstrap 90% interval [-0.73, 3.99] includes zero. The 12 origins step by 2 with h = 8, so they overlap heavily: they cover about 24 quarters of test data, roughly 3 independent 8-quarter blocks. The largest wins come from the last three origins (3.6, 4.6, 3.3 against 9.6, 5.4, 5.9).
**Why it matters**: "Beats the benchmark at every horizon" is true for the pooled numbers but rests on a thin test span. A planner who reads skill 0.20 may trust ETS over a trivial seasonal naive more than the evidence supports. Point forecasts differ from seasonal naive by under 7 PJ anyway (`ets.md`).
**Fix**: State the skill with an interval or a count of origins won; extend the test span (more origins, step 1, or a sliding-window version) where data allow. If ETS stays within noise of seasonal naive, say so next to the number.
**Owner**: /forecasting:forecast-baselines

### SERIOUS: Trend is one fixed slope over 30 years while recent growth is slowing
**Category**: 3 Model
**Evidence**: beta = 0.0001 (at the lower bound), so the trend is a fixed straight line from 1980. Decade mean level: 116.4 (1980s), 152.4 (1990s), 204.0 (2000s). Q3 peaks since 2006: 233, 245, 249, 252, i.e. +12, +4, +3. The damped form has phi = 0.98 and lower CV skill pooled, but damped has lower RMSE at h = 1, 2 and 5, and the two forecasts differ by 8.1 PJ by 2012 Q2 (238.7 against 246.8).
**Why it matters**: Over 8 quarters the undamped trend adds 5.5 PJ at the 2011 Q3 peak (258.6 against 253.1) and 8.1 PJ by 2012 Q2 against the damped model. For a capacity plan this is the size of the answer. `ets.md` says the horizon is short enough to ignore this, but the CV that supports the choice only covers 2002 to 2010, a period of steady growth.
**Fix**: Report the damped forecast beside the undamped one as a sensitivity range, or test trend choice on a later period with slower growth. Re-check once newer data are in.
**Owner**: /forecasting:forecast-ets

### SERIOUS: Additive error and season on a series whose level has nearly doubled
**Category**: 3 Model
**Evidence**: Mean level rises from 116 (1980s) to 204 (2000s). Residual sd by thirds of the 1980 window: 4.97, 5.06, 5.94 (+20% in the last third). `ets.md` states "no transformation (multiplicative ETS handles the growing swing)" but the chosen model is additive, so a growing swing is handled only through gamma = 0.26 drift. The M-form was rejected on a full-history fit that was bad for a different reason (noisy 1956 to 1975 data), and M forms on the 1980 window were never fitted and scored.
**Why it matters**: A constant interval width understates uncertainty as the level rises, and the rationale in the write-up contradicts the chosen model. Intervals are used for the planning bound.
**Fix**: Fit ETS(M,A,M) and ETS(M,Ad,M) on the 1980+ window and compare by CV on the same origins; or test a log transform. Correct the sentence in `ets.md` either way.
**Owner**: /forecasting:forecast-ets

### MINOR: 80% intervals under-cover and the conformal step was not repeated
**Category**: 5 Uncertainty
**Evidence**: Coverage 0.76 at 80%, 0.98 at 95%, 96 forecasts from 12 overlapping origins; per-horizon 80% range 0.67 to 0.83. `check_calibration` raised nothing (its binomial test ignores the overlap, so it is lenient). The conformal result (0.59 / 0.71) belongs to the full-history model; it was not re-run on 1980+. The 95% level over-covers while 80% under-covers, which points to errors that are not normal.
**Why it matters**: The planning advice leans on the 95% upper bound; that bound looks adequate, but the evidence base is small.
**Fix**: Run conformal intervals on the 1980+ window and compare coverage and Winkler score; keep the 95% bound as the planning number only with the origin count stated.
**Owner**: /forecasting:forecast-ets

### MINOR: Cross-validation origins sit in two of four seasons
**Category**: 4 Evaluation
**Evidence**: step_size = 2 gives cutoffs in Q2 and Q4 only (6 origins in Q2 and 6 in Q4, none in Q1 or Q3). Origins 2002 Q4 to 2008 Q2.
**Why it matters**: Forecasts that start from Q1 or Q3 are never scored; with a strong seasonal pattern, error can depend on the starting quarter.
**Fix**: Use step_size = 1 (or an odd step) so all four origin quarters appear.
**Owner**: /forecasting:forecast-baselines

### MINOR: Only one benchmark; no ARIMA comparison; symmetric loss for an asymmetric decision
**Category**: 4 Evaluation, 1 Problem fit
**Evidence**: Only SeasonalNaive is compared in the final analysis (Naive was run in `ets_gas.py` only). `ets.md` states ARIMA was not compared. Capacity shortfall and overbuild have different costs, but the primary measure is RMSE/MASE and no cost or service level was stated ("No plan ... existed, and I did not stop to ask").
**Why it matters**: Without a stated service level, "plan against the 95% upper bound" is a guess; a quantile score at the right level would show whether the intervals serve the decision.
**Fix**: Add a drift-with-season or ARIMA benchmark compared by CV, and write a plan that records the cost of shortfall against overbuild, then score with the quantile score at that level.
**Owner**: /forecasting:forecast-planner, /forecasting:forecast-arima

## Checked and found sound
- Residuals (3): Ljung-Box lag 8, stat 8.43, p = 0.393, mean -0.004; reproduced.
- Leakage (2): training data cut at origin in every window; test rows all after cutoff (`check_cv_design` clean). No transformation, so no lambda to leak. The data have no gaps and are all positive.
- Horizon (1, 4): CV scored h = 1 to 8, which matches the decision's 8 quarters. Forecast has 8 periods.
- Structural break (2): `check_break` on the 1980+ series did not flag. The earlier noisy 1956 to 1975 history was handled by the window, which is the right kind of fix, as long as the choice is reported as above.

## Handoff order
1. Resolve the data/decision date (fatal), then re-run the whole pipeline on current data.
2. Re-do evaluation: selection separate from reporting, all four origin quarters, skill with an interval.
3. Fit M forms and the damped sensitivity on the new window.
4. Run this audit again after the fixes.
