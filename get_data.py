"""Download the SCF Summary Extract files (1989-2025) and compute weighted
net worth for families with children, by education of the reference person.

Source: Federal Reserve Board, Survey of Consumer Finances, Summary Extract
Public Data (scfpYYYYexcel.zip). As of the 2025 release (Oct 9, 2026) every
year's extract has dollar variables inflation-adjusted to 2025 dollars.

Each family appears as 5 rows (implicates). Pooling all rows with WGT
reproduces the Fed's published estimates.

Output: data/networth_by_educ.csv
"""

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

YEARS = list(range(1989, 2026, 3))  # 1989, 1992, ..., 2025
URL = "https://www.federalreserve.gov/econres/files/scfp{year}excel.zip"
RAW = Path("data/raw")
OUT = Path("data/networth_by_educ.csv")

# Household ID is YY1 in most years but XX1 in 1989.
COLS = ["YY1", "XX1", "WGT", "EDCL", "KIDS", "NETWORTH"]

# EDCL: 1 = no high school diploma, 2 = high school diploma or GED,
#       3 = some college, 4 = college degree.
GROUPS = {
    "hs_or_less": [1, 2],
    "college": [4],
}


def download(year):
    """Return the extract CSV for a year, downloading it if not cached."""
    path = RAW / f"SCFP{year}.csv"
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL.format(year=year), headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
            path.write_bytes(z.read(name))
        print(f"downloaded {year}")
    df = pd.read_csv(path, usecols=lambda c: c.upper() in COLS).rename(columns=str.upper)
    return df.rename(columns={"XX1": "YY1"})


def weighted_median(x, w):
    order = np.argsort(x)
    x, w = x[order], w[order]
    cum = np.cumsum(w)
    return x[np.searchsorted(cum, cum[-1] / 2)]


def main():
    rows = []
    for year in YEARS:
        df = download(year)
        with_kids = df[df["KIDS"] > 0]
        for group, codes in GROUPS.items():
            g = with_kids[with_kids["EDCL"].isin(codes)]
            rows.append({
                "year": year,
                "group": group,
                "mean_networth": np.average(g["NETWORTH"], weights=g["WGT"]),
                "median_networth": weighted_median(g["NETWORTH"].to_numpy(), g["WGT"].to_numpy()),
                "share_of_families_with_kids": g["WGT"].sum() / with_kids["WGT"].sum(),
                "n_families": g["YY1"].nunique(),
            })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, float_format="%.4f")
    print(f"wrote {OUT}")
    print(out.pivot(index="year", columns="group", values="mean_networth").div(1e3).round(1))


if __name__ == "__main__":
    main()
