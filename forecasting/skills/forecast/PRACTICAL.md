# Practical problems

Reference for step 4 of [SKILL.md](SKILL.md). Check the table against the data before choosing models.

| Problem | Answer |
| --- | --- |
| Weekly, daily, sub-daily data | Long or non-integer period. Weekly: STL on the adjusted series with a non-seasonal model when seasonality drifts, Fourier terms with ARIMA errors when covariates matter. Daily: moving holidays (Easter, Eid, Chinese New Year) need dummies in a dynamic regression. MSTL and TBATS for several periods (see [MODELS.md](MODELS.md)) |
| Intermittent demand, small counts | Croston variants forecast size and interval separately; report a demand rate. Classic Croston is biased and gives no intervals; SBA corrects the bias. Counts with a minimum around 100 or more can be treated as continuous |
| Must stay positive | Model log(y); back-transformed forecasts and intervals stay positive |
| Must stay in [a, b] | Scaled logit: model log((y-a)/(b-y)), back-transform |
| Several reasonable models | Average them (see Combining in [MODELS.md](MODELS.md#combining)) |
| Interval for a sum of forecasts | Mean points add (bias-adjust back-transformed medians first); intervals never do, and errors across horizons of one series are correlated, so variances do not add either. Simulate future sample paths, sum within each path, take quantiles of the sums |
| Missing values | First ask whether missingness carries information (store closed on holidays). If so, do not fill: add dummies for the missing day and the day after in a dynamic regression. If random, interpolate with a fitted ARIMA, or use only the data after the last gap. statsforecast needs complete series; statsmodels SARIMAX accepts NaN directly |
| Outliers | Flag when the robust-STL remainder lies more than 3 IQR beyond the middle 50%. Replace (ARIMA interpolation) only when you believe the value is an error or will not recur; otherwise keep it and add a dummy at that date |
| Very short series | The only hard limit is more observations than parameters; there is no magic minimum of 30. Let AICc choose among candidates, it favours simple models on short data. Seasonal models need a few full seasons |
| Very long series | Truncate to recent years, or use a model whose parameters evolve |
| History before the first observation | Reverse the series, forecast, reverse back |

```python
from statsforecast.models import CrostonClassic, CrostonSBA, TSB, ADIDA, IMAPA
import numpy as np

intermittent = [CrostonClassic(), CrostonSBA(), TSB(alpha_d=0.2, alpha_p=0.2), ADIDA(), IMAPA()]

def to_logit(y, a, b):
    return np.log((y - a) / (b - y))

def from_logit(z, a, b):
    return (b - a) * np.exp(z) / (1 + np.exp(z)) + a
```

Training residuals are one-step; test errors run 1 to h steps and grow with h, so the two are not comparable. To judge overfitting, freeze the trained parameters and compute one-step forecasts on the test set, then compare those residuals with training. The fix is fewer parameters.

Judgmental overrides: log each one with its reason and measure whether overrides beat the model. Usually only large, documented adjustments based on new information do.
