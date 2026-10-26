---
layout: default
title: Data Visualization Guidance
permalink: /
description: "Draft Census Bureau guidance that helps developers create clear, accessible, and quality-compliant data visualizations."
---

# Make Census data visualizations clearer and easier to reuse

This site collects draft guidance, component patterns, and reproducible examples so federal developers can publish higher-quality charts and maps with less rework.

Developers should also reference the [Census Bureau Statistical Quality Standards](https://www2.census.gov/about/policies/quality/quality-standards.pdf) when designing and reviewing data visualizations.

<div class="home-hero-panel" role="note">
  <strong>Capstone draft.</strong> Content is exploratory and evolving. It is not finalized Census Bureau policy. Contributions follow a two-phase workflow: collaborative foundation updates first, then individual feature tracks.
</div>

## Start here

<div class="home-grid">
  <section class="home-card">
    <h2>Visualization types</h2>
    <p>Choose the right chart or map for your comparison, distribution, correlation, or geospatial question.</p>
    <a href="{{ site.baseurl }}/barchart.html">Browse chart guidance →</a>
  </section>
  <section class="home-card">
    <h2>Components</h2>
    <p>Apply shared building blocks: color, axes, legends, titles, notes, sources, and Section 508 requirements.</p>
    <a href="{{ site.baseurl }}/color.html">Browse components →</a>
  </section>
  <section class="home-card">
    <h2>Explore by tag</h2>
    <p>Filter pages by analytical intent such as Comparison, Distribution, Correlation, Geospatial, or Accessibility.</p>
    <a href="{{ site.baseurl }}/tags/comparison/">Open tag index →</a>
  </section>
  <section class="home-card">
    <h2>Code recipes</h2>
    <p>Reproduce examples in Python and R using public ACS-style data under <code>data/</code> and <code>scripts/</code>.</p>
    <a href="{{ site.baseurl }}/barchart.html#developer-implementation">See bar chart recipe →</a>
  </section>
</div>

## How this site is organized

1. **Visualization types** explain when to use a chart or map, what to do, and what to avoid.
2. **Components** cover cross-cutting design decisions that apply across many visuals.
3. **Tags** help you find pages by analytical task instead of browsing alphabetically.
4. **References** point to Census quality standards and external design systems used as benchmarks.

## Quality expectations

Every public visualization should:

- Communicate a clear message in the title and support it with readable encodings
- Cite the data source, vintage, and relevant methodology notes
- Meet Section 508 / WCAG expectations, including alt text and accessible data tables when needed
- Prefer reproducible open-source workflows over one-off screenshots when code is provided

## Next steps for contributors

Read [How to use this site]({{ site.baseurl }}/how-to-use.html) and [CONTRIBUTING.md](https://github.com/emolfino-census/data_viz_guidance/blob/main/CONTRIBUTING.md) before opening a pull request.
