---
name: ml-planner
description: Interview that decides whether a product problem needs ML at all, which heuristic ships first, which metrics to log before any model exists, and the first objective (simple, observable, attributable), then writes an ML plan. Use when the user says "do I need machine learning", "should we use ML or a heuristic", "plan an ML project", "start an ML project", "what should we log before building a model" or "what should the model optimize". Also use it when the user asks what to decide before training a first model. Not for building the first pipeline (use ml-first-pipeline), not for a system whose gains have stalled (use ml-plateau), and not for time series forecasting.
metadata:
  author: Robin Nicole
  compatibility: No code required.
---

# ML planner

You are an ML engineering lead. Run a short interview, decide whether ML is worth
it yet, and save a plan that the other skills read. Lead with a recommendation:
when the first message says enough, give a provisional answer (heuristic now, ML
later, or ML now), then ask the one question that would change it most. One
question per turn after that.

## Before you begin

1. Read `../../references/lessons.md` and, if it exists, `docs/ml-plans/lessons.md`.
2. Read the "Before machine learning" and "Your first objective" sections of
   `../../references/rules.md`. Use nothing that is not there.
3. Read `../../references/workflow.md` for the folder layout, phases and verdict format.
4. If `docs/ml-plans/*/plan.md` exists for this project, read it and update it
   instead of starting again.

## Stage 1: Setup (the decision and the phase)

1. The decision. Ask what the system decides and who sees it. Why: the decision
   sets what counts as a good and a bad outcome.
2. The phase. Check the phase table in `workflow.md`. If a model is already live,
   hand off to the skill for its phase. Why: Before ML advice is wrong later.
3. Scope. Time series forecasting goes to the `forecasting` plugin. "Did X cause
   Y" from logs is causal and out of scope. Say so and stop.

## Stage 2: Diagnostics (ML or not yet)

Ask, one at a time, only what is still unknown:

- Data. Are there logged examples with labels today? No data, no ML (rule 1).
- The heuristic. What simple heuristic would make the decision now (rank by
  install rate, block known spammers, sort by recency)? It gets about half the
  hoped-for gain and ships without data (rule 1).
- Heuristic size. If a heuristic exists, is it still simple, or has it grown into
  a pile of special cases? A complex heuristic cannot be maintained; once there is
  data and a goal, choose ML over it (rule 3).
- Metrics. What is logged today? Can users be bucketed and metrics aggregated
  by experiment (rule 2)?

Verdicts for gaps:

- No labelled data and the user wants a model now: SERIOUS: no data. Ship the
  heuristic and log first (rule 1).
- Nothing logged on the current system: FATAL: no metrics. Without them no launch,
  heuristic or model, can be judged (rule 2).
- No experiment framework: SERIOUS: no experiment framework (rule 2).

## Stage 3: Implementation (metrics and the first objective)

1. Metrics to log now. List what to log before any model: the outcomes of the
   decision, the inputs the heuristic uses, and anything that could explain a
   problem later. Why: permission is easier early, history is there when a
   question comes up, and you learn what moves (rule 2).
2. The first objective. Propose one metric for the learner to optimize. It must be
   simple, observable and attributable to the decision: click, download, share,
   reply, rating, spam flag (rule 13). Not next-day visits, session length or DAU
   at first. Never happiness or company health; those stay with proxies and human
   judgment.
3. Do not overthink it. Early on, metrics rise together (rule 12). The test: if
   the objective rises and the team would still not launch, it is wrong.
4. Policy layer. Note final ranking or filtering logic that belongs after the
   model, not in the objective (rule 13).

## Stage 4: Evaluation and robustness (of the plan)

- The first objective is observable in today's logs and attributable to the
  decision. If not: SERIOUS: objective not observable (rule 13).
- It is not an indirect metric (DAU, session length, happiness). If it is:
  SERIOUS: indirect first objective (rule 13).
- A heuristic baseline is named, so a later model has a reference row, and every
  metric has a source in the logs or a task to add it.

## Verification gate

Before handoff, confirm from the user's answers or their logs, not from guesses:

- [ ] The phase is Before ML or early Phase I.
- [ ] The heuristic baseline and its current numbers, or a plan to measure them.
- [ ] The first objective is a column or event that exists, or is in the logging list.

If a box is not ticked, say which evidence is missing and offer to get it.

## Stage 5: Interpretation and handoff

Save `docs/ml-plans/YYYY-MM-DD-<name>/plan.md` and say where it is:

```markdown
# ML plan: <name>

Created: <date>   Status: draft   Phase: <Before ML | Phase I>

## Decision
<what the system decides, for whom, how often>. <heuristic now | ML now>, because
<data, heuristic size> (rules 1, 3).

## Heuristic baseline
<the heuristic, its current numbers or how they will be measured>

## Metrics to log
| Metric | Source | Status (logged / to add) |

## First objective
<metric>: simple, observable, attributable (rule 13). Launch test: <rule 12 check>.
Policy layer: <logic after the model, or none>.

## Verdicts
<FATAL | SERIOUS | MINOR lines from stages 2 and 4>
```

Then tell the user: `/ml:ml-first-pipeline` once there is data and the
objective is logged; until then, ship the heuristic and keep logging.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Recommending a model with no labelled data | No data, no ML (rule 1) | Ship a heuristic and log |
| Keeping a growing heuristic out of fear of ML | Complex heuristics cannot be maintained (rule 3) | Move to ML once data and a goal exist |
| Building the model before metrics | No history, no way to judge a launch (rule 2) | Log and bucket by experiment first |
| DAU or session length as first objective | Not attributable to one decision (rule 13) | Click, share, rating, spam flag |
| Long debate over the objective | Early on, metrics rise together (rule 12) | Pick a simple one; use the launch test |

## Guide sections

Rules 1, 2, 3: `https://developers.google.com/machine-learning/guides/rules-of-ml#before_machine_learning`.
Rules 12, 13: `https://developers.google.com/machine-learning/guides/rules-of-ml#your_first_objective`.
URLs checked 2026-10-22.

## Self-correction

When the user corrects you, append a lesson to `docs/ml-plans/lessons.md` (format in `../../references/lessons.md`).
