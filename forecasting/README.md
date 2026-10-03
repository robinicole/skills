# forecasting

A plugin for forecasting skills. It lives here instead of `skills/` because Claude Code only finds skills one level deep in `~/.claude/skills/`, so a subfolder there would never load.

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
