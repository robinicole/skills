# Judgmental adjustment log

Use this log for every change a person makes to a statistical forecast, and for
every forecast made by judgment alone. Keep it next to the forecasts. Score it
with the same accuracy measures as the model (see `references/evaluation.md`).

Book: FPP3 chapter 6, judgmental adjustments (R: https://otexts.com/fpp3/judgmental-adjustments.html
[unverified URL]; Python edition chapter 6 [unverified URL]).

## Before you adjust

Answer all four. If any answer is "no", do not adjust.

1. Is there information the model cannot see (a promotion, a strike, a new contract)?
2. Is the effect large compared with the usual forecast error?
3. Can you write the reason in one sentence that someone else can check later?
4. Is the adjustment about the forecast, not about a target or a budget?

## Log

| ID | Date made | Series | Forecast origin | Forecast horizon | Model forecast | Adjusted forecast | Change (%) | Reason (one sentence) | Source of the information | Author | Actual | Model error | Adjusted error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | | | | |

## Review (every quarter)

- Mean absolute error of model forecasts against adjusted forecasts, for the
  adjusted rows only.
- Same comparison split by size of change (under 5%, 5 to 20%, over 20%).
- Share of adjustments upward. A share far from half suggests optimism or
  pressure from targets.
- Stop the kinds of adjustment that do not improve accuracy.
