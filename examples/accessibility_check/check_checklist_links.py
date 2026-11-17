#!/usr/bin/env python3
"""Check the links inside the Publication Quality Checklist folds.

For every link in a <ul class="checklist-folds"> block of a built page, this script
confirms that:
  * a same-page link (#anchor) points to an id that exists on that page, and
  * a site page link (page.html or page.html#anchor) points to a built page that
    exists, and to its anchor when one is given.

It also flags checklist folds with no "Read the full section" link, unless the fold
says plainly that the item does not apply to the page ("Does not apply to this page.").

Usage:
  python3 check_checklist_links.py --site /path/to/_site/data_viz_guidance
  python3 check_checklist_links.py --build /path/to/repo   (builds with Jekyll first)

Exit code 0 means no problems were found; 1 means at least one link is broken.
"""
import argparse, os, subprocess, sys, tempfile
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

# The ten Family D pages (eleven files: Grids has a component copy and a visualization-type copy).
PAGES = ["piechart.html", "donutchart.html", "sankeydiagram.html", "treemap.html",
         "grids-visualization-type.html", "grid.html", "mobiledesign.html", "color.html",
         "interactivechart.html", "note.html", "508.html"]
# A fold may leave out the "Read the full section" link only when its text starts with this.
NOT_APPLICABLE = "Does not apply to this page."


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.depth = 0          # depth inside ul.checklist-folds
        self.links = []         # (href, summary text, link text)
        self.folds = []         # summary text of each fold
        self.fold_has_full = []
        self.fold_text = []     # body text of each fold
        self._in_summary = False
        self._in_a = None
        self._summary = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if a.get("name") and tag == "a":
            self.ids.add(a["name"])
        if tag == "ul" and "checklist-folds" in (a.get("class") or "").split():
            self.depth = 1
            return
        if self.depth:
            if tag == "ul":
                self.depth += 1
            elif tag == "summary":
                self._in_summary, self._summary = True, ""
            elif tag == "a" and a.get("href"):
                self._in_a = [a["href"], ""]

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == "ul":
            self.depth -= 1
        elif tag == "summary":
            self._in_summary = False
            self.folds.append(self._summary.strip())
            self.fold_has_full.append(False)
            self.fold_text.append("")
        elif tag == "a" and self._in_a:
            href, text = self._in_a
            self.links.append((href, self.folds[-1] if self.folds else "", text.strip()))
            if text.strip().startswith("Read the full section") and self.fold_has_full:
                self.fold_has_full[-1] = True
            self._in_a = None

    def handle_data(self, data):
        if self._in_summary:
            self._summary += data
        elif self.depth and self.fold_text:
            self.fold_text[-1] += data
        if self._in_a:
            self._in_a[1] += data


def scan(path):
    p = PageScan()
    with open(path, encoding="utf-8") as f:
        p.feed(f.read())
    return p


def check(site):
    problems, checked = [], 0
    cache = {}
    for page in PAGES:
        path = os.path.join(site, page)
        if not os.path.exists(path):
            problems.append(f"{page}: built page not found")
            continue
        scan_ = cache.setdefault(page, scan(path))
        if not scan_.folds:
            problems.append(f"{page}: no checklist folds found")
        for summary, has_full, text in zip(scan_.folds, scan_.fold_has_full, scan_.fold_text):
            if not has_full and not text.strip().startswith(NOT_APPLICABLE):
                problems.append(f'{page}: fold "{summary}" has no "Read the full section" link')
        for href, summary, text in scan_.links:
            checked += 1
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                continue  # outside links are not checked here
            target_page = parts.path or page
            frag = unquote(parts.fragment)
            target_path = os.path.join(site, target_page.lstrip("/"))
            if not os.path.exists(target_path):
                problems.append(f'{page}: "{text}" under "{summary}" points to missing page {target_page}')
                continue
            if frag:
                tscan = cache.setdefault(target_page, scan(target_path))
                if frag not in tscan.ids:
                    problems.append(f'{page}: "{text}" under "{summary}" points to missing anchor #{frag} on {target_page}')
    return problems, checked


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--site", help="built site folder that contains piechart.html and the other pages")
    g.add_argument("--build", help="repository folder to build with Jekyll first")
    ap.add_argument("--jekyll", default="bundle exec jekyll", help="command used with --build")
    args = ap.parse_args()
    site = args.site
    if args.build:
        dest = tempfile.mkdtemp(prefix="checklist-site-")
        cmd = args.jekyll.split() + ["build", "-q", "-s", args.build, "-d", dest]
        subprocess.run(cmd, check=True)
        site = dest
    problems, checked = check(site)
    print(f"Checked {checked} checklist links on {len(PAGES)} pages.")
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("No missing pages or anchors found.")


if __name__ == "__main__":
    main()
