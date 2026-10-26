---
layout: default
title: How to use this site
permalink: how-to-use.html
description: "Orientation for developers and capstone contributors using the Data Visualization Guidance site."
---

# How to use this site

Use this page as a short orientation before editing guidance or building a new visualization.

## For developers publishing a visual

1. Start with the visualization type that matches your analytical task.
2. Cross-check shared component pages: **Titles**, **Color**, **Axes**, **Legends**, **Sources**, and **508 Compliance**.
3. Confirm the visual can stand alone: title, labels, source, and notes should make the message clear without surrounding narrative.
4. Provide an accessible fallback (alt text and, when needed, a data table or downloadable CSV).

## For capstone contributors

### Phase 1 — Collaborative foundation

- Review pages for unclear structure, placeholder metadata, broken links, and accessibility gaps.
- Keep naming, permalinks, and front matter consistent.
- Submit focused pull requests that improve shared structure before large individual features.

### Phase 2 — Individual proposed work

- Propose a feature track (architecture, code recipes, accessibility, new pages, or UX).
- Prefer public data from [data.census.gov](https://data.census.gov/) or the Census API.
- Document assumptions, libraries, and how reviewers can reproduce your examples.

## Front matter conventions

Guidance pages should include:

```yaml
layout: default
title: Example Page
permalink: example.html
tags: [Comparison]
description: "One sentence explaining what the page helps a reader do."
```

- Use existing tags when possible: `Comparison`, `Distribution`, `Correlation`, `Geospatial`, `Accessibility`.
- Keep descriptions specific. Avoid placeholders such as "Short Description of …".

## Local preview

```bash
bundle install
bundle exec jekyll serve
```

Then open `http://localhost:4000/data_viz_guidance/`.

If you are previewing from a fork, temporarily update `url` and `baseurl` in `_config.yml`, and restore the upstream values before opening a pull request.
