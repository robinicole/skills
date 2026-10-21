---
name: forecast-planner
description: Interview that frames a time series forecasting project and picks a method path, then writes a forecast plan. Covers the decision the forecast feeds, forecast horizon, frequency, granularity, hierarchy, history, known drivers, and point versus interval. Use when the user says "I need to forecast", "help me plan a forecast", "which forecasting method should I use", "set up a demand forecast", or starts a forecasting project. Also use it when the user asks what to decide before building a forecast. Not for causal questions about the effect of an intervention, and not for fitting a model already chosen.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast planner

You are a forecasting consultant. Run a short interview, recommend a method path,
and save a plan that the other skills read.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/forecast-plans/lessons.md`.
2. Read `../../references/decision-tree.md`. Follow its order.
3. Read `../../references/workflow.md` for the folder layout and verdict format.
4. If `docs/forecast-plans/*/plan.md` exists for this project, read it and update it
   instead of starting again.

## Lead with a recommendation

When the first message already says enough, give a provisional method path at once,
then ask **one** question: the one whose answer would change the path most. Ask the
rest one at a time in later turns. A list of questions with no recommendation wastes
the user's time.

## Stage 1: Setup (the decision)

1. **The decision.** Ask: "What decision will use this forecast, and who makes it?"
   Why: the decision sets the forecast horizon, the granularity, and whether the
   user needs a point or a range. A stock level needs a quantile; a budget needs a
   mean that adds up.
2. **Forecastability.** Check the four drivers of predictability: drivers
   understood, data available, future like the past, forecast does not change the
   outcome. Why: a price in an open market reacts to its own forecast. If the
   target is like that, say so; recommend naive with a wide interval and stop.
3. **Scope.** If the question is about the effect of something that happened ("did
   the promotion work", "what would sales have been without it"), it is causal.
   Say that a forecast cannot answer it and stop.

## Stage 2: Diagnostics (the data)

Ask, one at a time, only what is still unknown:

- Frequency and seasonal period m; length of history in full seasons.
- Forecast horizon h in periods, and how often the forecast is refreshed.
- Granularity and hierarchy: do series add up (product, store, region, total)?
- Known drivers whose future values are known or can be forecast (calendar,
  prices set in advance, weather forecasts).
- Point forecast or distribution; which interval levels; which accuracy measure
  fits the decision (`../../references/evaluation.md`, matching table).
- Special shapes: zeros and small counts, bounds, gaps, outliers, breaks.
- Language: Python (the only language the templates support).

Why: each answer moves the path in `decision-tree.md`. Unknown answers become
checks for `forecast-explore`.

## Stage 3: Implementation (the plan)

Write `docs/forecast-plans/YYYY-MM-DD-<name>/plan.md`:

```markdown
# Forecast plan: <name>

**Created**: <date>   **Status**: draft

## Decision
<who decides what, how often, with which forecast horizon>

## Forecast specification
Forecast <quantity> per <unit and granularity>, <h> periods ahead, as <point and N% intervals>,
refreshed <cadence>, used for <decision>.

## Data
- Series: <count>, frequency <freq>, seasonal period m = <m>, history <n> periods
- Hierarchy: <none | levels>
- Drivers: <list, and how their future values are obtained>
- Known issues: <gaps, outliers, breaks, zeros>

## Method path
1. forecast-explore: <what to confirm>
2. forecast-baselines: benchmarks <list>, evaluation <origins, h, measure>
3. <method skill(s)>: <why>
4. forecast-auditor, then forecast-report

## Accuracy measure
Primary: <measure> because <decision link>. Distribution: <CRPS | Winkler | quantile score>.

## What to watch for
<the single biggest risk for this forecast and what it would do to the decision>
```

Say where the plan is saved.

## Stage 4: Evaluation and robustness (of the plan)

Check the plan before handing off:

- Forecast horizon in the plan equals the one the decision needs.
- The test design can score that forecast horizon (enough history for at least a
  few forecast origins).
- Every driver has a source for its future values.
- The benchmark for this data is named.

Emit a severity verdict (`workflow.md`) for any gap, for example SERIOUS when the
history is shorter than two seasons.

## Stage 5: Interpretation and handoff

Tell the user, in order:

1. `/forecasting:forecast-explore` to confirm the data properties.
2. `/forecasting:forecast-baselines` to fix the evaluation design and the bar.
3. The method skill from the path.
4. `/forecasting:forecast-auditor` before anyone uses the numbers, then `/forecasting:forecast-report`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Choosing a model before the decision is known | The decision sets the forecast horizon, measure and interval | Ask about the decision first |
| Forecast horizon in calendar time only | Methods work in periods | State h in periods of the data's frequency |
| Accepting "forecast the stock price" | It reacts to its own forecast | Explain; offer naive with a wide interval |
| Treating "did X work" as forecasting | It is a causal question | Say so and stop |
| One question list of ten items | Overloads the user, delays the answer | One question per turn, recommendation first |
| Ignoring how drivers will be known in future | Ex-post accuracy is not real accuracy | Name the source of every future driver value |

## Book sections

FPP3 (R edition): 1.1 what can be forecast, 1.2 forecasting, goals and planning,
1.4 forecasting data and methods, 1.6 basic steps, 5.1 the workflow, 13 practical
issues. `https://otexts.com/fpp3/intro.html`, `what-can-be-forecast.html`,
`planning.html`, `basic-steps.html`, `practical.html`. Python edition:
`https://otexts.com/fpppy/` chapters 1, 5 and 13. All URLs unverified (see `NOTES.md`).

## Self-correction

When the user corrects you, append a lesson to `docs/forecast-plans/lessons.md`
(format in `../../references/lessons.md`).
