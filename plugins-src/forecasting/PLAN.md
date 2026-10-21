# PLAN: forecasting plugin rebuild

Status: approved 2026-10-21 with the decisions below.

## Decisions

1. Book access: build from the notes in `notes/`. Every book claim stays under
   "Unverified" in `NOTES.md` until it is checked against the pages.
2. Plugin name: `forecasting`. The new skills replace `forecast`, `backtest` and
   `reconcile` in `plugins-src/forecasting/`. Invoke as `/forecasting:forecast-planner`.
3. Trigger evals: both runners. A keyword matcher for routine runs, the Claude CLI
   on demand.
4. Manifests: Claude Code only.
5. Language: Python only. No R templates. R function names appear only as pointers
   to the book's R edition.
6. Data: Python reads the book's datasets from the `.rda` files in the authors'
   public data packages on GitHub, at pinned commits, with `pyreadr`
   (Not from the book). Nothing is copied into this repo.

Consequence: the R/Python parity check is dropped, because there is nothing to
compare. Template runs, the ground-truth check and the trigger evals stay.

## Skills

The brief's table holds. Changes, with the reason:

- `forecast-explore` takes chapter 3 transformations, and `forecast-baselines`
  takes the chapter 5 transformation and bias-adjustment material. One owner per
  concept: Box-Cox choice in explore, bias adjustment in baselines.
- `forecast-baselines` owns evaluation (train/test, time series cross-validation,
  accuracy measures). Method skills point to it instead of repeating it. This is
  the single source of truth rule.
- `forecast-judgmental` gets no code template. Chapter 6 has no code. It gets a
  markdown adjustment-log template instead.
- Descriptions must keep these pairs apart, because they overlap: regression and
  dynamic-regression (split on "autocorrelated errors / ARIMA errors"), advanced
  and practical (split on "method" versus "data problem"), auditor and baselines
  (split on "review an existing forecast" versus "build the baseline").

| Skill | Chapters | Purpose | Template |
|---|---|---|---|
| `forecast-planner` | 1, 5, 13 | Interview: decision, forecast horizon, frequency, granularity, hierarchy, history length, known future regressors, point or distribution. Recommends a method path. Writes `docs/forecast-plans/<date>-<name>/plan.md`. | none |
| `forecast-explore` | 2, 3, 4 | Plots, ACF, transformations, STL and classical decomposition, features to triage many series. | explore.py |
| `forecast-baselines` | 5 | Four benchmarks, residual diagnostics, bias adjustment, train/test, time series cross-validation, accuracy measures. | baselines.py |
| `forecast-regression` | 7 | Linear regression with trend, dummies, Fourier terms, predictors; predictor selection; ex-ante versus ex-post; spurious regression. | regression.py |
| `forecast-ets` | 8 | ETS taxonomy, selection by AICc, damping, intervals. | ets.py |
| `forecast-arima` | 9 | Stationarity, differencing, KPSS, ACF/PACF, automatic and seasonal ARIMA, ARIMA versus ETS. | arima.py |
| `forecast-dynamic-regression` | 10 | Regression with ARIMA errors, dynamic harmonic regression, lagged predictors, scenarios. | dynamic_regression.py |
| `forecast-hierarchical` | 11 | Hierarchical and grouped series, bottom-up, top-down, middle-out, MinT, evaluation per level. | hierarchical.py |
| `forecast-advanced` | 12 | Complex seasonality, Prophet, VAR, NNAR, bagging, only as far as the book recommends each. | advanced.py |
| `forecast-practical` | 13 | Weekly/daily/sub-daily, counts and intermittent, bounds, combinations, aggregate intervals, backcasting, short/long series, missing values, outliers. | practical.py |
| `forecast-judgmental` | 6 | Structured judgment, Delphi, analogies, scenarios, adjustments and their risks. | adjustment-log.md |
| `forecast-auditor` | 5, 13 | Stress test a finished forecast in five categories with severity fatal / serious / minor. Does not fix; hands off. | audit_checks.py |
| `forecast-report` | all | Compile plan, diagnostics, accuracy tables, plots, caveats for a technical or a business reader. | none |
| `forecast-exercises` | all | New exercises on simulated series of known structure. No book exercises. | simulate.py |

Auditor categories (proposal): 1 Problem fit (forecast horizon versus decision,
point versus distribution, unforecastable target), 2 Data (leakage, breaks,
missing values, outliers, revisions), 3 Model (residual checks, misspecification,
transformation and bias), 4 Evaluation (no baseline, wrong CV design,
scale-dependent metric across series, AICc across families, accuracy per forecast
horizon), 5 Uncertainty (interval calibration, intervals that ignore predictor
uncertainty, summed intervals).

## Terms (one per concept, used everywhere)

forecast horizon (h), seasonal period (m), forecast origin, training set, test
set, time series cross-validation, benchmark (the four simple methods), point
forecast, forecast distribution, prediction interval, residuals (innovation
residuals after a transformation), ex-ante / ex-post, coherent, reconciliation.

## Files

```
plugins-src/forecasting/
  .claude-plugin/plugin.json
  README.md  LICENSE  NOTICE  CHANGELOG.md  NOTES.md  PLAN.md
  notes/               chNN-<slug>.md, r-python-map.md, datasets.md
  skills/<14 names>/SKILL.md
  references/
    decision-tree.md  method-registry.md  evaluation.md  preflight.md
    lessons.md  dgp-library.md  glossary.md
    diagnostics/<method>.md
  templates/
    fpp_data.py  explore.py  baselines.py  regression.py  ets.py  arima.py
    dynamic_regression.py  hierarchical.py  advanced.py  practical.py
    simulate.py  audit_checks.py  adjustment-log.md
  evals/
    README.md  cases/trigger/*.yaml  cases/no_trigger/*.yaml
    run_templates.sh  ground_truth.py  trigger_eval.py
    runs/              git-ignored
```

Templates are runnable scripts with `# %%` section headers, so Phase 4 runs them
as they are. Each has the brief's nine sections.

| Template | Dataset |
|---|---|
| baselines.py | aus_production Beer |
| explore.py | aus_retail subset, canadian_gas |
| regression.py | us_change |
| ets.py | aus_production Gas, global_economy |
| arima.py | PBS h02, global_economy |
| dynamic_regression.py | us_change, us_gasoline |
| hierarchical.py | tourism |
| advanced.py | vic_elec (daily), us_change |
| practical.py | PBS intermittent subset, prices eggs |
| simulate.py | simulated ETS(A,A,N), ARIMA(1,1,1) |

Ground truth: simulate 200 series per model at n = 1000. Pass when the median
estimate of each parameter is within 10% of the true value (0.05 absolute for
values near zero).

## Eval plan

- Format: the reference's YAML (`name`, `description`, `skill`, `user_message`,
  `expected.should_trigger`), minus the `layer` field.
- Per skill: 2 explicit-trigger and 2 paraphrased-trigger prompts. 14 x 4 = 56.
- Shared no-trigger prompts, about 16, each expected to match no forecasting
  skill: causal questions (did the promo increase sales, CausalImpact on a
  campaign, counterfactual for a policy, DiD, A/B test lift), stock price
  prediction advice, generic ML classification (churn, fraud), plain descriptive
  statistics (average order value last quarter).
- Collision cases: each explicit prompt must match exactly one skill.
- Runner: open question 3.

## Phase 4 checks

1. Run every template end to end; fix every error. Outputs go to `evals/runs/`.
2. Ground-truth recovery for ETS and ARIMA.
3. Trigger evals: no no-trigger prompt matches; no explicit prompt matches two skills.
4. Self-audit: run `forecast-auditor` on one ETS analysis and one hierarchical analysis.
5. Copyright pass against my notes. The pass against the book pages cannot run
   here and is recorded as open.
6. `claude plugin validate` on the repo.
