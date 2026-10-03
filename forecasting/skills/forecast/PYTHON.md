# Python map and starter script

| Book (R) | Python |
| --- | --- |
| tsibble | pandas or Polars long frame `unique_id, ds, y` |
| feasts: ACF, STL, features | `statsmodels.tsa` (acf, STL, kpss, acorr_ljungbox); `tsfeatures` at scale |
| fable: ETS, ARIMA, NAIVE, SNAIVE, RW | `statsforecast.models`: AutoETS, AutoARIMA, Naive, SeasonalNaive, RandomWalkWithDrift |
| TSLM with fourier() | `statsmodels` DeterministicProcess + AutoARIMA with `X_df` |
| decomposition_model | `MSTL(trend_forecaster=...)` |
| CROSTON | CrostonClassic, CrostonSBA, TSB, ADIDA, IMAPA |
| NNETAR | `neuralforecast` or `mlforecast` |
| reconcile(), min_trace() | `hierarchicalforecast`: BottomUp, TopDown, MinTrace |
| accuracy(), stretch_tsibble() | `utilsforecast.evaluation.evaluate`, `StatsForecast.cross_validation` |
| forecast(bootstrap = TRUE) | `ConformalIntervals` via `prediction_intervals=` |

Starter script, monthly data. Tested with statsforecast 2.1 and utilsforecast 0.2.

```python
import pandas as pd
from functools import partial
from statsforecast import StatsForecast
from statsforecast.models import SeasonalNaive, AutoETS, AutoARIMA, MSTL
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mase, scaled_crps

df = (raw.rename(columns={"sku": "unique_id", "month": "ds", "units": "y"})
         .sort_values(["unique_id", "ds"]))

m, h = 12, 12
sf = StatsForecast(
    models=[SeasonalNaive(m), AutoETS(season_length=m), AutoARIMA(season_length=m),
            MSTL(season_length=m, trend_forecaster=AutoARIMA())],
    freq="MS", n_jobs=-1,
)

cv = sf.cross_validation(df=df, h=h, step_size=3, n_windows=10, level=[80, 95])
scores = evaluate(cv.drop(columns="cutoff"),
                  metrics=[partial(mase, seasonality=m), scaled_crps],
                  train_df=df, level=[80, 95])
print(scores.groupby("metric").mean(numeric_only=True))

fc = sf.forecast(df=df, h=h, level=[80, 95])
```
