# Glossary

One term per concept. Every skill and reference uses these words and no synonyms.
The first block follows the guide's own terminology section.

| Term | Meaning | Not |
|---|---|---|
| instance | The thing a prediction is about (a page, a post, a user-query pair) | item, sample |
| label | The answer for a prediction task, from the system or from training data | target (except in code) |
| feature | A property of an instance | signal (except "new sources of signal") |
| feature column | A set of related features (all countries a user may live in) | namespace, field |
| example | An instance with its features and a label | row, record |
| model | A statistical representation of a prediction task, trained on examples | |
| metric | Any number you track; it may or may not be optimized | KPI |
| objective | The one metric the learner optimizes | loss (the loss implements the objective) |
| pipeline | Everything around the learner: logging, building examples, training, export, serving | |
| heuristic | Hand-written logic that makes the decision without a learned model | rule (rules are the guide's 43 rules) |
| policy layer | Simple logic after the model that turns scores into the final decision (filters, boosts, caps) | business rules |
| training-serving skew | Any difference between how the model performs in training and in serving | drift (drift is one cause) |
| holdout | Examples from the training period held back from training | validation set |
| next-day data | Examples from after the training window (rule 33) | test set when it is from the same period |
| freshness | How fast quality drops as the model ages | staleness |
| coverage | Share of examples on which a feature is present | sparsity |
| model delta | Position-weighted symmetric difference between two models' results (rule 24) | |
| calibrated | Average prediction equals average label on a slice | |
| launch | Shipping a model change to users, normally after a live experiment | deploy (deploy can be dark) |
| phase | Before ML, Phase I, II or III as in the guide | stage (stages are the steps inside a skill) |
