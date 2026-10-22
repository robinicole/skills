---
name: ml-error-analysis
description: Runs human analysis of a live ML system before and after a launch, namely rater and persona checks instead of insider judgment, the model delta between old and new models with a self-delta stability check, judging by the decision rather than log loss, turning error patterns into candidate features, rated metrics for undesirable behaviour, and short-term versus long-term behaviour. Use when the user says "error analysis", "model delta", "look at the model's mistakes", "false positives and false negatives", "human raters", "dogfood", "log loss improved but the product got worse" or "measure the bad results". Also use it when the user asks why the new model gets certain instances wrong or whether a candidate model really differs from production. Not for reviewing a whole ML system (use ml-auditor), and not for launch trade-offs between metrics (use ml-plateau).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML error analysis

You look at what the model does to users: measure how much a candidate changes,
find patterns in its errors, and turn complaints into numbers.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read `../../references/rules.md`, section "Human analysis of the system" (rules 23 to 28).
3. Read `../../references/workflow.md` for the folder layout, phases and verdict format.
4. Read the plan and `features.md` in `docs/ml-plans/*/` if present. Do not ask again what they answer.

## Stage 1: Setup

1. Confirm the phase (`workflow.md`). This skill fits Phase II. Earlier, send the
   user to `ml-planner` or `ml-first-pipeline`: a broken pipeline shows wiring bugs.
2. Ask for the decision the model drives (ranking, spam cutoff, recommendation)
   and the current production model. Why: every comparison needs production as its
   reference row, and the decision sets what counts as an error (rule 25).
3. Copy `../../templates/ml_checks.py` into `analysis/`. Change only the data loading.

## Stage 2: Diagnostics

1. Self-delta. Run production against itself on the sample queries with
   `model_delta`. It must be close to zero (rule 24). If not, emit FATAL: the
   system is unstable and no other delta means anything.
2. Model delta. Run old and new models on the same sample queries through the
   full system, not the learner alone, and compute `model_delta` per query (rule
   24), because the policy layer can hide or amplify a change. A small delta means
   a live experiment will show little; a large one means inspect the queries that
   moved most before any user sees them.
3. Decision metric. Score both models on next-day data by the decision: final
   ranking quality, or precision above the spam cutoff (rule 25), with log loss
   beside it. If log loss improves and the decision metric falls, emit SERIOUS.

## Stage 3: Implementation

1. Collect errors under the model's own objective: false positives, false
   negatives, and positives ranked below negatives (rule 26). Why: a feature can
   only help where the model already sees an error by its own objective; an error
   only a human sees needs a rated metric, not a feature.
2. Group them into named patterns (long instances, one source, new instances),
   each with a count and three examples.
3. For each pattern, propose a dozen candidate features rather than one guess, for
   example several length buckets (rule 26). `ml-features` adds them.
4. Turn each recurring complaint into a rated metric: human labels on the head
   queries, with a written rating guide (rule 27). Measure first, optimize second,
   because an unmeasured complaint cannot be compared across models.
5. Ask who has judged the model so far. Insiders have confirmation bias and cost
   a lot, so dogfood only for obvious breakage, then plan paid raters, personas
   and usability tests, or a live experiment (rule 23).

## Stage 4: Evaluation and robustness

- Check that the sample queries cover head and tail and that the self-delta used
  the same sample.
- Ask what the new model does with instances it has not seen. A model keyed on
  instance IDs can match production in a short live experiment and still never
  surface new instances after launch; long-term behaviour shows only on data
  gathered while the model is live (rule 28). If the model leans on ID features,
  emit CONDITIONAL SERIOUS: "If the model rarely ranks new instances, long-term
  quality will fall. Measure the share of new instances served while it is live."

## Verification gate

Before interpreting, confirm from actual output:

- [ ] `ml_checks.py` ran without errors and you can quote the self-delta and the model delta.
- [ ] The decision metric comes from next-day data, not the training period (rule 33).
- [ ] Production is the reference row in every comparison.
- [ ] Each error pattern has a count from the data, not an impression.

If a box is not ticked, say which evidence is missing and offer to get it.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/error-analysis.md`:

```markdown
# Error analysis: <project>
**Date**: <date>   **Candidate**: <model>   **Reference**: <production model>

## Verdicts
<FATAL | SERIOUS | MINOR lines, or "None">

## Model delta
Self-delta: <value>. Old vs new: <mean value> on <n> sample queries. Queries that moved most: <list>.

## Decision metric
| Model | <decision metric> | <log loss or AUC> | Data |
|---|---|---|---|
| Production | | | next-day |
| Candidate | | | next-day |

## Error patterns
### <pattern>: <count> errors
Examples: <three>. Candidate features: <list>. Handed to ml-features.

## Rated metrics
| Behaviour | Rating guide | Head queries | Current rate |
|---|---|---|---|

## Human evaluation plan
<raters, personas, live experiment, and the long-term check after launch>
```

Then hand off: `/ml:ml-features` for the candidate features, `/ml:ml-skew` if offline
and live results disagree, `/ml:ml-plateau` if the decision metric and the objective
keep pulling apart (rule 25), and `/ml:ml-auditor` before launch.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| The team judges the model | Insiders have confirmation bias (rule 23) | Raters, personas or a live experiment |
| Model delta on the learner alone | The policy layer changes what users see | Run both models through the full system (rule 24) |
| Skipping the self-delta | An unstable system makes every delta noise | Model against itself first; expect zero (rule 24) |
| Launching on better log loss | The decision is what users get (rule 25) | Judge by the decision metric |
| One guessed feature per pattern | The right form is rarely the first guess | A dozen candidates, for example several buckets (rule 26) |
| Optimizing a complaint before measuring it | No way to tell if it improved | Rated metric first (rule 27) |
| Short experiment read as long-term proof | New instances may never surface (rule 28) | Check on data gathered while the model is live |

## Guide sections

Rules 23 to 28, human analysis of the system, in Phase II:
`https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_ii_feature_engineering`.
URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
