---
name: ml-first-pipeline
description: Builds the first model and its pipeline in Phase I, namely a simple interpretable model (logistic, linear or Poisson regression), infrastructure tests kept apart from the ML, checks for data dropped by a copied pipeline, heuristics turned into features or applied outside the model, a policy layer that keeps spam filtering apart from quality ranking, and calibration checks by slice. Use when the user says "first ML pipeline", "first model in production", "test the pipeline infrastructure", "copied the pipeline", "heuristic as a feature", "policy layer", "spam versus quality ranking" or "check calibration by slice". Also use it for questions about how examples reach the learner and how the first model plugs into the product. Not for deciding whether to use ML at all (use ml-planner), and not for monitoring a live model (use ml-monitoring).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML first pipeline

You are an ML engineer building a first launch. Get the pipeline right end to end
with a simple model, and write down what was tested.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read `../../references/rules.md`, Phase I and "Your first objective" (rules 4 to 7, 14, 15).
3. Read `../../references/workflow.md` for the folder layout and verdict format.
4. If `docs/ml-plans/*/plan.md` exists, read it. Take the decision, heuristic
   baseline and first objective from it; do not ask again.

Confirm the phase (`workflow.md`). No data or no objective yet: `/ml:ml-planner`.

## Stage 1: Setup

1. Ask how examples reach the learner, what makes a label good or bad, and how the
   model plugs into the product: live scoring or a precomputed table (rule 4).
   Why: these are the wiring decisions the first launch exists to settle.
2. Ask where the training data come from. If the pipeline was copied from another
   system, list its filters (rule 6). Why: old filters drop data the new use needs.
3. List every heuristic in the current system (rule 7). Why: each one must become
   a feature, a preprocessing step, a label change, or a policy layer rule.

## Stage 2: Diagnostics

1. Copied pipeline (rule 6). Look for filters on age, on what was shown, or on
   what was logged. If only seen instances are logged, there are no negatives for
   unseen ones. If sources are mixed and no feature names the source, emit
   SERIOUS. If a filter removes a class of examples the model must score, emit FATAL.
2. Heuristics (rule 7). For each, pick one option and say why: preprocess with it
   (block a blacklisted sender), use its score as a feature (raw first), feed its
   raw inputs as features, or change the label. Weigh the complexity each adds.
3. Spam and quality (rule 15). If one model both filters spam and ranks quality,
   emit SERIOUS. Spam is adversarial and needs fast updates, simple rules and
   creator reputation; quality ranking assumes good-faith content. Racy content is
   a third concern. Check that spam is removed from quality training data.

## Stage 3: Implementation

1. Model (rule 14). Use linear, logistic or Poisson regression with simple
   features. Why: their outputs are probabilities or expected values, and simple
   features make wiring bugs visible (rule 4). Copy `../../templates/ml_checks.py`
   into `analysis/` and change only the data loading. Refuse deep models, ensembles and
   tuning at this phase (`lessons.md`).
2. Infrastructure tests apart from the ML (rule 5). Encapsulate the learner and
   test the parts around it:
   - Data reaches the learner: feature columns are populated. Run
     `feature_coverage` from `ml_checks.py` on the examples the learner receives.
   - Statistics on examples match another path to the same data.
   - A model scores the same instance the same way in training and serving.
   - The pipeline can serve a fixed model.
   Why: a bug in the pipeline looks like a bad model and no ML change fixes it.
3. Policy layer (rules 13, 15). Put the final decision in simple logic after the
   model: spam filters (drop posts with more than three spam votes), caps, boosts.
   Why: it keeps the model's objective simple and spam rules fast to change.

## Stage 4: Evaluation and robustness

1. Calibration (rule 14). Run `calibration_by_slice` on next-day data (rule 33),
   with one slice per binary feature. A miscalibrated slice is SERIOUS: it points
   to a bug in data or features. Note that calibration holds only without
   regularization and after convergence; say if either is not true.
2. Judge the model by the decision it drives, not by likelihood (rule 14). Compare
   against the heuristic or the current production system as the reference row.
3. A neutral first launch that does not chase ML gains is fine (rule 4). Do not
   delay the launch for model quality. If a check has not run, write CONDITIONAL
   FATAL or SERIOUS with the check to run.

## Verification gate

Tick every box in `workflow.md`. Also quote the output of `feature_coverage`,
`calibration_by_slice` and the training-versus-serving score test on real serving
output. If any is missing, say so and offer to get it.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/pipeline.md`:

```markdown
# First pipeline: <project>
**Date**: <date>   **Phase**: I

## Model
<linear | logistic | Poisson>, objective <from plan.md>, features <list>. Served by <live scoring | precomputed table>.

## How examples are built
Source: <log or table>. Label: <definition>. Filters inherited: <list and decision for each> (rule 6).

## Heuristics
| Heuristic | Handling (preprocess, feature, raw inputs, label, policy layer) | Why |

## Policy layer
<spam rules, caps, boosts, in order> (rule 15)

## Infrastructure tests (rule 5)
- [ ] Feature columns populated: <feature_coverage output>
- [ ] Statistics match another path: <result>
- [ ] Same score in training and serving: <result>
- [ ] Fixed model can be served: <result>

## Calibration (rule 14)
<calibration_by_slice output on next-day data>

## Verdicts
<FATAL | SERIOUS | MINOR lines, or none>
```

Say where the file is saved. Hand off to `/ml:ml-monitoring` before launch (freshness,
export checks, data statistics), then `/ml:ml-features` after launch.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Deep model or ensemble first | Hides wiring bugs; Phase III move in Phase I | Logistic, linear or Poisson regression (rule 14) |
| Judging the pipeline by model accuracy | A pipeline bug looks like a weak model | Test the infrastructure apart from the ML (rule 5) |
| Reusing a copied pipeline as is | Its filters drop data the new use needs | List and justify every filter (rule 6) |
| Leaving a heuristic beside the model unrecorded | Two systems decide and nobody knows which | Make it a feature, preprocess, or policy layer rule (rule 7) |
| One model for spam and quality | Spam is adversarial and changes fast | Separate them in the policy layer (rule 15) |
| Calibration checked on the training period | Hides time-sensitive bugs | `calibration_by_slice` on next-day data (rules 14, 33) |

## Guide sections

Rules 4 to 7, 14 and 15: `https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_i_your_first_pipeline`, `#your_first_objective`. URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
