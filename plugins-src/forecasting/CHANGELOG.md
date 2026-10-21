# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: semantic.

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
