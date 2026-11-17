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

  compare  Put two saved runs side by side in one Markdown table.

Examples:
  python3 run_checks.py run --branch main --label before --out ~/checks/before --screenshots
  python3 run_checks.py run --src /path/to/repo --label after --out ~/checks/after
  python3 run_checks.py compare ~/checks/before/results.json ~/checks/after/results.json 

The script never reads or prints CENSUS_API_KEY, and it does not call the Census Data API.
Automated checks find only part of the possible WCAG issues; they are not a Section 508
conformance review.
"""
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


def write_summary(res, path):
    by_rule, per_page = res["summary"]["by_rule"], res["summary"]["per_page"]
    L = [f"# Check results: {res['label']}", "",
         f"Source: {res['source']} (commit {res['commit']}). Checked {len(res['pages'])} pages at 1280 px and 390 px.", "",
         "Automated checks find only part of the possible WCAG issues. These results are not a Section 508 conformance review.", "",
         "## axe-core failures by rule (elements, both widths)", "", "| Rule | Elements |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in by_rule.items()] or ["| none | 0 |"]
    L += ["", "## Per page", "", "| Width and page | Failures by rule | Sideways overflow (px) | Images that did not load |", "|---|---|---:|---:|"]
    for k, v in per_page.items():
        if "error" in v:
            L.append(f"| {k} | {v['error']} | |")
        else:
            rules = ", ".join(f"{r} {n}" for r, n in sorted(v["violations"].items())) or "none"
            L.append(f"| {k} | {rules} | {v['overflowPx']} | {len(v['brokenImages'])} |")
    lc = res["link_check"]
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
        L += [f"- {s['viewport']} {s['view']}: `{s['file']}`" + ("" if s["targetFound"] else " (section not on this version; page top shown)")
              for s in res["screenshots"]]
    open(path, "w").write("\n".join(L) + "\n")


def cmd_run(a):
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    work = tempfile.mkdtemp(prefix="checks-")
    if a.branch:
        src, commit = download_branch(a.repo, a.branch, work)
        source = f"{a.repo} branch {a.branch}"
    else:
        src, commit, source = os.path.abspath(a.src), "local", f"local folder {a.src}"
    site = build_site(src, os.path.join(out, "site"), a.jekyll, work)
    httpd, port = serve(os.path.join(out, "site"))
    pages = FAMILY_D + SHARED
    shot_dir = os.path.join(out, "screenshots")
    if a.screenshots:
        os.makedirs(shot_dir, exist_ok=True)
    cfg = {"nodeModules": a.node_modules, "chrome": a.chrome, "baseUrl": f"http://127.0.0.1:{port}/{BASEURL}/",
           "pages": pages, "axeTags": AXE_TAGS, "label": a.label, "shotDir": shot_dir,
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
           "alt_text": alt_text(site, pages), "screenshots": browser["screenshots"]}
    by_rule, per_page = summarize(res)
    res["summary"] = {"by_rule": by_rule, "per_page": per_page}
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)
    write_summary(res, os.path.join(out, "summary.md"))
    shutil.rmtree(work, ignore_errors=True)
    print(f"Wrote {os.path.join(out, 'summary.md')} and results.json")


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
