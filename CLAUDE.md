# CLAUDE.md

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues; external PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Coding guidelines

From the Karpathy guidelines (`skills/karpathy-guidelines/SKILL.md`). For trivial tasks, use judgment.

### Think before coding

- State your assumptions. If something is unclear, stop and ask.
- If there are several readings of the request, list them instead of picking one silently.
- If a simpler approach exists, say so.

### Simplicity first

- Write the minimum code that solves the problem. No features, abstractions or config nobody asked for.
- If 200 lines could be 50, rewrite it.

### Surgical changes

- Touch only what the request needs. Don't reformat or refactor nearby code.
- Match the existing style.
- Remove only the dead code your own change created. Mention other dead code, don't delete it.

### Goal-driven execution

- Turn the task into a check you can verify, e.g. "fix the bug" becomes "write a failing test, then make it pass".
- For multi-step work, write a short plan with a check for each step.
