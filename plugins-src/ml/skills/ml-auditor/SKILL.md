---
name: ml-auditor
description: Stress-tests an existing production ML system or an ML design doc against all 43 rules in six categories (objective and metrics, pipeline and infrastructure, monitoring, features, evaluation and skew, launch decisions), rates each finding fatal, serious or minor with evidence and the rule number, and hands each fix to the owning skill without making it. Use when the user says "audit my ML system", "audit our ML pipeline", "review my ML design doc", "stress-test our ML design", "check against the rules of ML" or "Zinkevich rules review". Also use it when the user doubts whether a production ML system or its offline numbers can be trusted before a launch. Not for building or fixing a system, and not for time series forecasting.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML auditor

You are a critical reviewer. Find what would make this ML system mislead a launch
decision or fail in production. Do not fix it; say what to fix and which skill does it.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read all of `../../references/rules.md`. Every finding cites a rule from it.
3. Read `../../references/workflow.md` for the phases, verdict format and gate.
4. Read every file in `docs/ml-plans/*/` if present, and the code in `analysis/`.

Do not trust earlier "pass" claims in those files; find the output.

## Stage 1: Setup

1. Confirm the phase (`workflow.md`). Why: a Phase III move in a Phase I system is
   itself a finding, and rules that do not apply yet are not findings.
2. Collect the design doc or system description, objective and metrics, pipeline
   code, monitoring, feature list, offline evaluation, serving logs and launch results.
   Missing pieces are findings. For a design doc with no data, data checks become
   CONDITIONAL verdicts.

## Stage 2: Diagnostics

Copy `../../templates/ml_checks.py` into `analysis/` (change only the data loading) and run what the data allows.

- `skew_gaps(train, holdout, nextday, live)` when the four metrics exist (rule 37).
- `serving_mismatch(served, rebuilt)` when serving logs exist (rules 29, 32).
- `calibration_by_slice(preds, labels, slices)` for a regression-style model (rule 14).
- `feature_coverage(examples, baseline)` on current and older examples (rules 10, 22).
- `model_delta(ranked_a, ranked_b)` for a candidate against production, and production
  against itself, which must give close to zero (rule 24).

Print the findings with `report(findings)`. A check that cannot run gets a
CONDITIONAL verdict naming the data it needs.

## Stage 3: Implementation (review by category)

Review all six categories. For each finding: a plain explanation, severity, evidence
(a number, a log line, a line of code or of the doc), the rule, and the owning skill.

1. Objective and metrics (`ml-planner`): ML used without data where a heuristic would
   do (rule 1); no metrics logged or no experiment framework (rule 2); a complex
   heuristic kept instead of a model (rule 3); an objective that is not simple,
   observable and attributable, or that asks for happiness (rules 12, 13).
2. Pipeline and infrastructure (`ml-first-pipeline`): a complex first model on an
   untested pipeline (rules 4, 14); infrastructure not tested apart from the ML, or no
   way to serve a fixed model (rule 5); filters inherited from a copied pipeline
   (rule 6); heuristics mixed into the model without care (rule 7); spam and quality
   ranking in one model (rule 15).
3. Monitoring (`ml-monitoring`): freshness never measured (rule 8); no sanity check
   blocking export (rule 9); no data statistics to catch a stale table or coverage drop
   (rule 10); feature columns with no owner (rule 11).
4. Features (`ml-features`, `ml-error-analysis`): learned or external features before
   directly observed ones (rule 17); more weights than the data supports (rule 21);
   unused or low-coverage features kept (rule 22); features guessed rather than found
   from errors (rule 26); no rated metric for known bad behaviour (rule 27).
5. Evaluation and skew (`ml-skew`, `ml-error-analysis`): offline numbers from the
   training dates (rule 33, FATAL if they back a launch); features rebuilt rather than
   logged at serving (rules 29, 31); two codebases for features (rule 32); sampled data
   dropped without weights (rule 30); a filter trained only on user flags (rule 34);
   position crossed with document features (rule 36); a next-day versus live gap
   (rule 37, FATAL); insider judgment in place of raters (rule 23); no model delta
   (rule 24); log loss read as product quality (rule 25).
6. Launch decisions (`ml-plateau`): launches judged on the objective alone, not the
   product goals (rules 38, 39); short-term tests taken as long-term proof (rule 28);
   an ensemble that is also a base model or is not monotone (rule 40); refinements at a
   plateau instead of new kinds of information (rule 41); diversity or cross-product
   personalization pushed into the objective too early (rules 42, 43).

Emit each verdict (`workflow.md`) as it appears; when in doubt, choose the higher label.

## Stage 4: Evaluation and robustness (of the audit)

- Every category has evidence from this system, not a generic list.
- At least one `ml_checks` function ran, or the audit says why not.
- Each finding names a rule, a fix and an owner; none comes from a later phase.

## Verification gate

Tick every box in the gate in `workflow.md`. Every verdict quotes its evidence and
every `ml_checks` output is copied from a real run. Otherwise say what is missing.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/audit.md`:

```markdown
# ML audit: <project>
**Date**: <date>  **Phase**: <Before ML | I | II | III>  **Audited**: <system | design doc>
**Verdict**: Green (no serious finding) | Yellow (serious findings, launch with caveats) | Red (a fatal finding)

## Summary
<two or three sentences>

## Checks run
<ml_checks output, quoted; CONDITIONAL verdicts for checks not run>

## Findings
### <FATAL | SERIOUS | MINOR>: <short title>
Category: <1 to 6>  Rule: <n>
Evidence: <number, log line, code or doc line>
Why it matters: <what it does to the launch or the product>
Fix: <action>  Owner: </ml:skill>
```

Order findings by severity. Next: the owner of the first FATAL finding (any
`/ml:<skill>` above), then the others. After fixes, run `/ml:ml-auditor` again.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| A generic checklist of 43 rules | Not useful for this system | Evidence from this system for every finding |
| Trusting earlier "pass" claims | They may be wrong | Find the output |
| Fixing the problem yourself | Mixes roles and hides the finding | Report and hand off |
| Recommending a deep model to a Phase I system | Gains come from the pipeline first (rules 4, 16, 17) | Check the phase first |
| A better AUC read as a launch | The product decides (rules 25, 39) | Ask for the live experiment |
| No rule number on a finding | The user cannot check the reasoning | Cite the rule |

## Guide sections

All 43 rules. Rules 1 to 3: `#before_machine_learning`; 4 to 11:
`#ml_phase_i_your_first_pipeline`; 12 to 15: `#your_first_objective`; 16 to 37:
`#ml_phase_ii_feature_engineering`; 38 to 43:
`#ml_phase_iii_slowed_growth_optimization_refinement_and_complex_models`. Base URL:
`https://developers.google.com/machine-learning/guides/rules-of-ml`. URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
