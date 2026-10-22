# The 43 rules, in short

Martin Zinkevich, *Rules of Machine Learning: Best Practices for ML Engineering*,
`https://developers.google.com/machine-learning/guides/rules-of-ml` (page last
updated 2025-08-25, read 2026-10-22). CC BY 4.0. Paraphrased; read the page for the
reasoning and the Google examples.

Section anchors (append to the URL): `#before_machine_learning`,
`#ml_phase_i_your_first_pipeline`, `#your_first_objective`,
`#ml_phase_ii_feature_engineering`,
`#ml_phase_iii_slowed_growth_optimization_refinement_and_complex_models`,
`#related_work`, `#appendix`. Monitoring, human analysis and training-serving skew
have no anchor; link the phase.

The core idea: do ML like a good engineer, not like an ML researcher. Most gains
come from good features, not clever algorithms. Get the pipeline solid end to end,
pick a reasonable objective, add common-sense features simply, and keep the
pipeline solid. Add complexity only when the simple moves run out, because every
bit of complexity slows later launches.

Skill that owns each rule in brackets.

## Before machine learning (`ml-planner`)

1. **Launch without ML if you must.** No data, no ML. A heuristic gets about half
   the gain you hope ML will give. Rank by install rate, block known spammers,
   sort contacts by recency.
2. **Design and implement metrics first.** Log everything before the ML system
   exists: permission is easier to get early, history is there when a question
   comes up, and you learn what moves. Use an experiment framework that buckets
   users and aggregates by experiment. Add a metric whenever you see a problem.
3. **Choose ML over a complex heuristic.** A simple heuristic ships; a complex one
   cannot be maintained. Once you have data and a goal, a learned model is easier
   to update.

## Phase I: your first pipeline (`ml-first-pipeline`)

4. **Keep the first model simple and get the infrastructure right.** The first
   model gives the biggest lift. Decide how examples reach the learner, what good
   and bad mean, and how the model plugs into the product (live scoring or a
   precomputed table). Simple features make wiring bugs visible. A "neutral" first
   launch that does not chase ML gains is fine.
5. **Test the infrastructure apart from the ML.** Encapsulate the learning part.
   Check that data reaches the learner (feature columns populated, stats match
   another path) and that a model scores the same in training and serving. Be able
   to serve a fixed model.
6. **Watch for dropped data when you copy a pipeline.** Copied pipelines carry
   filters meant for the old use (old posts dropped, only seen items logged, so
   no negatives for unseen ones). Mixed sources need a feature that names the
   source.
7. **Turn heuristics into features, or apply them outside the model.** Options:
   preprocess with the heuristic (block a blacklisted sender), use its score as a
   feature (raw first), feed its raw inputs as features, or change the label
   (downloads times star rating). Weigh the complexity each adds.

### Monitoring (`ml-monitoring`)

Alerts must be actionable; keep a dashboard.

8. **Know the freshness your system needs.** Measure quality of a model that is a
   day, a week, a quarter old. Ads models need daily updates; some search models
   degrade within a month. Freshness changes as feature columns change.
9. **Detect problems before exporting a model.** Sanity-check on held-out data
   (for example AUC) and block the export on failure. A bad unexported model is an
   email; a bad live model is a page.
10. **Watch for silent failures.** A joined table that stops updating decays the
    model quietly. One stale table, refreshed after six months, gave 2% on
    installs; a feature's coverage fell from 90% to 60% unnoticed. Track data
    statistics and look at the data.
11. **Give feature columns owners and documentation.** Who made it, who keeps it,
    what it is, where it comes from, why it should help.

### Your first objective (`ml-first-pipeline`, objective choice in `ml-planner`)

The objective is the one number the learner optimizes; metrics are everything you
measure.

12. **Do not overthink the objective you optimize directly.** Early on, metrics
    rise together. Keep it simple. If the objective goes up and you still decide
    not to launch, the objective is wrong.
13. **Pick a simple, observable, attributable first objective.** Click, download,
    share, reply, rating, spam flag. Not next-day visits, session length or DAU at
    first. Never ask the model for happiness or company health; use proxies and
    human judgment. Put final ranking logic in a simple policy layer.
14. **Start with an interpretable model.** Linear, logistic and Poisson regression
    give probabilities or expected values, and they are calibrated: on any slice
    defined by a binary feature, the average prediction equals the average label
    (no regularization, converged). That makes bugs visible. Judge by the decision
    the model drives, not by likelihood.
15. **Keep spam filtering and quality ranking apart in a policy layer.** Quality
    ranking assumes good-faith content; spam is adversarial and needs fast
    updates, simple rules (drop posts with more than three spam votes) and
    creator reputation. Remove spam from quality training data. Racy content is a
    third, separate concern.

## Phase II: feature engineering (`ml-features`)

Starts once an end-to-end system with unit and system tests is live and metrics
still rise.

16. **Plan to launch and iterate.** Expect a launch per quarter or more for years.
    Make it cheap to add, remove and recombine features and to run two or three
    copies of the pipeline side by side. Do not agonise over feature 16 of 35.
17. **Start with directly observed features, not learned ones.** Features from an
    external system (clusters, embeddings) have their own objective and can change
    meaning when that system updates. Deep and factored models are nonconvex, so
    run-to-run noise hides real changes. Build a non-deep baseline first.
18. **Use content features that generalise across contexts.** Signals gathered
    elsewhere (shares, watches, ratings in another surface) let new items enter.
    That is not personalisation: first learn whether people like the item here,
    then who likes it more.
19. **Use very specific features when you have the data.** Millions of simple
    features beat a few complex ones. IDs help head queries. Many sparse features
    are fine if together they cover over 90% of examples; regularization removes
    the ones that fire too rarely.
20. **Combine features in human-understandable ways.** Discretize continuous
    features (quantile buckets get most of the value) and cross feature columns.
    Crosses of three or more columns need a lot of data and overfit easily.
21. **Weights you can learn scale with data.** About 1,000 examples: a dozen
    engineered features (TF-IDF, dot products). About a million: feature
    intersections with regularization and selection. Billions: crosses up to about
    ten million features.
22. **Delete features you no longer use.** They are debt. Check coverage: a
    feature on 8% of users helps little; one on 1% of examples can still matter if
    90% of those are positive. You can add a feature back later.

### Human analysis of the system (`ml-error-analysis`)

23. **You are not a typical end user.** Dogfood to catch obvious breakage, then
    test anything near launch with paid raters or a live experiment. Insiders have
    confirmation bias and cost a lot. Use personas and usability tests.
24. **Measure the delta between models.** Before users see it, run old and new on
    sample queries through the full system and compute the position-weighted
    symmetric difference. Small delta: an experiment will show little. Large
    delta: inspect the queries that moved. A model against itself must give
    (close to) zero, or the system is unstable.
25. **Utilitarian performance beats predictive power.** What counts is the
    decision: final ranking quality, precision above the spam cutoff. If log loss
    improves and the product gets worse, find another feature; if it keeps
    happening, revisit the objective.
26. **Find patterns in the errors and turn them into features.** Look at false
    positives, false negatives, and positives ranked below negatives. A feature
    only helps where the model sees an error under its own objective. Add a dozen
    candidate features (several length buckets) rather than guessing one.
27. **Quantify undesirable behaviour.** Turn complaints into a rated metric (human
    labels on the head queries). Measure first, optimize second.
28. **Same short-term behaviour does not mean same long-term behaviour.** A model
    keyed on doc ID by query matched production in A/B tests, launched, and never
    surfaced new items. Long-term effects show only on data gathered while the
    model is live.

### Training-serving skew (`ml-skew`)

Skew has three causes: training and serving handle data differently, data change
between training and serving, and feedback loops between the model and what it
sees. Monitor it explicitly.

29. **Log the features you use at serving and train on that log.** At least for a
    sample. Teams that did it got quality gains and less code.
30. **Importance-weight sampled data; do not drop it arbitrarily.** Sampled at 30%,
    an example gets weight 10/3. Calibration survives. Data never shown to users
    can be dropped.
31. **A table joined at training and at serving may have changed in between.**
    Log the joined values at serving. If the table changes slowly, hourly or daily
    snapshots get close.
32. **Reuse code between training and serving.** Put the joined request data in
    one readable, testable object and convert it to the learner's format with one
    shared function. Do not use two languages.
33. **Train on data up to a date, test on data after it.** That mirrors
    production. Expect somewhat worse results; average rates move day to day, AUC
    should stay close.
34. **For filtering, trade a little short-term performance for clean data.** Users
    never see what the filter blocks, so their flags are biased. Let a held-out
    slice (say 1% of traffic) through unfiltered and label it: a filter blocking
    75% of negatives still blocks at least 74%. Breaks down above about 95% blocked.
    For measuring serving quality alone, 0.1% or less, about 10,000 examples, is
    enough.
35. **Ranking has built-in skew.** A big ranking change changes the data the model
    will see. Regularize features that span many queries more than per-query ones,
    allow only positive weights, and avoid document-only features.
36. **Avoid feedback loops with position.** Train with position features so the
    model learns position bias, serve every candidate with the same default
    position, and keep position separate (additive), never crossed with document
    features.
37. **Measure skew in three gaps.** Training versus holdout (always there, not
    always bad); holdout versus next-day (tune regularization for next-day; a big
    drop means time-sensitive features); next-day versus live (should be zero; a
    gap is an engineering bug).

## Phase III: slowed growth, refinement, complex models (`ml-plateau`)

Signs: monthly gains shrink and metrics start trading off. The rules here are
less settled; each team finds its way.

38. **Do not add features when the objective is the problem.** If launches stall
    because the objective misses the product goal, change the objective or the
    goal (for example, optimize clicks but decide launches partly on raters).
39. **Launch decisions are a proxy for long-term product goals.** An install model
    that raised installs but cut DAU by 5% did not launch. Engagement, 1- and
    30-day actives, revenue, advertiser ROI are all proxies. Easy launches are the
    ones where nothing gets worse. Teams resist trades between metrics (1M DAU and
    $4M/day versus 2M DAU and $2M/day); multi-objective learning with lower-bound
    constraints helps a little. No metric says where the product will be in five
    years.
40. **Keep ensembles simple.** A model is either an ensemble over other models'
    outputs or a base model over features, never both. The ensemble must be
    monotone in each base score, and base models should be interpretable and
    calibrated.
41. **At a plateau, add new kinds of information, not refinements.** Several
    quarters below 1% gain means build infrastructure for different signals: user
    history over day, week, year; other products; knowledge graphs; deep learning.
    Lower ROI expectations and weigh gain against complexity.
42. **Diversity, personalization and relevance are less tied to popularity than
    you think.** Popularity metrics (clicks, watch time, shares) will often give
    those features low or negative weight. Add them in post-processing; if
    long-term metrics rise, value them on their own and change the objective.
43. **Friends carry across products; interests do not.** Connection strength
    transfers between products. Personalization features across products mostly
    fail; raw cross-product data and "is active on the other product" sometimes
    help.
