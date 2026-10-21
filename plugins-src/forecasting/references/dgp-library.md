# Data-generating processes for exercises

Used by `forecast-exercises` and by the ground-truth check. Functions live in
`templates/simulate.py`. Each returns a long frame (`unique_id, ds, y`) and the
true parameters. Not from the book: the generators are written for this plugin;
the models they simulate are the book's.

| Function | Model | Parameters | What an exercise can test |
|---|---|---|---|
| `ets_aan` | ETS(A,A,N), error-correction form | alpha, beta, level, slope, sigma | Holt versus damped; parameter reading |
| `ets_ana` | ETS(A,N,A) with evolving season | alpha, gamma, m, amplitude, sigma | seasonal naive versus ETS; gamma near 0 |
| `arima` | ARIMA(p,d,q), no constant | ar, ma, d, sigma | differencing, ACF/PACF reading, order selection |
| `intermittent` | Bernoulli occurrence, Poisson size | p_demand, size_mean | Croston family; rate, not count |
| `hierarchy` | Total > A, B > A1, A2, B1, B2 | none | bottom-up versus MinT, coherence |
| `regression_arima_errors` | y = 10 + beta x + AR(1) error | beta, phi, sigma | regression versus dynamic regression; spurious fit |

## How to build an exercise

1. Pick one concept and one generator. State the true structure only in the
   answer key.
2. Choose parameters that make the concept visible (a large gamma to show an
   evolving season; phi near 0.9 to show autocorrelated errors).
3. Set the seed so the answer key is reproducible.
4. Ask the learner for a decision, not only a fit: which model, which forecast
   horizon is credible, what the intervals mean.
5. Grade against the truth: recovered parameters, chosen model, and
   cross-validated accuracy against the benchmark.

## Ground truth

`evals/ground_truth.py` simulates many series from `ets_aan` and `arima` and
checks that the median estimate is within 10% of the truth (0.05 absolute for
values near zero).
