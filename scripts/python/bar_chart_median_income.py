"""
Create a horizontal bar chart of median household income by state.

Data: ../data/median_household_income_by_state.csv
Source expectation: ACS table B19013 (refresh from data.census.gov for production)

Required packages:
  pip install pandas matplotlib
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "median_household_income_by_state.csv"
OUT_DIR = ROOT / "assets" / "examples"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUT_DIR / "bar_chart_median_income_top15.png"


def main() -> None:
    df = pd.read_csv(DATA)
    top = df.nlargest(15, "median_household_income").sort_values(
        "median_household_income", ascending=True
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top["state"], top["median_household_income"], color="#005ea2")
    ax.set_xlabel("Median household income (USD)")
    ax.set_title(
        "Highest median household income among states\nACS B19013 demo file"
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.grid(True, color="#d9e2ec", linewidth=0.8)
    ax.set_axisbelow(True)

    fig.text(
        0.01,
        0.01,
        "Source: ACS B19013 demo file in repository data/. Refresh from data.census.gov for official estimates.",
        fontsize=8,
        color="#4a5568",
    )
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
