---
name: ml-monitoring
description: Sets up monitoring for a production ML pipeline, namely freshness tests on models a day, a week and a quarter old, sanity checks that block a bad model export, data statistics that catch silent failures such as a stale joined table or a coverage drop, owners and documentation for each feature column, and alerts someone can act on, then writes monitoring.md. Use when the user says "model freshness", "how often to retrain the model", "block a bad model export", "silent failure in my pipeline", "stale joined table", "who owns this feature column" or "monitor my ML pipeline". Also use it for questions about which ML alerts to page on and what to put on the pipeline dashboard. Not for differences between training and serving (use ml-skew), and not for time series forecasting.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later, standard library only, for templates/ml_checks.py.
---

# ML monitoring

You are the engineer on call for this pipeline. Make sure a bad model or a broken
input is caught before users see it, and that every alert tells someone what to do.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read the Monitoring section of `../../references/rules.md` (rules 8 to 11).
3. Read `../../references/workflow.md` for the folder layout, phases and verdict format.
4. Read `plan.md` and `pipeline.md` in `docs/ml-plans/*/` if they exist. Do not ask
   again what they answer.

## Stage 1: Setup

1. Confirm the phase (`workflow.md`). Monitoring starts in Phase I, once a model is
   exported to serving. With no model yet, hand to `/ml:ml-planner`.
2. List the pipeline parts: the logs that feed examples, every joined table, the
   training job, the export step, the serving system. Why: each joined table is a
   place a silent failure can start (rule 10).
3. Ask what the alerts and dashboard look like today and who receives the pages.
   Why: an alert nobody can act on trains people to ignore alerts.
4. Copy `../../templates/ml_checks.py` into `analysis/`. Change only the data loading.

## Stage 2: Diagnostics

1. Freshness (rule 8). Score the current production model and copies that are a
   day, a week and a quarter old on the same next-day data. Why: the drop with age
   says how often to retrain. Ads models need daily updates; some search models
   degrade within a month. If no old copies are kept, emit CONDITIONAL SERIOUS:
   "If quality drops fast with age, then the retrain schedule is a guess. Keep
   dated model copies and run the freshness test."
2. Export gate (rule 9). Find the check, if any, that runs on holdout data (for
   example AUC) before export. If export runs with no check, emit SERIOUS. Why: a
   bad unexported model is an email; a bad live model is a page.
3. Joined tables (rule 10). For each table, find when it last updated. A table that
   stopped updating decays the model quietly; one stale table, refreshed after six
   months, gave 2% on installs. A table that stopped updating is SERIOUS.
4. Coverage (rule 10). Run `feature_coverage(examples, baseline)` on the current
   window against an earlier one. Each finding it returns is SERIOUS. Why: in the
   guide, a feature fell from 90% to 60% coverage and nobody noticed. Then look at
   a sample of examples by hand, because statistics miss what they do not measure.
5. Ownership (rule 11). For each feature column, check that someone is named as
   owner and that it has documentation. A column with no owner is MINOR, or
   SERIOUS when its coverage also dropped.

## Stage 3: Implementation

1. Retrain schedule: set it from the freshness curve, with margin before the
   quality drop the decision cannot accept (rule 8). Note that freshness changes
   when feature columns are added or removed, so the test runs again then.
2. Export gate: add the holdout check as a step that blocks export on failure, not
   a report someone reads afterwards (rule 9).
3. Data statistics: run `feature_coverage` on every training run with the last
   good run as the baseline, and check the last update time of every joined table
   (rule 10).
4. Feature column register: one row per feature column with who made it, who keeps
   it, what it is, where it comes from and why it should help (rule 11).
5. Alerts: for each alert, write the condition, the owner and the first action.
   Drop alerts that have no action. Keep a dashboard for the rest.

## Stage 4: Evaluation and robustness

- Break the export gate on purpose: feed it a model trained on shuffled labels and
  confirm the export is blocked.
- Run `feature_coverage` with one feature set to None on part of the examples and
  confirm it reports a coverage drop.
- Confirm each alert reaches its owner, and that the owner knows the first action.

## Verification gate

Apply the gate in `workflow.md`. In addition, before writing monitoring.md:

- [ ] The freshness numbers come from model copies scored on next-day data, not from
      an estimate.
- [ ] The export gate blocked a bad model in a real run, and you can quote the output.
- [ ] `feature_coverage` output is quoted for the current window.

## Stage 5: Interpretation and handoff

Write `docs/ml-plans/<project>/monitoring.md`:

```markdown
# Monitoring: <project>
**Date**: <date>   **Phase**: <I | II | III>

## Freshness (rule 8)
| Model age | Metric on next-day data | Change against production |
Retrain schedule: <cadence> because <reason>.

## Export gate (rule 9)
Check: <metric> on holdout, block if <condition>. Tested with: <bad model, result>.

## Data statistics (rule 10)
| Joined table | Last update | Alert if older than |
| Feature column | Coverage now | Baseline | Finding |

## Feature columns (rule 11)
| Feature column | Made by | Kept by | What it is | Source | Why it should help |

## Alerts
| Condition | Owner | First action |

## Verdicts
<FATAL | SERIOUS | MINOR findings, in the workflow.md format>
```

Then hand off. Suspected differences between training and serving go to
`/ml:ml-skew`. A working pipeline with rising metrics goes to `/ml:ml-features`.
Before a launch, run `/ml:ml-auditor`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Retraining on a fixed calendar picked by habit | The model may decay faster or slower | Measure models a day, a week and a quarter old (rule 8) |
| Checking a model after it is live | A bad live model is a page | Block the export on a failed holdout check (rule 9) |
| Watching only model metrics | A stale joined table decays the model quietly | Track update times and coverage (rule 10) |
| Trusting dashboards without looking at examples | Statistics miss what they do not measure | Read a sample of examples by hand (rule 10) |
| Feature columns nobody owns | Nobody fixes them when they break | Name an owner and document each column (rule 11) |
| Alerts with no first action | People learn to ignore them | Every alert has an owner and an action |

## Guide sections

Rules 8 to 11, Monitoring, inside Phase I:
`https://developers.google.com/machine-learning/guides/rules-of-ml#ml_phase_i_your_first_pipeline`.
URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md`
(format in `../../references/lessons.md`).
