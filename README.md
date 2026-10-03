# skills

My Claude Code config — `settings.json` and the skills in `skills/`.

Most are [Matt Pocock's engineering skills](https://github.com/mattpocock); the rest are mine.

## Install

```sh
git clone git@github.com:robinicole/skills.git ~/.claude
```

Skills in `~/.claude/skills/` work in every project. Invoke with `/<name>`.

In a project repo, run `/setup-matt-pocock-skills` once — it records that repo's issue tracker, triage labels, and domain-doc layout under `docs/agents/`.

## The skills

Lost? `/ask-matt` routes you.

**Plan** — `/grilling` stress-tests a plan by interviewing you (`/grill-me`, `/grill-with-docs` are shortcuts) · `/wayfinder` charts work too big for one session · `/to-spec` turns this conversation into a PRD · `/to-tickets` breaks a plan into tickets with blocking edges · `/prototype` answers one design question with throwaway code · `/research` sends a background agent to read primary sources.

**Build** — `/implement` works from a spec or tickets · `/tdd` runs the red-green loop · `/diagnosing-bugs` for hard bugs and perf regressions · `/code-review` checks a diff against repo standards and the originating spec · `/karpathy-guidelines` guards the usual LLM coding failure modes.

**Shape** — `/codebase-design` is the deep-module vocabulary · `/improve-codebase-architecture` scans for deepening opportunities and grills through one · `/domain-modeling` builds the ubiquitous language and records ADRs.

**Meta** — `/triage` moves issues and external PRs through a state machine · `/handoff` compacts a conversation for a fresh agent · `/teach` learns a topic across sessions · `/writing-great-skills` on writing one that behaves predictably.

Each `skills/<name>/SKILL.md` is the real documentation.

## Plugins in this repo

`forecasting/` is a plugin for forecasting skills, invoked as `/forecasting:<name>`. It's enabled in `settings.json`; see `forecasting/README.md` for how to add a skill.

## Plugins

Two keys in `settings.json`: a source under `extraKnownMarketplaces`, then `<plugin>@<marketplace>: true` under `enabledPlugins`. Restart Claude Code after editing.

```json
"extraKnownMarketplaces": { "ponytail": { "source": { "source": "github", "repo": "DietrichGebert/ponytail" } } },
"enabledPlugins": { "ponytail@ponytail": true }
```

| Plugin | Source | Invoke |
|---|---|---|
| `forecasting` | github `robinicole/skills` | `/forecasting:<name>` |
| `ponytail` | github `DietrichGebert/ponytail` | `/ponytail [lite\|full\|ultra]` |
| `humanizer` | github `blader/humanizer` | `/humanizer` |
| `i-have-adhd` | directory `~/.claude/i-have-adhd` (submodule: `git submodule update --init`) | `/i-have-adhd` |
| `learning-opportunities` | git `DrCatHicks/learning-opportunities.git` | `/learning-opportunities`, `/orient` |
| `learning-goal` | git `DrCatHicks/learning-goal.git` | `/learning-goal` |
