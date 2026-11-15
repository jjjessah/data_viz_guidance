#!/usr/bin/env python3
"""Draw a horizontal bar chart of how New York workers got to work in 2016.

Source: U.S. Census Bureau
Dataset: American Community Survey (ACS) 1-year estimates, 2016
Table: DP03, Selected Economic Characteristics (data profile)
API: https://api.census.gov/data/2016/acs/acs1/profile
Geography: New York state (state:36)
Universe: workers 16 years and over (DP03_0018E)

The six bars follow the categories and order in Grids Example 1,
"Driving Alone is Still Popular":

    Drove alone:            DP03_0019 (car, truck, or van, drove alone)
    Public transportation:  DP03_0021 (excluding taxicab)
    Carpool:                DP03_0020 (car, truck, or van, carpooled)
    Walked:                 DP03_0022
    Worked at home:         DP03_0024
    Other means:            DP03_0023

Each variable has an estimate (E), its margin of error (M), a percent
(PE), and the margin of error of the percent (PM). Margins of error are
at the 90 percent confidence level.

The program saves two versions of the chart:

    ny-commute-2016-gridlines.png     thin gray vertical gridlines at
                                      every 10 percent, drawn behind the
                                      bars, as in Example 1
    ny-commute-2016-recommended.png   no gridlines and no percent axis;
                                      the direct value labels carry the
                                      values (recommended for this chart)

Every bar has a direct value label, so readers do not need the
gridlines to read the values. The gridline version shows how to style
gridlines when a chart does need them.

The program uses acs_dp03_ny_2016_commute.csv when that file is present
so it can run offline without a key. It calls the API if the file is
missing, or if --refresh is passed. The Census Data API asks for a key
on each request. Set the key only in the environment, never in this file
or the saved table:

    export CENSUS_API_KEY=API_KEY_VALUE
    python3 examples/family_d/make_ny_commute_grid.py --refresh
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "acs_dp03_ny_2016_commute.csv"
OUT_DIR = HERE.parents[1] / "assets" / "family-d"
GRID_PATH = OUT_DIR / "ny-commute-2016-gridlines.png"
RECOMMENDED_PATH = OUT_DIR / "ny-commute-2016-recommended.png"
API_URL = "https://api.census.gov/data/2016/acs/acs1/profile"
STATE = "36"

TOTAL_CODE = "DP03_0018"
# Chart order, top to bottom, as in Example 1.
CATEGORIES = (
    ("Drove alone", "DP03_0019"),
    ("Public transportation", "DP03_0021"),
    ("Carpool", "DP03_0020"),
    ("Walked", "DP03_0022"),
    ("Worked at home", "DP03_0024"),
    ("Other means", "DP03_0023"),
)

# Contrast against white: bars 5.4:1, axis line 4.5:1, and gridlines
# 3.0:1 (at least 3:1 for graphics); text 15.9:1 and 7.5:1 (at least
# 4.5:1). Gridlines are thin so the bars stay primary; direct labels and
# the data table carry the values.
BAR_COLOR = "#00758A"
TEXT_COLOR = "#222222"
MUTED_TEXT = "#555555"
GRID_COLOR = "#949494"
AXIS_COLOR = "#767676"


def _clean_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def load_csv(path: Path) -> list[dict]:
    rows = []
    for raw in _clean_rows(path):
        rows.append(
            {
                "mode": raw["mode"],
                "variable": raw["variable"],
                "estimate": int(raw["estimate"]),
                "estimate_moe": int(raw["estimate_moe"]),
                "percent": float(raw["percent"]) if raw["percent"] else None,
                "percent_moe": float(raw["percent_moe"]) if raw["percent_moe"] else None,
            }
        )
    return rows


def fetch_api() -> list[dict]:
    codes = [TOTAL_CODE] + [code for _, code in CATEGORIES]
    fields = ["NAME"]
    for code in codes:
        fields += [f"{code}E", f"{code}M", f"{code}PE", f"{code}PM"]
    params = {"get": ",".join(fields), "for": f"state:{STATE}"}
    safe_query = urllib.parse.urlencode(params)
    key = os.environ.get("CENSUS_API_KEY")
    if key:
        params["key"] = key
    request = urllib.request.Request(
        f"{API_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "data-viz-guidance-example"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        hint = "" if key else " Set CENSUS_API_KEY in the environment."
        raise RuntimeError(f"Census API request failed ({safe_query}): {exc}.{hint}") from exc
    record = dict(zip(payload[0], payload[1]))
    labels = [("Workers 16 years and over", TOTAL_CODE)] + list(CATEGORIES)
    rows = []
    for mode, code in labels:
        # The total row has no percent: the API repeats the count in PE
        # and returns an annotation code in PM.
        is_total = code == TOTAL_CODE
        rows.append(
            {
                "mode": mode,
                "variable": code,
                "estimate": int(record[f"{code}E"]),
                "estimate_moe": int(record[f"{code}M"]),
                "percent": None if is_total else float(record[f"{code}PE"]),
                "percent_moe": None if is_total else float(record[f"{code}PM"]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("# U.S. Census Bureau, 2016 American Community Survey 1-Year Estimates, Table DP03\n")
        handle.write(f"# Census Data API: {API_URL}\n")
        handle.write("# Geography: New York (state:36). Universe: workers 16 years and over.\n")
        handle.write("# Margins of error are at the 90 percent confidence level. Leave API keys out of this file.\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=["mode", "variable", "estimate", "estimate_moe", "percent", "percent_moe"],
        )
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for field in ("percent", "percent_moe"):
                out[field] = "" if row[field] is None else f"{row[field]:.1f}"
            writer.writerow(out)


def load_rows(refresh: bool) -> list[dict]:
    if CSV_PATH.exists() and not refresh:
        return load_csv(CSV_PATH)
    try:
        rows = fetch_api()
    except RuntimeError as exc:
        if CSV_PATH.exists():
            print(f"API request failed; using the saved table. ({exc})")
            return load_csv(CSV_PATH)
        raise
    write_csv(CSV_PATH, rows)
    return rows


def draw(rows: list[dict], gridlines: bool, out_path: Path) -> None:
    by_code = {row["variable"]: row for row in rows}
    total = by_code[TOTAL_CODE]["estimate"]
    names = [name for name, _ in CATEGORIES]
    values = [by_code[code]["percent"] for _, code in CATEGORIES]

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(10, 5.4))
    positions = range(len(names))
    ax.barh(positions, values, height=0.62, color=BAR_COLOR, zorder=3)
    ax.invert_yaxis()

    # Both versions use the full 0 to 100 percent scale so bar lengths match.
    ax.set_xlim(0, 100)
    if gridlines:
        # Gridlines: regular 10 percent steps, gray at 3:1, thin, behind the bars.
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
        ax.set_axisbelow(True)
        ax.grid(axis="x", color=GRID_COLOR, linewidth=0.5, zorder=0)
    else:
        # Recommended: the value labels carry the values, so the percent
        # axis and gridlines are left out.
        ax.set_xticks([])
    ax.grid(axis="y", visible=False)

    for pos, value in zip(positions, values):
        ax.text(value + 0.8, pos, f"{value:.1f}%", va="center", ha="left",
                fontsize=11, color=TEXT_COLOR, zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    ax.set_yticks(list(positions))
    ax.set_yticklabels(names, fontsize=11, color=TEXT_COLOR)
    ax.tick_params(axis="x", labelsize=10, colors=TEXT_COLOR, length=0)
    ax.tick_params(axis="y", length=0)
    if gridlines:
        ax.set_xlabel("Percent of workers 16 years and over", fontsize=10, color=TEXT_COLOR)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)

    fig.text(0.02, 0.955, "Means of Transportation to Work in New York, 2016",
             fontsize=15, fontweight="bold", color=TEXT_COLOR, ha="left")
    subtitle = "Driving alone is still popular"
    if not gridlines:
        subtitle += " (percent of workers 16 years and over)"
    fig.text(0.02, 0.905, subtitle, fontsize=12, color=MUTED_TEXT, ha="left")
    fig.text(
        0.02, 0.025,
        f"Source: U.S. Census Bureau, 2016 American Community Survey 1-Year Estimates, Table DP03.\n"
        f"New York state, {total:,} workers 16 years and over.",
        fontsize=9, color=MUTED_TEXT, ha="left", va="bottom", linespacing=1.4,
    )
    fig.subplots_adjust(top=0.85, bottom=0.19 if gridlines else 0.14, left=0.2, right=0.97)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, facecolor="white")
    plt.close(fig)


def main() -> None:
    rows = load_rows("--refresh" in sys.argv)
    for row in rows:
        line = f"{row['mode']}: {row['estimate']:,} (+/-{row['estimate_moe']:,})"
        if row["percent"] is not None:
            line += f", {row['percent']:.1f}% (+/-{row['percent_moe']:.1f})"
        print(line)
    draw(rows, gridlines=True, out_path=GRID_PATH)
    draw(rows, gridlines=False, out_path=RECOMMENDED_PATH)
    print(f"Saved {GRID_PATH}")
    print(f"Saved {RECOMMENDED_PATH}")


if __name__ == "__main__":
    main()
