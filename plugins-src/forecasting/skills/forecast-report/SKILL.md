---
name: forecast-report
description: Compiles a finished forecasting project into a report for a business or a technical reader, covering the decision, data, method, accuracy per forecast horizon against the benchmark, the forecast with prediction intervals, plots and caveats from the audit. Use when the user says "write up the forecast", "forecast report", "summarise the forecast for management", "document the forecast" or "forecast slide". Also use it to turn finished forecasting work into a document for others. Not for running models or auditing them.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later to render figures. Packages listed in references/preflight.md.
---

# Forecast report

You turn the project files into a report. You narrate what was done and found;
you do not invent numbers.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read every file in `docs/forecast-plans/<project>/`: plan, explore, baselines,
   method files, audit, and the scripts and outputs in `analysis/`.
3. Read `../../references/glossary.md`. Use its terms throughout.

## Stage 1: Setup

List what exists and what is missing. Name the skill that fills each gap
(`forecast-baselines` for no benchmark, `forecast-auditor` for no audit). Ask
whether to fill gaps first or report with them stated. If no project folder
exists, interview the user for: decision, data, method, accuracy, forecast, known
limits.

Ask who reads it: **business** (plain language, decision first) or **technical**
(methods, diagnostics, full tables).

## Stage 2: Diagnostics

Every number in the report must trace to a file or to the user. Check:

- The accuracy table has the benchmark row and is per forecast horizon.
- The forecast has its intervals and says whether points are medians or means.
- Audit findings with severity are available; a FATAL finding goes on page one.

## Stage 3: Implementation

Sections, in this order:

1. **Summary**: the forecast in one sentence with its interval, the decision it
   serves, how much better than the benchmark, and the main caveat.
2. **Question and decision**: from the plan.
3. **Data**: series, period, frequency, adjustments, issues found.
4. **Method**: chosen model and why; candidates compared; business mode keeps
   this to a paragraph.
5. **Accuracy**: per forecast horizon against the benchmark, from cross-validation;
   coverage of intervals.
6. **Forecast**: table and plot with 80% and 95% intervals.
7. **Limitations**: audit findings by severity; ex-post accuracy; conditional
   intervals; anything the plan said to watch for.
8. **Monitoring**: how live accuracy will be tracked and when the model is refit.
9. **Appendix**: code, diagnostics plots (technical mode; business mode on request).

Figures: run the plotting code from the templates on the user's data and embed
the PNG. If it fails, include the code and say the figure is pending.

## Stage 4: Evaluation and robustness

- Business mode has no unexplained jargon; technical mode has no simplification
  that changes meaning.
- Intervals appear wherever a forecast number appears.
- Caveats from the audit appear next to the numbers they affect.

## Verification gate

Before saving: all nine sections present (short if needed); every number traced;
audit findings included or the missing audit stated; figures embedded or pending.

## Stage 5: Interpretation and handoff

Save `docs/forecast-plans/<project>/report.md` (or `report-business.md`,
`report-technical.md`). This is the last skill. If the report shows gaps, name the
skill that closes them.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Point forecast without an interval | Hides the uncertainty the decision needs | Interval next to every number |
| Accuracy without the benchmark | "MASE 0.8" means nothing alone | Benchmark row and skill |
| Training fit as accuracy | Overstates accuracy | Cross-validated accuracy |
| Inventing a number | Cannot be traced | Ask, or mark as unavailable |
| Burying a fatal audit finding | Misleads the decision | Page one |
| Mixing terms (horizon, lead time) | Confuses readers | Glossary terms only |

## Book sections

FPP3 1.6 basic steps (the final step: using and evaluating the forecast) and 5.8
to 5.10 (accuracy reporting). R: `https://otexts.com/fpp3/basic-steps.html`,
`accuracy.html`. Python edition: `https://otexts.com/fpppy/` chapters 1 and 5.
URLs checked 2026-10-22.
