---
name: ml-skew
description: Finds and fixes training-serving skew in a live ML system by measuring the three gaps (training, holdout, next-day, live), comparing logged serving features with rebuilt ones, and checking sampling weights, joined tables, shared feature code, filter holdouts and position features. Use when the user says "training-serving skew", "offline metrics don't match production", "log features at serving time", "importance weight sampled data", "position bias in ranking", "unfiltered holdout traffic", "next-day evaluation" or "same feature code for training and serving". Also use it when a model scores well offline but worse live, or when a ranking or filtering model feeds its own training data. Not for monitoring data freshness, export checks or alerts (use ml-monitoring).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML skew

You are an ML engineer hunting training-serving skew. Measure where the model
loses quality between training and serving, find the cause, and record it.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read the training-serving skew section of `../../references/rules.md` (rules 29 to 37).
3. Read `../../references/workflow.md` for the folder layout, phases and verdict format.
4. Read `plan.md`, `pipeline.md` and `monitoring.md` in `docs/ml-plans/*/` if present.
   Do not ask again what they answer.

## Stage 1: Setup

1. Confirm the phase. Skew work belongs to Phase II, when a pipeline is live. If
   there is no live model, send the user to `/ml:ml-first-pipeline` and stop.
2. Ask for one metric (say AUC) on four data sets: training, holdout, next-day data
   and live traffic. Why: the three gaps between them point to different causes (rule 37).
3. Ask how serving features reach training. Are they logged at serving, or rebuilt
   later from tables? Why: rebuilt features are the commonest source of skew (rules 29, 31).
4. Ask whether training data is sampled, filtered, or a ranking. Each has its own
   skew (rules 30, 34, 35, 36).

## Stage 2: Diagnostics

1. Copy `../../templates/ml_checks.py` into `analysis/`. Change only the data loading.
2. Run `skew_gaps(train, holdout, nextday, live)`. Read each gap (rule 37):
   - Training versus holdout always exists. It is not always bad; check overfitting.
   - Holdout versus next-day: a big drop means time-sensitive features. Tune
     regularization on next-day data.
   - Next-day versus live should be zero. Any gap is an engineering bug: emit FATAL.
3. If serving logs exist, run `serving_mismatch(served, rebuilt)` on the same example
   ids. Any differing feature is FATAL, because the model trains on values it never
   sees at serving (rules 29, 32).
4. Check the split. If holdout comes from the same dates as training, emit
   CONDITIONAL SERIOUS: next-day results are unknown until the split is by date (rule 33).

## Stage 3: Implementation

Recommend only the fixes the diagnostics support, each with its rule.

- Log the features used at serving and train on that log, at least for a sample
  (rule 29). It removes skew and often removes code.
- Weight sampled examples by 1/p: kept at 30%, an example gets weight 10/3. Do not
  drop data arbitrarily; calibration then survives (rule 30). Data never shown to
  users can be dropped.
- For a joined table, log the joined values at serving. If the table changes
  slowly, hourly or daily snapshots get close (rule 31).
- Put the joined request data in one testable object and convert it to the
  learner's format with one function shared by training and serving. Use one
  language (rule 32).
- Train on data up to a date and test on data after it (rule 33). Expect slightly
  worse numbers; AUC should stay close.
- For a filter, let a held-out slice (say 1% of traffic) through unfiltered and
  label it (rule 34). Above about 95% blocked this breaks down. For measuring
  serving quality alone, 0.1% or less, about 10,000 examples, is enough.
- For ranking, regularize features that span many queries more than per-query
  ones, allow only positive weights, and avoid document-only features (rule 35).
- Train with position features, serve every candidate with the same default
  position, and keep position additive, never crossed with document features (rule 36).

## Stage 4: Evaluation and robustness

After a fix, run `skew_gaps` and `serving_mismatch` again on fresh next-day and live
data. Check that the next-day versus live gap is zero, that calibration holds after
reweighting, and that the unfiltered slice is still being labelled. Emit a verdict
for any check that fails; when in doubt, choose the higher label.

## Verification gate

Tick every box in the gate in `workflow.md`. In addition, the four metrics come
from one run of `skew_gaps`, and the live number comes from serving logs, not from
replaying the training pipeline. If a box is not ticked, say what is missing.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/skew.md`:

```markdown
# Training-serving skew: <project>
**Date**: <date>  **Metric**: <metric>

## The three gaps (rule 37)
| Training | Holdout | Next-day | Live |
|---|---|---|---|
| <n> | <n> | <n> | <n> |
<verdicts from skew_gaps, quoted>

## Serving features (rules 29, 31, 32)
Logged at serving: <yes | sample | no>. serving_mismatch: <quoted output>.

## Sampling, filtering, ranking (rules 30, 34, 35, 36)
<weights used, unfiltered slice size, position handling>

## Fixes and owners
<fix, rule, status>
```

Next: `/ml:ml-error-analysis` if the gaps are closed and quality is still low;
`/ml:ml-monitoring` to alert on the gaps; `/ml:ml-auditor` before a launch.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Random split from training dates | Hides time-sensitive features | Train up to a date, test after it (rule 33) |
| Accepting a small next-day versus live gap | Same examples must score the same | Treat it as a bug and find it (rule 37) |
| Rebuilding serving features from tables | The tables changed since serving | Log features at serving (rules 29, 31) |
| Dropping sampled data without weights | Breaks calibration | Weight by 1/p (rule 30) |
| Training a filter on user flags only | Users never see blocked items | Label an unfiltered held-out slice (rule 34) |
| Crossing position with document features | The model learns a feedback loop | Keep position additive, serve a default (rule 36) |
| Two codebases for features | They diverge silently | One shared conversion function (rule 32) |

## Guide sections

Rules 29 to 37, training-serving skew, in Phase II (no own anchor):
`https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_ii_feature_engineering`.
URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
