---
name: forecast-judgmental
description: Structures forecasts made by judgment and reviews manual adjustments to statistical forecasts, using the Delphi method, forecasting by analogy, scenario planning, new product methods and a scored adjustment log. Use when the user says "no historical data", "new product forecast", "expert forecast", "Delphi", "override the statistical forecast", "manual adjustments" or "sales team forecast". Also use it for questions about changing forecast numbers by hand. Not for fitting statistical models.
metadata:
  author: Robin Nicole
  compatibility: No code required. Uses templates/adjustment-log.md.
---

# Forecast judgmental

You make judgment systematic, recorded and scored, so it can be checked later.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read the plan in `docs/forecast-plans/*/` if one exists.
3. Read `../../references/workflow.md`.

## Stage 1: Setup

Decide which case applies:

- **No data** (new product, new market, far forecast horizon): judgmental forecast.
- **Data and a model exist**, and someone wants to change the numbers: adjustment.

Write the forecasting task in one sentence (quantity, unit, forecast horizon,
point or range). Why: vague tasks give inconsistent answers between experts.

## Stage 2: Diagnostics

Check for the known failure modes before collecting any number:

- Anchoring on the last value or on a figure someone mentioned.
- Optimism, or targets disguised as forecasts.
- Group pressure from senior voices.
- Inconsistency between people or over time.

Say which ones are present and how the method below limits each.

## Stage 3: Implementation

- **Delphi**: a facilitator; several experts answer anonymously; the facilitator
  feeds back a summary with reasons; two or three rounds; the final forecast is the
  aggregate (median) with the spread. Why: anonymity removes the pull of seniority.
- **Analogy**: several similar cases, not one; adjust each for known differences;
  combine.
- **Scenarios**: a few internally consistent scenarios with stated assumptions,
  not a single number.
- **New products**: sales force composite, executive opinion, customer
  intentions. Each has a known bias (intentions overstate purchases); say it.
- **Adjustments**: copy `../../templates/adjustment-log.md`. Adjust only for
  information the model cannot see, only when the effect is large, and log the
  reason. Why: small adjustments mostly add noise.

## Stage 4: Evaluation and robustness

Score judgmental forecasts and adjustments like any other forecast
(`../../references/evaluation.md`). Every quarter, compare adjusted against
unadjusted forecasts on the adjusted rows, by size of change. Stop the kinds of
adjustment that do not help.

## Verification gate

Before interpretation: the task sentence is written, the method is named, every
number has an author and a reason in the log, and an outcome date is set for scoring.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/judgmental.md`: the method, the forecasts with
their spread, the failure modes addressed, and when they will be scored. Once data
exists, hand over to `/forecasting:forecast-planner` for a statistical forecast.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Anchoring on the last value | Biases every expert the same way | Ask for the forecast before showing recent values |
| Adjusting to meet a target | It is a goal, not a forecast | Keep goals and forecasts separate |
| Many small adjustments | Mostly noise | Large, documented adjustments only |
| One analogy | One case is an anecdote | Several analogies, combined |
| Open group meeting | Dominant voices win | Delphi, anonymous rounds |
| No record of reasons | Cannot learn which adjustments help | Adjustment log, scored quarterly |

## Book sections

FPP3 chapter 6: 6.1 beware of limitations, 6.2 key principles, 6.3 the Delphi
method, 6.4 forecasting by analogy, 6.5 scenario forecasting, 6.6 new product
forecasting, 6.7 judgmental adjustments. R: `https://otexts.com/fpp3/judgmental.html`,
`judgmental-beware.html`, `key-principles.html`, `delphimethod.html`,
`analogies.html`, `scenarios.html`, `new-product-forecasting.html`,
`judgmental-adjustments.html`. Python edition: `https://otexts.com/fpppy/`
chapter 6. URLs unverified (see `NOTES.md`).
