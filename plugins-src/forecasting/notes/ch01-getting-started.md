# Chapter 1: Getting started

## Section URLs

R edition [unverified]: `intro.html`, `what-can-be-forecast.html`, `planning.html`,
`data-methods.html`, `case-studies.html`, `basic-steps.html`, `perspective.html`,
`intro-exercises.html`.
Python edition [unverified]: same chapter, slugs not confirmed.

## Key concepts and decision rules

- What makes something forecastable: how well its drivers are understood, how much
  data exists, how similar the future is to the past, and whether the forecast feeds
  back on the outcome. A quantity that reacts to its own forecast (exchange rates,
  stock prices) is close to unforecastable. The honest forecast for those is "the
  same as today" with a wide range.
- Three horizons for business planning: short term (scheduling), medium term
  (resources), long term (strategy). The horizon decides what method is credible.
- A forecast is a distribution, not a number. Report a point forecast plus a
  prediction interval. The point is usually the mean or median of the forecast
  distribution.
- Vocabulary: forecasting (predicting the future), goals (what you want to happen),
  planning (how to get there). Do not confuse them.
- Method families: qualitative (no data or no relevant data), explanatory models
  (predictors drive the target), time series models (the target's own history),
  mixed models (both). Time series models often beat explanatory models because the
  system's structure need not be understood and the predictors need not be
  forecast.
- The forecasting workflow: define the problem, gather information (data and expert
  knowledge), explore, choose and fit models, evaluate, deploy and monitor.
- Talk to the people who collect the data and the people who use the forecasts.
  Their knowledge of breaks, promotions, definitions and the decision is part of the
  input.

## Model diagnostics the book recommends

None specific to this chapter; it frames the problem.

## Evaluation guidance

Introduced in principle: judge a model on forecasts of data it did not see.

## R functions and Python equivalents

No code beyond loading `fpp3` in R. The Python edition loads pandas and the Nixtla
libraries [unverified: exact imports].

## Common mistakes the book warns about

- Treating an unforecastable quantity as forecastable.
- Confusing forecasts with goals or plans.
- Skipping the problem definition and going straight to models.
