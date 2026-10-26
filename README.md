# Data Visualization Guidance (Draft)

Open draft guidance that helps federal developers publish clear, quality-compliant, and accessible Census Bureau data visualizations.

**Live site:** [emolfino-census.github.io/data_viz_guidance](https://emolfino-census.github.io/data_viz_guidance/)  
**Upstream repository:** [emolfino-census/data_viz_guidance](https://github.com/emolfino-census/data_viz_guidance)

> Important: This repository is for draft, exploratory, and internal development purposes only. It is not an official U.S. government site and should not be treated as finalized Census Bureau guidance.

## Purpose

This capstone project expands the existing GitHub Pages draft into a more consistent public resource by improving:

- Site architecture, navigation, and tagging
- Modular component documentation
- Section 508 / accessibility expectations
- Reproducible Python and R examples using public Census data

## Repository layout

```text
data_viz_guidance/
├── _layouts/                 # Site layouts (default, tag pages)
├── assets/css/               # Theme overrides and site styles
├── assets/js/                # Lightweight UI scripts
├── component/                # Cross-cutting guidance (color, axes, 508, …)
├── visualization_type/       # Chart and map guidance pages
├── tags/                     # Tag landing pages
├── additional_info/          # References and supporting material
├── data/                     # Public demo datasets
├── scripts/python/           # Python recipes
├── scripts/r/                # R recipes
├── index.md                  # Home page
├── how-to-use.md             # Contributor and developer orientation
├── CONTRIBUTING.md           # Contribution workflow
└── _config.yml               # Jekyll / GitHub Pages configuration
```

## Local development

### Prerequisites

- Git
- Ruby + Bundler (for Jekyll)
- Optional: Python 3.10+ and R 4.2+ for code recipes

### Run the site

```bash
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000/data_viz_guidance/`.

If you fork the repository and enable GitHub Pages on your account, temporarily update `url` and `baseurl` in `_config.yml`. Restore the upstream values before submitting a pull request.

## Capstone workflow

1. **Phase 1 — Collaborative foundation:** review the site, divide pages, and submit structural/content consistency improvements.
2. **Phase 2 — Individual proposed work:** develop a focused enhancement track and submit pull requests with documentation and demos.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [how-to-use.md](how-to-use.md) for details.

## Quality references

- [Census Bureau Statistical Quality Standards](https://www2.census.gov/about/policies/quality/quality-standards.pdf)
- U.S. Web Design System (USWDS) data visualization guidance
- Urban Institute Graphics Style Guide
- CFPB data visualization guidelines
- IBM Carbon data visualization guidance

## Contact

Open a GitHub Issue in this repository or coordinate through the Capstone sponsor mentors.
