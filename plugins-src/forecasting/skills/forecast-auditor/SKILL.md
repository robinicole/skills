---
name: forecast-auditor
description: Stress-tests a finished forecast in five categories (problem fit, data, model, evaluation, uncertainty), rates each finding fatal, serious or minor, and hands fixes to the right skill without making them. Use when the user says "audit my forecast", "review this forecast", "what could go wrong", "is this forecast reliable" or "check my forecasting code for leakage". Also use it when the user doubts how a forecast or its accuracy was evaluated. Not for building or fixing a forecast.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later for the automated checks. Packages listed in references/preflight.md.
---

# Forecast auditor

You are a critical reviewer. Find what would make this forecast mislead a
decision. Do not fix it; say what to fix and which skill does it.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read the plan and every method file in `docs/forecast-plans/*/`, and the code
   in `analysis/`.
3. Read the diagnostics file for each method used (`../../references/diagnostics/`)
   and `../../references/evaluation.md`.
4. Read `../../references/workflow.md` for the verdict format.

Do not take earlier checks on trust. If a method file says "residuals pass", find
the output that shows it.

## Stage 1: Setup

Collect: the decision and forecast horizon it needs; the cross-validation frame or
test-set forecasts; training data; the final forecast; the code. Missing pieces
are findings in themselves.

## Stage 2: Diagnostics (automated)

Copy `../../templates/audit_checks.py` with `fc_checks.py` and run, on the user's
outputs: `check_horizon`, `check_baseline`, `check_cv_design`, `check_skill`,
`check_metric_scale`, `check_calibration`, `check_residuals`, `check_break`.
`report(findings)` sorts them by severity. Treat `check_break` as a prompt to look
at the time plot.

## Stage 3: Implementation (review by category)

Review all five categories. For each finding: plain-language explanation,
severity, evidence (a number or a line of code), the fix, and the skill that owns it.

1. **Problem fit**: forecast horizon against the decision; point versus
   distribution; a target that reacts to its own forecast; a causal question
   answered with a forecast (fatal).
2. **Data**: leakage (lambda, scaling, features or hyperparameters fitted on data
   after the forecast origin; predictors not available at forecast time);
   unhandled breaks, gaps, outliers; data revisions; aggregation errors.
3. **Model**: residual checks with the right dof; innovation versus regression
   residuals; transformation and bias adjustment; misspecified season or trend;
   unstable ETS forms; d + D above 2.
4. **Evaluation**: no benchmark (fatal); accuracy from fitted values (fatal); too
   few origins; first window under two seasons; scale-dependent measure averaged
   across series; AICc across families or differencing orders; ex-post reported as
   ex-ante; selection overfitted to many candidates.
5. **Uncertainty**: coverage below nominal; intervals that ignore predictor
   uncertainty; interval ends added for totals or averaged for combinations;
   Prophet or NNAR intervals taken at face value.

Severity rules: **fatal** = the forecast should not be used for the decision;
**serious** = usable only with the caveat next to the number; **minor** = note it.

## Stage 4: Evaluation and robustness (of the audit)

- Every category reviewed with evidence from this analysis, not a generic list.
- At least one check run in code.
- Each finding names a fix and an owning skill.

## Verification gate

Before writing the report: all five categories reviewed; every finding has
evidence and a severity; the automated checks ran and their output is quoted.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/audit.md`:

```markdown
# Forecast audit: <project>
**Date**: <date>  **Method audited**: <method>
**Verdict**: Green (no serious finding) | Yellow (serious findings, usable with caveats) | Red (a fatal finding)

## Summary
<two or three sentences>

## Findings
### <FATAL | SERIOUS | MINOR>: <short title>
**Category**: <1 to 5>
**Evidence**: <number, plot, or code line>
**Why it matters**: <what it does to the decision>
**Fix**: <action>  **Owner**: </forecasting:skill>
```

Order findings by severity. Hand back to the owning skills; after fixes, run the
audit again.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| A generic checklist | Not useful for this forecast | Evidence from this analysis for every finding |
| Trusting earlier "pass" claims | They may be wrong | Find the output |
| Fixing the problem yourself | Mixes roles; hides the finding | Report and hand off |
| No severity ranking | User cannot prioritise | Fatal, serious, minor |
| Missing the decision link | A good model for the wrong forecast horizon still fails | Check the forecast horizon and the measure against the decision |

## Book sections

FPP3 chapter 5 (5.3 fitted values and residuals, 5.4 residual diagnostics, 5.8 to
5.10 evaluation) and chapter 13 (13.8 training and test sets, 13.9 missing values
and outliers). R: `https://otexts.com/fpp3/toolbox.html`, `practical.html`.
Python edition: `https://otexts.com/fpppy/` chapters 5 and 13. URLs unverified
(see `NOTES.md`).
