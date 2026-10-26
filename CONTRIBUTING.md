# Contributing

Thank you for helping improve the Census Bureau Data Visualization Guidance draft site.

This repository supports a UMGC DATA 690 Capstone sponsored by the U.S. Census Bureau. Content is exploratory and is not official finalized guidance.

## Workflow

1. Fork the upstream repository (`emolfino-census/data_viz_guidance`) or work from your assigned fork.
2. Create a feature branch for your changes.
3. Make focused updates to assigned pages or proposed features.
4. Preview locally with Jekyll when possible.
5. Open a pull request into the upstream `main` branch.

### Phase 1 (Weeks 1–2): Collaborative foundation

- Improve consistency of metadata, navigation, tagging, and shared layout.
- Prefer small, reviewable pull requests.
- Coordinate page ownership with teammates to avoid conflicting edits.

### Phase 2 (Weeks 3+): Individual feature tracks

- Propose a focus area such as architecture, accessibility, code recipes, or new guidance pages.
- Include reproducible Python and/or R examples when adding implementation guidance.
- Use only public data (for example, data.census.gov).

## Content standards

- Write clear, actionable guidance. Prefer concrete do/avoid rules over vague advice.
- Keep front matter complete: `title`, `permalink`, `description`, and `tags` when relevant.
- Preserve permalinks unless a rename is intentional and coordinated.
- Add alt text for images and keep contrast readable.
- Cite sources and data vintages for any example that uses data.

## Code recipe standards

- Place shared demo data in `data/`.
- Place scripts in `scripts/python/` and `scripts/r/`.
- Prefer open-source libraries and self-contained examples.
- Note required packages and expected outputs in the related guidance page.

## Pull request checklist

- [ ] Description explains the problem and the change
- [ ] Related pages were reviewed for consistency
- [ ] No secrets or non-public data were added
- [ ] Images include meaningful alt text
- [ ] `_config.yml` still points at the upstream GitHub Pages `url` / `baseurl` unless the PR is intentionally changing hosting
