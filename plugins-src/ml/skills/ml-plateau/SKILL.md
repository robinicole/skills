---
name: ml-plateau
description: Guides a Phase III ML system whose launches gain under about 1% and whose metrics trade off, namely checking whether the objective rather than the features is the problem, reading a live experiment across several metrics as a proxy for long-term goals, keeping ensembles simple and monotone over calibrated base models, adding qualitatively new information instead of refinements, valuing diversity and personalization apart from popularity, and choosing which cross-product data transfers, then writes plateau.md. Use when the user says "gains have plateaued", "metrics trade off", "A/B test with mixed results", "objective is misaligned", "ensemble of models", "new sources of signal", "diversity versus popularity" or "cross-product features". Also use it when a candidate model raises one product metric and lowers another and the team cannot agree whether to launch. Not for a system still in Phase I or II (use ml-first-pipeline or ml-features), and not for time series forecasting.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML plateau

You are an ML engineer advising a mature system whose easy gains are gone. Find
what limits it (objective, launch decision or information) and record the next move.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read the Phase III section of `../../references/rules.md` (rules 38 to 43).
3. Read `../../references/workflow.md` for the folder layout, phases and verdict format.
4. Read `plan.md`, `features.md`, `error-analysis.md` and `skew.md` in
   `docs/ml-plans/*/` if present. Do not ask again what they answer.

## Stage 1: Setup

1. Confirm the phase. Ask for the gain of each of the last few launches. Phase III
   means several quarters below about 1% and metrics that trade off (rule 41). If
   gains are still larger, or the pipeline is not tested and monitored, send the
   user to `/ml:ml-features` or `/ml:ml-first-pipeline` and stop. Why: Phase III
   moves on an earlier system add complexity that slows every later launch.
2. Ask for the objective and the product goal it stands for. If the two diverge,
   more features will not help (rule 38).
3. Ask how launches are decided: metrics, decider, last rejected launch (rule 39).
4. Ask what the model is built on: features, other models' scores, or both (rule 40).

## Stage 2: Diagnostics

1. Objective gap. Compare recent objective gains with movement in the product
   metrics. If the objective rose and the product metrics did not, emit SERIOUS:
   the objective is the limit, not the features (rule 38).
2. Launch readout. For the candidate's live experiment, write one row per metric
   with its change: engagement, 1-day and 30-day actives, revenue, advertiser ROI,
   or whatever the team tracks. Mark each as better, worse or flat. If nothing is
   worse, it is an easy launch. If any is worse, it is a trade, and the decision
   belongs to the people who own the product goals, not to the objective (rule 39).
3. Ensemble shape. If one model takes both features and other models' outputs,
   emit SERIOUS (rule 40). If the combiner can lower the final score when a base
   score rises, emit SERIOUS: it is not monotone.
4. Copy `../../templates/ml_checks.py` into `analysis/`, change only the data loading,
   and run `calibration_by_slice` on each base model. Why: the ensemble assumes
   calibrated base models (rule 40).
5. Note diversity or personalization features with low or negative weight (rule 42).

## Stage 3: Implementation

Recommend only the moves the diagnostics support, each with its rule.

- If the objective is the limit, change the objective or the launch criteria
  before adding features. For example, optimize clicks but decide launches partly
  on rater judgments (rule 38).
- State each trade in the units the team uses, such as 1M DAU and $4M a day
  against 2M DAU and $2M a day, and name who decides. Multi-objective learning
  with lower-bound constraints on each metric helps a little; it does not remove
  the decision (rule 39).
- Split a mixed model into base models over features and one ensemble over their
  outputs. Keep the ensemble monotone in each base score and the base models
  interpretable and calibrated (rule 40).
- After several quarters below 1%, build infrastructure for new kinds of
  information instead of refining existing features: user history over a day, a
  week and a year, data from other products, knowledge graphs, deep learning.
  Lower ROI expectations and weigh each gain against its complexity (rule 41).
- Add diversity or personalization in post-processing, in the policy layer. If
  long-term metrics rise, value it on its own and change the objective (rule 42).
- Across products, use connection strength between users. Expect most
  cross-product personalization features to fail; try raw cross-product data and
  "is active on the other product" first (rule 43).

## Stage 4: Evaluation and robustness

Judge each change by its live experiment across all launch metrics, not by the
objective alone (rule 39). For a post-processing change, watch the long-term
metrics before folding it into the objective (rule 42). After restructuring an
ensemble, run `calibration_by_slice` again on the base models. Emit a verdict for
any check that fails; when in doubt, choose the higher label.

## Verification gate

Tick every box in the gate in `workflow.md`. In addition, every metric in the
launch readout comes from the live experiment, with the production model as the
control. If a box is not ticked, say what is missing.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/plateau.md`:

```markdown
# Plateau review: <project>
**Date**: <date>  **Recent launch gains**: <list>

## Objective alignment (rule 38)
Objective: <objective>. Product goal: <goal>. Gap: <yes | no, evidence>.

## Launch readout (rule 39)
| Metric | Change | Better / worse / flat |
|---|---|---|
| <metric> | <n> | <...> |
Trade: <none | stated in units>. Decided by: <owner>.

## Ensemble (rule 40)
Shape: <base models + ensemble | mixed>. Monotone: <yes | no>.
calibration_by_slice: <quoted output>.

## New information and post-processing (rules 41, 42, 43)
<sources planned, expected gain, complexity cost, owner>

```

Next: `/ml:ml-features` to log any new feature columns; `/ml:ml-error-analysis` to
rate a post-processing change; `/ml:ml-auditor` before a launch.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| More features when the objective misses the goal | Gains on the objective do not reach the product | Change the objective or the launch criteria (rule 38) |
| Launching on the objective alone | Other product metrics can fall | Read the experiment across all launch metrics (rule 39) |
| Hiding a metric trade inside a weighted sum | The decision belongs to the goal owners | State the trade in units and name who decides (rule 39) |
| One model over features and other models' scores | Hard to debug, failures spread | Base models over features, ensemble over outputs (rule 40) |
| Refining old features after quarters under 1% | Refinements have run out | Add new kinds of information (rule 41) |
| Expecting popularity metrics to reward diversity | They give it low or negative weight | Add it in post-processing, watch long-term metrics (rule 42) |
| Copying interest features across products | Interests rarely transfer | Use connection strength and raw cross-product data (rule 43) |

## Guide sections

Rules 38 to 43, Phase III:
`https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_iii_slowed_growth_optimization_refinement_and_complex_models`.
URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
