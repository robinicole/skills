# Preflight: missing packages

Every template starts with `preflight(...)` from `templates/fc_checks.py`. It
detects missing packages and prints the install command. It never installs.

## The rule

1. **Detect.** Run the template. Its first lines report missing packages.
2. **Report.** Tell the user which packages are missing and show the command.
3. **Ask.** "Do you want me to install these, or will you install them?"
4. **Install only after an explicit yes.** Then run the template again to confirm.

Required packages block the run. Optional packages (Prophet in `advanced.py`)
only skip their section.

## Import name and pip name

| Import | pip |
|---|---|
| `sklearn` | `scikit-learn` |
| `statsforecast` | `statsforecast` |
| `mlforecast` | `mlforecast` |
| `hierarchicalforecast` | `hierarchicalforecast` |
| `utilsforecast` | `utilsforecast` |
| `coreforecast` | `coreforecast` (installed with statsforecast) |
| `pyreadr` | `pyreadr` (book datasets only) |

## Versions the templates were run with

Python 3.13, statsforecast 2.1.1, mlforecast 1.1.0, hierarchicalforecast 1.5.3,
utilsforecast 0.2.17, coreforecast 0.0.19, statsmodels 0.15.0, pandas 2.3.3,
numpy 2.5.4, scikit-learn 1.9.1, prophet 1.5.0, pyreadr (latest on 2026-10-21).

## Install command

```bash
pip install statsforecast mlforecast hierarchicalforecast utilsforecast statsmodels \
    pandas numpy matplotlib scikit-learn pyreadr
pip install prophet   # optional, advanced.py only
```

## Template files

Copy `fpp_data.py` and `fc_checks.py` next to any template you run. Set
`FC_OUT` for the output folder and `FPP_DATA_CACHE` for the data cache.
