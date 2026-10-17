# skills

My Claude Code skills and config. Every skill I write ships as a plugin under `plugins-src/`, and this repo doubles as the `robinicole-skills` marketplace.

## Install

```sh
SKILLS_DIR=/path/to/skills   # wherever you want the clone
git clone git@github.com:robinicole/skills.git "$SKILLS_DIR"
for f in CLAUDE.md docs; do ln -sfn "$SKILLS_DIR/$f" ~/.claude/$f; done
```

`~/.claude` holds symlinks to `CLAUDE.md` and `docs/` in this repo, so edit and commit here. `~/.claude/settings.json` is a plain local file and is not tracked.

Nothing goes in `~/.claude/skills/`. Write skills inside a plugin in `plugins-src/` (see below).

## Matt Pocock's skills

[Matt Pocock's engineering skills](https://github.com/mattpocock/skills) come from the `mattpocock-skills` plugin in the official marketplace. Invoke as `/mattpocock-skills:<name>` (or `/<name>` when no other skill shares the name).

In a project repo, run `/setup-matt-pocock-skills` once. It records that repo's issue tracker, triage labels and domain-doc layout under `docs/agents/`. If you don't know which skill to use, `/ask-matt` picks one.

**Plan:** `/grilling` stress-tests a plan by interviewing you (`/grill-me`, `/grill-with-docs` are shortcuts) · `/wayfinder` charts work too big for one session · `/to-spec` turns this conversation into a PRD · `/to-tickets` breaks a plan into tickets with blocking edges · `/prototype` answers one design question with throwaway code · `/research` sends a background agent to read primary sources.

**Build:** `/implement` works from a spec or tickets · `/tdd` runs the red-green loop · `/diagnosing-bugs` for hard bugs and perf regressions · `/code-review` checks a diff against repo standards and the originating spec · `/core:karpathy-guidelines` guards against the usual LLM coding mistakes.

**Shape:** `/codebase-design` is the deep-module vocabulary · `/improve-codebase-architecture` scans for deepening opportunities and grills through one · `/domain-modeling` builds the ubiquitous language and records ADRs.

**Meta:** `/triage` moves issues and external PRs through a state machine · `/handoff` compacts a conversation for a fresh agent · `/teach` learns a topic across sessions · `/core:writing-great-skills` covers writing skills that behave predictably.

The plugin's `skills/*/SKILL.md` files are the real documentation.

## Plugins in this repo

Each folder in `plugins-src/` is a plugin listed in `.claude-plugin/marketplace.json` and enabled in `~/.claude/settings.json`. (Not `plugins/`, which is Claude Code's own cache dir.)

| Plugin | Skills |
|---|---|
| `core` | `ponytail` (plus `-audit`, `-review`, `-debt`, `-gain`, `-help`), `no-ai-slop`, `karpathy-guidelines`, `writing-great-skills`, `asd-ste100`, `i-have-adhd`, see `plugins-src/core/README.md` |
| `forecasting` | `forecast`, `backtest`, `reconcile`, see `plugins-src/forecasting/README.md` |

New skill: `plugins-src/<plugin>/skills/<name>/SKILL.md`. New plugin: `plugins-src/<plugin>/.claude-plugin/plugin.json` plus an entry in `marketplace.json` and `<plugin>@robinicole-skills: true` in `~/.claude/settings.json`. Check with `claude plugin validate .`. The marketplace source is GitHub, so push, then `/plugin marketplace update robinicole-skills`.

## Adding plugins

Two keys in `~/.claude/settings.json`: a source under `extraKnownMarketplaces`, then `<plugin>@<marketplace>: true` under `enabledPlugins`. Restart Claude Code after editing.

```json
"extraKnownMarketplaces": { "humanizer": { "source": { "source": "github", "repo": "blader/humanizer" } } },
"enabledPlugins": { "humanizer@humanizer": true }
```

Or from the terminal, which edits `settings.json` for you:

```sh
claude plugin marketplace add blader/humanizer
claude plugin marketplace add https://github.com/DrCatHicks/learning-opportunities.git
claude plugin marketplace add https://github.com/DrCatHicks/learning-goal.git
claude plugin marketplace add robinicole/skills
claude plugin marketplace add anthropics/claude-plugins-official

claude plugin install humanizer@humanizer
claude plugin install learning-opportunities@learning-opportunities
claude plugin install orient@learning-opportunities
claude plugin install learning-goal@learning-goal
claude plugin install core@robinicole-skills
claude plugin install forecasting@robinicole-skills
claude plugin install mattpocock-skills@claude-plugins-official
```

Inside a session, the same thing is `/plugin marketplace add <source>` and `/plugin install <plugin>@<marketplace>`.

| Plugin | Source | Invoke |
|---|---|---|
| `core` | github `robinicole/skills` | `/core:<name>` |
| `forecasting` | github `robinicole/skills` | `/forecasting:<name>` |
| `humanizer` | github `blader/humanizer` | `/humanizer` |
| `learning-opportunities` | git `DrCatHicks/learning-opportunities.git` | `/learning-opportunities`, `/orient` |
| `learning-goal` | git `DrCatHicks/learning-goal.git` | `/learning-goal` |
| `mattpocock-skills` | github `anthropics/claude-plugins-official` | `/mattpocock-skills:<name>` |
