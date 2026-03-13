#!/usr/bin/env python3
"""
WFH productivity hypothetical — economist-style ridge plot (Nicholls colors).
Perspectives: Undergraduate Students, MBA Students, Working Professionals, Executives.
X-axis: Likert 1–5 (same scale as HR SJT effectiveness visuals: 1=Not effective,
  2=Somewhat ineffective, 3=Moderately effective, 4=Effective, 5=Highly effective).
  See Teaching/MNGT 425 - HR Analytics/Student Data/README_EFFECTIVENESS_VISUALS.md.
Economist-style red header line and tag (README). Logo bottom-right, cropped to top 82% (no tagline). Footer with source and μ (n).
Run from repo root: python3 scripts/infographic_wfh_ridges.py
Requires: numpy, scipy, matplotlib (pip install numpy scipy matplotlib).
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Two clusters: optimistic (Undergrads, Working Prof) = darker; skeptical (MBA, Executives) = lighter
CLUSTER_OPTIMISTIC = "#A6192E"   # darker red — Undergraduate Students, Working Professionals
CLUSTER_SKEPTICAL = "#e8a0a0"   # lighter red — MBA Students, Executives
CLUSTER_OPTIMISTIC_EDGE = "#6b0f1a"
CLUSTER_SKEPTICAL_EDGE = "#c45c5c"

# Repo root: walk up until we find static/
_resolved = Path(__file__).resolve()
REPO_ROOT = _resolved.parent
for _ in range(5):
    if (REPO_ROOT / "static").is_dir():
        break
    REPO_ROOT = REPO_ROOT.parent
OUT_DIR = REPO_ROOT / "static" / "images" / "infographics"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "wfh_productivity_ridges.png"

# Footer: lab website (People Analytics Lab of the Bayou)
FOOTER_WEBSITE = "https://bayoupal.nicholls.edu"

# Logo path: optional, placed bottom-right, cropped to top 82%
LOGO_PATHS = [
    REPO_ROOT / "static" / "images" / "lab_emblem.png",
    Path("/Users/ccastille/Documents/GitHub/Teaching/MNGT 425 - HR Analytics/hr-sjt-assessment/lab-emblem.png"),
]

# Perspectives: more realistic — students & working professionals see WFH as helpful; MBA & executives more pessimistic
# Order: bottom to top on plot (Undergrad, MBA, Working Prof, Exec)
PERSPECTIVES = [
    {"name": "Undergraduate Students", "n": 42, "mean": 3.8, "sd": 0.65},
    {"name": "MBA Students", "n": 28, "mean": 3.0, "sd": 0.7},
    {"name": "Working Professionals", "n": 45, "mean": 4.0, "sd": 0.6},
    {"name": "Executives", "n": 12, "mean": 2.9, "sd": 0.75},
]

# Likert 1–5
X_MIN, X_MAX = 1, 5
N_X = 300
np.random.seed(42)


def smooth_kde_clipped(data, x_grid, bw_mult=1.0):
    """KDE evaluated on x_grid, clipped to [1,5] for smooth tails."""
    data = np.asarray(data)
    data = np.clip(data, X_MIN, X_MAX)
    if len(data) < 2:
        return np.zeros_like(x_grid)
    try:
        kde = stats.gaussian_kde(data, bw_method="scott")
        kde.set_bandwidth(kde.factor * bw_mult)
    except Exception:
        return np.zeros_like(x_grid)
    dens = kde(x_grid)
    dens = np.clip(dens, 0, None)
    if dens.max() > 0:
        dens = dens / dens.max()
    return dens


def main():
    fig = plt.figure(figsize=(10, 6.5), facecolor="white")
    # Title and red line/rect aligned with left edge of y-axis labels (the "U" in Undergraduate)
    AXES_LEFT, AXES_BOTTOM, AXES_WIDTH, AXES_HEIGHT = 0.10, 0.26, 0.62, 0.48  # chart higher so footnote doesn't overlap curve
    CONTENT_LEFT = 0.01   # title and footnote aligned left with y-axis labels
    HEADER_Y = 0.90
    TITLE_Y, TAKEAWAY_Y = 0.84, 0.80
    FOOTER_Y = 0.06   # footer block; first line at FOOTER_Y+0.06, well below chart
    ECONOMIST_RED = "#E3120B"
    DARK_GRAY = "#1a1a2e"
    TEXT_GRAY = "#555"
    # Logo above footnote; pushed down and slightly smaller
    LOGO_LEFT, LOGO_BOTTOM, LOGO_W, LOGO_H = 0.74, 0.09, 0.20, 0.20
    LOGO_CROP_TOP_FRAC = 0.82

    # Red header line and tag above title (no overlap)
    fig.add_artist(plt.Line2D([CONTENT_LEFT, 0.92], [HEADER_Y, HEADER_Y], color=ECONOMIST_RED, linewidth=0.6, transform=fig.transFigure))
    from matplotlib.patches import Rectangle
    fig.add_artist(Rectangle((CONTENT_LEFT, HEADER_Y - 0.018), 0.04, 0.018, facecolor=ECONOMIST_RED, transform=fig.transFigure))

    ax = fig.add_axes([AXES_LEFT, AXES_BOTTOM, AXES_WIDTH, AXES_HEIGHT])
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Effectiveness rating (1 = Not effective, 5 = Highly effective)", fontsize=10, color=DARK_GRAY)
    ax.set_ylabel("")
    step = 0.88
    ax.set_ylim(0, 4 * step * 1.15)

    x_grid = np.linspace(X_MIN, X_MAX, N_X)
    base = 0
    # step already set above for ylim

    # reversed order: bottom to top = Executives(0), Working Prof(1), MBA(2), Undergrad(3)
    # Optimistic cluster (darker): Undergrad, Working Prof.  Skeptical (lighter): MBA, Executives.
    for i, persp in enumerate(reversed(PERSPECTIVES)):
        name, n, mean, sd = persp["name"], persp["n"], persp["mean"], persp["sd"]
        raw = np.random.normal(mean, sd, n)
        raw = np.clip(raw, X_MIN, X_MAX)
        dens = smooth_kde_clipped(raw, x_grid, bw_mult=1.2)
        y_curve = base + dens * step * 0.88
        is_skeptical = i in (0, 2)  # Executives, MBA
        fill_color = CLUSTER_SKEPTICAL if is_skeptical else CLUSTER_OPTIMISTIC
        edge_color = CLUSTER_SKEPTICAL_EDGE if is_skeptical else CLUSTER_OPTIMISTIC_EDGE
        ax.fill_between(x_grid, base, y_curve, color=fill_color, alpha=0.9, linewidth=0)
        ax.plot(x_grid, y_curve, color=edge_color, linewidth=1, alpha=0.95)
        # Two-line labels with paragraph spacing (name on first line, (n = x) on second)
        label = f"{name}\n(n = {n})"
        ax.text(-0.08, base + step * 0.45, label, transform=ax.get_yaxis_transform(), fontsize=9,
                verticalalignment="center", horizontalalignment="right", color=DARK_GRAY, linespacing=1.35)
        base += step

    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(colors=DARK_GRAY)

    # Title and takeaway only (no "Hypothetical effectiveness..." line)
    fig.text(CONTENT_LEFT, TITLE_Y, "Do work-from-home arrangements enhance productivity?",
             fontsize=16, fontweight="bold", color=DARK_GRAY)
    fig.text(CONTENT_LEFT, TAKEAWAY_Y, "Students and working professionals more optimistic; MBA students and executives less so.",
             fontsize=10, color=TEXT_GRAY, style="italic")

    # Footer: multiple lines with more vertical spacing so text isn't squished
    n_total = sum(p["n"] for p in PERSPECTIVES)
    FOOTER_LINE_DROP = 0.028   # vertical gap between lines
    fig.text(CONTENT_LEFT, FOOTER_Y + 0.06, "Hypothetical data for illustration only. Not from actual study data.",
             fontsize=9, color=TEXT_GRAY)
    line_y = FOOTER_Y + 0.06 - FOOTER_LINE_DROP
    for p in PERSPECTIVES:
        fig.text(CONTENT_LEFT, line_y, f"{p['name']}: M = {p['mean']:.1f}, SD = {p['sd']:.1f} (n = {p['n']}).",
                 fontsize=8, color=TEXT_GRAY)
        line_y -= FOOTER_LINE_DROP
    fig.text(CONTENT_LEFT, line_y, f"Total N = {n_total}. {FOOTER_WEBSITE}",
             fontsize=8, color=TEXT_GRAY)

    # Logo bottom-right; crop to top 82% to cut off "Using evidence to transform organizations"
    logo_path = None
    for p in LOGO_PATHS:
        if p.is_file():
            logo_path = p
            break
    if logo_path:
        try:
            from matplotlib import image as mimage
            img = mimage.imread(logo_path)
            h, w = img.shape[:2]
            crop_h = int(h * LOGO_CROP_TOP_FRAC)
            img_cropped = img[:crop_h, :, :] if img.ndim == 3 else img[:crop_h, :]
            ax_logo = fig.add_axes([LOGO_LEFT, LOGO_BOTTOM, LOGO_W, LOGO_H])
            ax_logo.imshow(img_cropped, aspect="equal")
            ax_logo.axis("off")
        except Exception as e:
            print("Logo not placed:", e)

    fig.savefig(OUT_FILE, dpi=150, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    plt.close()
    print("Saved:", OUT_FILE)


if __name__ == "__main__":
    main()
