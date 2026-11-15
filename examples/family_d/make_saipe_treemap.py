#!/usr/bin/env python3
"""Draw a treemap of 2020 SNAP participation in Midwest counties.

Source: U.S. Census Bureau
Dataset: Small Area Income and Poverty Estimates (SAIPE)
Year: 2020
File: https://www.census.gov/data-tools/demo/saipe_treemap/snap.2020.json

The official SAIPE SNAP treemap tool file is grouped by region and state.
This script keeps the Midwest region: Illinois, Indiana, Iowa, Kansas,
Michigan, Minnesota, Missouri, Nebraska, North Dakota, Ohio, South Dakota,
and Wisconsin. Rectangle size is the number of SNAP participants
(snappop). Color is the participation rate (ratio) in the same five bins
used by the tool: less than 10 percent, 10 to 20, 20 to 30, 30 to 40,
and more than 40 percent.

Shannon County, South Dakota, is in the official file with blank
population and SNAP counts (the county was renamed Oglala Lakota County).
The script omits that row from the treemap.

The Example 1 screenshot shows 2020, not 2022. The heading and alt text
on the Treemap page already use 2020.

No API key is required.

    python3 examples/family_d/make_saipe_treemap.py

The program uses saipe_snap_2020_midwest.csv when that file is present so
it can run offline. It downloads snap.2020.json if the table is missing,
or if --refresh is passed.
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "saipe_snap_2020_midwest.csv"
OUT_PATH = HERE.parents[1] / "assets" / "family-d" / "saipe-midwest-snap-2020.png"
SNAP_JSON_URL = "https://www.census.gov/data-tools/demo/saipe_treemap/snap.2020.json"
YEAR = "2020"
REGION = "Midwest"

# Bin edges match the official SAIPE SNAP treemap tool.
# Fills are a sequential green palette. Text is white or near-black so that
# labeled rectangles meet a 4.5:1 contrast ratio against the fill.
BIN_COLORS = (
    (10.0, "#D9F0D3", "#1b1b1b", "Less than 10%"),
    (20.0, "#8FCF8A", "#1b1b1b", "10% to 20%"),
    (30.0, "#347A4F", "#ffffff", "20% to 30%"),
    (40.0, "#1F5D3B", "#ffffff", "30% to 40%"),
    (None, "#0B2E1F", "#ffffff", "More than 40%"),
)


STATE_ABBR = {
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Michigan": "MI", "Minnesota": "MN", "Missouri": "MO", "Nebraska": "NE",
    "North Dakota": "ND", "Ohio": "OH", "South Dakota": "SD", "Wisconsin": "WI",
}


def bin_style(rate: float) -> tuple[str, str, str]:
    for edge, fill, text, label in BIN_COLORS:
        if edge is None or rate < edge:
            return fill, text, label
    return BIN_COLORS[-1][1], BIN_COLORS[-1][2], BIN_COLORS[-1][3]


def _comment_aware_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        filtered = (line for line in handle if not line.startswith("#"))
        return list(csv.DictReader(filtered))


def _parse_optional_int(value: str):
    if value is None or value == "":
        return None
    return int(value)


def _parse_optional_float(value: str):
    if value is None or value == "":
        return None
    return float(value)


def load_csv(path: Path) -> list[dict]:
    rows = []
    for raw in _comment_aware_rows(path):
        rows.append(
            {
                "year": raw.get("year", YEAR),
                "region": raw.get("region", REGION),
                "state": raw["state"],
                "state_abbrev": raw["state_abbrev"],
                "state_fips": raw["state_fips"],
                "county": raw["county"],
                "totalpop": _parse_optional_int(raw.get("totalpop", "")),
                "snappop": _parse_optional_int(raw.get("snappop", "")),
                "ratio": _parse_optional_float(raw.get("ratio", "")),
            }
        )
    return rows


def counties_from_json(payload: dict) -> list[dict]:
    region = next(
        child for child in payload["children"] if child["name"] == REGION
    )
    rows = []
    for state in region["children"]:
        for county in state["children"]:
            rows.append(
                {
                    "year": YEAR,
                    "region": REGION,
                    "state": state["name"],
                    "state_abbrev": state["abbrev"],
                    "state_fips": state["fips"],
                    "county": county["name"],
                    "totalpop": _parse_optional_int(county.get("totalpop", "")),
                    "snappop": _parse_optional_int(county.get("snappop", "")),
                    "ratio": _parse_optional_float(county.get("ratio", "")),
                }
            )
    return rows


def fetch_json() -> list[dict]:
    request = urllib.request.Request(
        SNAP_JSON_URL,
        headers={"User-Agent": "data-viz-guidance-example"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Download failed for {SNAP_JSON_URL}: {exc}") from exc
    return counties_from_json(payload)


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "year",
        "region",
        "state",
        "state_abbrev",
        "state_fips",
        "county",
        "totalpop",
        "snappop",
        "ratio",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(
            "# U.S. Census Bureau, Small Area Income and Poverty Estimates (SAIPE), "
            "SNAP participation, 2020\n"
        )
        handle.write(f"# Source file: {SNAP_JSON_URL}\n")
        handle.write(
            "# Geography: Midwest region counties. snappop is SNAP participants; "
            "ratio is the participation rate.\n"
        )
        handle.write(
            "# Shannon County, SD is present in the official file with blank "
            "population and SNAP counts.\n"
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "year": row["year"],
                    "region": row["region"],
                    "state": row["state"],
                    "state_abbrev": row["state_abbrev"],
                    "state_fips": row["state_fips"],
                    "county": row["county"],
                    "totalpop": "" if row["totalpop"] is None else row["totalpop"],
                    "snappop": "" if row["snappop"] is None else row["snappop"],
                    "ratio": "" if row["ratio"] is None else row["ratio"],
                }
            )


def load_rows(refresh: bool) -> tuple[list[dict], str]:
    if CSV_PATH.exists() and not refresh:
        return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
    try:
        rows = fetch_json()
    except RuntimeError as exc:
        if CSV_PATH.exists():
            print(f"Download failed; using the saved table. ({exc})")
            return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
        raise
    if refresh:
        write_csv(CSV_PATH, rows)
    return rows, "official SAIPE snap.2020.json file"


def _layout_row(sizes, x, y, dx, dy):
    covered = sum(sizes)
    rects = []
    if dx >= dy:
        width = covered / dy if dy else 0
        cursor = y
        for size in sizes:
            height = size / width if width else 0
            rects.append((x, cursor, width, height))
            cursor += height
    else:
        height = covered / dx if dx else 0
        cursor = x
        for size in sizes:
            width = size / height if height else 0
            rects.append((cursor, y, width, height))
            cursor += width
    return rects


def _worst_aspect(sizes, x, y, dx, dy) -> float:
    worst = 1.0
    for _, _, width, height in _layout_row(sizes, x, y, dx, dy):
        if width <= 0 or height <= 0:
            return float("inf")
        worst = max(worst, width / height, height / width)
    return worst


def squarify(values, x, y, width, height):
    """Return a (x, y, w, h) rectangle for each value, in the same order."""
    values = [max(0.0, float(value)) for value in values]
    total = sum(values)
    if total <= 0 or width <= 0 or height <= 0:
        return [(x, y, 0.0, 0.0) for _ in values]
    areas = [value / total * width * height for value in values]
    return _squarify(areas, x, y, width, height)


def _squarify(areas, x, y, dx, dy):
    if not areas:
        return []
    if len(areas) == 1:
        return [(x, y, dx, dy)]

    placed = []
    remaining = list(areas)
    cx, cy, cdx, cdy = x, y, dx, dy
    while remaining:
        if cdx <= 0 or cdy <= 0:
            placed.extend((cx, cy, 0.0, 0.0) for _ in remaining)
            break
        row = [remaining.pop(0)]
        while remaining:
            candidate = row + [remaining[0]]
            if _worst_aspect(candidate, cx, cy, cdx, cdy) <= _worst_aspect(
                row, cx, cy, cdx, cdy
            ):
                row = candidate
                remaining.pop(0)
            else:
                break
        row_rects = _layout_row(row, cx, cy, cdx, cdy)
        placed.extend(row_rects)
        covered = sum(row)
        if cdx >= cdy:
            width = covered / cdy if cdy else 0
            cx += width
            cdx -= width
        else:
            height = covered / cdx if cdx else 0
            cy += height
            cdy -= height
    return placed


def drawable(rows: list[dict]) -> list[dict]:
    kept = []
    for row in rows:
        if row["snappop"] is None or row["ratio"] is None or row["snappop"] <= 0:
            continue
        kept.append(row)
    return kept


def short_label(county: str) -> str:
    # "Cook County, IL" -> "Cook Co., IL"
    return county.replace(" County", " Co.")


AXES_HEIGHT_IN = 5.6  # height of the treemap area in inches; one data unit


def label_fits(text: str, cw: float, ch: float, fontsize: float = 6.2) -> bool:
    # Conservative fit check. One data unit equals the treemap height, and the
    # axes use an equal aspect, so data units convert directly to points.
    points_per_data = AXES_HEIGHT_IN * 72
    lines = text.split("\n")
    text_w = 0.58 * fontsize * max(len(line) for line in lines) / points_per_data
    text_h = 1.30 * fontsize * len(lines) / points_per_data
    return text_w <= cw * 0.90 and text_h <= ch * 0.82


def draw(rows: list[dict], source_note: str) -> None:
    counties = drawable(rows)
    if not counties:
        raise SystemExit("No Midwest counties with SNAP counts were found.")

    by_state: dict[str, list[dict]] = {}
    for row in counties:
        by_state.setdefault(row["state"], []).append(row)
    # Largest states first, which keeps the official tool's "big tile" reading
    # pattern and makes Cook, Wayne, and Cuyahoga easier to label.
    state_names = sorted(
        by_state,
        key=lambda name: sum(row["snappop"] for row in by_state[name]),
        reverse=True,
    )
    state_totals = [
        sum(row["snappop"] for row in by_state[name]) for name in state_names
    ]

    # Wide layout like Example 1. The treemap fills the width of the figure,
    # the legend runs across the top, and the note sits directly below.
    fig_w, fig_h = 13.5, 7.6
    axes_left, axes_bottom, axes_w_in = 0.01, 0.115, 13.5 * 0.98
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([axes_left, axes_bottom, 0.98, AXES_HEIGHT_IN / fig_h])
    width = axes_w_in / AXES_HEIGHT_IN
    ax.set_xlim(0, width)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.invert_yaxis()

    # Largest states are placed first, then mirrored left to right so Illinois
    # and Ohio sit on the right, as in Example 1.
    state_rects = squarify(state_totals, 0, 0, width, 1)
    state_rects = [(width - sx - sw, sy, sw, sh) for sx, sy, sw, sh in state_rects]
    pad = 0.003
    header_h = 0.032

    labeled = []
    for name, (sx, sy, sw, sh) in zip(state_names, state_rects):
        members = sorted(by_state[name], key=lambda row: row["snappop"], reverse=True)
        # Gray name strip at the top of each state, as in Example 1.
        ax.add_patch(
            Rectangle((sx, sy), sw, header_h, facecolor="#D6D6D6",
                      edgecolor="#1b1b1b", linewidth=1.1, zorder=1)
        )
        # Use the postal abbreviation when the full name does not fit.
        header_label = name
        if 0.62 * 8 * len(name) / (AXES_HEIGHT_IN * 72) > sw - 0.012:
            header_label = STATE_ABBR.get(name, name)
        ax.text(sx + 0.006, sy + header_h / 2, header_label, ha="left", va="center",
                fontsize=8, fontweight="bold", color="#1b1b1b", zorder=3, clip_on=True)
        ax.add_patch(
            Rectangle((sx, sy), sw, sh, facecolor="white", edgecolor="#1b1b1b",
                      linewidth=1.1, zorder=1)
        )
        inner_x = sx + pad
        inner_y = sy + header_h + pad
        inner_w = max(sw - 2 * pad, 0)
        inner_h = max(sh - header_h - 2 * pad, 0)
        county_rects = squarify(
            [row["snappop"] for row in members], inner_x, inner_y, inner_w, inner_h
        )
        # Mirror counties so the largest sits at the lower right of each state,
        # as in Example 1.
        county_rects = [
            (2 * inner_x + inner_w - cx - cw, 2 * inner_y + inner_h - cy - ch, cw, ch)
            for cx, cy, cw, ch in county_rects
        ]
        for row, (cx, cy, cw, ch) in zip(members, county_rects):
            fill, text_color, _ = bin_style(row["ratio"])
            ax.add_patch(
                Rectangle((cx, cy), cw, ch, facecolor=fill, edgecolor="white",
                          linewidth=0.25, zorder=2)
            )
            chosen = None
            county = row["county"]
            candidates = [short_label(county)]
            if ", " in county:
                base, st = county.rsplit(", ", 1)
                short = base.replace(" County", " Co.")
                candidates.append(f"{short}\n{st}")
                shorter = base.replace(" County", "").replace(" Parish", "")
                candidates.append(f"{shorter}\n{st}")
            for label in candidates:
                if label_fits(label, cw, ch):
                    chosen = label
                    break
            if chosen:
                ax.text(cx + cw / 2, cy + ch / 2, chosen, ha="center", va="center",
                        fontsize=6.2, color=text_color, zorder=3, clip_on=True)
                labeled.append(county)

    handles = [
        Patch(facecolor=fill, edgecolor="#1b1b1b", linewidth=0.5, label=label)
        for edge, fill, text, label in BIN_COLORS
    ]
    fig.legend(
        handles=handles,
        title="SNAP participation rate:",
        loc="upper left",
        bbox_to_anchor=(axes_left, 0.925),
        ncol=len(handles),
        frameon=False,
        fontsize=8.5,
        title_fontsize=9,
        alignment="left",
    )
    fig.text(axes_left, 0.975, "SNAP participation in Midwest counties, 2020",
             ha="left", va="top", fontsize=14, color="#1b1b1b")
    omitted = [
        row["county"]
        for row in rows
        if row["snappop"] is None or row["ratio"] is None
    ]
    omit_note = ""
    if omitted:
        omit_note = (
            " Omitted because the official file has no counts: "
            + ", ".join(omitted)
            + "."
        )
    largest = max(counties, key=lambda row: row["snappop"])
    note = (
        "Rectangle size is the number of SNAP participants. Color is the participation rate. "
        f"{len(counties):,} Midwest counties are shown.{omit_note}\n"
        f"Largest county: {largest['county']}, {largest['snappop']:,} participants "
        f"({largest['ratio']:.1f}%).\n"
        "Source: U.S. Census Bureau, Small Area Income and Poverty Estimates (SAIPE), "
        f"2020 SNAP participation ({source_note})."
    )
    fig.text(axes_left, 0.015, note, ha="left", va="bottom", fontsize=7.5,
             color="#1b1b1b", linespacing=1.4)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    plt.close(fig)
    return labeled


def main() -> None:
    refresh = "--refresh" in sys.argv
    rows, source_note = load_rows(refresh)
    counties = drawable(rows)
    print(f"Midwest counties in the file: {len(rows)}")
    print(f"Counties drawn (with SNAP counts): {len(counties)}")
    missing = [row["county"] for row in rows if row not in counties]
    if missing:
        print("Omitted:", ", ".join(missing))
    top = sorted(counties, key=lambda row: row["snappop"], reverse=True)[:8]
    print("Largest counties:")
    for row in top:
        print(
            f"  {row['county']}: {row['snappop']:,} participants, "
            f"{row['ratio']:.1f}% rate"
        )
    mahoning = [row for row in counties if "Mahoning" in row["county"]]
    if mahoning:
        row = mahoning[0]
        fill, _, label = bin_style(row["ratio"])
        print(
            f"Mahoning County check (2020 is 21.3% / 20–30% bin): "
            f"{row['ratio']:.1f}% ({label})"
        )
    labeled = draw(rows, source_note)
    print(f"Labeled {len(labeled)} counties")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
