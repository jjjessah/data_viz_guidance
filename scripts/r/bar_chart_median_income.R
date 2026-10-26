# Create a horizontal bar chart of median household income by state.
# Data: ../../data/median_household_income_by_state.csv
# Source expectation: ACS table B19013 (refresh from data.census.gov for production)
#
# Required packages:
#   install.packages(c("readr", "dplyr", "ggplot2"))

library(readr)
library(dplyr)
library(ggplot2)

root <- normalizePath(file.path("..", ".."))
data_path <- file.path(root, "data", "median_household_income_by_state.csv")
out_dir <- file.path(root, "assets", "examples")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
out_png <- file.path(out_dir, "bar_chart_median_income_top15_r.png")

df <- read_csv(data_path, show_col_types = FALSE)

top <- df |>
  slice_max(order_by = median_household_income, n = 15) |>
  arrange(median_household_income) |>
  mutate(state = factor(state, levels = state))

p <- ggplot(top, aes(x = median_household_income, y = state)) +
  geom_col(fill = "#005ea2") +
  labs(
    title = "Highest median household income among states",
    subtitle = "ACS B19013 demo file",
    x = "Median household income (USD)",
    y = NULL,
    caption = "Source: ACS B19013 demo file in repository data/. Refresh from data.census.gov for official estimates."
  ) +
  theme_minimal(base_size = 12) +
  theme(
    panel.grid.major.y = element_blank(),
    plot.title = element_text(face = "bold")
  )

ggsave(out_png, p, width = 10, height = 7, dpi = 150)
message("Wrote ", out_png)
