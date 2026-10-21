# Workflow rules shared by every skill

## Project folder

Every skill reads and writes one folder in the user's project:

```
docs/forecast-plans/YYYY-MM-DD-<name>/
  plan.md            forecast-planner
  explore.md         forecast-explore (findings per series or group)
  baselines.md       forecast-baselines (benchmarks, evaluation design, scores)
  <method>.md        each method skill: choices, diagnostics, scores
  analysis/          copied templates and the user's adapted scripts
  audit.md           forecast-auditor
  report.md          forecast-report
docs/forecast-plans/lessons.md   lessons learned in this project
```

If a plan exists, read it and do not ask again what it already answers. If none
exists, create the folder with today's date and a short name.

Copy templates from the plugin's `templates/` folder into `analysis/`, together
with `fpp_data.py` and `fc_checks.py`. Change only the data section and the names
of columns. The templates were run as they are; restructuring them brings bugs.

## Severity verdicts

Emit a verdict as soon as a check reveals a problem, before any interpretation.

> **FATAL: <check name>**
> <One sentence: what was found.>
> Do not use this forecast until this is fixed.

> **SERIOUS: <check name>**
> <One sentence: what was found.>
> The forecast can be used only with this caveat stated next to it.

> **MINOR: <check name>**
> <One sentence.>

When the check has not been run yet, write **CONDITIONAL FATAL** (or SERIOUS):
"If <condition>, then <consequence>. Run <check> and report the result."

Use only these three labels. When in doubt, choose the higher one. If the user goes
on after a FATAL verdict, repeat it word for word in the interpretation.

## Verification gate

Before Stage 5 (interpretation), confirm from actual output, not from the code:

- [ ] The script ran without errors.
- [ ] You can quote the chosen model and its parameters.
- [ ] You can quote cross-validated accuracy per forecast horizon, with the benchmark row.
- [ ] You can quote the residual check (Ljung-Box lag, p-value).
- [ ] You can quote interval coverage when intervals are reported.

If a box is not ticked, say which evidence is missing and offer to run the step.
If the user goes on anyway, carry the gap as a caveat. Do not write "the results
show" before the gate passes.

## Explain the why

Every recommendation comes with one or two sentences on why it matters for this
user's decision. The user should learn to see the problem, not only follow steps.

## Self-correction

When the user corrects you, or a run shows a mistake, append a lesson to
`docs/forecast-plans/lessons.md` in the user's project, in the format of
`references/lessons.md`. Read both files at the start of every skill.

## Out of scope

- Causal questions ("did X increase Y", "what would have happened without X",
  CausalImpact, difference-in-differences, A/B test effects). A forecast is not a
  counterfactual. Say so and stop.
- Investment advice on prices of traded assets. The book's answer for such series
  is a naive forecast with a wide interval; say that, and no more.
- Classification and general machine learning without a time index.
