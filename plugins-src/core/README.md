# core

General skills I use in every project. Invoke as `/core:<name>`.

## Skills

| Skill | What it does | Copied from |
|---|---|---|
| `karpathy-guidelines` | Guards the usual LLM coding failure modes | mine |
| `writing-great-skills` | How to write a skill that behaves predictably | mine |
| `asd-ste100` | Rewrites text in Simplified Technical English so an agent cannot misread it | [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) @ `32511c6` (MIT) |
| `i-have-adhd` | Shapes output for an ADHD reader: next action first, numbered steps, no tangents | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) @ `1ecea19` (MIT) |
| `no-ai-slop` | Edits drafts to sound human, or flags AI-slop patterns | [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) @ `000650b` (MIT) |
| `ponytail`, `ponytail-audit`, `-debt`, `-gain`, `-help`, `-review` | Laziest solution that works; audits and reviews for over-engineering | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ `16352ac`, v5.3.2 (MIT) |

Third-party skills are copied as-is, skills folder only — their hooks are not included, so `ponytail` and `i-have-adhd` do not switch on by themselves at session start; invoke them with `/core:ponytail` or `/core:i-have-adhd`. To update a copy, re-copy `skills/<name>/` from the upstream repo and update the commit hash in this table.
