# Accessibility and consistency checker

`run_checks.py` builds one copy of the site with Jekyll, serves it on this computer, and records:

- axe-core results by rule (WCAG 2.0 to 2.2, levels A and AA, plus best-practice rules) at 1280 px and 390 px wide, with every folding section opened
- pages that are wider than the screen, and pages that do not load
- the checklist link check (`check_checklist_links.py`): every "Read the full section" link must reach a heading that exists, and a fold without that link must say "Does not apply to this page."
- code-include parity: each file in `_includes/code/` must be identical to a script in `examples/family_d/`
- image alt text, and images that do not load, on the checked pages

It checks all ten Family D pages, in eleven files: Pie Chart, Donut Chart, Sankey Diagram, Treemap, both Grids and Gridlines files (`grids-visualization-type.html` and `grid.html`), Mobile Design, Color, Interactive Chart, Notes, and 508 Compliance. It also checks five pages that share the site layout: Home, Bar Chart, Dual Axes, Titles, and the Distribution tag page. It can save matching screenshots at both widths.

Automated checks find only part of the possible WCAG issues. The results are not a Section 508 conformance review.

## What the results show

Each run writes `summary.md`. It opens with "At a glance" totals and a "What to fix" list. For each failing element, the list gives:

- the page, the source file that makes it (for example `visualization_type/PieChart.md`), and the screen width (desktop 1280 px or phone 390 px)
- the element: its CSS selector and the start of its HTML
- why it failed, in axe-core's words (for example the measured contrast ratio and the ratio required)
- a "How to fix" link to the rule's guide

Problems that repeat on several pages are listed once. At most five elements are shown for one rule on one page; the counts include every element, and `results.json` has the full list. Tables with counts by rule and by page follow the list.

## See results on GitHub

The workflow `.github/workflows/accessibility-check.yml` runs this checker on GitHub's computers. Nothing needs to be installed. It runs by itself after every commit to any branch (except `gh-pages`) and on pull requests from other forks. It can also be started by hand.

1. Commit a change to a branch, for example with **Commit changes** in the GitHub editor or with **Upload files**.
2. Open the **Actions** tab at the top of the repository.
3. In the list, click the newest run named **Accessibility check**. A yellow dot means it is still running, which usually takes a few minutes. A green check means it finished. A red X means a checklist link is broken or the site did not build.
4. On the run page, stay on **Summary** and scroll down. The checker's report appears there, starting with "At a glance" and "What to fix".
5. For screenshots and the full data, scroll to **Artifacts** at the bottom of the Summary and click **accessibility-results** to download a zip file. It holds `summary.md`, `results.json`, and the `screenshots` folder.
6. Open the source file named in "What to fix", find the element (the HTML snippet shows its text), and make the change. The "How to fix" link explains the rule.
7. Commit the fix to the same branch. The check runs again. Open the new run and confirm the item is gone.

To start a run by hand: **Actions** tab, **Accessibility check** in the left list, **Run workflow**, choose the branch, then **Run workflow**.

On a pull request page, the check also appears near the bottom in the checks box. Click **Details** next to **Accessibility check**, then **Summary**, to reach the same report.

The run does not fail because of axe-core failures, because some pages outside Family D still have known failures. Read the "What to fix" list on every run. The run fails (red X) only when the checklist link check on the Family D pages finds a broken link, or when the site does not build or the checker cannot finish. Downloaded results are kept for 30 days.

## Setup for running on a computer (once)

- Ruby with Bundler, then the gems in this folder's `Gemfile`:
  `BUNDLE_GEMFILE=examples/accessibility_check/Gemfile bundle install`
  The `Gemfile` pins `jekyll-relative-links` to 0.6.1, the version GitHub Pages uses, so image paths, including images inside links, behave the way they do on the live site.
- Node.js, with playwright-core and axe-core installed outside the repository so the site build does not copy them:
  `npm install --prefix ~/accessibility-check-tools playwright-core axe-core`
- Chrome or Chromium.

## Run on a computer

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
- Each run writes `summary.md`, `results.json`, the built site, and (with `--screenshots`) PNG files to the `--out` folder. Open `summary.md` in any text editor, or preview it as Markdown, to read "What to fix".
- `--fail-on-broken-links` ends the run with exit code 1 when the checklist link check on the Family D pages fails. The GitHub workflow uses it. axe-core failures never change the exit code.
- `compare` prints a Markdown table of the two runs, with totals for the Family D pages and for the other pages.

The build adds `jekyll-relative-links`, which GitHub Pages turns on by default, so relative image paths behave the way they do on the live site.

The checker does not run the chart scripts, does not call the Census Data API, and never reads `CENSUS_API_KEY`.
