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

- R 4.4.3 at `/opt/r-env` (conda-forge, because CRAN mirrors are denied). fable
  0.5.0, feasts 0.5.0, tsibble 1.2.0, fpp3 1.0.3, urca, nnet, forecast.
  `fable.prophet` is not installed (not checked on conda-forge yet).
- Python 3.13 venv at `/home/user/.venv-fc`: statsforecast 2.1.1, mlforecast 1.1.0,
  hierarchicalforecast 1.5.3, utilsforecast 0.2.17, coreforecast 0.0.19,
  statsmodels 0.15.0, pandas 2.3.3, numpy 2.5.4.

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
- `coreforecast.scalers.boxcox_lambda` argument for the Guerrero method.
- Key names of the `model_` dict in fitted statsforecast models.
- Whether `fable.prophet` is installable from conda-forge.
