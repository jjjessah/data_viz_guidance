---
layout: default
title: Grids and Gridlines
permalink: grids-visualization-type.html
description: "How to use gridlines and map graticules to support data reading without distracting from the data."
---

# Grids and Gridlines

## Purpose and Overview

Grids provide reference lines that help readers understand values and compare data points. They can improve precision in large charts and make subtle differences easier to see.

In line graphs, bar charts, and similar visualizations, gridlines help readers trace data points to values on the x- or y-axis. Gridlines are optional; use them when data points aren't directly labeled.

On maps, reference grids can help readers locate places beyond the geographic boundaries shown, such as county or state lines. Graticules show latitude and longitude. They can provide context on reference maps but are not always needed on thematic maps using Census Bureau data.

## When This Guidance Applies

Apply this guidance when deciding whether to include gridlines in a chart or graticules on a map, and when choosing their appearance.

In addition to the guidance provided in this section, relevant guidance can also be found in the Axes, Color, and Map Layout sections.

## Essential Requirements

* Use a subdued color, such as gray, that keeps gridlines visible without cluttering the visualization.
* Render gridlines behind data marks so they do not obscure points, bars, or lines. Gridlines may cross data marks; the concern is visual layering and readability, not preventing every intersection.
* Keep gridlines from interfering with labels and other text.

## Recommended Practices

* Use gridlines when they help readers trace unlabeled data points to axis values.
* Consider removing gridlines when direct labels already provide the values readers need.
* Keep gridlines visually secondary to the data.
* Use map graticules when latitude and longitude help readers understand location.
* Apply the same subdued styling to graticules so they do not distract from the map's contents.

## Practices to Avoid

* Do not draw gridlines over data marks in a way that obscures them.
* Do not use gridlines so prominent that they compete with the data.
* Avoid unnecessary gridlines when direct labels already make values clear.
* Do not add graticules to a thematic map unless they help readers interpret it.

## Accessibility
 
* Keep axis and tick labels at a contrast of at least 4.5:1 against the background, and make sure gridlines do not cross through text in a way that reduces that contrast.
* If readers must use the gridlines to read values, keep those lines at least 3:1 against the background. Even then, draw them thinner or lighter than the data so the series stays primary.
* Do not rely on gridlines alone when precise values matter. Use direct labels or provide a data table.
* On maps, add graticules only when they help interpretation, and keep their labels readable at the intended size.
* For full requirements, see the [508 Compliance](508.html), [Color](color.html), and [Axes](axes.html) pages. Meeting these bullets does not by itself mean a visualization is 508 compliant.
 

## Census Data Examples

***Example 1:*** Driving Alone is Still Popular

![Horizontal bar chart showing transportation to work in New York using 2016 American Community Survey estimates. Driving alone accounts for 52.6 percent, followed by public transportation at 28.4 percent. Light gray vertical gridlines mark the percentage scale, while each bar also has a direct value label.]({{ '/component/assets/grid1.png' | relative_url }})

This example demonstrates the following practice well:

* Soft gray gridlines remain in the background of the visualization.

This chart could be improved:

* Each bar is directly labeled so that the gridlines may be unnecessary. Consider removing them for a cleaner presentation.

***Example 2:*** Median Sales Price of New Single-Family Homes Sold

![Line chart showing median sales prices of new single-family homes sold from 2019 to 2023 for the United States and four regions, in thousands of dollars. Light gray horizontal gridlines help readers estimate prices. All series end higher than in 2019, with the Northeast highest in 2023. Region names directly label the lines at the right.]({{ '/component/assets/grid2.png' | relative_url }})

[View the Census Bureau housing story containing the example](https://www.census.gov/library/stories/2024/06/national-housing-month.html).

This example demonstrates the following practices well:

* Soft gray gridlines do not interfere with interpretation of the chart.
* Labels remain clear and readable.
* Gridlines help readers estimate values and interpret the chart.

## Developer Implementation

### Reproduce the New York commute example

The script draws the bar chart in Example 1 from the 2016 American Community Survey 1-year estimates, Table DP03, for New York state, keeping the six categories and their order from Example 1. It saves two versions. The first keeps thin gray vertical gridlines at every 10 percent, drawn behind the bars, to show how to style gridlines so they stay secondary to the data. The gridline color, #949494, has a 3:1 contrast ratio against the white background, so the gridlines remain usable on charts that depend on them; thin lines keep them visually behind the bars. The second, the recommended version, leaves out the gridlines and the percent axis, as suggested under Example 1, because every bar already has a direct value label. Gridlines are worth keeping when readers need to estimate values that are not labeled, such as in line graphs, scatter plots, dense time series, or small multiples that share an axis.

<a href="{{ '/examples/family_d/make_ny_commute_grid.py' | relative_url }}">Download the Python script</a>. It needs Python 3 and the matplotlib package. The program uses the saved table `examples/family_d/acs_dp03_ny_2016_commute.csv` so it can run offline. It calls the Census Data API only if that file is missing, or if the `--refresh` flag is used. To refresh the table, request a free Census Data API key at https://api.census.gov/data/key_signup.html and set it in the environment. Leave the key out of the program, this page, and the saved table:

<pre style="white-space: pre-wrap; overflow: visible;"><code>export CENSUS_API_KEY=API_KEY_VALUE
python3 examples/family_d/make_ny_commute_grid.py --refresh</code></pre>

Without `--refresh`, run:

<pre style="white-space: pre-wrap; overflow: visible;"><code>python3 examples/family_d/make_ny_commute_grid.py</code></pre>

The script saves [the version with gridlines]({{ '/assets/family-d/ny-commute-2016-gridlines.png' | relative_url }}) and [the recommended version]({{ '/assets/family-d/ny-commute-2016-recommended.png' | relative_url }}).

#### With gridlines (reproduces Example 1)

![Horizontal bar chart of means of transportation to work in New York using 2016 American Community Survey 1-year estimates. Of 9,291,557 workers 16 years and over, 52.6 percent drove alone and 28.4 percent used public transportation, followed by carpool at 6.5 percent, walked at 6.2 percent, worked at home at 4.3 percent, and other means at 2.0 percent. Thin gray vertical gridlines mark every 10 percent behind the bars, and each bar has a direct value label.]({{ '/assets/family-d/ny-commute-2016-gridlines.png' | relative_url }})

#### Recommended: without gridlines

![The same horizontal bar chart of means of transportation to work in New York in 2016, without gridlines or a percent axis. Each bar has a direct value label: drove alone 52.6 percent, public transportation 28.4 percent, carpool 6.5 percent, walked 6.2 percent, worked at home 4.3 percent, and other means 2.0 percent.]({{ '/assets/family-d/ny-commute-2016-recommended.png' | relative_url }})

The two versions differ only where the script checks `gridlines`: the gridline version adds the 10 percent ticks, the gridlines, and the axis title, and the recommended version removes the percent axis and moves "percent of workers 16 years and over" into the subtitle.

Estimates for workers 16 years and over in New York, 2016. Margins of error are at the 90 percent confidence level.

| Means of transportation | Estimate | Margin of error | Percent | Percent margin of error |
|---|---:|---:|---:|---:|
| Drove alone | 4,888,039 | ±27,150 | 52.6% | ±0.3 |
| Public transportation (excluding taxicab) | 2,636,851 | ±24,680 | 28.4% | ±0.3 |
| Carpool | 606,605 | ±15,551 | 6.5% | ±0.2 |
| Walked | 577,983 | ±13,519 | 6.2% | ±0.1 |
| Worked at home | 400,213 | ±12,682 | 4.3% | ±0.1 |
| Other means | 181,866 | ±7,655 | 2.0% | ±0.1 |
| Workers 16 years and over | 9,291,557 | ±26,473 | 100.0% | |

{% include code-example.html file="grids_bar_chart.py" title="Show Python code for the New York commute bar charts" %}


## Common Errors and Misinterpretations

| Issue | Why It Matters | Recommended Correction |
|---|---|---|
| Gridlines are more prominent than the data | Readers may focus on the grid rather than the values or patterns. | Use a subdued color and keep gridlines visually secondary. |
| Gridlines obscure data marks | Points, bars, or lines become harder to read. | Render gridlines behind the data marks. |
| Gridlines interfere with labels | Text becomes harder to read. | Adjust the styling or layout to keep labels clear. |
| Gridlines repeat information already supplied by direct labels | Extra lines can add clutter without helping interpretation. | Consider removing unnecessary gridlines. |
| Graticules add no useful location information | They can distract from the map's main message. | Omit them unless they help readers interpret location. |
| "Behind the data" is interpreted as "never crosses a data position" | Useful reference lines may be removed unnecessarily. | Allow intersections while keeping gridlines behind and visually subordinate to the data. |

## Publication Quality Checklist

<ul class="checklist-folds">
  <li>
    <details>
      <summary>The visualization fits the analytical question.</summary>
      <div class="checklist-fold-body">
        <p>Gridlines are optional. The page says to use them when they help readers trace unlabeled data points to axis values, and to consider removing them when direct labels already give the values.</p>
        <p><a href="#recommended-practices">Read the full section: Recommended Practices</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Relevant alternatives were considered.</summary>
      <div class="checklist-fold-body">
        <p>The New York example shows two versions of the same chart: one with gridlines, which reproduces Example 1, and a recommended version without them, because every bar already has a direct value label.</p>
        <p><a href="#recommended-without-gridlines">Read the full section: Recommended: without gridlines</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Data source, geography, reference period, and units are documented.</summary>
      <div class="checklist-fold-body">
        <p>The New York example names its source as the 2016 American Community Survey 1-year estimates, Table DP03, for New York state, and its table covers workers 16 years and over. Source line guidance is on the site-wide <a href="source.html">Sources</a> page.</p>
        <p><a href="#reproduce-the-new-york-commute-example">Read the full section: Reproduce the New York commute example</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Data transformations and aggregation are appropriate.</summary>
      <div class="checklist-fold-body">
        <p>This page does not cover data transformation. The New York example keeps the six categories and their order from Example 1, and its table lists each estimate, percent, and margin of error.</p>
        <p><a href="#reproduce-the-new-york-commute-example">Read the full section: Reproduce the New York commute example</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Missing values and relevant uncertainty are addressed.</summary>
      <div class="checklist-fold-body">
        <p>The New York table gives margins of error at the 90 percent confidence level. The Accessibility section says not to rely on gridlines alone when precise values matter, and to use direct labels or a data table. More on uncertainty is on the site-wide <a href="uncertainty.html">Visualizing Uncertainty</a> page.</p>
        <p><a href="#reproduce-the-new-york-commute-example">Read the full section: Reproduce the New York commute example</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Existing accessibility, scaling, and axes guidance has been followed.</summary>
      <div class="checklist-fold-body">
        <p>Axis and tick labels need a contrast of at least 4.5:1, and gridlines that readers must use to read values need at least 3:1 against the background. Full requirements are on the site-wide <a href="508.html">508 Compliance</a>, <a href="color.html">Color</a>, and <a href="axes.html">Axes</a> pages.</p>
        <p><a href="#accessibility">Read the full section: Accessibility</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Chart-specific limitations and caveats are explained.</summary>
      <div class="checklist-fold-body">
        <p>Gridlines should not obscure data marks or compete with the data, and unnecessary gridlines add clutter when direct labels already make values clear. Graticules belong on a thematic map only when they help readers interpret it.</p>
        <p><a href="#practices-to-avoid">Read the full section: Practices to Avoid</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>Code examples have been executed and verified.</summary>
      <div class="checklist-fold-body">
        <p>The Developer Implementation section gives a downloadable Python script that saves both versions, the saved table it uses so it can run offline, and the commands that run it. It names the one setting in the script where the two versions differ.</p>
        <p><a href="#developer-implementation">Read the full section: Developer Implementation</a></p>
      </div>
    </details>
  </li>
  <li>
    <details>
      <summary>The visualization has undergone the appropriate review.</summary>
      <div class="checklist-fold-body">
        <p>This page does not describe a formal review process. Its Common Errors and Misinterpretations table lists issues to look for, why they matter, and the recommended correction.</p>
        <p><a href="#common-errors-and-misinterpretations">Read the full section: Common Errors and Misinterpretations</a></p>
      </div>
    </details>
  </li>
</ul>
 
## Related Pages
 
* [Axes](axes.html): gridlines support the scale; axis titles, ticks, and baselines are covered there.
* [Line Graphs](linegraph.html): a common use of light gridlines behind a series.
* [Map Layout](maplayout.html): related guidance when considering graticules on a thematic map.
* [Color](color.html): keep gridlines visible enough to use without overpowering the data.
* [Typography](typography.html): keep labels readable so gridlines do not cut through or crowd text.
* [508 Compliance](508.html): contrast and text alternatives that also apply to labeled axes and gridlines.
