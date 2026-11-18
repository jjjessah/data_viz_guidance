#!/usr/bin/env python3
"""Repeatable accessibility and consistency checks for the data visualization guidance site.

Two commands:

  run      Build one copy of the site with Jekyll, serve it locally, and record:
             * axe-core results by rule (WCAG 2.0-2.2 A and AA, plus best-practice rules)
               at 1280 px and 390 px, with every <details> block opened
             * sideways page overflow at each width
             * the checklist link check (check_checklist_links.py)
             * code-include parity: each _includes/code file must be identical to a
               script in examples/family_d
             * image alt text on the checked pages
           Optional: screenshots of the same views at both widths.
           summary.md opens with a "What to fix" list: each failing element with its page,
           screen width, CSS selector, a short piece of its HTML, the reason it failed, and
           a link to a guide for fixing it.

  compare  Put two saved runs side by side in one Markdown table.

Examples:
  python3 run_checks.py run --branch main --label before --out ~/checks/before --screenshots
  python3 run_checks.py run --src /path/to/repo --label after --out ~/checks/after
  python3 run_checks.py compare ~/checks/before/results.json ~/checks/after/results.json
  python3 run_checks.py run --src . --label pr --out /tmp/results --fail-on-broken-links

With --fail-on-broken-links, the run ends with exit code 1 when the checklist link check
on the Family D pages fails. axe-core failures never change the exit code.

The script never reads or prints CENSUS_API_KEY, and it does not call the Census Data API.
Automated checks find only part of the possible WCAG issues; they are not a Section 508
conformance review.
"""
import sys
sys.dont_write_bytecode = True  # keep __pycache__ out of the repository folder
import argparse, collections, functools, hashlib, http.server, io, json, os, re, shutil
import socketserver, subprocess, sys, tarfile, tempfile, threading, urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_checklist_links  # noqa: E402

BASEURL = "data_viz_guidance"
# The ten Family D pages, in eleven files: Grids has a visualization-type copy and a component copy.
FAMILY_D = ["piechart.html", "donutchart.html", "sankeydiagram.html", "treemap.html",
            "grids-visualization-type.html", "grid.html", "mobiledesign.html", "color.html",
            "interactivechart.html", "note.html", "508.html"]
# Pages outside Family D that share the site layout.
SHARED = ["index.html", "barchart.html", "axesdual.html", "title.html", "tags/distribution/"]
WIDTHS = {"desktop": "desktop (1280 px)", "phone": "phone (390 px)"}
# In "What to fix", show at most this many elements for one rule on one page.
MAX_ELEMENTS = 5
# An identical failing element found on this many pages or more is listed once, as a shared problem.
SHARED_MIN_PAGES = 3
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
SCREENSHOTS = [
    {"name": "home", "page": "index.html"},
    {"name": "piechart_top", "page": "piechart.html"},
    {"name": "piechart_figure_table", "page": "piechart.html",
     "open": "#md-commute details", "scrollTo": "#md-commute summary"},
    {"name": "piechart_checklist", "page": "piechart.html",
     "open": ".checklist-folds li:nth-child(5) details", "scrollTo": "#publication-quality-checklist"},
    {"name": "donut_tables", "page": "donutchart.html",
     "scrollTo": "#reproduce-the-state-and-local-expenditure-example"},
    {"name": "grids_example", "page": "grids-visualization-type.html",
     "scrollTo": "#reproduce-the-new-york-commute-example"},
    {"name": "grid_component_example", "page": "grid.html",
     "scrollTo": "#reproduce-the-new-york-commute-example"},
    {"name": "color_checklist", "page": "color.html",
     "open": ".checklist-folds li:nth-child(3) details", "scrollTo": "#publication-quality-checklist"},
    {"name": "note_examples", "page": "note.html", "scrollTo": "#census-data-examples"},
    {"name": "mobile_example2", "page": "mobiledesign.html",
     "scrollTo": "p:has(+ p img[src$=\"MobileDesign2.png\"])"},
    {"name": "pie_md_figure", "page": "piechart.html",
     "scrollTo": "#md-commute"},
    {"name": "donut_no_moe", "page": "donutchart.html",
     "scrollTo": "p:has(a[href*=\"2017_methodology.pdf\"])"},
    {"name": "note_example2", "page": "note.html",
     "scrollTo": "p:has(+ p img[src$=\"Note2.png\"])"},
]


def download_branch(repo, branch, dest):
    url = f"https://api.github.com/repos/{repo}/tarball/{branch}"
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        top = t.getnames()[0].split("/")[0]
        t.extractall(dest, filter="data")
    commit = top.rsplit("-", 1)[-1]
    return os.path.join(dest, top), commit


# GitHub Pages turns on these plugins even when _config.yml does not list them.
# jekyll-relative-links rewrites relative image paths such as assets/x.png the way the live site does.
PAGES_DEFAULT_PLUGINS = ["jekyll-relative-links"]


def config_overlay(src, work):
    """Write a small extra config that keeps the site's plugins and adds the GitHub Pages defaults."""
    text = open(os.path.join(src, "_config.yml"), encoding="utf-8").read()
    m = re.search(r"^plugins:\s*\n((?:[ \t]+-[^\n]*\n?)+)", text, re.M)
    plugins = re.findall(r"-\s*([\w.-]+)", m.group(1)) if m else []
    plugins += [p for p in PAGES_DEFAULT_PLUGINS if p not in plugins]
    path = os.path.join(work, "pages_defaults.yml")
    with open(path, "w") as f:
        f.write("plugins:\n" + "".join(f"  - {p}\n" for p in plugins))
    return path


def build_site(src, site_root, jekyll_cmd, work):
    target = os.path.join(site_root, BASEURL)
    if os.path.exists(site_root):
        shutil.rmtree(site_root)
    overlay = config_overlay(src, work)
    cmd = jekyll_cmd.split() + ["build", "-q", "-s", src, "-d", target,
                                "--config", os.path.join(src, "_config.yml") + "," + overlay]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Jekyll build failed:\n" + r.stderr[-3000:])
    return target


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=root)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


class ImgScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main, self.imgs = 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.in_main += 1
        elif tag == "img" and self.in_main:
            self.imgs.append((a.get("src", ""), a.get("alt")))

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main -= 1


def alt_text(site, pages):
    out = {}
    for p in pages:
        path = os.path.join(site, p, "index.html") if p.endswith("/") else os.path.join(site, p)
        if not os.path.exists(path):
            continue
        s = ImgScan()
        s.feed(open(path, encoding="utf-8").read())
        missing = [src for src, alt in s.imgs if alt is None or not alt.strip()]
        with_number = sum(1 for _, alt in s.imgs if alt and re.search(r"\d", alt))
        out[p] = {"images": len(s.imgs), "missing_alt": missing, "alt_with_number": with_number}
    return out


def code_parity(src):
    inc = os.path.join(src, "_includes", "code")
    ex = os.path.join(src, "examples", "family_d")
    if not os.path.isdir(inc):
        return {"status": "not applicable", "files": {}}
    digest = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    scripts = {}
    if os.path.isdir(ex):
        for f in sorted(os.listdir(ex)):
            if f.endswith(".py"):
                scripts.setdefault(digest(os.path.join(ex, f)), []).append(f)
    files = {}
    for f in sorted(os.listdir(inc)):
        p = os.path.join(inc, f)
        if os.path.isfile(p):
            match = scripts.get(digest(p))
            files[f] = match[0] if match else None
    status = "pass" if files and all(files.values()) else "fail"
    return {"status": status, "files": files}


def link_check(site):
    folds = sum(len(check_checklist_links.scan(os.path.join(site, p)).folds)
                for p in check_checklist_links.PAGES if os.path.exists(os.path.join(site, p)))
    if folds == 0:
        return {"status": "not applicable", "folds": 0, "links": 0, "problems": []}
    problems, checked = check_checklist_links.check(site)
    return {"status": "pass" if not problems else "fail", "folds": folds,
            "links": checked, "problems": problems}


def summarize(results):
    by_rule = collections.Counter()
    per_page = {}
    for key, r in results["browser"]["pages"].items():
        if "error" in r:
            per_page[key] = {"error": r["error"]}
            continue
        counts = collections.Counter()
        for v in r["violations"]:
            counts[v["id"]] += len(v["nodes"])
            by_rule[v["id"]] += len(v["nodes"])
        per_page[key] = {"violations": dict(counts), "overflowPx": r["overflowPx"],
                         "brokenImages": r.get("brokenImages", [])}
    return dict(sorted(by_rule.items())), per_page


def page_sources(src):
    """Map each built page (such as piechart.html) to the Markdown or HTML file that makes it."""
    out = {}
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_site")) and d not in ("examples", "node_modules", "vendor")]
        for f in files:
            if not f.endswith((".md", ".html")):
                continue
            path = os.path.join(root, f)
            try:
                head = open(path, encoding="utf-8").read(2000)
            except (OSError, UnicodeDecodeError):
                continue
            m = re.match(r"---\s*\n(.*?)\n---", head, re.S)
            if not m:
                continue
            pm = re.search(r"^permalink:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", m.group(1), re.M)
            if not pm:
                continue
            link = pm.group(1).strip().lstrip("/")
            out[link or "index.html"] = os.path.relpath(path, src)
    return out


def _one_line(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip().replace("`", "'")
    if len(text) <= limit:
        return text
    cut = text[: limit - 3]
    if " " in cut[limit // 2:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ;,") + "..."


def _why(summary):
    """Turn axe's failureSummary into one plain sentence group."""
    parts, cur = [], None
    for line in (summary or "").splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("fix any of the following"):
            cur = ["Fix one of these:", []]
            parts.append(cur)
        elif low.startswith("fix all of the following"):
            cur = ["Fix all of these:", []]
            parts.append(cur)
        else:
            if cur is None:
                cur = ["", []]
                parts.append(cur)
            cur[1].append(line.rstrip("."))
    text = " ".join((h + " " if h else "") + "; ".join(items) + "." for h, items in parts if items)
    return _one_line(text, 500)


def what_to_fix(res):
    """Build the "What to fix" section of summary.md."""
    pages = res["pages"]
    sources = res.get("page_sources", {})
    # (page, rule) -> {"rule": violation info, "elements": {(target, html): {...}}}
    found = collections.OrderedDict()
    for key, r in res["browser"]["pages"].items():
        width, page = key.split(" ", 1)
        if "error" in r:
            continue
        for v in r["violations"]:
            slot = found.setdefault((page, v["id"]), {"rule": v, "elements": collections.OrderedDict()})
            for n in v["nodes"]:
                e = slot["elements"].setdefault((n["target"], n["html"]), {"widths": [], "why": n.get("failureSummary", "")})
                if width not in e["widths"]:
                    e["widths"].append(width)
    # Identical elements failing the same rule on many pages usually come from the shared layout.
    spread = collections.defaultdict(set)
    for (page, rule), slot in found.items():
        for el in slot["elements"]:
            spread[(rule, el)].add(page)
    shared = {k: v for k, v in spread.items() if len(v) >= SHARED_MIN_PAGES}

    def label(page):
        src = sources.get(page)
        group = "Family D" if page in FAMILY_D else "other page"
        return f"`{page}` ({group}" + (f", file `{src}`" if src else "") + ")"

    def element_lines(target, html, info, show_why=True):
        widths = " and ".join(WIDTHS[w] for w in info["widths"])
        L = [f"- Element `{_one_line(target, 140)}` at {widths}",
             f"  - HTML: `{_one_line(html, 120)}`"]
        why = _why(info["why"])
        if why and show_why:
            L.append(f"  - Why: {why}")
        return L

    def rule_block(v, counts, elements, extra=None):
        """Rule heading, one shared "Why" when every shown element has the same reason, then the elements."""
        impact = f"{v['impact']}, " if v.get("impact") else ""
        guide = f" [How to fix]({v['helpUrl']})" if v.get("helpUrl") else ""
        out = [f"**{v['id']}** ({impact}{counts}): {v.get('help', '')}.{guide}", ""]
        shown = elements[:MAX_ELEMENTS]
        reasons = {_why(info["why"]) for _, info in shown}
        common = len(shown) > 1 and len(reasons) == 1 and "" not in reasons
        if common:
            out += [f"Why (same for each element below): {reasons.pop()}", ""]
        for (target, html), info in shown:
            out += element_lines(target, html, info, show_why=not common)
            if extra:
                out += extra((target, html))
        if len(elements) > MAX_ELEMENTS:
            more = len(elements) - MAX_ELEMENTS
            out.append(f"- ...and {more} more element{'' if more == 1 else 's'} for this rule (see results.json).")
        return out + [""]

    def plural(n, word):
        return f"{n} {word}{'' if n == 1 else 's'}"

    L = ["## What to fix", "",
         "Each item names the page, the screen width, the element that failed (its CSS selector and the start of its HTML), "
         "why it failed, and a link to a guide for fixing it. Problems repeated on several pages come first, then the Family D pages, then the other pages. "
         f"An element that fails at both widths is listed once. At most {MAX_ELEMENTS} elements are shown for one rule on one page; "
         "the counts include every element, and results.json has the full list.", ""]
    any_item = False

    if shared:
        any_item = True
        L += ["### Problems repeated on several pages", "",
              "The same element fails the same rule on each page listed. Check whether it comes from a shared file, "
              "such as `_layouts/default.html`, or from the same Markdown on each page, such as `- [ ]` checkboxes. "
              "The same kind of fix usually works on every page listed.", ""]
        by_rule = collections.OrderedDict()
        for (rule, el), pgs in shared.items():
            by_rule.setdefault(rule, []).append((el, pgs))
        for rule, items in by_rule.items():
            v = next(slot["rule"] for (p, r), slot in found.items() if r == rule)
            pg_of = dict(items)
            elements = []
            for el, pgs in items:
                first = next(p for p in pages if p in pgs)
                elements.append((el, found[(first, rule)]["elements"][el]))
            L += rule_block(v, plural(len(items), "element") + " repeated across pages", elements,
                            extra=lambda el: [f"  - Pages ({len(pg_of[el])}): " + ", ".join(f"`{p}`" for p in pages if p in pg_of[el])])

    per_page = res["summary"]["per_page"]
    for page in pages:
        items = []
        for width in WIDTHS:
            v = per_page.get(f"{width} {page}", {})
            if "error" in v:
                items.append(f"- The page did not load at {WIDTHS[width]}: {v['error']}.")
            elif v.get("overflowPx", 0) > 0:
                items.append(f"- The page is {v['overflowPx']} px wider than the screen at {WIDTHS[width]}, so readers must scroll sideways.")
        broken = sorted({s for w in WIDTHS for s in per_page.get(f"{w} {page}", {}).get("brokenImages", [])})
        items += [f"- Image did not load: `{b}`." for b in broken]
        alt = res.get("alt_text", {}).get(page, {})
        items += [f"- Image has no alt text: `{m}`." for m in alt.get("missing_alt", [])]
        rules_here = [(rule, slot) for (p, rule), slot in found.items() if p == page]
        for rule, slot in rules_here:
            own = [(el, info) for el, info in slot["elements"].items() if (rule, el) not in shared]
            n_shared = len(slot["elements"]) - len(own)
            fails = per_page.get(f"desktop {page}", {}).get("violations", {}).get(rule, 0) + \
                per_page.get(f"phone {page}", {}).get("violations", {}).get(rule, 0)
            counts = f"{plural(len(slot['elements']), 'element')}, {plural(fails, 'failure')} counting both widths"
            if n_shared:
                counts += f"; {n_shared} listed under repeated problems"
            if items:
                items.append("")
            if own:
                items += rule_block(slot["rule"], counts, own)[:-1]
            else:
                impact = f"{slot['rule']['impact']}, " if slot["rule"].get("impact") else ""
                items += [f"**{rule}** ({impact}{counts}): {slot['rule'].get('help', '')}."]
        if items:
            any_item = True
            L += [f"### {label(page)}", ""] + items + [""]

    lc = res["link_check"]
    if lc["status"] == "fail":
        any_item = True
        L += ["### Checklist links (Family D pages)", ""] + [f"- {p}" for p in lc["problems"]] + [""]
    cp = res["code_parity"]
    bad = [f for f, m in cp["files"].items() if not m]
    if bad:
        any_item = True
        L += ["### Code panels", ""] + [f"- `_includes/code/{f}` is not identical to any script in `examples/family_d/`. "
                                        "Copy the script into the include file again so the code panel matches the chart." for f in bad] + [""]
    clean = [p for p in pages if not any(p == q for q, _ in found) and all(
        "error" not in per_page.get(f"{w} {p}", {}) and not per_page.get(f"{w} {p}", {}).get("overflowPx")
        and not per_page.get(f"{w} {p}", {}).get("brokenImages") for w in WIDTHS)
        and not res.get("alt_text", {}).get(p, {}).get("missing_alt")]
    if any_item and clean:
        L += ["### Pages with no automated problems found", "", ", ".join(f"`{p}`" for p in clean), ""]
    if not any_item:
        L += ["Nothing to fix was found on the checked pages. Automated checks find only part of the possible WCAG issues, "
              "so keyboard, zoom, and screen reader review is still needed.", ""]
    return L


def write_summary(res, path):
    by_rule, per_page = res["summary"]["by_rule"], res["summary"]["per_page"]
    L = [f"# Check results: {res['label']}", "",
         f"Source: {res['source']} (commit {res['commit']}). Checked {len(res['pages'])} pages at 1280 px and 390 px.", "",
         "Automated checks find only part of the possible WCAG issues. These results are not a Section 508 conformance review.", ""]
    fam = sum(n for k, v in per_page.items() if k.split(" ", 1)[1] in FAMILY_D for n in v.get("violations", {}).values())
    oth = sum(n for k, v in per_page.items() if k.split(" ", 1)[1] not in FAMILY_D for n in v.get("violations", {}).values())
    lc = res["link_check"]
    L += ["## At a glance", "",
          f"- axe-core failures on the Family D pages: {fam} elements (both widths).",
          f"- axe-core failures on the other checked pages: {oth} elements (both widths).",
          f"- Checklist links on the Family D pages: {lc['status']} ({lc['links']} links checked).",
          f"- Code panels match their scripts: {res['code_parity']['status']}.", ""]
    L += what_to_fix(res)
    L += ["## axe-core failures by rule (elements, both widths)", "", "| Rule | Elements |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in by_rule.items()] or ["| none | 0 |"]
    L += ["", "## Per page", "", "| Width and page | Failures by rule | Sideways overflow (px) | Images that did not load |", "|---|---|---:|---:|"]
    for k, v in per_page.items():
        if "error" in v:
            L.append(f"| {k} | {v['error']} | | |")
        else:
            rules = ", ".join(f"{r} {n}" for r, n in sorted(v["violations"].items())) or "none"
            L.append(f"| {k} | {rules} | {v['overflowPx']} | {len(v['brokenImages'])} |")
    L += ["", "## Checklist links", "", f"Status: {lc['status']}. Folds: {lc['folds']}. Links checked: {lc['links']}."]
    L += [f"- {p}" for p in lc["problems"]]
    cp = res["code_parity"]
    L += ["", "## Code-include parity", "", f"Status: {cp['status']}."]
    L += [f"- `_includes/code/{f}`: " + (f"identical to `examples/family_d/{m}`" if m else "no identical script found")
          for f, m in cp["files"].items()]
    L += ["", "## Image alt text", "", "| Page | Images | Missing alt | Alt text with a number |", "|---|---:|---:|---:|"]
    L += [f"| {p} | {a['images']} | {len(a['missing_alt'])} | {a['alt_with_number']} |" for p, a in res["alt_text"].items()]
    broken = sorted({f"{k.split(' ', 1)[1]}: {src}" for k, v in per_page.items() for src in v.get("brokenImages", [])})
    if broken:
        L += ["", "## Images that did not load", ""] + [f"- `{b}`" for b in broken]
    if res.get("screenshots"):
        L += ["", "## Screenshots", ""]
        base = os.path.dirname(os.path.abspath(path))
        L += [f"- {s['viewport']} {s['view']}: `{os.path.relpath(s['file'], base)}`" + ("" if s["targetFound"] else " (section not on this version; page top shown)")
              for s in res["screenshots"]]
    open(path, "w").write("\n".join(L) + "\n")


def local_commit(src):
    """Short commit id of a local checkout, or "local" when it is not a git folder."""
    sha = os.environ.get("GITHUB_SHA") if os.environ.get("GITHUB_ACTIONS") == "true" else None
    if sha:
        return sha[:7]
    try:
        r = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "local"
    except (OSError, subprocess.SubprocessError):
        return "local"


def cmd_run(a):
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    work = tempfile.mkdtemp(prefix="checks-")
    if a.branch:
        src, commit = download_branch(a.repo, a.branch, work)
        source = f"{a.repo} branch {a.branch}"
    else:
        src, commit, source = os.path.abspath(a.src), local_commit(os.path.abspath(a.src)), f"local folder {a.src}"
        if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY"):
            source = f"{os.environ['GITHUB_REPOSITORY']} {os.environ.get('GITHUB_REF_NAME', '')}".strip() + " (GitHub Actions)"
    site = build_site(src, os.path.join(out, "site"), a.jekyll, work)
    httpd, port = serve(os.path.join(out, "site"))
    pages = FAMILY_D + SHARED
    shot_dir = os.path.join(out, "screenshots")
    if a.screenshots:
        os.makedirs(shot_dir, exist_ok=True)
    cfg = {"nodeModules": a.node_modules, "chrome": a.chrome, "baseUrl": f"http://127.0.0.1:{port}/{BASEURL}/",
           "pages": pages, "axeTags": AXE_TAGS, "label": re.sub(r"[^\w.-]+", "-", a.label), "shotDir": shot_dir,
           "screenshots": SCREENSHOTS if a.screenshots else [], "resultFile": os.path.join(work, "browser.json")}
    cfg_path = os.path.join(work, "cfg.json")
    json.dump(cfg, open(cfg_path, "w"))
    r = subprocess.run(["node", os.path.join(HERE, "browser_checks.js"), cfg_path])
    httpd.shutdown()
    if r.returncode != 0:
        sys.exit("Browser checks failed.")
    browser = json.load(open(cfg["resultFile"]))
    res = {"label": a.label, "source": source, "commit": commit, "pages": pages, "browser": browser,
           "link_check": link_check(site), "code_parity": code_parity(src),
           "alt_text": alt_text(site, pages), "screenshots": browser["screenshots"],
           "page_sources": {p: f for p, f in page_sources(src).items() if p in pages}}
    by_rule, per_page = summarize(res)
    res["summary"] = {"by_rule": by_rule, "per_page": per_page}
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)
    write_summary(res, os.path.join(out, "summary.md"))
    shutil.rmtree(work, ignore_errors=True)
    print(f"Wrote {os.path.join(out, 'summary.md')} and results.json")
    lc = res["link_check"]
    print(f"axe-core failures: {sum(by_rule.values())} elements. Checklist links: {lc['status']}.")
    if a.fail_on_broken_links and lc["status"] == "fail":
        sys.exit(f"Checklist link check failed on the Family D pages ({len(lc['problems'])} problems). See summary.md.")


def cmd_compare(a):
    b, c = json.load(open(a.before)), json.load(open(a.after))
    rules = sorted(set(b["summary"]["by_rule"]) | set(c["summary"]["by_rule"]))
    L = [f"| Measure | {b['label']} | {c['label']} |", "|---|---:|---:|"]
    for r in rules:
        L.append(f"| axe `{r}` (elements, both widths) | {b['summary']['by_rule'].get(r, 0)} | {c['summary']['by_rule'].get(r, 0)} |")
    tot = lambda x: sum(x["summary"]["by_rule"].values())
    L.append(f"| axe total (elements, both widths) | {tot(b)} | {tot(c)} |")
    def group(x, pages):
        return sum(n for k, v in x["summary"]["per_page"].items() if k.split(" ", 1)[1] in pages
                   for n in v.get("violations", {}).values())
    L.append(f"| axe total, Family D pages | {group(b, FAMILY_D)} | {group(c, FAMILY_D)} |")
    L.append(f"| axe total, other pages | {group(b, SHARED)} | {group(c, SHARED)} |")
    nf = lambda x: sum(1 for v in x["summary"]["per_page"].values() if "error" in v)
    L.append(f"| Page views that did not load | {nf(b)} | {nf(c)} |")
    of = lambda x: sum(1 for v in x["summary"]["per_page"].values() if v.get("overflowPx", 0) > 0)
    L.append(f"| Page views wider than the screen | {of(b)} | {of(c)} |")
    lk = lambda x: f"{x['link_check']['status']} ({x['link_check']['links']} links)"
    L.append(f"| Checklist links | {lk(b)} | {lk(c)} |")
    cp = lambda x: f"{x['code_parity']['status']} ({sum(1 for m in x['code_parity']['files'].values() if m)} of {len(x['code_parity']['files'])})"
    L.append(f"| Code-include parity | {cp(b)} | {cp(c)} |")
    al = lambda x: sum(len(v["missing_alt"]) for v in x["alt_text"].values())
    L.append(f"| Images without alt text | {al(b)} | {al(c)} |")
    bi = lambda x: len({(k.split(' ', 1)[1], s) for k, v in x["summary"]["per_page"].items() for s in v.get("brokenImages", [])})
    L.append(f"| Images that did not load (unique, checked pages) | {bi(b)} | {bi(c)} |")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="build, serve, and check one copy of the site")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--src", help="local repository folder")
    g.add_argument("--branch", help="branch to download from GitHub")
    r.add_argument("--repo", default="jjjessah/data_viz_guidance", help="GitHub owner/name for --branch")
    r.add_argument("--label", required=True, help="short name for this run, such as before or after")
    r.add_argument("--out", required=True, help="folder for results, the built site, and screenshots")
    r.add_argument("--screenshots", action="store_true", help="also save screenshots at both widths")
    r.add_argument("--fail-on-broken-links", action="store_true",
                   help="exit with code 1 when the checklist link check on the Family D pages fails")
    r.add_argument("--jekyll", default="bundle exec jekyll", help="command that runs Jekyll")
    r.add_argument("--node-modules", default=os.environ.get("CHECKER_NODE_MODULES", os.path.join(HERE, "node_modules")),
                   help="folder with playwright-core and axe-core")
    r.add_argument("--chrome", default=os.environ.get("CHECKER_CHROME", "/usr/bin/google-chrome"),
                   help="path to Chrome or Chromium")
    r.set_defaults(func=cmd_run)
    c = sub.add_parser("compare", help="compare two results.json files")
    c.add_argument("before")
    c.add_argument("after")
    c.set_defaults(func=cmd_compare)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
