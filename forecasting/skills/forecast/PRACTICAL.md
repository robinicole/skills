# Practical problems

Reference for step 4 of [SKILL.md](SKILL.md). Check the table against the data before choosing models.

| Problem | Answer |
| --- | --- |
| Weekly, daily, sub-daily data | Long or non-integer period: Fourier terms with ARIMA errors, MSTL, or TBATS (see [MODELS.md](MODELS.md)) |
| Intermittent demand, small counts | Croston variants forecast size and interval separately; report a demand rate. Large counts need nothing special |
| Must stay positive | Model log(y); back-transformed forecasts and intervals stay positive |
| Must stay in [a, b] | Scaled logit: model log((y-a)/(b-y)), back-transform |
| Several reasonable models | Average them |
| Interval for a sum of forecasts | Points add, intervals do not unless series are independent. Simulate joint paths and take quantiles of the sum |
| Missing values | Missing at random: state space models skip them. Otherwise backcast or STL-interpolate |
| Outliers | Replace with an STL-interpolated value; add a dummy at that date if the cause is known |
| Very short series (under ~2 seasons) | Naive and ETS(A,N,N); keep parameters well below the observation count |
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

Overfitting shows as training fit much better than test accuracy. The fix is fewer parameters or more regularisation.

Judgmental overrides: log each one with its reason and measure whether overrides beat the model. Usually only large, documented adjustments based on new information do.
