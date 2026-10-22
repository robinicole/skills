---
name: forecast-explore
description: Explores time series before forecasting with time, seasonal and subseries plots, lag plots, ACF, Box-Cox lambda, STL and classical decomposition, outlier flags, and trend and seasonal strength features to triage many series. Use when the user says "explore my time series", "decompose this series", "STL", "is there seasonality", "seasonal plot", "ACF plot" or "which series are seasonal". Also use it for questions about trend, seasonality or transformations in a series. Not for fitting forecasting models or scoring forecast accuracy.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast explore

You find the structure in the data so that the method choice rests on evidence.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/explore.md`.
3. Read the plan in `docs/forecast-plans/*/plan.md` if one exists.
4. Read `../../references/workflow.md` (folder, verdicts, verification gate).

## Stage 1: Setup

Get the data into long format `unique_id, ds, y`, one row per period per series.
Copy `../../templates/explore.py`, `fpp_data.py` and `fc_checks.py` into the
project's `analysis/` folder; replace section 1 with the user's data.

Why: every later skill expects this format, and the plots need a regular index.

Check the preflight output. Missing packages: follow `../../references/preflight.md`
(report, ask, install only after yes).

## Stage 2: Diagnostics

Run the checks in `diagnostics/explore.md`, in order:

1. Regular index, gaps listed, duplicates removed. Why: methods assume one value per period.
2. Time plot. Name trend, seasonality, cycles, breaks, outliers. Why: cycles and
   seasonality need different models; a break may mean training only on recent data.
3. Seasonal and subseries plots. Why: they show whether the seasonal shape is
   stable or drifting, which decides between a fixed and an evolving season.
4. ACF and lag plots. Why: they confirm m and show leftover autocorrelation.
5. Ljung-Box on the series. Why: white noise has nothing to forecast beyond its mean.

## Stage 3: Implementation

1. Transformation. When the seasonal swing grows with the level, compute the
   Guerrero lambda and round it (0 = log). When it does not, skip it.
2. STL decomposition on the transformed series. Choose the seasonal window from
   the seasonal plot: larger for a stable pattern. Use the remainder to flag
   outliers (beyond 3 IQR of the middle half).
3. Many series: compute trend and seasonal strength per series and scatter them.
   Group series with similar features.

Why: these outputs feed the model choice (transformation, additive or
multiplicative, seasonal or not, one model per group).

## Stage 4: Evaluation and robustness

Exploration does not score forecasts. Check robustness of the findings instead:

- Does the season type hold in the first and the second half of the data?
- Do the outliers survive a second seasonal window?
- Are the feature groups stable when one year is dropped?

## Verification gate

Apply the gate in `workflow.md`, adapted: you must quote the lambda (or "none"),
m, the seasonal and trend strength, and the outlier dates from actual output.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/explore.md` with, per series or group: m,
trend yes/no, seasonality additive or multiplicative, transformation and lambda,
breaks and outliers with dates, and the plots used.

Hand off to `/forecasting:forecast-baselines`. Point to the method skill the
findings suggest (see `decision-tree.md`, Q4).

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Calling a cycle seasonality | Cycles have no fixed period; seasonal models will mis-forecast them | Seasonality only with a fixed calendar period |
| Taking m from the calendar without checking | Weekly data has period 52.18, not 52 | Confirm on seasonal plot and ACF |
| Box-Cox when the swing is constant | Adds bias and wider intervals for nothing | Transform only when the swing grows with level |
| Using the seasonally adjusted series to spot turning points | It still holds the noisy remainder | Use the trend-cycle component |
| Classical decomposition for analysis | Fixed season, no trend at the ends, not robust | STL |
| Deleting outliers | They may recur and carry information | Keep with a dummy; replace only errors |
| One model per series for hundreds of short series | Overfits the selection | Group by features |

## Book sections

FPP3 chapter 2 (time plots, seasonal and subseries plots, lag plots,
autocorrelation, white noise), chapter 3 (transformations, components, moving
averages, classical decomposition, STL), chapter 4 (features). R:
`https://otexts.com/fpp3/graphics.html`, `decomposition.html`, `features.html`.
Python edition: `https://otexts.com/fpppy/` chapters 2 to 4. URLs checked 2026-10-22.
