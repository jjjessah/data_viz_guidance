#!/usr/bin/env python3
"""Draw a Sankey diagram of UVA master's first-year employment outcomes.

Source: U.S. Census Bureau, Longitudinal Employer-Household Dynamics
Dataset: Post-Secondary Employment Outcomes (PSEO) Flows
Release: R2023Q4 (this release matches the Sankey Diagram Example 1 screenshot)
File: https://lehd.ces.census.gov/data/pseo/R2023Q4/va/pseof_va.csv.gz

Selection:
    institution        00374500 (University of Virginia)
    degree_level       07 (master's)
    cip_level          2
    cipcode            14 Engineering, 45 Social Sciences,
                       27 Mathematics and Statistics
    grad_cohort        0000 (all cohorts)
    grad_cohort_years  5
    agg_level_pseo     40
    geo_level          N, geography 00 (nation)
    ind_level          A, industry 00 (all industries)
    outcomes           y1_grads_emp and y1_grads_nme (year-1)

The current PSEO explorer release (2026Q2) shows different shares for the
same selection. This script uses the 2023Q4 counts so the chart matches
the screenshot: Engineering 67 percent, Social Sciences 21 percent,
Mathematics and Statistics 12 percent; Employed 51 percent, and
No or very low earnings observed 49 percent.

No API key is required.

    python3 examples/family_d/make_pseo_sankey.py

The program uses pseo_uva_masters_flows_R2023Q4.csv when that file is
present so it can run offline. It downloads the 2023Q4 Virginia flows
file if the table is missing, or if --refresh is passed.
"""

from __future__ import annotations

import csv
import gzip
import io
import sys
import urllib.error
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "pseo_uva_masters_flows_R2023Q4.csv"
OUT_PATH = HERE.parents[1] / "assets" / "family-d" / "pseo-uva-masters-flows.png"
FLOWS_URL = "https://lehd.ces.census.gov/data/pseo/R2023Q4/va/pseof_va.csv.gz"
RELEASE = "R2023Q4"
INSTITUTION = "00374500"
INSTITUTION_NAME = "University of Virginia"
DEGREE_LEVEL = "07"
CIP_LEVEL = "2"
GRAD_COHORT = "0000"
GRAD_COHORT_YEARS = "5"
AGG_LEVEL = "40"
GEO_LEVEL = "N"
GEOGRAPHY = "00"
IND_LEVEL = "A"
INDUSTRY = "00"

# Display order matches the Example 1 screenshot (top to bottom).
PROGRAMS = (
    ("14", "Engineering"),
    ("45", "Social Sciences"),
    ("27", "Mathematics and Statistics"),
)
CIP_LABELS = dict(PROGRAMS)

# Program fills follow a color-blind-safe palette. Outcome fills match the
# screenshot's contrast: a dark teal for employed and a medium gray for
# no or very low earnings. Flow ribbons are a mid gray.
PROGRAM_COLORS = {
    "Engineering": "#0072B2",
    "Social Sciences": "#56B4E9",
    "Mathematics and Statistics": "#E69F00",
}
EMPLOYED_COLOR = "#117A65"
NME_COLOR = "#5C5C5C"
FLOW_COLORS = {
    "Engineering": "#7AA8C4",
    "Social Sciences": "#A9D0E8",
    "Mathematics and Statistics": "#E6C36A",
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
                "release": raw.get("release", RELEASE),
                "institution": raw["institution"],
                "institution_name": raw.get("institution_name", INSTITUTION_NAME),
                "degree_level": raw["degree_level"],
                "degree_label": raw.get("degree_label", "Master's"),
                "cip_level": raw.get("cip_level", CIP_LEVEL),
                "cipcode": raw["cipcode"],
                "cip_label": raw.get("cip_label") or CIP_LABELS[raw["cipcode"]],
                "grad_cohort": raw["grad_cohort"],
                "grad_cohort_years": raw["grad_cohort_years"],
                "agg_level_pseo": raw["agg_level_pseo"],
                "geo_level": raw["geo_level"],
                "geography": raw["geography"],
                "ind_level": raw["ind_level"],
                "industry": raw["industry"],
                "y1_grads_emp": int(raw["y1_grads_emp"]),
                "y1_grads_nme": int(raw["y1_grads_nme"]),
                "status_y1_grads_emp": raw.get("status_y1_grads_emp", ""),
                "status_y1_grads_nme": raw.get("status_y1_grads_nme", ""),
            }
        )
    return rows


def _keep_row(row: dict[str, str]) -> bool:
    return (
        row.get("institution") == INSTITUTION
        and row.get("degree_level") == DEGREE_LEVEL
        and row.get("cipcode") in CIP_LABELS
        and row.get("cip_level") == CIP_LEVEL
        and row.get("grad_cohort") == GRAD_COHORT
        and row.get("grad_cohort_years") == GRAD_COHORT_YEARS
        and row.get("agg_level_pseo") == AGG_LEVEL
        and row.get("geo_level") == GEO_LEVEL
        and row.get("geography") == GEOGRAPHY
        and row.get("ind_level") == IND_LEVEL
        and row.get("industry") == INDUSTRY
    )


def parse_flows_file(handle) -> list[dict]:
    rows = []
    for raw in csv.DictReader(handle):
        if not _keep_row(raw):
            continue
        rows.append(
            {
                "release": RELEASE,
                "institution": raw["institution"],
                "institution_name": INSTITUTION_NAME,
                "degree_level": raw["degree_level"],
                "degree_label": "Master's",
                "cip_level": raw["cip_level"],
                "cipcode": raw["cipcode"],
                "cip_label": CIP_LABELS[raw["cipcode"]],
                "grad_cohort": raw["grad_cohort"],
                "grad_cohort_years": raw["grad_cohort_years"],
                "agg_level_pseo": raw["agg_level_pseo"],
                "geo_level": raw["geo_level"],
                "geography": raw["geography"],
                "ind_level": raw["ind_level"],
                "industry": raw["industry"],
                "y1_grads_emp": int(raw["y1_grads_emp"]),
                "y1_grads_nme": int(raw["y1_grads_nme"]),
                "status_y1_grads_emp": raw.get("status_y1_grads_emp", ""),
                "status_y1_grads_nme": raw.get("status_y1_grads_nme", ""),
            }
        )
    return rows


def fetch_release() -> list[dict]:
    request = urllib.request.Request(
        FLOWS_URL,
        headers={"User-Agent": "data-viz-guidance-example"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Download failed for {FLOWS_URL}: {exc}") from exc
    try:
        with gzip.open(io.BytesIO(payload), "rt", encoding="utf-8") as handle:
            rows = parse_flows_file(handle)
    except OSError:
        # Some environments already decompress Content-Encoding: gzip.
        text = payload.decode("utf-8")
        rows = parse_flows_file(io.StringIO(text))
    if len(rows) != 3:
        raise RuntimeError(
            f"Expected 3 program rows from {FLOWS_URL}, found {len(rows)}"
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "release",
        "institution",
        "institution_name",
        "degree_level",
        "degree_label",
        "cip_level",
        "cipcode",
        "cip_label",
        "grad_cohort",
        "grad_cohort_years",
        "agg_level_pseo",
        "geo_level",
        "geography",
        "ind_level",
        "industry",
        "y1_grads_emp",
        "y1_grads_nme",
        "status_y1_grads_emp",
        "status_y1_grads_nme",
    ]
    order = {code: i for i, (code, _) in enumerate(PROGRAMS)}
    rows = sorted(rows, key=lambda row: order[row["cipcode"]])
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(
            "# U.S. Census Bureau, Post-Secondary Employment Outcomes (PSEO) Flows, release R2023Q4\n"
        )
        handle.write(f"# Source file: {FLOWS_URL}\n")
        handle.write(
            "# Selection: institution 00374500, degree_level 07, cip_level 2, "
            "CIP 14/45/27, grad_cohort 0000, grad_cohort_years 5,\n"
        )
        handle.write(
            "# agg_level_pseo 40, geo_level N, geography 00, ind_level A, industry 00, year-1 outcomes.\n"
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(refresh: bool) -> tuple[list[dict], str]:
    if CSV_PATH.exists() and not refresh:
        return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
    try:
        rows = fetch_release()
    except RuntimeError as exc:
        if CSV_PATH.exists():
            print(f"Download failed; using the saved table. ({exc})")
            return load_csv(CSV_PATH), f"saved table {CSV_PATH.name}"
        raise
    if refresh:
        write_csv(CSV_PATH, rows)
    return rows, f"PSEO {RELEASE} flows file"


def rounded_share(part: int, whole: int) -> int:
    # Match the explorer's displayed integer percents (half up).
    return int((100.0 * part / whole) + 0.5)


def _ribbon(x0, x1, y0_top, y0_bot, y1_top, y1_bot):
    mid = (x0 + x1) / 2
    verts = [
        (x0, y0_top),
        (mid, y0_top),
        (mid, y1_top),
        (x1, y1_top),
        (x1, y1_bot),
        (mid, y1_bot),
        (mid, y0_bot),
        (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    return PathPatch(
        MplPath(verts, codes),
        facecolor=None,
        edgecolor="none",
        lw=0,
    )


def draw(rows: list[dict], source_note: str) -> None:
    by_cip = {row["cipcode"]: row for row in rows}
    missing = [code for code, _ in PROGRAMS if code not in by_cip]
    if missing:
        raise SystemExit(f"Missing CIP rows: {missing}")

    programs = []
    for code, label in PROGRAMS:
        row = by_cip[code]
        employed = row["y1_grads_emp"]
        nme = row["y1_grads_nme"]
        programs.append(
            {
                "label": label,
                "employed": employed,
                "nme": nme,
                "total": employed + nme,
            }
        )
    grand_total = sum(item["total"] for item in programs)
    employed_total = sum(item["employed"] for item in programs)
    nme_total = sum(item["nme"] for item in programs)

    fig, ax = plt.subplots(figsize=(11.2, 6.6))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    left_x, left_w = 0.02, 0.30
    right_x, right_w = 0.68, 0.30
    flow_x0 = left_x + left_w
    flow_x1 = right_x
    top, bottom = 0.90, 0.08
    gap = 0.035
    usable = (top - bottom) - 2 * gap
    scale = usable / grand_total

    # Left nodes, top to bottom.
    left_boxes = []
    y = top
    for item in programs:
        height = item["total"] * scale
        y0 = y - height
        left_boxes.append((item, y0, y))
        y = y0 - gap

    # Right nodes: Employed on top, NME below, same total height.
    right_usable = usable + 2 * gap
    right_gap = 0.045
    right_scale = (right_usable - right_gap) / grand_total
    emp_h = employed_total * right_scale
    nme_h = nme_total * right_scale
    emp_top = top
    emp_bot = emp_top - emp_h
    nme_top = emp_bot - right_gap
    nme_bot = nme_top - nme_h

    # Flows: consume each left node from the top (employed, then NME).
    # Consume the right employed node from the top, then the NME node.
    emp_cursor = emp_top
    nme_cursor = nme_top
    for item, y0, y1 in left_boxes:
        cursor = y1
        for kind, count, dest_cursor, dest_update in (
            (
                "employed",
                item["employed"],
                emp_cursor,
                "emp",
            ),
            (
                "nme",
                item["nme"],
                nme_cursor,
                "nme",
            ),
        ):
            height = count * scale
            left_top = cursor
            left_bot = cursor - height
            if dest_update == "emp":
                right_top = emp_cursor
                right_bot = emp_cursor - count * right_scale
                emp_cursor = right_bot
            else:
                right_top = nme_cursor
                right_bot = nme_cursor - count * right_scale
                nme_cursor = right_bot
            patch = _ribbon(flow_x0, flow_x1, left_top, left_bot, right_top, right_bot)
            patch.set_facecolor(FLOW_COLORS[item["label"]])
            patch.set_alpha(0.75)
            ax.add_patch(patch)
            cursor = left_bot

    def node_box(x, y0, y1, facecolor, text, text_color):
        rect = FancyBboxPatch(
            (x, y0),
            left_w if x < 0.5 else right_w,
            y1 - y0,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor=facecolor,
            edgecolor="#1b1b1b",
            linewidth=0.7,
        )
        ax.add_patch(rect)
        ax.text(
            x + (left_w if x < 0.5 else right_w) / 2,
            (y0 + y1) / 2,
            text,
            ha="center",
            va="center",
            fontsize=8.5,
            color=text_color,
            linespacing=1.25,
        )

    for item, y0, y1 in left_boxes:
        share = rounded_share(item["total"], grand_total)
        label = f"{item['label']}\n{share}%"
        # Light program fills use dark text; the gold math fill is still dark
        # enough that black text meets 4.5:1.
        text_color = "#1b1b1b"
        if item["label"] == "Engineering":
            text_color = "white"
        node_box(left_x, y0, y1, PROGRAM_COLORS[item["label"]], label, text_color)

    emp_share = rounded_share(employed_total, grand_total)
    nme_share = rounded_share(nme_total, grand_total)
    node_box(
        right_x,
        emp_bot,
        emp_top,
        EMPLOYED_COLOR,
        f"Employed\n{emp_share}%",
        "white",
    )
    node_box(
        right_x,
        nme_bot,
        nme_top,
        NME_COLOR,
        f"No or very low\nearnings observed\n{nme_share}%",
        "white",
    )

    ax.set_title(
        "First-year employment outcomes for University of Virginia master's graduates",
        fontsize=13,
        color="#1b1b1b",
        pad=12,
        loc="left",
        x=0.02,
    )
    note = (
        "Programs: Engineering, Social Sciences, and Mathematics and Statistics. "
        "All graduate cohorts in 5-year groups, year-1 outcomes, all industries, nation.\n"
        f"Counts: Engineering {programs[0]['total']:,} "
        f"({programs[0]['employed']:,} employed, {programs[0]['nme']:,} no or very low earnings); "
        f"Social Sciences {programs[1]['total']:,} "
        f"({programs[1]['employed']:,}, {programs[1]['nme']:,}); "
        f"Mathematics and Statistics {programs[2]['total']:,} "
        f"({programs[2]['employed']:,}, {programs[2]['nme']:,}). "
        f"Total {grand_total:,}.\n"
        "Source: U.S. Census Bureau, Post-Secondary Employment Outcomes Flows, "
        f"release {RELEASE} ({source_note}). "
        "The current explorer release (2026Q2) shows different shares for the same selection."
    )
    fig.text(0.02, 0.015, note, ha="left", va="bottom", fontsize=7.0, color="#1b1b1b",
             wrap=True)
    fig.subplots_adjust(top=0.88, bottom=0.22, left=0.02, right=0.98)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150)
    plt.close(fig)


def main() -> None:
    refresh = "--refresh" in sys.argv
    rows, source_note = load_rows(refresh)
    order = {code: i for i, (code, _) in enumerate(PROGRAMS)}
    rows = sorted(rows, key=lambda row: order[row["cipcode"]])
    grand = sum(row["y1_grads_emp"] + row["y1_grads_nme"] for row in rows)
    employed = sum(row["y1_grads_emp"] for row in rows)
    nme = sum(row["y1_grads_nme"] for row in rows)
    for row in rows:
        total = row["y1_grads_emp"] + row["y1_grads_nme"]
        print(
            f"{row['cip_label']}: {total} graduates "
            f"({row['y1_grads_emp']} employed, {row['y1_grads_nme']} no or very low earnings), "
            f"{rounded_share(total, grand)}%"
        )
    print(
        f"Employed {employed} ({rounded_share(employed, grand)}%), "
        f"No or very low earnings observed {nme} ({rounded_share(nme, grand)}%), "
        f"total {grand}"
    )
    draw(rows, source_note)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
