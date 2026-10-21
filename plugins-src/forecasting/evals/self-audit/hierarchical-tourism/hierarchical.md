# Hierarchical forecast: Australian domestic overnight trips

Units: trips in thousands per quarter. Scripts in `analysis/`, outputs in `outputs/`.

## Structure
Grouped, not a strict hierarchy: Purpose crosses the geography (State > Region), so top-down and middle-out do not apply to the final model.

| Level | Series |
|---|---|
| Total | 1 |
| State | 8 |
| Purpose | 4 |
| State x Purpose | 32 |
| State > Region | 76 |
| Region x Purpose (bottom) | 304 |

Total 425. Bottom count 304 equals the raw series count. Check passed.

## Base model and methods
Base: AutoETS (m=4) per series, with fitted values. Seasonal naive was the template's benchmark. Compared on the grouped structure: bottom-up, MinT-OLS, MinT-wls_struct, MinT-shrink. Normality intervals (80, 95). Top-down and middle-out were run only on the Total > State > Region sub-hierarchy, single split.
Training has about 72 quarters against 304 bottom series, so the sample covariance is not usable; shrinkage was used.

## Coherence
Base ETS gap: 1613 (trips, thousands; incoherent as expected). All reconciled versions: gap 0.000. Final forecast: gap 0.0.

## Accuracy: MASE by level, mean of 6 origins (h=8, origins one year apart, last window 2016 Q1 to 2017 Q4)

| Method | Total | State | Purpose | State x Purpose | State>Region | Bottom |
|---|---|---|---|---|---|---|
| ETS (base) | **1.636** | 1.356 | 1.412 | 1.128 | 1.024 | 0.908 |
| Bottom-up | 2.448 | 1.587 | 1.857 | 1.216 | 1.037 | 0.908 |
| MinT-OLS | 1.692 | **1.270** | **1.349** | **1.101** | **0.959** | 0.956 |
| MinT-wls_struct | 1.993 | 1.383 | 1.510 | 1.103 | 0.968 | 0.914 |
| MinT-shrink | 1.952 | 1.371 | 1.500 | 1.094 | 0.964 | **0.884** |

Share of 6 origins where the method beats base ETS: OLS at State 4/6, Purpose 6/6, Total 0/6; shrink at Bottom 6/6, State 1/6, Total 0/6.
Single split (template, 2016 Q1 to 2017 Q4) ranked shrink best overall (0.970 vs 1.028). The six-origin result differs by level, so the single split was not enough to choose.

## Where reconciliation lost
- Total: every reconciled method is worse than base ETS (0/6 origins). OLS is the closest (1.692 vs 1.636). Bottom-up is much worse (2.448).
- State: shrink and wls_struct are no better than base; bottom-up loses.
- Bottom: OLS loses (0.956 vs 0.908).

## Interval coverage (mean over 6 origins; nominal 80% / 95%)

| Level | Base ETS | MinT-OLS | MinT-shrink |
|---|---|---|---|
| Total | 62% / 83% | 48% / 65% | 17% / 29% |
| State | 65% / 84% | 73% / 87% | 39% / 56% |
| Purpose | 68% / 85% | 69% / 88% | 35% / 56% |
| Bottom | 76% / 89% | 88% / 96% | 75% / 89% |

Intervals are too narrow at the top for every method. At the Total, OLS intervals cover 48% for a nominal 80%.

## Negatives
Backtest negative point forecasts (< -0.5), 6 origins: base 14, bottom-up 14, OLS 50, shrink 11, wls_struct 7. The final forecast uses `nonnegative=True` (min 0.0006, coherent). That option was not back-tested.

## Recommendation
Use MinT-OLS, non-negative, for the state allocation. It is best at State, Purpose, State x Purpose and Region, and has the best interval coverage. It is not the best method for the Total (base ETS, 1.636 vs 1.692, is slightly ahead, and the difference is small). If the Total is also a decision input, use the reconciled Total anyway so the numbers add up, and widen its interval (see caveats).

## Final forecast (MinT-OLS, non-negative), 8-quarter sum, thousands of trips

| State | Sum 2018Q1-2019Q4 | Share | Base ETS share |
|---|---|---|---|
| NSW | 68,757 | 30.3% | 30.9% |
| Victoria | 54,999 | 24.2% | 24.5% |
| Queensland | 47,900 | 21.1% | 21.4% |
| Western Australia | 21,869 | 9.6% | 9.5% |
| South Australia | 14,874 | 6.5% | 6.3% |
| Tasmania | 7,504 | 3.3% | 3.0% |
| ACT | 6,570 | 2.9% | 2.8% |
| Northern Territory | 4,752 | 2.1% | 1.7% |

Total by quarter: 29,003; 27,465; 27,165; 28,157; 29,916; 28,376; 28,075; 29,068. Full series and intervals: `outputs/hier_forecast_final.csv`.
Shares are the sums of point forecasts; the state shares differ by up to 0.4 points between OLS and base, so the allocation is not sensitive to the method at the state level. The NT share moves most (2.1% vs 1.7%).

## Caveats
- SERIOUS: interval coverage. Total intervals cover far less than nominal, so use them only with this caveat; do not budget against the 80% band at the Total.
- SERIOUS: no explore.md or baselines.md exist. Only the template's seasonal-naive benchmark was run on the one split. The base model is untuned ETS with no residual (Ljung-Box) check, so the verification gate is not fully met.
- Six origins overlap heavily (windows of 8 quarters, step 4), so the origins are not independent.
- 2018+ forecasts assume the 1998-2017 pattern continues; no external events are modelled.
