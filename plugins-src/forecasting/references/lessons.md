# Lessons

Known mistakes. Every skill reads this file before it starts. Do not repeat them.

Lessons the user teaches in a project go to `docs/forecast-plans/lessons.md` in
that project, in the same format. Read both files.

Format:

```
### <Skill>: <short description>
**Trigger**: when this tends to happen
**Mistake**: what went wrong
**Rule**: what to do instead
**Source**: <book section | template run | user correction>, <date>
```

### All: AICc across model families
**Trigger**: Comparing ETS with ARIMA, or ARIMA models with different d or D.
**Mistake**: Picking the lowest AICc across them.
**Rule**: AICc compares models only inside one family, fitted to the same data with the same transformation and differencing. Across those, use time series cross-validation.
**Source**: Book sections 9.6, 9.9 and 9.10; arima.py run, 2026-10-21.

### All: Accuracy on the training set
**Trigger**: Reporting residual RMSE or R squared as forecast accuracy.
**Mistake**: Fitted values are one-step predictions from a model that saw the data.
**Rule**: Report accuracy on a test set or from time series cross-validation, per forecast horizon.
**Source**: Book section 5.8.

### All: Forecast horizon in cross-validation
**Trigger**: Cross-validation with h shorter than the decision needs.
**Mistake**: Accuracy at short forecast horizons says little about long ones.
**Rule**: Score every forecast horizon the decision uses.
**Source**: audit_checks.py demo, 2026-10-21.

### Baselines: RMSE per forecast horizon
**Trigger**: Scoring each forecast horizon separately.
**Mistake**: Averaging per-origin RMSE values of one error each, which equals MAE.
**Rule**: Average squared errors over series and forecast origins first, then take the square root. `fc_checks.score_cv` does this.
**Source**: baselines.py run, 2026-10-21.

### Baselines: Guerrero lambda at its bound
**Trigger**: Box-Cox on a series whose variance does not change with the level.
**Mistake**: Using a lambda that sits at the search bound (for example -0.9).
**Rule**: Check the time plot. If the seasonal swing does not grow with the level, do not transform.
**Source**: baselines.py run on beer production, 2026-10-21.

### ARIMA: Choosing among differencing orders by AICc
**Trigger**: The automatic search and a hand-picked model differ in d.
**Mistake**: Taking the lower AICc.
**Rule**: Rank by AICc inside each (d, D) group, then compare groups by cross-validation.
**Source**: arima.py run on H02, 2026-10-21.

### Dynamic regression: Fourier K at the edge of the search
**Trigger**: AICc keeps falling as K grows for a long seasonal period.
**Mistake**: Taking the largest K searched.
**Rule**: When the best K is the largest tried, extend the range or cap K by hand and say so.
**Source**: dynamic_regression.py run on weekly gasoline, 2026-10-21.

### Practical: Intermittent example that ends in zeros
**Trigger**: Scoring Croston methods on a series whose last years are all zero.
**Mistake**: Naive scores zero error and looks perfect.
**Rule**: Look at the end of the series before choosing the test set. A series that has stopped is a different problem (retirement, not forecasting).
**Source**: practical.py run on PBS J06, 2026-10-21.

### Hierarchical: Reconciliation can lose at some levels
**Trigger**: Reporting one overall accuracy for a hierarchy.
**Mistake**: MinT improved the bottom level but lost at the top in the tourism split.
**Rule**: Report accuracy at every level a decision uses.
**Source**: hierarchical.py run on tourism, 2026-10-21.

### Auditor: CUSUM break test
**Trigger**: Using a CUSUM test on a trending series.
**Mistake**: Calling a curved trend a structural break.
**Rule**: Treat the test as a prompt to look at the time plot, not as a finding.
**Source**: audit_checks.py run on gas production, 2026-10-21.

### ETS: Noisy early history drives the model choice
**Trigger**: A long series whose early, low-level years are much noisier in relative terms.
**Mistake**: Taking the AICc choice on the full history (ETS(M,A,M) on gas production); residuals failed Ljung-Box and the intervals were far too wide.
**Rule**: Plot the innovation residuals over time. If their spread changes, compare training windows by cross-validation on the same origins, and say the window was chosen after seeing results.
**Source**: Self-audit run of forecast-ets on aus_production Gas, 2026-10-21.

### Hierarchical: Base residuals and per-level coverage skipped
**Trigger**: Many base series (hundreds) in a reconciliation run.
**Mistake**: The self-audit run reconciled 425 ETS models without residual checks and found the total's 80% interval covered under half the time.
**Rule**: Report the residual pass rate per level and interval coverage per level; both are in the verification gate.
**Source**: Self-audit run of forecast-hierarchical on tourism, 2026-10-21.

### All: Forecast origin years before the decision
**Trigger**: Book datasets, or any extract that stops long before today.
**Mistake**: Both self-audit runs issued forecasts for periods that had already happened (2010 to 2012, 2018 to 2019) as inputs to a decision made in 2026.
**Rule**: Compare the last observation date with the decision date before modelling. Get newer data, or label the work as a backtest or an exercise.
**Source**: forecast-auditor self-audit, 2026-10-21.

### All: Model chosen on the origins that report its accuracy
**Trigger**: Choosing a training window, form or reconciliation method by cross-validation, then quoting the same scores.
**Mistake**: The quoted skill over the benchmark is the best of several tries, so it is optimistic.
**Rule**: Report accuracy on later origins that the choice did not use, or the range over all options; give the count of origins won.
**Source**: forecast-auditor self-audit, 2026-10-21.

### Baselines: Step size that skips seasons
**Trigger**: `step_size` that shares a factor with m (2 with quarterly data, 3 or 6 with monthly).
**Mistake**: Every forecast origin falls in the same few seasons.
**Rule**: Use `step_size=1`, or a step with no common factor with m. `audit_checks.check_origin_seasons` flags it.
**Source**: forecast-auditor self-audit, 2026-10-21.
