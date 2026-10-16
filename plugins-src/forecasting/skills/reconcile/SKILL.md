---
name: reconcile
description: Reconcile forecasts across a hierarchy or grouped structure so levels add up, using MinT. Use when series aggregate (SKU, category, store, region, total), the user mentions hierarchical or grouped forecasting, or forecasts at different levels disagree.
---

# Reconcile

When series add up, forecast every level, then reconcile so the numbers are **coherent** (each aggregate equals the sum of its children) and each level borrows strength from the others. Reconciliation sits on top of any base forecast: ETS, ARIMA, boosted.

## Structure

A **hierarchy** nests strictly: store inside region. A **grouped** structure crosses attributes, category × region, with no single nesting order. Both reduce to one summing matrix S that maps bottom series to every aggregate; `aggregate` builds it from a spec. Middle-out works only on a strict hierarchy.

## Methods

| Method | How | Weakness |
| --- | --- | --- |
| Bottom-up | Forecast leaves, sum | Leaves are noisy; misses aggregate-level signal |
| Top-down | Forecast total, split by proportions (forecast proportions beat historical ones) | Simple and reliable at the top, good with low counts; loses leaf dynamics, and no top-down split is unbiased even when the base forecasts are |
| Middle-out | Forecast a middle level, sum up, split down | Both weaknesses, one per side |
| MinT | Combine all base forecasts to minimise the total reconciled error variance | Needs the base error covariance; the sample estimate fails with many series, shrinkage fixes that |

MinT with the shrinkage covariance (`mint_shrink`) is the default. `ols` and `wls_struct` need no residuals (`wls_struct` weights by how many bottom series each node sums), so use them when base forecasts are judgmental or the model has no fitted values. Intervals reconcile two ways: Gaussian (apply the same combination to the mean and covariance; the default `normality`) or by reconciling each bootstrap sample path when normality does not hold (`bootstrap`). Both need `level=` in the reconcile call.

## Steps

1. Build every level and S. `aggregate` adds no total on its own, so the spec starts with a single-valued `total` column. Done when `tags` starts with `total`, lists each level, and the bottom level matches the raw series count.
2. Forecast every level with `fitted=True` (MinT needs in-sample errors). Done when every series in `Y_df` has base forecasts and fitted values.
3. Reconcile with BottomUp and MinT side by side. Done when both reconciled columns (`AutoETS/BottomUp`, `AutoETS/MinTrace_method-mint_shrink`) exist and an aggregate equals the sum of its children within rounding.
4. Backtest with the `forecasting:backtest` skill, reporting every level that ships, on a scaled metric (MASE, CRPS skill); RMSE across levels is dominated by the aggregates. Reconciliation usually improves most levels but can lose at some, so a method that wins at the total can lose at the leaves. Done when the score table has one block per level.

## Code

```python
from statsforecast import StatsForecast
from statsforecast.models import AutoETS
from hierarchicalforecast.utils import aggregate
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace

# raw: columns region, store, category, ds, y
raw["total"] = "total"
spec = [["total"], ["total", "region"], ["total", "region", "store"],
        ["total", "region", "store", "category"]]
Y_df, S_df, tags = aggregate(df=raw, spec=spec)

sf = StatsForecast(models=[AutoETS(season_length=12)], freq="MS")
Y_hat = sf.forecast(df=Y_df, h=12, level=[80, 95], fitted=True)
Y_fit = sf.forecast_fitted_values()

hrec = HierarchicalReconciliation(reconcilers=[BottomUp(), MinTrace(method="mint_shrink")])
Y_rec = hrec.reconcile(Y_hat_df=Y_hat, Y_df=Y_fit, S_df=S_df, tags=tags,
                       level=[80, 95], intervals_method="normality")   # or "bootstrap"
```
