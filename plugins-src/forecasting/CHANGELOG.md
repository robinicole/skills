# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: semantic.

## [0.4.0] - 2026-10-22

### Changed

- Merged `forecast-dynamic-regression` into `forecast-regression`, which now covers
  linear regression, regression with ARIMA errors and weekly data. Thirteen skills.
- Book claims, thresholds and section links checked against both editions of the
  book; broken section links replaced.
- `dynamic_regression.py`: deterministic-trend example caps the AR order as the
  Python edition does, and now matches the book.

## [0.3.0] - 2026-10-21

### Changed

- Rebuilt the plugin around *Forecasting: Principles and Practice*. The skills
  `forecast`, `backtest` and `reconcile` are replaced by fourteen skills: a planner,
  explore, baselines, regression, ETS, ARIMA, dynamic regression, hierarchical,
  advanced, practical, judgmental, auditor, report and exercises.

### Added

- Shared references (decision tree, method registry, evaluation, diagnostics per
  method, preflight, lessons, simulation library, glossary).
- Runnable Python templates for every method skill, with a loader for the book's
  datasets.
- Trigger and no-trigger eval cases with a keyword runner and a Claude CLI runner,
  a template runner, and a ground-truth check for ETS and ARIMA.

## [0.2.0]

- Skills `forecast`, `backtest`, `reconcile` (Python, statsforecast).
