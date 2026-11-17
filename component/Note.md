---
layout: default
title: Notes 
permalink: note.html
description: "How to use notes and captions to explain data visualization terms, context, limitations, and sources."
---

# Notes

## Purpose and Overview

Visualizations should be understandable on their own, even when embedded in a larger document, such as a working paper. Readers should be able to understand the main points without moving back and forth between the figure and the surrounding text.

Along with clear titles, subtitles, and axes, notes and captions provide:

* Clarity: Explain the meaning and intent of the visualization.
* Context: Supply background information needed to understand the data.
* Emphasis: Highlight important findings or qualifications.

Notes provide additional context, such as definitions of terms and symbols, information about the universe and sampling, and explanations of comparisons that are not statistically significant. Notes generally appear below the graphics within the visualization frame and begin with “Notes:”.

In some publications, captions provide a concise summary of the visualization and insights that may not be immediately apparent. Captions should be informative and understandable to readers unfamiliar with the subject. They appear directly below the visualization, outside its frame.

## When This Guidance Applies

Apply this guidance when a static or interactive visualization needs definitions, context, limitations, or other explanations beyond its title, axes, and legend.

In addition to this section, relevant guidance is in the 508 Compliance, Interactive Chart, Legends, and Titles sections.

## Essential Requirements

* In a static visualization, place notes at the bottom, either within the frame or adjacent to the graphic. Include only source statements below the notes.
* Place captions outside the visualization frame and adjacent to the visualization.
* In an interactive visualization, place notes at the bottom of the graphic or make them available through a clearly identified information button or pop-up. Use an accessible button with a descriptive name that can be operated with a keyboard; do not make notes available only on hover.

  Example information control:

  ![Information icon shown as a lowercase i inside a circle.](assets/Note3.png)

* Include DMS and DRB identifiers when required by the applicable review or publication process. Consult the Statistical Quality Standards and the requirements for the specific product.

## Recommended Practices

* Define jargon and symbols that are not explained in the legend.
* State the universe, meaning the population covered by the data, if it is not already clear from the title, legend, axes, or other nearby text.
* Explain relevant sampling information and statistical limitations.
* Identify comparisons that are not statistically significant when needed to prevent misinterpretation.
* Explain whether categories overlap when readers might otherwise assume that each observation belongs to only one category.
* Use plain language and include the details readers need to draw accurate conclusions.
* Keep notes close to the visualization and make them readable.
* Use a consistent source citation style. A recommended format is:

  Source: U.S. Census Bureau, [Program/Publication], [Page number], [Posted date/Date of source data], [Project No. ####### / Approval CBDRB-FY##-###], [URL or DOI], Accessed on [Date].

  Include the fields and identifiers that apply to the product.

## Practices to Avoid

* Do not leave technical terms or unexplained symbols for readers to interpret on their own.
* Do not omit information about the universe when its absence could change how readers interpret the data.
* Do not leave overlapping categories unexplained when readers might assume they are mutually exclusive.
* Do not hide essential qualifications in hover-only content.
* Do not make readers search the surrounding document for information needed to understand the visualization.

## Census Data Examples

***Example 1:*** Land Improvements to Pre-1950 Owner-Occupied Single Family Homes: 2019–2021

The note explains exclusions from the universe and defines a term used in the visualization. If a home can have more than one type of land improvement, the note should also explain that the categories are not mutually exclusive.

![Horizontal bar chart showing land improvements to pre-1950 owner-occupied single-family homes in 2019–2021. Landscaping or sprinkler system replacement is most common at 9.4 percent. The note explains that replacement includes additions, defines recreational structures, and excludes improvements to multiunit buildings because they were not asked about.](assets/Note1.png)

Source: [Cost of Improving and Maintaining Older Homes Higher for New Owners](https://www.census.gov/library/stories/2023/10/older-home-costs.html), U.S. Census Bureau story, October 12, 2023, Figure 3. The data come from the 2021 American Housing Survey.

***Example 2:*** A Demographic Portrait of Supplemental Nutrition Assistance Program (SNAP) in Select States

The note at the bottom provides additional context and includes DRB approval information. Include approval identifiers when required for the product.

![SNAP eligibility dashboard for Arizona, with tabs for Eligibility, Access, and Characteristics. Two county maps compare eligibility for the full population and children aged 0–17. Statewide estimates for 2019 to 2021 are 25.3 percent overall, plus or minus 0.7 percentage points, and 36.9 percent for children, plus or minus 1.5 percentage points. Notes and source information appear beneath the maps and summary graphics.](assets/Note2.png)

The note in the screenshot is small at this size. It says which states are included, that estimates with a potential disclosure risk are grayed out on the maps, and which Disclosure Review Board approvals cover the estimates.

Access the full visualization: [Supplemental Nutrition Assistance Program (SNAP) Eligibility & Access](https://www.census.gov/library/visualizations/interactive/snap-eligibility-access.html).

## Common Errors and Misinterpretations

| Issue | Why It Matters | Recommended Correction |
|---|---|---|
| Terms or symbols are not defined | Readers may misunderstand the data. | Define them in the note if they are not explained elsewhere. |
| The universe is unclear | Readers may assume the data cover a different population. | State the universe and relevant exclusions. |
| Overlapping categories are not explained | Readers may assume categories are mutually exclusive or add them incorrectly. | Explain that an observation can belong to more than one category, when applicable. |
| Relevant statistical limitations are missing | Readers may draw unsupported conclusions from comparisons. | Explain the limitations and relevant statistical significance information. |
| Notes are available only on hover | Touchscreen and keyboard users may not be able to access them. | Provide visible notes or an accessible information button. |
| Applicable approval identifiers are missing | Required review information may be incomplete. | Include the identifiers required for the specific product. |

## Publication Quality Checklist

<ul class="checklist-folds">
  <li>
    <details>
      <summary>The visualization fits the analytical question.</summary>
      <div class="checklist-fold-body">
        <p>A visualization should be understandable on its own. Notes and captions add the clarity, context, and emphasis readers need without moving back and forth between the figure and the surrounding text.</p>
        <p><a href="#purpose-and-overview">Read the full section: Purpose and Overview</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Relevant alternatives were considered.</summary>
      <div class="checklist-fold-body">
        <p>Notes go at the bottom of a static visualization, within the frame or next to the graphic, and begin with “Notes:”. Captions summarize the visualization and sit outside its frame, next to it. Choose the one that fits the publication.</p>
        <p><a href="#essential-requirements">Read the full section: Essential Requirements</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Data source, geography, reference period, and units are documented.</summary>
      <div class="checklist-fold-body">
        <p>Use a consistent source citation style, such as: Source: U.S. Census Bureau, [Program/Publication], [Page number], [Posted date/Date of source data], [Project No. / Approval], [URL or DOI], Accessed on [Date]. Only source statements go below the notes. Source line guidance is on the site-wide <a href="source.html">Sources</a> page.</p>
        <p><a href="#recommended-practices">Read the full section: Recommended Practices</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Data transformations and aggregation are appropriate.</summary>
      <div class="checklist-fold-body">
        <p>State the universe, meaning the population the data cover, when it is not already clear, and explain whether categories overlap. Example 1 explains which homes are excluded from the universe.</p>
        <p><a href="#recommended-practices">Read the full section: Recommended Practices</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Missing values and relevant uncertainty are addressed.</summary>
      <div class="checklist-fold-body">
        <p>Explain relevant sampling information and statistical limitations, and identify comparisons that are not statistically significant when needed to prevent misinterpretation. More on uncertainty is on the site-wide <a href="uncertainty.html">Visualizing Uncertainty</a> page.</p>
        <p><a href="#recommended-practices">Read the full section: Recommended Practices</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Existing accessibility, scaling, and axes guidance has been followed.</summary>
      <div class="checklist-fold-body">
        <p>In an interactive visualization, notes go at the bottom of the graphic or behind an accessible information button with a descriptive name that works with a keyboard, never on hover only. Full requirements are on the site-wide <a href="508.html">508 Compliance</a> page.</p>
        <p><a href="#essential-requirements">Read the full section: Essential Requirements</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Chart-specific limitations and caveats are explained.</summary>
      <div class="checklist-fold-body">
        <p>Do not leave technical terms, symbols, or overlapping categories unexplained, and do not make readers search the surrounding document for information needed to understand the visualization.</p>
        <p><a href="#practices-to-avoid">Read the full section: Practices to Avoid</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Code examples have been executed and verified.</summary>
      <div class="checklist-fold-body">
        <p>Does not apply to this page. This page has no code example.</p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>The visualization has undergone the appropriate review.</summary>
      <div class="checklist-fold-body">
        <p>Include DMS and DRB identifiers when the applicable review or publication process requires them, and consult the Statistical Quality Standards and the requirements for the specific product. Example 2 shows approval information in its note.</p>
        <p><a href="#essential-requirements">Read the full section: Essential Requirements</a></p>
      </div>
    </details>
  </li>
</ul>
 
## Related Pages
 
* [Sources](source.html): source lines and notes often sit together under a chart.
* [Titles](title.html): the title, subtitle, and notes should work as one information hierarchy.
* [Interactive Chart](interactivechart.html): do not place essential notes only in a hover popup.
* [Mobile Design for Interactive Visualizations](mobiledesign.html): notes need to remain readable when the layout reflows.
* [508 Compliance](508.html): text alternatives and visibility requirements that apply to notes as well as to the chart.
