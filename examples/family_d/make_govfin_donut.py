#!/usr/bin/env python3
"""Draw donut charts of 2017 state and local government expenditure.

Source: U.S. Census Bureau
Dataset: Annual Survey of State and Local Government Finances
Year: 2017
API: https://api.census.gov/data/timeseries/govslocalfin
Selection: GOVTYPE=001 (state and local combined), United States and Alabama
Amounts: the API reports AMOUNT in thousands of dollars

The eight chart groups follow the legend in the Donut Chart Example 2
screenshot. Each group uses the function total codes below, not education
or utility subtotals:

    Education:          LF0107
    Administration:     LF0180, LF0183, LF0186, LF0189
    Health & Welfare:   LF0123, LF0129, LF0132, LF0135, LF0138
    Parks & Recreation: LF0168
    Public Safety:      LF0153, LF0156, LF0159, LF0162
    Transportation:     LF0141, LF0144, LF0147, LF0150
    Utilities:          LF0199
    Other:              LF0120, LF0165, LF0171, LF0174, LF0177,
                        LF0193, LF0196, and LF0192 (Interest on General Debt)

The donut total is general expenditure (LF0103) plus utility expenditure
(LF0199). With Interest on General Debt in Other, the eight groups sum to
that total.

These figures are the Census Data API vintage retrieved on 2026-11-14.
That vintage does not match the June 2020 dashboard screenshot on the
Donut Chart page: the United States total here is $3,309,381,532,000
against $3,311,141,581,000 in the screenshot, and Alabama is
$43,131,484,000 against $44,974,894,000. The script does not substitute
the screenshot totals.

Set a Census Data API key only in the environment. Do not paste it into
this file:

    export CENSUS_API_KEY=API_KEY_VALUE
    python3 examples/family_d/make_govfin_donut.py

The program uses govslocalfin_2017_expenditure.csv when that file is
present so it can run offline. It calls the API if the file is missing,
or if --refresh is passed. Leave the key out of the program and the
saved table.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "govslocalfin_2017_expenditure.csv"
OUT_PATH = HERE.parents[1] / "assets" / "family-d" / "state-local-spending-2017.png"
API_URL = "https://api.census.gov/data/timeseries/govslocalfin"
YEAR = "2017"
GOVTYPE = "001"

# Function total codes in each Example 2 legend group.
GROUPS = OrderedDict(
    [
        ("Education", ("LF0107",)),
        ("Administration", ("LF0180", "LF0183", "LF0186", "LF0189")),
        ("Health & Welfare", ("LF0123", "LF0129", "LF0132", "LF0135", "LF0138")),
        ("Parks & Recreation", ("LF0168",)),
        ("Public Safety", ("LF0153", "LF0156", "LF0159", "LF0162")),
        ("Transportation", ("LF0141", "LF0144", "LF0147", "LF0150")),
        ("Utilities", ("LF0199",)),
        (
            "Other",
            (
                "LF0120",
                "LF0165",
                "LF0171",
                "LF0174",
                "LF0177",
                "LF0193",
                "LF0196",
                "LF0192",
            ),
        ),
    ]
)
REFERENCE_CODES = ("LF0090", "LF0103", "LF0199")
CODE_TO_GROUP = {
    code: name for name, codes in GROUPS.items() for code in codes
}

# Fills are dark enough to stand apart from a white page, and from each
# other for common kinds of color blindness. Black outlines separate the
# slices. Text in the legend is dark on white.
COLORS = {
    "Education": "#0072B2",
    "Administration": "#E69F00",
    "Health & Welfare": "#D55E00",
    "Parks & Recreation": "#009E73",
    "Public Safety": "#56B4E9",
    "Transportation": "#CC79A7",
    "Utilities": "#332288",
    "Other": "#000000",
}

PLACES = (
    ("United States", "us:*"),
    ("Alabama", "state:01"),
)

# Totals shown on the June 2020 dashboard screenshot (Example 2).
SCREENSHOT_TOTALS = {
    "United States": 3_311_141_581_000,
    "Alabama": 44_974_894_000,
}


def _comment_aware_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        filtered = (line for line in handle if not line.startswith("#"))
        return list(csv.DictReader(filtered))


def load_csv(path: Path) -> list[dict]:
    rows = []
    for raw in _comment_aware_rows(path):
        rows.append(
            {
                "geography": raw["geography"],
                "geo_for": raw["geo_for"],
                "year": raw["year"],
                "govtype": raw["govtype"],
                "agg_desc": raw["agg_desc"],
                "agg_desc_label": raw["agg_desc_label"],
                "amount_thousands": int(raw["amount_thousands"]),
                "amount_dollars": int(raw["amount_dollars"]),
                "category": raw.get("category", ""),
                "role": raw.get("role", ""),
            }
        )
    return rows


def _api_rows(geo_for: str, geography: str) -> list[dict]:
    params = {
        "get": "AGG_DESC,AGG_DESC_LABEL,GOVTYPE,AMOUNT",
        "for": geo_for,
        "time": YEAR,
        "GOVTYPE": GOVTYPE,
    }
    safe_query = urllib.parse.urlencode(params)
    key = os.environ.get("CENSUS_API_KEY")
    if key:
        params = dict(params)
        params["key"] = key
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "data-viz-guidance-example"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Census API request failed for {geography} ({safe_query}): {exc}"
        ) from exc
    if not payload or not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(
            f"Census API returned no data for {geography} ({safe_query})"
        )
    header, body = payload[0], payload[1:]
    index = {name: i for i, name in enumerate(header)}
    wanted = set(CODE_TO_GROUP) | set(REFERENCE_CODES)
    rows = []
    for rec in body:
        code = rec[index["AGG_DESC"]]
        if code not in wanted:
            continue
        thousands = int(rec[index["AMOUNT"]])
        in_group = code in CODE_TO_GROUP
        in_ref = code in REFERENCE_CODES
        if in_group and in_ref:
            role = "total+category"
        elif in_ref:
            role = "total"
        else:
            role = "category"
        rows.append(
            {
                "geography": geography,
                "geo_for": geo_for,
                "year": rec[index["time"]] if "time" in index else YEAR,
                "govtype": rec[index["GOVTYPE"]],
                "agg_desc": code,
                "agg_desc_label": rec[index["AGG_DESC_LABEL"]],
                "amount_thousands": thousands,
                "amount_dollars": thousands * 1000,
                "category": CODE_TO_GROUP.get(code, ""),
                "role": role,
            }
        )
    return rows


def fetch_api() -> list[dict]:
    rows = []
    for geography, geo_for in PLACES:
        rows.extend(_api_rows(geo_for, geography))
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "geography",
        "geo_for",
        "year",
        "govtype",
        "agg_desc",
        "agg_desc_label",
        "amount_thousands",
        "amount_dollars",
        "category",
        "role",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(
            "# U.S. Census Bureau, 2017 Annual Survey of State and Local Government Finances\n"
        )
        handle.write(
            "# Census Data API: https://api.census.gov/data/timeseries/govslocalfin\n"
        )
        handle.write(
            "# Selection: time=2017, GOVTYPE=001 (state and local combined), "
            "United States and Alabama\n"
        )
        handle.write(
            "# AMOUNT is reported in thousands of dollars. Leave API keys out of this file.\n"
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(refresh: bool) -> tuple[list[dict], str]:
    if CSV_PATH.exists() and not refresh:
        return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
    try:
        rows = fetch_api()
    except RuntimeError as exc:
        if CSV_PATH.exists():
            print(f"API request failed; using the saved table. ({exc})")
            return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
        raise
    if refresh:
        write_csv(CSV_PATH, rows)
    return rows, "Census Data API"


def dollars_text(value: int) -> str:
    return f"${value:,.0f}"


def group_amounts(rows: list[dict], geography: str) -> OrderedDict[str, int]:
    by_code = {
        row["agg_desc"]: row["amount_dollars"]
        for row in rows
        if row["geography"] == geography
    }
    amounts: OrderedDict[str, int] = OrderedDict()
    for name, codes in GROUPS.items():
        amounts[name] = sum(by_code[code] for code in codes)
    return amounts


def place_total(rows: list[dict], geography: str) -> int:
    by_code = {
        row["agg_desc"]: row["amount_dollars"]
        for row in rows
        if row["geography"] == geography
    }
    return by_code["LF0103"] + by_code["LF0199"]


def draw(rows: list[dict], source_note: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 7.2))
    fig.patch.set_facecolor("white")

    for ax, (geography, _) in zip(axes, PLACES):
        amounts = group_amounts(rows, geography)
        total = place_total(rows, geography)
        group_sum = sum(amounts.values())
        if group_sum != total:
            raise SystemExit(
                f"{geography}: group sum {group_sum} does not equal "
                f"general plus utility expenditure {total}"
            )
        labels = list(amounts)
        values = list(amounts.values())
        colors = [COLORS[name] for name in labels]
        ax.pie(
            values,
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops={
                "width": 0.45,
                "edgecolor": "white",
                "linewidth": 1.2,
            },
        )
        # A thin black ring keeps slices distinct for color-vision deficiency.
        ax.pie(
            values,
            colors=["none"] * len(values),
            startangle=90,
            counterclock=False,
            wedgeprops={
                "width": 0.45,
                "edgecolor": "#1b1b1b",
                "linewidth": 0.5,
                "fill": False,
            },
        )
        ax.set_title(geography, fontsize=13, color="#1b1b1b", pad=8)
        center = (
            f"{geography}\n"
            f"{dollars_text(total)}"
        )
        ax.text(
            0,
            0,
            center,
            ha="center",
            va="center",
            fontsize=8.5,
            color="#1b1b1b",
            linespacing=1.35,
        )
        ax.set_aspect("equal")

    handles = [
        Patch(facecolor=COLORS[name], edgecolor="#1b1b1b", linewidth=0.5, label=name)
        for name in GROUPS
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, 0.18),
    )

    us_total = place_total(rows, "United States")
    al_total = place_total(rows, "Alabama")
    title = (
        "State and local government expenditure, 2017"
    )
    fig.suptitle(title, fontsize=15, color="#1b1b1b", y=0.98)
    note = (
        "Combined state and local governments (GOVTYPE 001). The total is general "
        "expenditure plus utility expenditure. Other includes Interest on General Debt.\n"
        f"United States total: {dollars_text(us_total)}. "
        f"Alabama total: {dollars_text(al_total)}.\n"
        "The June 2020 dashboard screenshot on this page shows "
        f"{dollars_text(SCREENSHOT_TOTALS['United States'])} and "
        f"{dollars_text(SCREENSHOT_TOTALS['Alabama'])}.\n"
        "Source: U.S. Census Bureau, 2017 Annual Survey of State and Local Government Finances, "
        f"Census Data API ({source_note})."
    )
    fig.text(0.5, 0.015, note, ha="center", va="bottom", fontsize=7.4, color="#1b1b1b")
    fig.subplots_adjust(top=0.88, bottom=0.32, left=0.04, right=0.96, wspace=0.08)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    plt.close(fig)


def main() -> None:
    refresh = "--refresh" in sys.argv
    rows, source_note = load_rows(refresh)
    for geography, _ in PLACES:
        amounts = group_amounts(rows, geography)
        total = place_total(rows, geography)
        print(f"{geography} total (general + utility): {dollars_text(total)}")
        screenshot = SCREENSHOT_TOTALS[geography]
        delta = total - screenshot
        print(
            f"  Screenshot total: {dollars_text(screenshot)} "
            f"(difference {dollars_text(delta)})"
        )
        for name, value in amounts.items():
            share = 100 * value / total
            print(f"  {name}: {dollars_text(value)} ({share:.1f}%)")
    draw(rows, source_note)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
