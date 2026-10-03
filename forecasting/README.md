# forecasting

A plugin for forecasting skills. It lives here instead of `skills/` because Claude Code only finds skills one level deep in `~/.claude/skills/`, so a subfolder there would never load.

## Skills

| Skill | What it does |
| --- | --- |
| `/forecasting:forecast` | Seven steps from framing the problem to shipped intervals. Points to `EXPLORE.md`, `MODELS.md`, `PRACTICAL.md` and `PYTHON.md` for detail |
| `/forecasting:backtest` | Rolling-origin evaluation per horizon, scored against seasonal naive |
| `/forecasting:reconcile` | Makes forecasts add up across a hierarchy, with MinT |

All three can also start on their own when a conversation matches their description. The content comes from Hyndman and Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed), with the R code replaced by Python (statsforecast 2.1, utilsforecast 0.2, hierarchicalforecast 1.5). Every code block was run against those versions.

## Adding a skill

Create `skills/<name>/SKILL.md` in this folder:

```markdown
---
name: <name>
description: What it does. Use when ...
---

Instructions.
```

Invoke it as `/forecasting:<name>`.

## Enabling the plugin

`settings.json` at the repo root already registers this repo as the `robinicole-skills` marketplace and enables `forecasting@robinicole-skills`. Claude Code pulls the plugin from GitHub, so a new skill shows up after you push it and run `/plugin marketplace update robinicole-skills`.
