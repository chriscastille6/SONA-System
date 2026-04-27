# MNGT 425 — Economist-style visuals

Python and R scripts here generate ridge-plot style infographics for teaching and lab materials.

**Effectiveness visuals (per-incident):** Formatting and pipeline for HR SJT tactic-by-incident charts (horizontal stacked bars, 1–5 Likert, Economist-style) are documented in:

`Teaching/MNGT 425 - HR Analytics/Student Data/README_EFFECTIVENESS_VISUALS.md`

That README is the source of truth for layout constants, colors, lab emblem position, and scale (1 = Not effective … 5 = Highly effective). The aggregate “by perspective” ridge plot below uses the same 1–5 scale and Nicholls/lab branding for consistency.

## Work-from-home productivity hypothetical

**Preferred: Python** — Nicholls colors, 1–5 Likert, lab logo in bottom right.

- **Script:** `infographic_wfh_ridges.py` (also in repo `scripts/infographic_wfh_ridges.py`)
- **Perspectives:** Undergraduate Students, MBA Students, Working Professionals, Executives (with sample sizes in labels).
- **X-axis:** Likert 1–5 (Not effective to Highly effective).
- **Visual:** Density ridges with smooth tails, Nicholls red (#A6192E); lab emblem in bottom right.

### Run (Python)

```bash
# From repo root (install once: pip install numpy scipy matplotlib)
python3 Teaching/MNGT425/infographic_wfh_ridges.py
# or
python3 scripts/infographic_wfh_ridges.py
```

Output: `static/images/infographics/wfh_productivity_ridges.png`. Place the lab logo at `static/images/lab_emblem.png` so the script and the infographic page can use it.

### Alternative: R

**Script:** `infographic_wfh_ridges.R` (also in repo `scripts/infographic_wfh_ridges.R`)

```r
install.packages(c("ggplot2", "ggridges", "viridis", "dplyr"))
# From repo root:
Rscript scripts/infographic_wfh_ridges.R
```

Then reload the infographic page to see the chart.
