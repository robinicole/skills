# Diagnostics: hierarchical and grouped forecasts

Checks for `forecast-hierarchical`. Severity as in `baselines.md`.
Book: FPP3 11.1 to 11.6 (sections checked 2026-10-22).

## Structure is right

**Why**: a wrong summing matrix makes every reconciled forecast wrong.
**Test**: `tags` lists every level; the bottom level count equals the raw series
count; the total exists (add a constant `total` column before `aggregate`).
**Severity**: fatal. **Fix**: rebuild the spec.

## Method fits the structure

**Why**: top-down and middle-out need a strict hierarchy.
**Test**: does the structure cross attributes (grouped)?
**Severity**: serious. **Fix**: bottom-up or MinT for grouped structures.

## Coherence after reconciliation

**Why**: the point of reconciliation.

```python
S = S_df.set_index("unique_id"); wide = R.pivot(index="unique_id", columns="ds", values=col)
gap = abs(S.loc[wide.index].to_numpy() @ wide.loc[list(S.columns)].to_numpy() - wide.to_numpy()).max()
```

**Failure**: gap above rounding. **Severity**: fatal. **Fix**: check the column used and the tags.

## MinT covariance

**Why**: the sample covariance fails when there are more series than observations.
**Test**: number of series against number of training observations.
**Severity**: serious if `mint_cov` is used with many series.
**Fix**: `mint_shrink`; `wls_struct` or `ols` when there are no fitted values.

## Accuracy at every level

**Why**: reconciliation usually helps most levels but can lose at some.
**Test**: scale-free accuracy (MASE, RMSSE) per level, base against reconciled.
**Failure**: one overall number; RMSE pooled across levels.
**Severity**: serious. **Fix**: one row per level (`hierarchical.py` section 6).

## Negative forecasts

**Why**: reconciliation can give negative values for non-negative data.
**Severity**: minor. **Fix**: `MinTrace(method="mint_shrink", nonnegative=True)`.
