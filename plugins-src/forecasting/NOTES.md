# NOTES

Working notes for the rebuild of the `forecasting` plugin from
*Forecasting: Principles and Practice* (3rd edition, R) and its Python edition.
Build phases follow the brief: study the structure reference, read both books,
plan, build, validate, deliver.

## Phase 0: patterns from the structure reference

Source: `everyday-causal-skills` by Robson Tigre, commit `5317ebc`, MIT. Files
were read from Appendix A of the brief. The repository was not cloned.

### Manifests and repo files

- `.claude-plugin/plugin.json`: name, description, version, author, repository,
  license, keywords. The same block is repeated for Codex (`.codex-plugin`),
  Cursor (`.cursor-plugin`) and Gemini (`gemini-extension.json` + `GEMINI.md`).
  This repo is already a marketplace (`.claude-plugin/marketplace.json` at the
  repo root), so only the plugin-level `plugin.json` is needed here.
- `GEMINI.md` doubles as a one-page workflow summary: stages, how skills
  connect, guardrails, skill table. Useful as the model for the plugin README.
- `README.md`: problem statement, two worked example conversations, skill
  table, how the compilation skills work, install per platform, resources,
  roadmap.
- `CHANGELOG.md`: Keep a Changelog format, semantic versioning.
- `pyproject.toml` versions the eval harness, not the plugin, and declares the
  template dependencies as extras so the eval environment matches the
  templates.
- `.gitignore` excludes `docs/` (generated plans), eval run outputs, and
  local Claude config.

### Staged workflow

Every method skill runs five stages: 1 Setup, 2 Assumptions, 3 Implementation,
4 Robustness, 5 Interpretation. Each stage says what to do and why. A
"Verification gate" between 4 and 5 lists checks that must come from actual
code output before any interpretation. Severity verdicts (FATAL, SERIOUS) are
emitted as fixed blocks as soon as a diagnostic reveals a problem, with a
CONDITIONAL FATAL form when the diagnostic has not yet been run.

### Handoff between skills

- The planner is the entry point. It writes `docs/causal-plans/<date>-<name>/plan.md`
  and ends with "Here's what I recommend next" naming the method skill.
- Each method skill starts with "Before You Begin": read `references/lessons.md`,
  the assumption checklist, the method-registry section, and the plan if one
  exists. If a plan exists the skill extracts the design from it and does not
  re-ask.
- Each skill ends with "Integration": skills before, skills after, skills to use
  if assumptions fail. Output files sit next to the plan
  (`implementation.md`, `analysis.[R|py]`, `audit.md`, `report.md`).
- The auditor runs after an analysis, finds threats in five categories with a
  severity each, and does not fix. The report skill is terminal and reads all
  artifacts.

### Plan document as shared context

`plan.md` carries: objective, question, design, recommended method with
rationale and alternative, assumptions to verify, data requirements, threats,
next steps as a checklist, and "What to watch for" (the single biggest threat).
Downstream skills read it automatically.

### Package preflight

`references/preflight.md`: detect, report, offer to install, install only after
an explicit yes. The detect snippet is template code (R `requireNamespace`,
Python `importlib.util.find_spec`) and never installs. Required packages gate
the run; optional ones are noted and skipped. A mapping table covers Python
import name versus pip name.

### Common mistakes table

Each method skill ends with "Rationalization Shortcuts" (shortcut, reality) and
"Common Issues". `references/lessons.md` holds dated lessons in a fixed format
(trigger, mistake, rule, source) that every skill reads first and appends to
when the user corrects it.

### Frontmatter descriptions

`name`, `description`, `metadata.author`, `metadata.compatibility`. The
description states what the skill does, lists trigger phrases in quotes
("Use when user says ..."), and ends with a "Not for ..." sentence that
points away from neighbouring skills.

### Eval cases

`evals/cases/layer0/*.yaml` with fields `name`, `description`, `layer`, `skill`,
`user_message`, `expected.should_trigger`. Explicit-trigger and paraphrase
cases per skill, plus no-trigger cases. The causal plugin's
`no_trigger_time_series_forecast.yaml` says "Forecast next month's revenue
using ARIMA" must not trigger a causal skill. The forecasting plugin mirrors
this: causal questions must not trigger a forecasting skill.

### Templates

One file per method and language. Sections: Prerequisites (preflight snippet
and load block), Data Preparation, Estimation (one block per variant),
Diagnostics, Results Table, Visualization. Code is commented line by line and
skills say "copy the template exactly, adapt only variable names".

### Reused code

If the preflight snippet or the eval case layout is copied, the MIT notice
goes in `NOTICE`.

## Phase 1 status

**Blocked: the books could not be read.** The environment's network policy denies
`otexts.com` (proxy answers 403 to CONNECT; logged 2026-10-21). The Internet
Archive and the authors' sites are also denied. The book's source repository is
not public on GitHub under `robjhyndman/fpp3` (that repo is the data package).

What was done instead:

- Chapter notes in `notes/` were drafted from prior knowledge of the book, in my
  own words, and every URL in them is marked `[unverified]`.
- Datasets were listed from the installed R data packages (verified).
- The R to Python map uses signatures read from the installed packages
  (verified against the packages, not against the Python edition).

## Environment

- Python 3.13 venv: statsforecast 2.1.1, mlforecast 1.1.0, hierarchicalforecast
  1.5.3, utilsforecast 0.2.17, coreforecast 0.0.19, statsmodels 0.15.0, pandas
  2.3.3, numpy 2.5.4, scikit-learn 1.9.1, prophet 1.5.0, pyreadr.
- R 4.4.3 with fable 0.5.0, feasts 0.5.0, tsibble 1.2.0, fpp3 1.0.3 (conda-forge,
  because CRAN mirrors are denied). After the decision to go Python only, R was used
  only to read function lists and dataset structures for `notes/`. No R template
  ships.

## Decisions after Phase 2

See `PLAN.md`: build from the notes, plugin name `forecasting`, Python only, no
other platform manifests, keyword and CLI trigger runners, book data read from the
GitHub `.rda` files with pyreadr.

## Parity

Dropped with the Python-only decision: there is no R template to compare with.
Spot checks against values I remember from the book (all unverified, see below)
agreed: Algeria exports SES alpha 0.84; Egypt exports ARIMA(2,0,1); H02 candidate
ARIMA(3,0,1)(0,1,2)[12]; consumption on income with ARIMA(1,0,2) errors, income
coefficient 0.198; insurance quotes with one lag of TV adverts, coefficients 1.25
and 0.146, ARIMA(1,0,2) errors; us_change regression coefficients 0.74, 0.047,
-0.053, -0.17; gas Guerrero lambda 0.11.

Known gaps between the Python templates and the book's R code:

| Item | Book (R) | Python here | Effect |
|---|---|---|---|
| NNAR | `NNETAR()` averages 20 networks with its own defaults and simulates intervals | MLPRegressor via mlforecast, 20 seeds, no intervals | Point forecasts differ; no interval |
| Bootstrap intervals | `forecast(bootstrap = TRUE)` | conformal intervals, or statsmodels `simulate` | Different interval method |
| Sample paths | `generate()` on any model | only statsmodels ETS/SARIMAX `simulate` | Aggregate intervals use statsmodels ETS |
| CRPS | exact from the forecast distribution | approximated from interval quantiles (`fc_checks.crps_from_intervals`) | Approximation; more levels = closer |
| STL defaults | feasts window defaults | statsmodels defaults (seasonal 7 unless set) | Components differ unless windows are set |
| Damped ETS | phi search range per fable | statsforecast bounds phi to [0.8, 0.98] | phi hits 0.8 more often |
| Deterministic trend example | book restricts the ARIMA error order | AutoARIMA chose ARIMA(2,0,1) errors on aus_airpassengers to 2016 | Different error model; the lesson (narrower intervals) holds |

## Validation results (2026-10-21)

| Check | Result |
|---|---|
| Templates (`evals/run_templates.sh`) | 11 of 11 run without errors |
| Ground truth (`evals/ground_truth.py`, 200 series, n = 1000) | 8 of 8 parameters within tolerance |
| Trigger, keyword mode | 72 cases, 0 failures, 26 paraphrases informational |
| Trigger, CLI mode, run 1 | 55 of 72 pass; all 16 no-trigger pass; 17 under-triggers, no wrong skill |
| Trigger, CLI mode, run 2 (after adding "Also use it for questions about ..." to ten descriptions, 3 turns) | 64 of 72 pass; all 16 no-trigger pass; 8 under-triggers, no wrong skill |
| `claude plugin validate` | passes; warnings: no icon; `core` plugin has no author |
| Quotations over 15 words | none |

Remaining CLI under-triggers: four short conceptual questions answered in text
("MAPE or MASE?", "what does a PACF cut-off at lag 2 suggest?", the simplest
benchmark, a smoothing method that flattens the trend), and four prompts where
Claude first tried to list files (Bash, Glob), which the test blocks in an empty
folder. Results vary between runs: explore explicit 1 passed in a targeted rerun
and failed in the full run. Pushing the descriptions harder risks triggering on
unrelated prompts; left as is.

## Self-audit (Phase 4 step 6)

Headless runs with `claude -p --plugin-dir`, outputs in `evals/self-audit/`:

| Run | Turns | Cost (USD) | Result |
|---|---|---|---|
| forecast-ets on aus_production Gas, h = 8 | 11 | 0.42 | ETS(A,A,A) on 1980+, beats seasonal naive per forecast horizon, residuals white |
| forecast-auditor on that run | 7 | 0.34 | Red: 1 fatal (forecast origin 2010, decision 2026), 4 serious, 3 minor |
| forecast-hierarchical on tourism, h = 8 | 12 | 0.37 | Grouped, 425 series, MinT-OLS non-negative; six origins; coherence gap 0 |
| forecast-auditor on that run | 10 | 0.35 | Red: 1 fatal (same data-age issue), 4 serious, 4 minor |

Skill and template changes made because of these audits:

- `workflow.md`: new "Forecast origin" rule; planner asks for the last
  observation date against the decision date.
- `evaluation.md`: keep choosing and reporting apart; report origins won and the
  spread; origins in every season; tie rule (Not from the book, Diebold-Mariano cited).
- `forecast-ets`: refit all forms after changing the training window.
- `forecast-hierarchical`: residual pass rate per level, coverage per level,
  back-test `nonnegative=True`, multi-origin evaluation.
- Templates: `step_size=1` in `ets.py`, `arima.py`, `practical.py`; four-origin
  evaluation with per-level coverage in `hierarchical.py`;
  `audit_checks.check_origin_seasons`; the leakage message states the cutoff convention.
- `references/lessons.md`: five lessons from these runs.

The fatal finding in both audits comes from the book data ending in 2010 and 2017;
the prompts did not say the work was an exercise. The auditor was right to flag it.

## Copyright check

Not possible against the book pages (site blocked). All text was written fresh
in my own words from the notes; no single-line quotation over 15 words exists in
skills, references, notes or README. Open: compare against the pages once they
are reachable.

## Unverified

- Every section URL of both editions (slugs in `notes/` are from memory).
- Which Python libraries the Python edition uses, and per chapter. Expected
  statsforecast, mlforecast, hierarchicalforecast, utilsforecast, maybe
  neuralforecast. Not confirmed.
- Where the Python edition loads its datasets from.
- Every decision rule and threshold in `notes/` as attributed to the book, in
  particular: seasonal-strength threshold 0.64 for seasonal differencing; damping
  range 0.8 to 0.98; NNAR default k = (p + P + 1) / 2; Fourier K values for weekly
  data; Guerrero as the book's lambda method; BIC preference for VAR lag order.
- Whether chapter 13 of the online edition has a nowcasting section.
- The URL of the prison population CSV used in chapter 11.
- Every R and Python edition page slug used in the skills (aligned with `notes/`, not checked).
- That the Python edition uses the same section numbering as the R edition.
- The T/5 cap on the Ljung-Box lag as a book rule.
- Whether the book uses dof > 0 for ETS residual tests (the templates use 0).
- Holt-Winters as its own page (`holt-winters.html`) in chapter 8.
- The "training and test sets" section (13.8) and its page name.
- Values remembered from the book's examples listed under Parity.
