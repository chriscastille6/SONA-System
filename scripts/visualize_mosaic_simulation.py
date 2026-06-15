#!/usr/bin/env python3
"""Generate HTML and PNG charts from docs/mosaic_simulation_results.csv."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "docs" / "mosaic_simulation_results.csv"
OUT = ROOT / "docs" / "mosaic_simulation_charts.html"
FIG_DIR = ROOT / "docs" / "figures"


def main():
    df = pd.read_csv(CSV)
    none = df[(df.mitigation == "none") & (df.scenario != "linkage_roster_attack")]

    def series_json(cohort, scenarios):
        parts = []
        for scen in scenarios:
            s = none[(none.cohort == cohort) & (none.scenario == scen)].sort_values("N")
            if s.empty:
                continue
            parts.append(
                {
                    "label": scen.replace("gender+", "").replace("+", " / "),
                    "x": s.N.astype(int).tolist(),
                    "y": [round(v * 100, 1) for v in s.p_unique_mean],
                }
            )
        return parts

    student = series_json(
        "student",
        [
            "gender+age_band+status",
            "gender+age_exact",
            "gender+age_exact+status",
            "gender+age_band+status+week",
        ],
    )
    hr = series_json(
        "hr",
        ["race", "race+job", "race+job+years", "race+job+years+creds"],
    )
    lk = df[df.scenario == "linkage_roster_attack"].sort_values("N")
    linkage = {
        "x": lk.N.astype(int).tolist(),
        "y": [round(v * 100, 2) for v in lk.linkage_p_success_mean],
    }
    mit = df[
        (df.cohort == "student")
        & (df.N == 100)
        & (df.scenario == "gender+age_exact+status")
        & (df.mitigation.isin(["none", "age_bands", "suppress_k"]))
    ]

    import json

    data = json.dumps({"student": student, "hr": hr, "linkage": linkage})
    mit_rows = mit[["mitigation", "p_unique_mean", "frac_below_k_mean"]].to_dict("records")

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><title>Mosaic simulation</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 24px; max-width: 900px; color: #222; }}
  h1 {{ font-size: 1.35rem; }} h2 {{ font-size: 1.05rem; margin-top: 2rem; }}
  canvas {{ max-width: 100%; margin-bottom: 1.5rem; }}
  .note {{ color: #555; font-size: 0.9rem; }}
</style>
</head><body>
<h1>Mosaic / re-identification simulation</h1>
<p class="note">Source: mosaic_simulation_results.csv · P(unique) = share in singleton QI cell · K=5</p>
<h2>Student cohort — P(unique)</h2>
<canvas id="student"></canvas>
<h2>Student — fraction with k &lt; 5 (exact age + status)</h2>
<canvas id="belowk"></canvas>
<h2>HR cohort — P(unique)</h2>
<canvas id="hr"></canvas>
<h2>Roster linkage & mitigations (N=100)</h2>
<canvas id="linkage"></canvas>
<canvas id="mit"></canvas>
<script>
const DATA = {data};
const mitData = {json.dumps(mit_rows)};
function lineChart(id, seriesList, yLabel) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{
      labels: seriesList[0].x.map(String),
      datasets: seriesList.map((s, i) => ({{
        label: s.label,
        data: s.y,
        tension: 0.2,
        fill: false,
      }})),
    }},
    options: {{
      scales: {{
        x: {{ title: {{ display: true, text: 'Sample size N' }} }},
        y: {{ title: {{ display: true, text: yLabel }}, min: 0, max: 100 }},
      }},
    }},
  }});
}}
lineChart('student', DATA.student, 'P(unique) %');
lineChart('hr', DATA.hr, 'P(unique) %');
new Chart(document.getElementById('linkage'), {{
  type: 'line',
  data: {{
    labels: DATA.linkage.x.map(String),
    datasets: [{{ label: 'P(linkage)', data: DATA.linkage.y, borderColor: '#b45309' }}],
  }},
  options: {{ scales: {{ y: {{ min: 0, max: 15, title: {{ display: true, text: '%' }} }} }} }},
}});
new Chart(document.getElementById('mit'), {{
  type: 'bar',
  data: {{
    labels: mitData.map(r => r.mitigation),
    datasets: [
      {{ label: 'P(unique) %', data: mitData.map(r => (r.p_unique_mean*100).toFixed(1)) }},
      {{ label: 'Below K %', data: mitData.map(r => (r.frac_below_k_mean*100).toFixed(1)) }},
    ],
  }},
}});
const bk = {json.dumps(
        [
            {
                "x": none[(none.cohort == "student") & (none.scenario == "gender+age_exact+status")]
                .sort_values("N")
                .N.astype(int)
                .tolist(),
                "y": [
                    round(v * 100, 1)
                    for v in none[(none.cohort == "student") & (none.scenario == "gender+age_exact+status")]
                    .sort_values("N")
                    .frac_below_k_mean
                ],
            }
        ]
    )};
new Chart(document.getElementById('belowk'), {{
  type: 'line',
  data: {{ labels: bk[0].x.map(String), datasets: [{{ label: 'k < 5', data: bk[0].y, borderColor: '#dc2626' }}] }},
  options: {{ scales: {{ y: {{ min: 0, max: 100, title: {{ display: true, text: '% of sample' }} }} }} }},
}});
</script>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")
    write_png_figures(df, none, mit)


def write_png_figures(df, none, mit) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        print("Skipping PNG figures (install matplotlib):", exc)
        return

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("ggplot")

    def line_plot(
        path: Path,
        title: str,
        series_list: list[tuple[str, pd.DataFrame]],
        y_col: str = "p_unique_mean",
        ylabel: str = "Percent",
    ) -> None:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for label, sub in series_list:
            sub = sub.sort_values("N")
            ax.plot(sub.N, sub[y_col] * 100, marker="o", label=label)
        ax.set_xlabel("Sample size N")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=8, loc="best")
        ax.set_ylim(bottom=0)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)

    student_scenarios = [
        ("Age band + status", "gender+age_band+status"),
        ("Exact age only", "gender+age_exact"),
        ("Exact age + status", "gender+age_exact+status"),
        ("+ completion week", "gender+age_band+status+week"),
    ]
    line_plot(
        FIG_DIR / "mosaic_student_p_unique.png",
        "Student cohort — P(unique) by sample size",
        [
            (label, none[(none.cohort == "student") & (none.scenario == scen)])
            for label, scen in student_scenarios
        ],
    )

    below_k = none[
        (none.cohort == "student") & (none.scenario == "gender+age_exact+status")
    ].sort_values("N")
    line_plot(
        FIG_DIR / "mosaic_student_below_k.png",
        "Student — share in cells with k < 5 (exact age + status)",
        [("Below K threshold", below_k)],
        y_col="frac_below_k_mean",
        ylabel="Percent of sample",
    )

    hr_scenarios = [
        ("Race only", "race"),
        ("Race + job", "race+job"),
        ("+ years in HR", "race+job+years"),
        ("+ credential count", "race+job+years+creds"),
    ]
    line_plot(
        FIG_DIR / "mosaic_hr_p_unique.png",
        "HR cohort — P(unique) by sample size",
        [
            (label, none[(none.cohort == "hr") & (none.scenario == scen)])
            for label, scen in hr_scenarios
        ],
    )

    lk = df[df["linkage_p_success_mean"].notna()].sort_values("N")
    line_plot(
        FIG_DIR / "mosaic_linkage.png",
        "Roster linkage attack — P(linkage success)",
        [("Linkage", lk)],
        y_col="linkage_p_success_mean",
        ylabel="Percent",
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    labels = ["No mitigation", "Age bands", "Suppress k<5"]
    mit_map = {"none": 0, "age_bands": 1, "suppress_k": 2}
    mit_sorted = mit[mit.mitigation.isin(mit_map)].copy()
    mit_sorted["idx"] = mit_sorted.mitigation.map(mit_map)
    mit_sorted = mit_sorted.sort_values("idx")
    x = range(len(mit_sorted))
    w = 0.35
    ax.bar(
        [i - w / 2 for i in x],
        mit_sorted.p_unique_mean * 100,
        width=w,
        label="P(unique)",
    )
    ax.bar(
        [i + w / 2 for i in x],
        mit_sorted.frac_below_k_mean * 100,
        width=w,
        label="Share in cells k < 5",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percent")
    ax.set_title("Mitigations at N = 100 (gender + exact age + status)")
    ax.legend()
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mosaic_mitigation_n100.png", dpi=150)
    plt.close(fig)
    print(f"Wrote PNG figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
