# Accessibility and consistency checker

`run_checks.py` builds one copy of the site with Jekyll, serves it on this computer, and records:

- axe-core results by rule (WCAG 2.0 to 2.2, levels A and AA, plus best-practice rules) at 1280 px and 390 px wide, with every folding section opened
- pages that are wider than the screen, and pages that do not load
- the checklist link check (`check_checklist_links.py`): every "Read the full section" link must reach a heading that exists, and a fold without that link must say "Does not apply to this page."
- code-include parity: each file in `_includes/code/` must be identical to a script in `examples/family_d/`
- image alt text, and images that do not load, on the checked pages

It checks all ten Family D pages, in eleven files: Pie Chart, Donut Chart, Sankey Diagram, Treemap, both Grids and Gridlines files (`grids-visualization-type.html` and `grid.html`), Mobile Design, Color, Interactive Chart, Notes, and 508 Compliance. It also checks five pages that share the site layout: Home, Bar Chart, Dual Axes, Titles, and the Distribution tag page. It can save matching screenshots at both widths.

Automated checks find only part of the possible WCAG issues. The results are not a Section 508 conformance review.

## Setup (once)

- Ruby with Bundler, then the gems in this folder's `Gemfile`:
  `BUNDLE_GEMFILE=examples/accessibility_check/Gemfile bundle install`
  The `Gemfile` pins `jekyll-relative-links` to 0.6.1, the version GitHub Pages uses, so image paths, including images inside links, behave the way they do on the live site.
- Node.js, with playwright-core and axe-core installed outside the repository so the site build does not copy them:
  `npm install --prefix ~/accessibility-check-tools playwright-core axe-core`
- Chrome or Chromium.

## Run

From the repository folder, with the results written outside the repository:

```
export BUNDLE_GEMFILE=examples/accessibility_check/Gemfile
export CHECKER_NODE_MODULES=~/accessibility-check-tools/node_modules
export CHECKER_CHROME=/usr/bin/google-chrome

python3 examples/accessibility_check/run_checks.py run --branch main --label before --out ~/checks/before --screenshots
python3 examples/accessibility_check/run_checks.py run --branch ux-visual-design --label after --out ~/checks/after --screenshots
python3 examples/accessibility_check/run_checks.py compare ~/checks/before/results.json ~/checks/after/results.json
```

- `--branch` downloads that branch of `jjjessah/data_viz_guidance` from GitHub. Use `--repo owner/name` for another fork, or `--src .` to check the local folder.
- Each run writes `summary.md`, `results.json`, the built site, and (with `--screenshots`) PNG files to the `--out` folder.
- `compare` prints a Markdown table of the two runs, with totals for the Family D pages and for the other pages.

The build adds `jekyll-relative-links`, which GitHub Pages turns on by default, so relative image paths behave the way they do on the live site.

The checker does not run the chart scripts, does not call the Census Data API, and never reads `CENSUS_API_KEY`.
