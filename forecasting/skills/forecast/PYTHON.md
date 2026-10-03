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

Starter script, monthly data. Scoring the `cv` frame is the `forecasting:backtest` skill.

```python
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import SeasonalNaive, AutoETS, AutoARIMA, MSTL

df = (raw.rename(columns={"sku": "unique_id", "month": "ds", "units": "y"})
         .sort_values(["unique_id", "ds"]))

m, h = 12, 12
sf = StatsForecast(
    models=[SeasonalNaive(m), AutoETS(season_length=m), AutoARIMA(season_length=m),
            MSTL(season_length=m, trend_forecaster=AutoARIMA())],
    freq="MS", n_jobs=-1,
)

cv = sf.cross_validation(df=df, h=h, step_size=3, n_windows=10, level=[80, 95])
# score cv with forecasting:backtest, then fit the winner

fc = sf.forecast(df=df, h=h, level=[80, 95])
```
