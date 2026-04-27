#!/usr/bin/env python3
"""
WFH productivity hypothetical — economist-style ridge plot (Nicholls colors).
Perspectives: Undergraduate Students, MBA Students, Working Professionals, Executives.
X-axis: Likert 1–5 (same as HR SJT effectiveness visuals; see Student Data/README_EFFECTIVENESS_VISUALS.md).
Lab logo in bottom right. Run from repo root: python3 scripts/infographic_wfh_ridges.py
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Nicholls colors
NICHOLLS_RED = "#A6192E"
NICHOLLS_RED_DARK = "#8a1526"

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

# Logo path: optional, placed bottom-right
LOGO_PATHS = [
    REPO_ROOT / "static" / "images" / "lab_emblem.png",
    Path("/Users/ccastille/Documents/GitHub/Teaching/MNGT 425 - HR Analytics/hr-sjt-assessment/lab-emblem.png"),
]

# Perspectives and hypothetical sample sizes (order: bottom to top on plot)
PERSPECTIVES = [
    {"name": "Undergraduate Students", "n": 42, "mean": 2.8, "sd": 0.7},
    {"name": "MBA Students", "n": 28, "mean": 3.2, "sd": 0.65},
    {"name": "Working Professionals", "n": 45, "mean": 3.6, "sd": 0.6},
    {"name": "Executives", "n": 12, "mean": 3.9, "sd": 0.55},
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
    # Normalize so peak is reasonable for stacking
    if dens.max() > 0:
        dens = dens / dens.max()
    return dens


def main():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Effectiveness rating (1 = Not effective, 5 = Highly effective)", fontsize=10)
    ax.set_ylabel("")
    ax.set_ylim(0, 4 * 1.2)

    x_grid = np.linspace(X_MIN, X_MAX, N_X)
    base = 0
    step = 1.0

    # Reverse so Executives at top, Undergrad at bottom
    for i, persp in enumerate(reversed(PERSPECTIVES)):
        name, n, mean, sd = persp["name"], persp["n"], persp["mean"], persp["sd"]
        # Simulate ratings (1–5)
        raw = np.random.normal(mean, sd, n)
        raw = np.clip(raw, X_MIN, X_MAX)
        dens = smooth_kde_clipped(raw, x_grid, bw_mult=1.2)
        y_curve = base + dens * step * 0.9
        ax.fill_between(x_grid, base, y_curve, color=NICHOLLS_RED, alpha=0.85, linewidth=0)
        ax.plot(x_grid, y_curve, color=NICHOLLS_RED_DARK, linewidth=1, alpha=0.9)
        label = f"{name} (n = {n})"
        ax.text(-0.08, base + step * 0.45, label, transform=ax.get_yaxis_transform(), fontsize=10,
                verticalalignment="center", horizontalalignment="right")
        base += step

    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_title("Do work-from-home arrangements enhance productivity?\nHypothetical effectiveness ratings by perspective (1–5 Likert)", fontsize=12)
    plt.tight_layout(rect=[0, 0, 0.88, 1])

    # Logo in bottom right
    logo_path = None
    for p in LOGO_PATHS:
        if p.is_file():
            logo_path = p
            break
    if logo_path:
        try:
            from matplotlib import image as mimage
            img = mimage.imread(logo_path)
            # Position in figure coordinates (0,0 = bottom-left, 1,1 = top-right)
            # Small logo in bottom-right
            logo_size = 0.12
            left = 1 - logo_size - 0.02
            bottom = 0.02
            ax_logo = fig.add_axes([left, bottom, logo_size, logo_size])
            ax_logo.imshow(img)
            ax_logo.axis("off")
        except Exception as e:
            print("Logo not placed:", e)

    fig.savefig(OUT_FILE, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("Saved:", OUT_FILE)


if __name__ == "__main__":
    main()
