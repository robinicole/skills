# Evals

| Script | What it checks | Cost |
|---|---|---|
| `run_templates.sh` | Every template runs end to end; logs and plots in `runs/` | free, about 5 minutes |
| `ground_truth.py` | ETS(A,A,N) and ARIMA(1,1,1) parameters are recovered from simulated series | free, about 1 minute |
| `trigger_eval.py` | Trigger phrases in the skill descriptions (keyword mode) | free |
| `trigger_eval.py --mode cli` | The skill Claude actually calls for each prompt, with this plugin loaded | about $0.07 per case |

Python: the venv used for the build had statsforecast 2.1.1, mlforecast 1.1.0,
hierarchicalforecast 1.5.3, utilsforecast 0.2.17, statsmodels 0.15.0, prophet 1.5.0.
Set `PYTHON=/path/to/python` for `run_templates.sh`.

## Cases

`cases/trigger/*.yaml`: four per skill, two explicit and two paraphrased.
`cases/no_trigger/*.yaml`: causal questions, trading advice, classification,
descriptive statistics, general questions. No forecasting skill may trigger on them.

```yaml
name: trigger_ets_explicit_1
description: forecast-ets should trigger on a explicit prompt
skill: forecast-ets
kind: explicit          # explicit | paraphrase | causal | stock | ml | descriptive | other
user_message: Fit an exponential smoothing model (ETS) to my monthly sales and explain the parameters.
expected:
  should_trigger: true
```

The CLI mode runs `claude -p` in an empty folder with `--plugin-dir` pointing at
this plugin, blocks file and shell tools, and stops at the first Skill call or after three turns. Other
plugins installed for the user stay loaded, so the test also shows competition
from them.

Outputs go to `runs/`, which git ignores.
