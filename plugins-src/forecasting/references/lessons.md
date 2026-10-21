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
**Source**: Book chapters 8 and 9 [unverified section]; arima.py run, 2026-10-21.

### All: Accuracy on the training set
**Trigger**: Reporting residual RMSE or R squared as forecast accuracy.
**Mistake**: Fitted values are one-step predictions from a model that saw the data.
**Rule**: Report accuracy on a test set or from time series cross-validation, per forecast horizon.
**Source**: Book chapter 5 [unverified section].

### All: Forecast horizon in cross-validation
**Trigger**: Cross-validation with h shorter than the decision needs.
**Mistake**: Accuracy at short horizons says little about long ones.
**Rule**: Score every forecast horizon the decision uses.
**Source**: audit_checks.py demo, 2026-10-21.

### Baselines: RMSE per horizon
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
