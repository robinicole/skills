"""Load the datasets of Forecasting: Principles and Practice (3rd ed) in Python.

Not from the book: the book's R edition loads these from the R packages
tsibbledata, tsibble and fpp3. This module downloads the same .rda files from
the packages' public GitHub repositories, at pinned commits, reads them with
pyreadr and converts the time index. Files are cached in FPP_DATA_CACHE
(default ~/.cache/fpp_data). The data are GPL-3 and are not stored in this repo.

Usage:
    from fpp_data import load, to_long
    raw = load("aus_production")                    # wide frame, one row per period
    df = to_long(raw, y="Beer")                      # unique_id, ds, y
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import pandas as pd

_REPOS = {
    "tsibbledata": "https://raw.githubusercontent.com/tidyverts/tsibbledata/"
                   "ccfcb321bb4f0e12b7287f5a8f752097e35a20a5/data/",
    "fpp3": "https://raw.githubusercontent.com/robjhyndman/fpp3/"
            "12beccaaf4f2f2d578d6da76d3fe314f689f9c6f/data/",
    "tsibble": "https://raw.githubusercontent.com/tidyverts/tsibble/"
               "720cba7c8ab2ddba84cd5db281b45b12bf3b361c/data/",
}

# name -> (package, index column, index kind, pandas frequency, key columns)
# index kinds: "days" = days since 1970-01-01 (tsibble yearweek/yearmonth/yearquarter),
#              "year" = integer year, "utc_melbourne" = UTC timestamps shown in Melbourne time
DATASETS = {
    "aus_production": ("tsibbledata", "Quarter", "days", "QS", []),
    "aus_retail": ("tsibbledata", "Month", "days", "MS", ["State", "Industry"]),
    "aus_livestock": ("tsibbledata", "Month", "days", "MS", ["Animal", "State"]),
    "PBS": ("tsibbledata", "Month", "days", "MS", ["Concession", "Type", "ATC1", "ATC2"]),
    "global_economy": ("tsibbledata", "Year", "year", "YS", ["Country"]),
    "pelt": ("tsibbledata", "Year", "year", "YS", []),
    "vic_elec": ("tsibbledata", "Time", "utc_melbourne", "30min", []),
    "tourism": ("tsibble", "Quarter", "days", "QS", ["Region", "State", "Purpose"]),
    "us_change": ("fpp3", "Quarter", "days", "QS", []),
    "us_employment": ("fpp3", "Month", "days", "MS", ["Series_ID"]),
    "us_gasoline": ("fpp3", "Week", "days", "W-MON", []),
    "souvenirs": ("fpp3", "Month", "days", "MS", []),
    "insurance": ("fpp3", "Month", "days", "MS", []),
    "canadian_gas": ("fpp3", "Month", "days", "MS", []),
    "aus_arrivals": ("fpp3", "Quarter", "days", "QS", ["Origin"]),
    "aus_airpassengers": ("fpp3", "Year", "year", "YS", []),
    "boston_marathon": ("fpp3", "Year", "year", "YS", ["Event"]),
    "prices": ("fpp3", "year", "year", "YS", []),
    "guinea_rice": ("fpp3", "Year", "year", "YS", []),
}


def _cache_dir() -> Path:
    d = Path(os.environ.get("FPP_DATA_CACHE", Path.home() / ".cache" / "fpp_data"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def load(name: str) -> pd.DataFrame:
    """Return the dataset as a pandas frame with the time index converted.

    The index column keeps its book name (Quarter, Month, Year, ...) and holds
    pandas Timestamps. Key and measure columns are unchanged.
    """
    import pyreadr

    if name not in DATASETS:
        raise KeyError(f"{name!r} is not in fpp_data.DATASETS: {sorted(DATASETS)}")
    pkg, idx, kind, _, _ = DATASETS[name]
    path = _cache_dir() / f"{name}.rda"
    if not path.exists():
        urllib.request.urlretrieve(_REPOS[pkg] + f"{name}.rda", path)
    df = next(iter(pyreadr.read_r(str(path)).values())).copy()
    if kind == "days":
        df[idx] = pd.Timestamp("1970-01-01") + pd.to_timedelta(df[idx].astype("int64"), unit="D")
    elif kind == "year":
        df[idx] = pd.to_datetime(df[idx].astype("int64").astype(str), format="%Y")
    elif kind == "utc_melbourne":
        df[idx] = (pd.to_datetime(df[idx]).dt.tz_localize("UTC")
                   .dt.tz_convert("Australia/Melbourne").dt.tz_localize(None))
    for col in df.columns:
        if str(df[col].dtype) == "category":
            df[col] = df[col].astype(str)
    return df.sort_values(DATASETS[name][4] + [idx]).reset_index(drop=True)


def freq(name: str) -> str:
    """Pandas frequency string to pass to StatsForecast(freq=...)."""
    return DATASETS[name][3]


def to_long(df: pd.DataFrame, y: str, name: str | None = None,
            keys: list[str] | None = None, time: str | None = None) -> pd.DataFrame:
    """Convert a loaded dataset to the Nixtla long format unique_id, ds, y.

    keys default to the dataset's tsibble keys; unique_id joins them with "/".
    A series with no keys gets unique_id equal to the measure name.
    """
    if name is not None:
        _, idx, _, _, k = DATASETS[name]
        time = time or idx
        keys = k if keys is None else keys
    if time is None:
        raise ValueError("pass name= or time=")
    keys = keys or []
    out = df[[*keys, time, y]].rename(columns={time: "ds", y: "y"})
    if keys:
        out.insert(0, "unique_id", out[keys].astype(str).agg("/".join, axis=1))
        out = out.drop(columns=keys)
    else:
        out.insert(0, "unique_id", y)
    return out.sort_values(["unique_id", "ds"]).reset_index(drop=True)
