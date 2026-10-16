# Metrics

Reference for steps 1, 5 and 6 of [SKILL.md](SKILL.md).

## Matching the metric to the decision

Each metric is minimised by a different feature of the forecast distribution, so it decides what "best" means. Pick it from how the numbers get used.

| The forecast is used as | Primary metric | Why |
| --- | --- | --- |
| A total to be summed (budgets, capacity) | RMSE, or RMSSE across series | Minimised by the mean, and means add. After a log or Box-Cox transform the back-transformed point is the median, so bias-adjust it to the mean first (see Box-Cox in [EXPLORE.md](../forecast/EXPLORE.md)) |
| A typical value for planning | MAE, or MASE across series | Minimised by the median |
| A stock level at service level p | Quantile score at p | Minimised by the p-quantile |
| A risk range or a full distribution | CRPS, plus coverage | Scores the whole distribution |
| A number on a business slide | MAPE as a secondary figure only | Readable, but skewed and undefined at zero |

## Point metrics

| Metric | Definition | Optimal forecast | Use | Watch for |
| --- | --- | --- | --- | --- |
| MAE | mean abs error | Median | One series, own scale | Not comparable across series |
| RMSE | root mean squared error | Mean | Forecasts that will be summed | Outlier-sensitive |
| MASE | MAE / in-sample MAE of one-step seasonal naive | Median | Across series; the default | 1.0 means as good as seasonal naive on training data; denominator from training data only |
| RMSSE | RMSE / in-sample RMSE of one-step seasonal naive | Mean | M5-style comparisons | Squared errors scaled by mean squared naive change, training data only |
| MAPE | mean abs error / actual, % | | Business reporting only | Undefined at zero, needs a true zero (not temperature), penalises over-forecasts more |
| sMAPE | | | Legacy only | Unstable near zero and not symmetric; prefer MASE |

## Distributional metrics

A proper scoring rule is minimised only by the true distribution, so widening or narrowing intervals cannot game it. Coverage alone can be gamed; always pair it with one of these.

| Metric | Definition | Reads as |
| --- | --- | --- |
| Quantile (pinball) | 2p(y - q) if y ≥ q, else 2(1 - p)(q - y) (FPP3 scaling) | Absolute error tilted toward the side the quantile covers; p = 0.5 gives absolute error |
| Winkler | Width + 2/α × distance of any miss outside | Narrow and honest beats wide |
| CRPS | Quantile score averaged over all p | MAE of a whole distribution |
| Coverage | Share of actuals inside the interval | Calibration check, not a score |

```python
import numpy as np

def winkler(y, lo, hi, alpha):
    width = hi - lo
    below = np.where(y < lo, 2 / alpha * (lo - y), 0.0)
    above = np.where(y > hi, 2 / alpha * (y - hi), 0.0)
    return (width + below + above).mean()
```
