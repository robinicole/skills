---
name: reconcile
description: Reconcile forecasts across a hierarchy or grouped structure so levels add up, using MinT. Use when series aggregate (SKU, category, store, region, total), the user mentions hierarchical or grouped forecasting, or forecasts at different levels disagree.
---

# Reconcile

When series add up, forecast every level, then reconcile so the numbers are **coherent** (each aggregate equals the sum of its children) and each level borrows strength from the others. Reconciliation sits on top of any base forecast: ETS, ARIMA, boosted.

## Structure

A **hierarchy** nests strictly: store inside region. A **grouped** structure crosses attributes, category × region, with no single nesting order. Both reduce to one summing matrix S that maps bottom series to every aggregate; `aggregate` builds it from a spec.

## Methods

| Method | How | Weakness |
| --- | --- | --- |
| Bottom-up | Forecast leaves, sum | Leaves are noisy; misses aggregate-level signal |
| Top-down | Forecast total, split by historical proportions | Loses leaf dynamics; biased even with a perfect total |
| Middle-out | Forecast a middle level, sum up, split down | Both weaknesses, one per side |
| MinT | Combine all base forecasts to minimise reconciled error variance | Needs the error covariance; shrinkage estimate handles it |

MinT with the shrinkage covariance (`mint_shrink`) is the default. WLS on variances (`wls_var`) is the fallback when there are too many series for shrinkage. Probabilistic forecasts reconcile the same way, through sample paths.

## Steps

1. Build every level and S. Done when `tags` lists each level and the bottom level matches the raw series count.
2. Forecast every level with `fitted=True` (MinT needs in-sample errors). Done when every series in `Y_df` has base forecasts and fitted values.
3. Reconcile with BottomUp and MinT side by side. Done when both reconciled columns exist and an aggregate equals the sum of its children within rounding.
4. Backtest with the `forecasting:backtest` skill, reporting every level that ships. A method that wins at the total can lose at the leaves. Done when the score table has one block per level.

## Code

Tested with hierarchicalforecast 1.5.

```python
from statsforecast import StatsForecast
from statsforecast.models import AutoETS
from hierarchicalforecast.utils import aggregate
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace

# raw: columns region, store, category, ds, y
spec = [["region"], ["region", "store"], ["region", "store", "category"]]
Y_df, S_df, tags = aggregate(df=raw, spec=spec)

sf = StatsForecast(models=[AutoETS(season_length=12)], freq="MS")
Y_hat = sf.forecast(df=Y_df, h=12, fitted=True)
Y_fit = sf.forecast_fitted_values()

hrec = HierarchicalReconciliation(reconcilers=[BottomUp(), MinTrace(method="mint_shrink")])
Y_rec = hrec.reconcile(Y_hat_df=Y_hat, Y_df=Y_fit, S_df=S_df, tags=tags)
```
