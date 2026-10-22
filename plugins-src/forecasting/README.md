# forecasting

Claude Code skills for time series forecasting in Python. They follow the method of
Rob J Hyndman and George Athanasopoulos, *Forecasting: Principles and Practice*
(3rd edition, [R edition](https://otexts.com/fpp3/), [Python edition](https://otexts.com/fpppy/)).
The book text and exercises belong to its authors. The skills paraphrase its
methods and link to the book sections; read the book for the reasoning.

**Status.** Book claims, thresholds and section links were checked against both
editions on 2026-10-22 (see "Book check" in `NOTES.md`). The Python templates were
run end to end.

## Workflow

```
forecast-planner -> forecast-explore -> forecast-baselines -> method skill
    -> forecast-auditor -> forecast-report
```

Start anywhere. Skills share one project folder, `docs/forecast-plans/<date>-<name>/`,
so each skill reads what the earlier ones found.

| Skill | Use it to |
|---|---|
| `/forecasting:forecast-planner` | Frame the decision, the forecast horizon and the data; get a method path and a plan |
| `/forecasting:forecast-explore` | Plots, ACF, transformations, STL, features for many series |
| `/forecasting:forecast-baselines` | Benchmarks, residual checks, bias adjustment, cross-validation, accuracy measures |
| `/forecasting:forecast-regression` | Regression with predictors: trend, dummies, Fourier terms, ARIMA errors, weekly data, lagged predictors, scenarios |
| `/forecasting:forecast-ets` | Exponential smoothing |
| `/forecasting:forecast-arima` | ARIMA and seasonal ARIMA |
| `/forecasting:forecast-hierarchical` | Hierarchical and grouped series, reconciliation |
| `/forecasting:forecast-advanced` | Multiple seasonality, Prophet, VAR, neural networks, bagging |
| `/forecasting:forecast-practical` | Intermittent demand, bounds, combinations, totals, gaps, outliers |
| `/forecasting:forecast-judgmental` | Forecasts without data; manual adjustments and their log |
| `/forecasting:forecast-auditor` | Stress-test a finished forecast; fatal, serious, minor findings |
| `/forecasting:forecast-report` | Report for a business or technical reader |
| `/forecasting:forecast-exercises` | Practice on simulated series with known answers |

The skills also start on their own when a request matches their description.
They do not trigger on causal questions ("did the promotion work"), trading
advice, or classification tasks.

## Guardrails

- **Benchmarks first.** Every model is scored against mean, naive, seasonal naive
  and drift on the same forecast origins.
- **Verification gate.** No interpretation before the code has run and its output
  is quoted.
- **Severity verdicts.** Fatal, serious, minor, emitted as soon as a check fails.
- **Packages.** Templates detect missing packages and print the install command;
  the agent installs only after you say yes.

## Layout

```
skills/<name>/SKILL.md   the skills
references/              decision tree, method registry, evaluation, diagnostics per method,
                         workflow rules, lessons, glossary, simulation library, preflight
templates/               runnable Python: one per method, plus fpp_data.py (book datasets),
                         fc_checks.py (shared checks), simulate.py, audit_checks.py
evals/                   trigger cases, template runner, ground-truth check
notes/                   chapter notes (own words), R to Python map, dataset list
```

## Install

From GitHub, inside Claude Code:

```
/plugin marketplace add robinicole/skills
/plugin install forecasting@robinicole-skills
```

From a local clone, for one session (no install):

```bash
claude --plugin-dir /path/to/skills/plugins-src/forecasting
```

## Requirements

Python 3.10 or later. See `references/preflight.md`:

```bash
pip install statsforecast mlforecast hierarchicalforecast utilsforecast statsmodels \
    pandas numpy matplotlib scikit-learn pyreadr
pip install prophet   # optional
```

The templates download the book's datasets on first use from the authors' public
R data packages (tsibbledata, tsibble, fpp3; GPL-3) and cache them in
`~/.cache/fpp_data`. No data is stored in this repo.

## Checks

```bash
bash evals/run_templates.sh              # run every template
python evals/ground_truth.py             # ETS and ARIMA parameter recovery
python evals/trigger_eval.py             # trigger phrases (free)
python evals/trigger_eval.py --mode cli  # real trigger test with the Claude CLI (costs tokens)
```

## Credits

Structure (planner, method skills, auditor, report, exercises, preflight, eval
cases) adapted from [everyday-causal-skills](https://github.com/RobsonTigre/everyday-causal-skills)
by Robson Tigre (MIT); see `NOTICE`. Licence: MIT (`LICENSE`).
