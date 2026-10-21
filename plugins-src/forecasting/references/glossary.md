# Glossary

One term per concept. Every skill and reference uses these words and no synonyms.

| Term | Meaning | Not |
|---|---|---|
| forecast horizon (h) | Number of periods ahead a forecast covers | lead time, horizon length |
| seasonal period (m) | Number of observations in one seasonal cycle (12 for monthly with yearly seasonality) | frequency, season length |
| forecast origin | The last time point whose data the forecast uses | cutoff (only as the column name in code) |
| training set | Data used to fit a model | in-sample (except for "in-sample fit") |
| test set | Data held back to score forecasts | holdout, validation set |
| time series cross-validation | Scoring forecasts from many forecast origins, each fitted only on data up to that origin | backtest, walk-forward |
| benchmark | One of the four simple methods: mean, naive, seasonal naive, drift | baseline model, bar |
| point forecast | One number per period, usually the mean or median of the forecast distribution | prediction, estimate |
| forecast distribution | The probability distribution of the future value | predictive distribution |
| prediction interval | Range expected to contain the future value with a stated probability | confidence interval |
| residuals | Observation minus fitted value; after a transformation, use innovation residuals on the transformed scale | errors (errors are on the test set) |
| forecast errors | Observation minus forecast, on the test set | residuals |
| ex-ante forecast | A forecast that uses only information available at the forecast origin, including forecasts of predictors | real forecast |
| ex-post forecast | A forecast that uses actual later values of predictors; it measures model error only | |
| coherent | Forecasts that add up across a hierarchy the same way the data do | consistent |
| reconciliation | Adjusting base forecasts so they are coherent | |
| transformation | Box-Cox, log or scaled logit applied before modelling | |
| bias adjustment | Turning a back-transformed median into a mean | |
| skill score | 1 minus (model score divided by benchmark score); positive means better than the benchmark | |
