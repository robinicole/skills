# Plan: Australian tourism hierarchy (written by forecast-hierarchical, no planner run)

Decision: tourism budget allocation by state. Data: `tourism` (FPP3), quarterly trips (thousands), 1998 Q1 to 2017 Q4, 304 Region x Purpose series.
Horizon: 8 quarters (2018 Q1 to 2019 Q4). Levels wanted: Total, State, Purpose; all must add up.
Choices made without asking: grouped structure (Purpose crosses geography), ETS base model, point plus 80/95% intervals.
Missing: explore.md and baselines.md were not produced. Only the seasonal-naive benchmark inside the template was run.
