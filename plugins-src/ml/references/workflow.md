# Workflow rules shared by every skill

## Project folder

Every skill reads and writes one folder in the user's project:

```
docs/ml-plans/YYYY-MM-DD-<name>/
  plan.md              ml-planner (decision, heuristic baseline, metrics, first objective)
  pipeline.md          ml-first-pipeline (model, infrastructure tests, policy layer)
  monitoring.md        ml-monitoring (freshness, export checks, data stats, owners)
  features.md          ml-features (feature log: added, crossed, removed, coverage)
  error-analysis.md    ml-error-analysis (model delta, error patterns, rated metrics)
  skew.md              ml-skew (the three gaps, logging, sampling)
  plateau.md           ml-plateau (objective alignment, launch trade-offs, new signals)
  audit.md             ml-auditor
  analysis/            copied templates and the user's scripts
docs/ml-plans/lessons.md   lessons learned in this project
```

If a plan exists, read it and do not ask again what it already answers. If none
exists, create the folder with today's date and a short name.

Copy `templates/ml_checks.py` into `analysis/` when a skill runs a check. Change
only the data loading.

## Where is the system?

Ask first which phase the system is in, because the rules differ by phase:

| Phase | Signs | Skill |
|---|---|---|
| Before ML | No model yet, maybe a heuristic | `ml-planner` |
| Phase I | First model, pipeline being built | `ml-first-pipeline`, `ml-monitoring` |
| Phase II | Pipeline live and tested, metrics still rising | `ml-features`, `ml-error-analysis`, `ml-skew` |
| Phase III | Gains under about 1% a launch, metrics trade off | `ml-plateau` |

Do not recommend a Phase III move (ensembles, deep models, new data sources) to a
Phase I system. That is the most common failure this guide exists to stop.

## Severity verdicts

Emit a verdict as soon as a check reveals a problem, before any interpretation.

> **FATAL: <check name>**
> <One sentence: what was found.>
> Do not launch or trust this model until this is fixed.

> **SERIOUS: <check name>**
> <One sentence: what was found.>
> Launch only with this caveat stated next to the result.

> **MINOR: <check name>**
> <One sentence.>

When the check has not been run yet, write **CONDITIONAL FATAL** (or SERIOUS):
"If <condition>, then <consequence>. Run <check> and report the result."

Use only these three labels. When in doubt, choose the higher one. If the user goes
on after a FATAL verdict, repeat it word for word in the interpretation.

## Verification gate

Before interpreting, confirm from actual output, not from reading code:

- [ ] Any script ran without errors and you can quote its output.
- [ ] Offline numbers come from data after the training window (rule 33).
- [ ] Every comparison has the current production system (or the heuristic) as its
      reference row.
- [ ] Claims about serving come from serving logs, not from the training pipeline.

If a box is not ticked, say which evidence is missing and offer to get it. Do not
write "the results show" before the gate passes.

## Cite the rule

Every recommendation names its rule number ("rule 29") and gives one or two
sentences on why it matters for this user's system. Link the phase section from
`rules.md` when the user wants the reasoning.

## Self-correction

When the user corrects you, or a run shows a mistake, append a lesson to
`docs/ml-plans/lessons.md` in the user's project, in the format of
`references/lessons.md`. Read both files at the start of every skill.

## Out of scope

- Time series forecasting: use the `forecasting` plugin.
- Model architecture research, hyperparameter tuning recipes, and teaching ML
  theory. The guide is about engineering a product ML system.
- Causal effect estimation from observational data. An A/B test readout for a
  launch decision is in scope (`ml-plateau`); "did X cause Y" from logs is not.
