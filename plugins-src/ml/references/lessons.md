# Lessons

Known mistakes. Every skill reads this file before it starts. Do not repeat them.

Lessons the user teaches in a project go to `docs/ml-plans/lessons.md` in that
project, in the same format. Read both files.

Format:

```
### <Skill>: <short description>
**Trigger**: when this tends to happen
**Mistake**: what went wrong
**Rule**: what to do instead
**Source**: <guide rule | template run | user correction>, <date>
```

### All: Fancy model before the pipeline works
**Trigger**: The user asks for a better model while the system is in Before ML or Phase I.
**Mistake**: Suggesting deep models, ensembles or tuning.
**Rule**: Check the phase first (`workflow.md`). Until the pipeline is tested end to end and monitored, the next gain comes from infrastructure and simple features.
**Source**: Guide overview and rules 4, 16, 17, 2026-10-22.

### All: Offline evaluation on the training period
**Trigger**: Reporting a random split from the same dates as training.
**Mistake**: It hides time-sensitive features and leakage.
**Rule**: Score on data after the training window (rule 33). Report training, holdout and next-day side by side (rule 37).
**Source**: Guide rules 33 and 37, 2026-10-22.

### All: Better log loss read as a better product
**Trigger**: A model wins on AUC or log loss.
**Mistake**: Calling it a launch.
**Rule**: Judge by the decision it drives and by the live experiment on the product metrics (rules 25 and 39).
**Source**: Guide rules 25 and 39, 2026-10-22.
