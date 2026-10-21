# PLAN: everyday-forecasting-skills

Status: draft for approval. Nothing below is built yet.

## Where it lives

- Folder: `plugins-src/everyday-forecasting-skills/` in this repo. It replaces
  `plugins-src/forecasting/` (skills `forecast`, `backtest`, `reconcile`).
- The brief's OUTPUT_DIR (`~/code/everyday-forecasting-skills`) and "initialise a
  git repo" do not apply: your request says replace the skills in this repo, so the
  work is committed to branch `claude/laughing-goldberg-0ztov2`.
- On approval: delete `plugins-src/forecasting/`, rename the marketplace entry, and
  update the root `README.md` tables. Invocation changes from
  `/forecasting:forecast` to `/everyday-forecasting-skills:forecast-planner`.
- Reuse from the old plugin: its Python snippets were run against the same library
  versions. I will check each one again and reuse it where it fits.

## Blocker to clear first

The network policy denies `otexts.com`, so Phase 1 is not done. The notes in
`notes/` are written from memory and every URL is marked `[unverified]`. Hard
rules 3 and 4 (book first, record uncertainty) cannot be met until the pages are
read. See open question 1.

## Skills

The brief's table holds. Changes, with the reason:

- `forecast-explore` takes chapter 3 transformations, and `forecast-baselines`
  takes the chapter 5 transformation and bias-adjustment material. One owner per
  concept: Box-Cox choice in explore, bias adjustment in baselines.
- `forecast-baselines` owns evaluation (train/test, time series cross-validation,
  accuracy measures). Method skills point to it instead of repeating it. This is
  the single source of truth rule.
- `forecast-judgmental` gets no template. Chapter 6 has no code. It gets a
  markdown adjustment-log template instead.
- Descriptions must keep these pairs apart, because they overlap: regression and
  dynamic-regression (split on "autocorrelated errors / ARIMA errors"), advanced
  and practical (split on "method" versus "data problem"), auditor and baselines
  (split on "review an existing forecast" versus "build the baseline").

| Skill | Chapters | Purpose | Template |
|---|---|---|---|
| `forecast-planner` | 1, 5, 13 | Interview: decision, forecast horizon, frequency, granularity, hierarchy, history length, known future regressors, point or distribution. Recommends a method path. Writes `docs/forecast-plans/<date>-<name>/plan.md`. | none |
| `forecast-explore` | 2, 3, 4 | Plots, ACF, transformations, STL and classical decomposition, features to triage many series. | explore |
| `forecast-baselines` | 5 | Four benchmarks, residual diagnostics, bias adjustment, train/test, time series cross-validation, accuracy measures. | baselines |
| `forecast-regression` | 7 | Linear regression with trend, dummies, Fourier terms, predictors; predictor selection; ex-ante versus ex-post; spurious regression. | regression |
| `forecast-ets` | 8 | ETS taxonomy, selection by AICc, damping, intervals. | ets |
| `forecast-arima` | 9 | Stationarity, differencing, KPSS, ACF/PACF, automatic and seasonal ARIMA, ARIMA versus ETS. | arima |
| `forecast-dynamic-regression` | 10 | Regression with ARIMA errors, dynamic harmonic regression, lagged predictors, scenarios. | dynamic_regression |
| `forecast-hierarchical` | 11 | Hierarchical and grouped series, bottom-up, top-down, middle-out, MinT, evaluation per level. | hierarchical |
| `forecast-advanced` | 12 | Complex seasonality, Prophet, VAR, NNAR, bagging, only as far as the book recommends each. | advanced |
| `forecast-practical` | 13 | Weekly/daily/sub-daily, counts and intermittent, bounds, combinations, aggregate intervals, backcasting, short/long series, missing values, outliers. | practical |
| `forecast-judgmental` | 6 | Structured judgment, Delphi, analogies, scenarios, adjustments and their risks. | adjustment log (markdown) |
| `forecast-auditor` | 5, 13 | Stress test a finished forecast in five categories with severity fatal / serious / minor. Does not fix; hands off. | audit checklist code (leakage, CV design, calibration) |
| `forecast-report` | all | Compile plan, diagnostics, accuracy tables, plots, caveats for a technical or a business reader. | none |
| `forecast-exercises` | all | New exercises on simulated series of known structure. No book exercises. | simulate |

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
plugins-src/everyday-forecasting-skills/
  .claude-plugin/plugin.json
  README.md  LICENSE  NOTICE  CHANGELOG.md  NOTES.md  PLAN.md
  notes/               chNN-<slug>.md, r-python-map.md, datasets.md
  skills/<14 names>/SKILL.md
  references/
    decision-tree.md  method-registry.md  evaluation.md  preflight.md
    lessons.md  dgp-library.md  glossary.md
    diagnostics/{explore,baselines,regression,ets,arima,dynamic-regression,
                 hierarchical,advanced,practical}.md
  templates/
    r/{explore,baselines,regression,ets,arima,dynamic_regression,
       hierarchical,advanced,practical,simulate}.R
    python/{same names}.py
    judgmental/adjustment-log.md
  data/export_book_data.R     writes CSVs to data/csv/ (git-ignored)
  evals/
    README.md
    cases/trigger/*.yaml   cases/no_trigger/*.yaml
    run_templates.sh       runs every template in R and Python, saves to runs/
    parity.py              compares R and Python outputs per method
    ground_truth.py        ETS and ARIMA parameter recovery
    trigger_eval.py        checks prompts against skill descriptions
    runs/                  git-ignored
```

Change from the reference: templates are runnable `.R` and `.py` scripts with
`## Section` comment headers, not markdown. Reason: Phase 4 must run every
template end to end, and a script runs as is. Each script has the nine sections
from the brief.

Data: Python templates read CSVs that `export_book_data.R` writes from
`tsibbledata`/`fpp3`. Both languages then use identical data, which the parity
check needs. The repo does not ship the GPL data files.

Manifests: Claude Code only (`plugin.json` plus the existing repo
`marketplace.json`). The reference's Codex, Cursor and Gemini manifests are left
out unless you want them (open question 4).

## Template and parity plan

| Template | R dataset | Python | Expected parity gap |
|---|---|---|---|
| baselines | aus_production Beer | statsforecast benchmarks | none |
| explore | aus_retail subset, canadian_gas | statsmodels STL | STL defaults differ, components not compared numerically |
| regression | us_change | statsmodels OLS | none |
| ets | aus_production, global_economy | AutoETS | small; optimiser differences |
| arima | PBS h02, global_economy | AutoARIMA | possible different order chosen |
| dynamic_regression | us_change, us_gasoline | AutoARIMA + X_df | possible order differences |
| hierarchical | tourism | hierarchicalforecast | MinT shrinkage estimator may differ |
| advanced | vic_elec, us_change | MSTL, VAR, MLForecast | NNAR has no Python equivalent: documented gap |
| practical | PBS intermittent subset, prices eggs | Croston variants, logit | Croston bias variants may differ |
| simulate | simulated ETS(A,A,N) and ARIMA(1,1,1) | same | seeds differ; compare recovery, not paths |

Ground truth: simulate 500 series per model at n = 200 and n = 1000. Pass when the
median estimate of each parameter is within 10% (or 0.05 absolute for values near
zero) of the true value at n = 1000.

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

1. Run every template in both languages; fix every error.
2. Parity table in `NOTES.md`; every gap over 5% gets a cause.
3. Ground-truth recovery for ETS and ARIMA.
4. Trigger evals: no no-trigger prompt matches; no explicit prompt matches two skills.
5. Self-audit: run `forecast-auditor` on one ETS analysis and one hierarchical analysis.
6. Copyright pass: compare skill and reference text with the book pages (needs
   the pages, see blocker).
7. `claude plugin validate` on the repo.

## Open questions

1. **Book access.** Can you add `otexts.com` to the allowed domains of this cloud
   environment (environment settings, Network access)? Without it I cannot verify
   any section URL, decision rule, the Python edition's libraries, or run the
   copyright check. Alternatives: you paste or upload the pages, or I build from
   the memory-based notes and leave every book claim in "Unverified". I recommend
   the allow-list.
2. **Plugin name and replacement.** Follow the brief (`everyday-forecasting-skills`,
   long invocation prefix) and delete the old `forecasting` plugin? Or keep the
   short name `forecasting` with the new skills inside?
3. **Trigger eval runner.** Claude Code picks skills with the model, so a keyword
   matcher only approximates it. Options: (a) call `claude -p` with all
   descriptions and ask which skill fits, which needs a logged-in CLI and costs
   tokens; (b) a deterministic keyword and phrase matcher, free but weaker;
   (c) both, (b) in CI and (a) on demand. I recommend (c).
4. **Other platforms.** Add Codex, Cursor and Gemini manifests like the reference?
   I recommend no: this repo is a Claude Code marketplace.
5. **Prophet.** The Python `prophet` package installs from PyPI. R `fable.prophet`
   is not yet confirmed on conda-forge (CRAN is blocked here). If it cannot be
   installed, the advanced R template covers Prophet in text only. Acceptable?
6. **Datasets.** OK to generate the Python datasets from R with
   `export_book_data.R`, so a Python-only user needs R once? Alternative: point
   Python templates to the Python edition's data source once I can confirm it.
