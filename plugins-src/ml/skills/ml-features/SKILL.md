---
name: ml-features
description: Plans Phase II feature engineering for a live, tested ML pipeline, namely cheap launch-and-iterate cycles, directly observed features before learned ones, content features that generalise across contexts, very specific features, discretization and crosses, the number of weights the data can support, and removing unused features by coverage, then keeps a feature log. Use when the user says "feature engineering", "feature cross", "discretize a feature", "bucketize", "embedding features", "delete unused features", "too many features for my data" or "feature log". Also use it for questions about which kind of feature to add next while metrics still rise. Not for finding features from model errors (use ml-error-analysis), and not for a plateau where new features stopped helping (use ml-plateau).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML features

You are an ML engineer in Phase II. Help the user add, combine and remove features
simply, and keep a feature log that the other skills read.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read `../../references/rules.md`, section "Phase II: feature engineering" (rules 16 to 22).
3. Read `../../references/workflow.md` for the folder layout and verdict format.
4. If `docs/ml-plans/*/plan.md`, `pipeline.md` or `features.md` exists for this
   project, read them and update `features.md` instead of starting again.

## Stage 1: Setup (the phase)

1. Confirm the phase. Phase II starts once the pipeline is live with unit and system
   tests and metrics still rise. If not, emit SERIOUS and send the user to
   `/ml:ml-first-pipeline`. Why: features cannot fix a pipeline that drops data.
2. If gains are under about 1% a launch and metrics trade off, the system is in
   Phase III. Send the user to `/ml:ml-plateau` and stop.
3. Ask for the number of examples per training run, the current feature columns,
   and the launch cadence. Why: data size sets how many weights the model can learn
   (rule 21), and cadence sets how cheap iteration must be (rule 16).

## Stage 2: Diagnostics (the current features)

- Iteration cost (rule 16). Ask how long it takes to add, remove or recombine one
  feature, and whether two or three copies of the pipeline can run side by side.
  Expect a launch per quarter or more for years, so slow iteration is SERIOUS.
- Learned features (rule 17). List features that come from another system
  (clusters, embeddings). They have their own objective and can change meaning
  when that system updates. If there is no non-deep baseline, emit SERIOUS.
- Coverage (rules 19, 22). Copy `templates/ml_checks.py` into `analysis/` and run
  `feature_coverage(examples)` on recent examples. Why: coverage decides what a
  feature can contribute and what can go.
- Model size against data (rule 21). Compare the number of features with the
  tiers below. A model with far more weights than its tier is CONDITIONAL SERIOUS
  until next-day data shows it does not overfit.

| Examples | What the data supports (rule 21) |
|---|---|
| About 1,000 | A dozen engineered features (TF-IDF, dot products) |
| About a million | Feature intersections with regularization and selection |
| Billions | Crosses up to about ten million features |

## Stage 3: Implementation (the next features)

Propose candidates in this order, and say why each fits this system:

1. Directly observed features first (rule 17). Why: their meaning is stable and
   a convex model gives repeatable results, so a real change is visible.
2. Content features gathered in other contexts (rule 18): shares, watches or
   ratings from another surface. Why: they let new instances enter. They are not
   personalisation; first learn whether people like the instance here.
3. Very specific features when data allows (rule 19): IDs for head queries, many
   simple sparse features. Many sparse features are fine if together they cover
   over 90% of examples; regularization removes the ones that fire too rarely.
4. Discretize continuous features into quantile buckets, and cross feature columns
   (rule 20). Why: both stay human-understandable. Crosses of three or more
   columns need a lot of data and overfit easily; flag them as SERIOUS below the
   billions tier.
5. Removal candidates (rule 22). A feature on 8% of users helps little; one on 1%
   of examples can still matter if 90% of those are positive. Check both coverage
   and label rate before deleting. A feature can be added back later.

Do not agonise over feature 16 of 35 (rule 16); batch small additions.

## Stage 4: Evaluation and robustness

- Score every change on next-day data, with the current production model as the
  reference row (rule 33). Why: a random split hides time-sensitive features.
- Re-run `feature_coverage(examples, baseline=...)` against the earlier period.
  A SERIOUS coverage drop is a silent failure; hand it to `/ml:ml-monitoring`.
- For each removal, confirm the next-day metric does not fall (rule 22).

## Verification gate

- [ ] `feature_coverage` ran and its output is quoted.
- [ ] Offline numbers come from data after the training window (rule 33).
- [ ] Every comparison has the production model as its reference row.
- [ ] Each removal has coverage and label rate, not coverage alone.

If a box is not ticked, say which evidence is missing and offer to get it.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/features.md`:

```markdown
# Feature log: <project>

**Updated**: <date>   **Examples per run**: <n> (rule 21 tier: <1k | 1M | billions>)
**Iteration**: <time to add a feature>, parallel pipelines <yes | no> (rule 16)

## Log
| Date | Change | Feature column | Kind | Coverage | Next-day effect | Rule | Owner |
|---|---|---|---|---|---|---|---|
| <date> | added / crossed / bucketed / removed | <name> | observed / learned / content / specific | <%> | <+/- metric> | <n> | <who> |

## Learned features
<feature, producing system, last change> (rule 17)

## Verdicts
<FATAL / SERIOUS / MINOR lines, verbatim>

## Next
<the next two or three candidates and why>
```

Then hand off: `/ml:ml-skew` to check new features at serving, `/ml:ml-error-analysis`
for the next feature from model errors, `/ml:ml-auditor` before the launch decision.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Embeddings from another system as the first features | They change meaning when that system updates (rule 17) | Directly observed features and a non-deep baseline first |
| A three-column cross on a million examples | Needs a lot of data and overfits (rules 20, 21) | Two-column crosses, regularized, or quantile buckets |
| Deleting a feature on coverage alone | 1% coverage can matter at a 90% positive rate (rule 22) | Check coverage and label rate |
| Keeping every feature ever added | Unused features are debt (rule 22) | Remove them; add back later if needed |
| Long debate over one feature | Many launches are coming (rule 16) | Make iteration cheap and batch small changes |
| Calling cross-context content features personalisation | They say whether the instance is liked here, not by whom (rule 18) | Learn popularity here first, then who likes it more |

## Guide sections

Rules 16 to 22, Phase II: feature engineering. URLs checked 2026-10-22.
`https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_ii_feature_engineering`

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
