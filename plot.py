"""Plot mean net worth of families with children, by education of the
reference person, 1989-2025, as a black-and-white journal figure.
Reads data/networth_by_educ.csv (see get_data.py).

Output: figures/mean_networth_by_educ.png and .pdf
"""

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

DATA = Path("data/networth_by_educ.csv")
OUT = Path("figures/mean_networth_by_educ")

# Series are told apart by line style and marker, not color.
SERIES = {
    "college": dict(label="College degree", ls="-", marker="o", mfc="black"),
    "hs_or_less": dict(label="High school or less", ls="--", marker="s", mfc="white"),
}

CAPTION = ("Figure 1. Mean net worth of families with children, by education of the "
           "reference person, 1989–2025 (thousands of 2025 dollars).")
NOTE = ("Note: Families with children are those with at least one child in the household "
        "(KIDS > 0). “High school or less” combines reference persons with no high school "
        "diploma and those with a diploma or GED; families whose reference person has some "
        "college are excluded. Estimates pool all five implicates using survey weights. "
        "Source: Board of Governors of the Federal Reserve System, Survey of Consumer "
        "Finances, Summary Extract Public Data, 1989–2025.")

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 10,
})


def main():
    df = pd.read_csv(DATA)
    wide = df.pivot(index="year", columns="group", values="mean_networth") / 1e3

    fig, ax = plt.subplots(figsize=(6.5, 5.2))

    for key, style in SERIES.items():
        s = wide[key]
        ax.plot(s.index, s.values, color="black", lw=1.2, ms=5, mec="black", mew=1, **style)
        for x in (s.index[0], s.index[-1]):
            ax.annotate(f"{s[x]:,.0f}", (x, s[x]), xytext=(0, 7), textcoords="offset points",
                        ha="center", fontsize=8.5)

    ax.set_xticks(wide.index)
    ax.set_xticklabels(wide.index, rotation=45)
    ax.set_xlim(wide.index.min() - 1, wide.index.max() + 1)
    ax.set_ylim(0, 2600)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylabel("Mean net worth (thousands of 2025 dollars)")
    ax.set_xlabel("Survey year")
    ax.tick_params(direction="out", length=3, width=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper left", frameon=False)

    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.36)
    fig.text(0.02, 0.2, CAPTION, fontsize=10, weight="bold", va="top", wrap=True)
    fig.text(0.02, 0.14, "\n".join(textwrap.wrap(NOTE, 135)), fontsize=8, va="top")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT.with_suffix(f".{ext}"), dpi=300)
    print(f"wrote {OUT}.png and {OUT}.pdf")


if __name__ == "__main__":
    main()
