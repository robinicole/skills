# Chapter 11: Forecasting hierarchical and grouped time series

## Section URLs

R edition [unverified]: `hierarchical.html`, `hts.html`, `gts.html`,
`single-level.html`, `reconciliation.html`, `tourism.html`, `prison.html`,
`rec-prob.html`, `hierarchical-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed.

## Key concepts and decision rules

- A hierarchy nests strictly (country > state > region). A grouped structure
  crosses attributes with no single nesting (state x purpose). Mixed structures
  combine both. All are described by a summing matrix S that maps the bottom-level
  series to every aggregate.
- Coherent forecasts add up the same way the data do. Base forecasts from
  independent models at each level are not coherent.
- Single-level approaches: bottom-up (forecast leaves, sum; loses no information
  at the bottom but leaves are noisy and no aggregate-level information is used);
  top-down (forecast the total, split by proportions: average historical
  proportions, proportions of historical averages, or forecast proportions, which
  do best; simple and reliable at the top, loses leaf dynamics, and biased even
  when the base forecasts are unbiased); middle-out (one middle level, bottom-up
  above it, top-down below it; hierarchies only).
- Reconciliation: any coherent method is a linear combination of all base
  forecasts, written with a matrix G; the reconciled forecasts are S G times the
  base forecasts. Unbiasedness requires S G S = S. MinT (minimum trace) chooses G
  to minimise the total variance of the reconciled forecast errors, using the
  base forecast error covariance. Variants: OLS (identity covariance), WLS with
  structural weights (number of bottom series per node, no residuals needed), WLS
  with variance scaling (residual variances), MinT with the sample covariance
  (fails when there are more series than observations), MinT with shrinkage (the
  default).
- Reconciliation usually improves accuracy at most levels but can lose at some;
  evaluate every level that matters. Scale-free measures per level; RMSE across
  levels is dominated by the top.
- Prediction intervals: reconcile the whole distribution, for Gaussian forecasts
  by applying the same combination to the covariance, otherwise by reconciling
  bootstrapped sample paths.
- Examples in the book: Australian tourism (hierarchy and grouped), prison
  population (grouped).

## Model diagnostics the book recommends

Check coherence after reconciliation (each parent equals the sum of its children).
Compare base and reconciled accuracy per level.

## Evaluation guidance

Accuracy at every level, on a scale-free measure, base versus bottom-up versus
MinT; test set long enough for the decision horizon.

## R functions and Python equivalents

| R (fable) | Python [unverified] |
|---|---|
| `aggregate_key(state / region, y = sum(y))` | `hierarchicalforecast.utils.aggregate(df, spec)`; add a constant `total` column, spec lists the levels |
| `aggregate_key((state * purpose), ...)` grouped | the same `aggregate` with a spec that lists each crossing as its own level |
| `reconcile(fit, bu = bottom_up(base), td = top_down(base), mint = min_trace(base, method="mint_shrink"))` | `HierarchicalReconciliation(reconcilers=[BottomUp(), TopDown(method=), MiddleOut(), MinTrace(method="mint_shrink")])` |
| `min_trace(method="ols"/"wls_struct"/"wls_var"/"mint_cov"/"mint_shrink")` | `MinTrace(method="ols"/"wls_struct"/"wls_var"/"mint_cov"/"mint_shrink")` |
| `forecast()` on a reconciled mable | `hrec.reconcile(Y_hat_df=, Y_df=fitted_values, S_df=, tags=, level=, intervals_method="normality"/"bootstrap")` |
| `accuracy()` grouped by level | `utilsforecast.evaluation.evaluate` grouped by `tags` |

## Common mistakes the book warns about

- Reporting accuracy only at the top level.
- Using sample-covariance MinT with many series.
- Assuming reconciliation helps every level.
- Applying middle-out to a grouped structure.
