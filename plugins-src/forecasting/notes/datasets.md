# Datasets

Listed from the installed R packages `tsibbledata` 0.4.1 and `fpp3` 1.0.3
(GitHub `tidyverts/tsibbledata`, `robjhyndman/fpp3`), plus `tsibble::tourism`.
Both packages are GPL-3. The underlying data mostly come from public
statistics agencies.

**Python sources not confirmed.** The Python edition could not be fetched, so
where it loads each dataset from is unknown. Proposal in `PLAN.md`: an R script
exports the needed datasets to CSV on the user's machine, and the Python
templates read the CSV. This keeps R and Python on identical data for the parity
check and avoids redistributing GPL data files in this repo.

| Dataset | Package | Index | Keys | Interval | Planned use |
|---|---|---|---|---|---|
| aus_production | tsibbledata | Quarter | none | quarterly | baselines (Beer), ETS, decomposition |
| aus_retail | tsibbledata | Month | State, Industry | monthly | exploration, features, ETS/ARIMA |
| PBS | tsibbledata | Month | Concession, Type, ATC1, ATC2 | monthly | ARIMA (h02), intermittent subsets |
| vic_elec | tsibbledata | Time | none | 30 min | complex seasonality, dynamic regression with temperature |
| global_economy | tsibbledata | Year | Country | yearly | ETS non-seasonal, ARIMA |
| aus_livestock | tsibbledata | Month | Animal, State | monthly | exercises |
| gafa_stock | tsibbledata | Date | Symbol | irregular | naive benchmark, unforecastable example |
| pelt | tsibbledata | Year | none | yearly | cycles versus seasonality, VAR |
| tourism | tsibble | Quarter | Region, State, Purpose | quarterly | hierarchical and grouped |
| us_change | fpp3 | Quarter | none | quarterly | regression, dynamic regression, VAR |
| us_employment | fpp3 | Month | Series_ID | monthly | decomposition |
| us_gasoline | fpp3 | Week | none | weekly | weekly data, Fourier terms |
| bank_calls | fpp3 | DateTime | none | 5 min | complex seasonality |
| souvenirs | fpp3 | Month | none | monthly | log transform, regression |
| insurance | fpp3 | Month | none | monthly | lagged predictors |
| canadian_gas | fpp3 | Month | none | monthly | changing seasonality, STL |
| aus_arrivals | fpp3 | Quarter | Origin | quarterly | exercises |
| boston_marathon | fpp3 | Year | Event | yearly | piecewise trend |
| prices | fpp3 | year | none | yearly | bounded forecasts (eggs) |
| guinea_rice | fpp3 | Year | none | yearly | short series |
| aus_airpassengers | fpp3 | Year | none | yearly | short series, drift |

Not in either package: the prison population data used in the hierarchical chapter
is read from `https://OTexts.com/fpp3/extrafiles/prison_population.csv` (checked
2026-10-22). The Python edition ships every dataset as CSV in
`https://otexts.com/fpppy/data/fpppy_data.zip`.
