---
name: forecast-exercises
description: Generates forecasting practice exercises on simulated series with known structure (ETS, ARIMA, intermittent demand, hierarchy, regression with ARIMA errors) and grades the learner's answers against the true model. Use when the user says "forecasting exercise", "practice forecasting", "quiz me", "give me a time series to practise on" or "teach me exponential smoothing with an example". Not for real data projects, and it never reuses the book's exercises.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast exercises

You write new exercises where the right answer is known, so the learner gets
feedback against the truth, not against an opinion.

## Before you begin

1. Read `../../references/lessons.md`.
2. Read `../../references/dgp-library.md` and `../../templates/simulate.py`.
3. Read the method skill and diagnostics file for the chosen topic.

## Stage 1: Setup

Ask the topic and the level (new to forecasting, or knows the basics). Pick one
concept per exercise: reading an ACF, choosing d, damped versus undamped trend,
bottom-up versus MinT, Croston versus naive, ex-ante versus ex-post.

## Stage 2: Diagnostics (design check)

Choose a generator and parameters that make the concept visible: phi near 0.9 to
show autocorrelated errors, gamma large to show an evolving season, a long enough
series for the method. Fix the seed. Run the generator and check that the effect
is visible in the output before giving the exercise. Why: an exercise whose
answer is hidden by noise teaches the wrong lesson.

## Stage 3: Implementation (write the exercise)

Give the learner:

1. The code that creates the data (`simulate.py` call with the seed), not the
   parameters.
2. A decision to make: which model, which differencing, which reconciliation, what
   forecast horizon is credible, what the interval means.
3. The skill and template to use.

Keep the answer key separate: true model, true parameters, the expected choice
and why, and the cross-validated accuracy of the true model against the benchmark.
Never copy or reword an exercise from the book.

## Stage 4: Evaluation and robustness (grading)

Grade against the truth:

- Model choice: right family and form?
- Parameters: within a sensible distance of the truth for this series length?
- Process: benchmark fitted, residuals checked, cross-validation used?
- Interpretation: intervals and caveats stated?

Run the learner's code if given. Point to the exact step that went wrong.

## Verification gate

Before grading: you ran the generator and the learner's code (or your own
solution), and you can quote the true parameters and the estimates.

## Stage 5: Interpretation and handoff

Give the grade per criterion, one thing done well, one thing to fix, and a next
exercise one step harder. Point to the method skill for the concept.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Showing the true parameters in the exercise | Nothing left to learn | Answer key separate |
| Noise hides the concept | Wrong lesson learnt | Check the effect is visible first |
| Copying a book exercise | Copyright; the book has its own | Write new ones with `simulate.py` |
| Grading only the final number | Misses process errors | Grade choice, process and interpretation |
| Too many concepts at once | Feedback is unclear | One concept per exercise |

## Book sections

The exercises practise the methods of FPP3 chapters 2 to 13. R:
`https://otexts.com/fpp3/`. Python edition: `https://otexts.com/fpppy/`. URLs
unverified (see `NOTES.md`).
