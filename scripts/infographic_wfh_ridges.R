# Work-from-home productivity hypothetical — economist-style ridge plot
# Install once: install.packages(c("ggplot2", "ggridges", "viridis", "dplyr"))
# Run from repo root or set out_dir to your Teaching/MNGT425 folder.

library(ggplot2)
library(ggridges)
library(viridis)
library(dplyr)

# Output directory: static assets for web infographic
# Run from repo root (scripts/) or repo root; or from Teaching/MNGT425
script_dir <- if (file.exists("static/images/infographics")) {
  "static/images/infographics"
} else if (file.exists("../static/images/infographics")) {
  "../static/images/infographics"
} else if (file.exists("../../static/images/infographics")) {
  "../../static/images/infographics"
} else {
  try_dir <- "static/images/infographics"
  dir.create(try_dir, recursive = TRUE, showWarnings = FALSE)
  try_dir
}
out_file <- file.path(script_dir, "wfh_productivity_ridges.png")

# Hypothetical: "Do work-from-home arrangements enhance productivity?"
# Simulated productivity ratings (1–10) by position; overlapping distributions.
set.seed(42)
positions <- factor(c("Individual contributors", "Managers", "Directors", "Executives"),
                    levels = rev(c("Individual contributors", "Managers", "Directors", "Executives")))

wfh_data <- data.frame()
for (i in seq_along(positions)) {
  # Slightly different means by level (hypothetical: higher roles rate WFH productivity higher)
  mean_rating <- 4.2 + (i - 1) * 0.5 + rnorm(1, 0, 0.1)
  mean_rating <- max(1, min(10, mean_rating))
  n_per <- 80
  ratings <- rnorm(n_per, mean = mean_rating, sd = 1.4)
  ratings <- pmax(1, pmin(10, ratings))
  wfh_data <- rbind(wfh_data, data.frame(
    Position = positions[i],
    Productivity_rating = ratings
  ))
}

p <- ggplot(wfh_data, aes(x = Productivity_rating, y = Position, fill = after_stat(x))) +
  geom_density_ridges_gradient(scale = 2.2, rel_min_height = 0.01) +
  scale_fill_viridis(name = "Productivity (1–10)", option = "C") +
  labs(
    title = "Do work-from-home arrangements enhance productivity?",
    subtitle = "Hypothetical productivity ratings by position (illustrative)",
    x = "Productivity rating (1 = much lower at home, 10 = much higher at home)",
    y = "Position"
  ) +
  theme_ridges() +
  theme(
    legend.position = "none",
    panel.grid.major.x = element_blank(),
    plot.title = element_text(size = 14, hjust = 0),
    plot.subtitle = element_text(size = 10, color = "gray40", hjust = 0)
  ) +
  xlim(1, 10)

ggsave(out_file, p, width = 8, height = 5, dpi = 150, bg = "white")
message("Saved: ", normalizePath(out_file))
