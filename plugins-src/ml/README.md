# ml

Claude Code skills for engineering machine learning systems in products. They
follow Martin Zinkevich, [*Rules of Machine Learning: Best Practices for ML
Engineering*](https://developers.google.com/machine-learning/guides/rules-of-ml)
(Google, CC BY 4.0). The skills paraphrase its 43 rules and cite them by number;
read the guide for the reasoning and the examples.

The guide's stance: do ML like a good engineer, not like an ML researcher. Ship
a heuristic, log metrics, keep the first model simple, get the pipeline right,
and add complexity only when simple moves stop paying.

## Workflow

```
ml-planner -> ml-first-pipeline -> ml-monitoring
    -> ml-features / ml-error-analysis / ml-skew -> ml-plateau
ml-auditor at any point
```

Each skill first asks which phase the system is in (before ML, Phase I, II, III),
because the right move depends on it. Skills share one project folder,
`docs/ml-plans/<date>-<name>/`.

| Skill | Rules | Use it to |
|---|---|---|
| `/ml:ml-planner` | 1-3, 12, 13 | Decide whether to use ML, ship a heuristic, log metrics, choose the first objective |
| `/ml:ml-first-pipeline` | 4-7, 14, 15 | Simple first model, infrastructure tests, heuristics as features, policy layer |
| `/ml:ml-monitoring` | 8-11 | Freshness, checks before export, silent failures, feature owners |
| `/ml:ml-features` | 16-22 | Feature engineering: specific features, crosses, scale to data, cleanup |
| `/ml:ml-error-analysis` | 23-28 | Model delta, error patterns, rated metrics, short versus long term |
| `/ml:ml-skew` | 29-37 | Training-serving skew: logging, sampling, joins, next-day tests, position |
| `/ml:ml-plateau` | 38-43 | Phase III: objective alignment, launch trade-offs, ensembles, new signals |
| `/ml:ml-auditor` | all | Review a system against the rules; fatal, serious, minor findings |

They do not trigger on time series forecasting (use `forecasting`), ML theory, or
causal questions from observational data.

## Layout

```
skills/<name>/SKILL.md   the skills
references/              rules.md (the 43 rules in short, with section links),
                         workflow, glossary, lessons
templates/ml_checks.py   calibration, model delta, skew gaps, serving mismatch,
                         feature coverage (standard library only)
evals/                   trigger cases and runner
```

## Install

```
/plugin marketplace add robinicole/skills
/plugin install ml@robinicole-skills
```

Local, one session: `claude --plugin-dir /path/to/skills/plugins-src/ml`.

## Checks

```bash
python templates/ml_checks.py            # self-check of the checks
python evals/trigger_eval.py             # trigger phrases (free, needs pyyaml)
python evals/trigger_eval.py --mode cli  # real trigger test with the Claude CLI (costs tokens)
```

## Credits

Content: Martin Zinkevich, Rules of Machine Learning (CC BY 4.0), see `NOTICE`.
Structure from this repo's `forecasting` plugin. Licence: MIT (`LICENSE`).
