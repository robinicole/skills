"""Hierarchical template: hierarchical and grouped series, bottom-up, top-down,
middle-out and MinT reconciliation, coherence check, accuracy at every level.

Book: FPP3 chapter 11 (R: https://otexts.com/fpp3/hierarchical.html [unverified URL];
Python edition chapter 11 [unverified URL]).
Python: hierarchicalforecast (aggregate, HierarchicalReconciliation) on statsforecast ETS.
Run: python hierarchical.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsforecast": "statsforecast", "utilsforecast": "utilsforecast",
                     "hierarchicalforecast": "hierarchicalforecast", "pyreadr": "pyreadr"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

from functools import partial

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.evaluation import evaluate
from hierarchicalforecast.methods import BottomUp, MiddleOut, MinTrace, TopDown
from hierarchicalforecast.utils import aggregate
from statsforecast import StatsForecast
from statsforecast.models import AutoETS, SeasonalNaive
from utilsforecast.losses import mase, rmsse

from fc_checks import out_dir
from fpp_data import load

OUT = out_dir()
LEVELS = [80, 95]
m, h = 4, 8

# %% 1 Data
# Australian domestic overnight trips: quarterly, by State, Region and Purpose.
raw = load("tourism").rename(columns={"Quarter": "ds", "Trips": "y"})
raw["total"] = "Total"                     # aggregate() adds no total by itself
# Strict hierarchy: Total > State > Region (top-down and middle-out need this).
spec_h = [["total"], ["total", "State"], ["total", "State", "Region"]]
# Grouped structure: Purpose crossed with the geography (no single nesting order).
spec_g = [["total"], ["total", "State"], ["total", "Purpose"], ["total", "State", "Purpose"],
          ["total", "State", "Region"], ["total", "State", "Region", "Purpose"]]
raw_h = raw.groupby(["total", "State", "Region", "ds"], as_index=False)["y"].sum()
Yh, Sh, tags_h = aggregate(df=raw_h, spec=spec_h)
Yg, Sg, tags_g = aggregate(df=raw, spec=spec_g)
print({k: len(v) for k, v in tags_g.items()})

# %% 2 Exploration needed for this method
# Check the structure, and look at a few levels: the total is smooth, the bottom is noisy.
fig, ax = plt.subplots(3, 1, figsize=(8, 7))
for a, uid in zip(ax, ["Total", "Total/Victoria", "Total/Victoria/Melbourne"]):
    s = Yh[Yh["unique_id"] == uid]
    a.plot(s["ds"], s["y"]); a.set_title(uid)
fig.tight_layout(); fig.savefig(OUT / "hier_levels.png", dpi=120); plt.close(fig)

# %% 3 Baselines
base_models = [AutoETS(season_length=m, alias="ETS"), SeasonalNaive(season_length=m)]

# %% 4 Model fit
# Train/test: hold out the last h quarters. Base forecasts for EVERY series at
# every level, with fitted values (MinT needs in-sample errors).
def split(Y):
    cut = Y["ds"].sort_values().unique()[-h]
    return Y[Y["ds"] < cut], Y[Y["ds"] >= cut]


def base_forecasts(Y_train):
    sf = StatsForecast(models=base_models, freq="QS", n_jobs=-1)
    fc = sf.forecast(df=Y_train, h=h, level=LEVELS, fitted=True)
    return fc, sf.forecast_fitted_values()


Yh_tr, Yh_te = split(Yh)
Yg_tr, Yg_te = split(Yg)
fch, fith = base_forecasts(Yh_tr)
fcg, fitg = base_forecasts(Yg_tr)

rec_h = HierarchicalReconciliation(reconcilers=[
    BottomUp(), TopDown(method="forecast_proportions"),
    MiddleOut(middle_level="total/State", top_down_method="forecast_proportions"),
    MinTrace(method="ols"), MinTrace(method="wls_struct"), MinTrace(method="mint_shrink")])
Rh = rec_h.reconcile(Y_hat_df=fch, Y_df=fith, S_df=Sh, tags=tags_h)
rec_g = HierarchicalReconciliation(reconcilers=[BottomUp(), MinTrace(method="wls_struct"),
                                                 MinTrace(method="mint_shrink")])
Rg = rec_g.reconcile(Y_hat_df=fcg, Y_df=fitg, S_df=Sg, tags=tags_g,
                     level=LEVELS, intervals_method="normality")

# %% 5 Diagnostics
# Coherence: each aggregate must equal the sum of its children after reconciliation.
S = Sg.set_index("unique_id")
bottom_ids = list(S.columns)
for col in ["ETS", "ETS/MinTrace_method-mint_shrink"]:
    wide = Rg.pivot(index="unique_id", columns="ds", values=col)
    gap = np.abs(S.loc[wide.index].to_numpy() @ wide.loc[bottom_ids].to_numpy() - wide.to_numpy()).max()
    print(f"{col}: largest gap between a series and the sum of its bottom series = {gap:.3f}")

# %% 6 Evaluation with time series cross-validation
# Accuracy per level on scale-free measures (RMSE across levels is dominated by
# the top). One train/test split here; for a decision, repeat over several
# forecast origins with StatsForecast.cross_validation and reconcile each window.
def level_scores(R, Y_te, Y_tr, tags):
    df = Y_te.merge(R, on=["unique_id", "ds"])
    models = [c for c in R.columns if c not in ("unique_id", "ds") and "-lo-" not in c and "-hi-" not in c]
    return evaluate(df=df, tags=tags, models=models, train_df=Y_tr,
                    metrics=[partial(mase, seasonality=m), partial(rmsse, seasonality=m)])


sh = level_scores(Rh, Yh_te, Yh_tr, tags_h)
sg = level_scores(Rg, Yg_te, Yg_tr, tags_g)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
print("Hierarchy, MASE by level:\n", sh[sh["metric"] == "mase"].set_index("level").round(3).T)
print("Grouped, MASE by level:\n", sg[sg["metric"] == "mase"].set_index("level").round(3).T)
sh.to_csv(OUT / "hier_scores_hierarchy.csv", index=False)
sg.to_csv(OUT / "hier_scores_grouped.csv", index=False)

# %% 7 Forecast with prediction intervals and a plot
# Refit on all data and reconcile the final forecasts (grouped structure, MinT).
fc_all, fit_all = base_forecasts(Yg)
final = rec_g.reconcile(Y_hat_df=fc_all, Y_df=fit_all, S_df=Sg, tags=tags_g,
                        level=LEVELS, intervals_method="normality")
col = "ETS/MinTrace_method-mint_shrink"
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
for a, uid in zip(ax, ["Total", "Total/Holiday"]):
    s, f = Yg[Yg["unique_id"] == uid], final[final["unique_id"] == uid]
    a.plot(s["ds"], s["y"], color="black")
    a.plot(f["ds"], f[col], label="MinT")
    a.fill_between(f["ds"], f[f"{col}-lo-95"], f[f"{col}-hi-95"], alpha=0.2)
    a.set_title(uid)
fig.tight_layout(); fig.savefig(OUT / "hier_forecast.png", dpi=120); plt.close(fig)
final.to_csv(OUT / "hier_forecast.csv", index=False)

# %% 8 What to report
# - The structure: levels, number of series per level, hierarchy or grouped.
# - The base model and the reconciliation methods compared.
# - A coherence check after reconciliation.
# - Scale-free accuracy at every level that a decision uses, base against reconciled.
# - Where reconciliation lost accuracy, if anywhere.
# - Reconciled forecasts with intervals and the interval method (normality or bootstrap).
print("Done. Outputs in", OUT)
