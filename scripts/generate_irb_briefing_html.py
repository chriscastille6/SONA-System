#!/usr/bin/env python3
"""
Generate IRB_BRIEFING_JULIANN_JON.html from IRB_BRIEFING_JULIANN_JON.json.
Mirrors the professional styling of the Psychological Assessments FERPA document.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "IRB_BRIEFING_JULIANN_JON.json"
HTML_PATH = REPO_ROOT / "IRB_BRIEFING_JULIANN_JON.html"

CSS = """
    * { box-sizing: border-box; }
    body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; color: #1f2937; max-width: 800px; margin: 0 auto; padding: 24px; background: #fff; }
    h1 { font-size: 1.5rem; margin: 0 0 0.5rem; color: #111; border-bottom: 2px solid #2563eb; padding-bottom: 0.25rem; }
    h2 { font-size: 1.15rem; margin: 1.25rem 0 0.5rem; color: #1e40af; }
    h3 { font-size: 1rem; margin: 0.75rem 0 0.35rem; color: #374151; }
    p { margin: 0 0 0.5rem; }
    ul { margin: 0.25rem 0 0.5rem; padding-left: 1.25rem; }
    li { margin-bottom: 0.2rem; }
    .subtitle { font-size: 0.9rem; color: #6b7280; margin-bottom: 0.25rem; }
    .doc-byline { font-size: 0.85rem; color: #4b5563; margin: 0 0 1rem; }
    .section-block { margin: 1rem 0; }
    .study-card { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 6px; padding: 0.75rem 1rem; margin: 0.75rem 0; overflow-wrap: break-word; word-break: break-word; }
    .study-card h3 { margin-top: 0; }
    .study-card dl { margin: 0.25rem 0 0; }
    .study-card .field { margin: 0.2rem 0; }
    .study-card .field strong { color: #374151; margin-right: 0.25rem; }
    .issues-table { width: 100%; table-layout: fixed; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.95rem; }
    .issues-table th, .issues-table td { padding: 0.4rem 0.6rem; text-align: left; border-bottom: 1px solid #e5e7eb; overflow-wrap: break-word; word-break: break-word; }
    .issues-table th { background: #f8fafc; color: #374151; font-weight: 600; width: 22%; }
    .doc-table { width: 100%; table-layout: fixed; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.9rem; }
    .doc-table th, .doc-table td { padding: 0.35rem 0.5rem; text-align: left; border-bottom: 1px solid #e5e7eb; overflow-wrap: break-word; word-break: break-word; }
    .doc-table th { background: #f8fafc; color: #374151; font-weight: 600; width: 18%; }
    .doc-table td:nth-child(2) { width: 18%; }
    .doc-table td:nth-child(3) { width: 64%; }
    .contact-block { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 0.75rem 1rem; margin-top: 1rem; }
    .doc-header { text-align: center; margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid #e5e7eb; }
    .doc-header .institution { font-size: 0.95rem; font-weight: 600; color: #1e40af; letter-spacing: 0.02em; margin-bottom: 0.15rem; }
    .doc-header .office { font-size: 0.85rem; color: #4b5563; margin-bottom: 0.5rem; }
    .access-list { list-style: none; padding-left: 0; }
    .access-list li { margin-bottom: 0.35rem; padding-left: 1em; text-indent: -1em; }
    .access-list li::before { content: "• "; color: #2563eb; font-weight: bold; }
    ol { margin: 0.25rem 0 0.5rem; padding-left: 1.5rem; }
    .watermark { position: fixed; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; z-index: -1; opacity: 0.14; font-size: 5rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.1em; transform: rotate(-28deg); }
    a { overflow-wrap: break-word; word-break: break-word; }
    @media print {
      @page { size: letter; margin: 14mm; }
      body { padding: 0; max-width: none; }
      h2 { page-break-after: avoid; }
      h3 { page-break-after: avoid; }
      .study-card { page-break-inside: avoid; }
      .contact-block { page-break-inside: avoid; }
      .federal-audit-card { page-break-inside: avoid; }
      ol { margin: 0.25rem 0 0.5rem; padding-left: 1.5rem; }
      table { page-break-inside: auto; }
      tr { page-break-inside: avoid; page-break-after: auto; }
    }
"""


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        b = json.load(f)

    meta = b["meta"]
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        f"  <title>{meta['title']}</title>",
        "  <style>",
        CSS,
        "  </style>",
        "</head>",
        "<body>",
        "  <div class=\"watermark\" aria-hidden=\"true\">DRAFT</div>",
        "  <div class=\"doc-header\">",
        "    <p class=\"institution\">NICHOLLS STATE UNIVERSITY</p>",
        "    <p class=\"office\">Human Subjects Institutional Review Board</p>",
        f"    <h1>{meta['title']}</h1>",
        f"    <p class=\"subtitle\">{meta['purpose']}</p>",
        f"    <p class=\"doc-byline\">{meta['date']}</p>",
        "  </div>",
        "",
        "  <h2>1. Project Documents (IRB Applications)</h2>",
        "  <table class=\"doc-table\">",
        "    <thead><tr><th>Study</th><th>Document</th><th>Link</th></tr></thead>",
        "    <tbody>",
    ]

    for row in b["project_documents"]:
        link = row.get("link", "#")
        link_text = row.get("link_text", "View")
        html_parts.append(
            f"      <tr><td><strong>{row['study']}</strong></td><td>{row['document']}</td><td><a href=\"{link}\">{link_text}</a></td></tr>"
        )
    html_parts.extend(["    </tbody>", "  </table>", ""])

    html_parts.append("  <h2>2. Studies Proposed for Review</h2>")

    for s in b["studies"]:
        status_str = f" <em>({s['status']})</em>" if s.get("status") else ""
        html_parts.append(
            f"  <div class=\"study-card\">"
        )
        html_parts.append(
            f"    <h3>{s['id']}. {s['name']} — {s['subtitle']}{status_str}</h3>"
        )
        for f in s["fields"]:
            html_parts.append(f"    <p class=\"field\"><strong>{f['label']}:</strong> {f['value']}</p>")
        if s.get("request"):
            html_parts.append(f"    <p><strong>Request:</strong> {s['request']}</p>")
        if s.get("change"):
            html_parts.append(f"    <p><strong>Change:</strong> {s['change']}</p>")
        if s.get("lai_link"):
            html_parts.append(f"    <p><strong>LAI link:</strong> <a href=\"{s['lai_link']}\">{s['lai_link']}</a></p>")
        if s.get("procedures"):
            html_parts.append(f"    <p><strong>Procedures:</strong> {s['procedures']}</p>")
        if s.get("note"):
            html_parts.append(f"    <p><strong>Note:</strong> {s['note']}</p>")
        if s.get("suggested_reviewers"):
            html_parts.append(f"    <p><strong>Suggested reviewers:</strong> {s['suggested_reviewers']}</p>")
        html_parts.append("  </div>")

    html_parts.extend([
        "",
        "  <h2>3. Issues to Be Aware Of</h2>",
        "  <table class=\"issues-table\">",
        "    <thead><tr><th>Study</th><th>Issue</th></tr></thead>",
        "    <tbody>",
    ])
    for row in b["issues"]:
        html_parts.append(f"      <tr><td><strong>{row['study']}</strong></td><td>{row['issue']}</td></tr>")
    html_parts.extend(["    </tbody>", "  </table>", ""])

    access = b["access"]
    html_parts.extend([
        "  <h2>4. Access</h2>",
        "  <ul class=\"access-list\">",
        f"    <li><strong>Admin:</strong> <a href=\"{access['admin']}\">Admin panel</a></li>",
        f"    <li><strong>Researcher dashboard:</strong> <a href=\"{access['researcher_dashboard']}\">Study list</a></li>",
        "  </ul>",
        "",
        "  <h2>5. Full IRB Documents (for review)</h2>",
        "  <ul>",
    ])
    for d in b["full_documents"]:
        if isinstance(d, dict):
            link = d.get("link", "#")
            link_text = d.get("link_text", d.get("label", "View"))
            label = d.get("label", "")
            html_parts.append(f"    <li><strong>{label}:</strong> <a href=\"{link}\">{link_text}</a></li>")
        else:
            html_parts.append(f"    <li>{d}</li>")
    html_parts.append("  </ul>")

    # Section 6: Federal Audit Compliance (if present)
    if "federal_audit" in b:
        fa = b["federal_audit"]
        html_parts.extend([
            "",
            "  <h2>6. Federal Audit Compliance (No Credit/Bonus)</h2>",
            "  <div class=\"study-card\">",
            f"    <p><strong>Context:</strong> {fa.get('context', '')}</p>",
            f"    <p><strong>Why no credit/bonus changes FERPA:</strong> {fa.get('why_no_credit', '')}</p>",
            "  </div>",
            "",
            "  <h3>Minimum Requirements</h3>",
        ])
        for req in fa.get("requirements", []):
            html_parts.append(f"  <p><strong>{req.get('area', '')}:</strong></p>")
            html_parts.append("  <ul>")
            for item in req.get("items", []):
                html_parts.append(f"    <li>{item}</li>")
            html_parts.append("  </ul>")
        html_parts.extend([
            "",
            "  <h3>Disable Without Credit</h3>",
            "  <ul>",
        ])
        for item in fa.get("disable_without_credit", []):
            html_parts.append(f"    <li>{item}</li>")
        html_parts.extend([
            "  </ul>",
            "",
            "  <h3>Formalization Options</h3>",
            "  <table class=\"doc-table\">",
            "    <thead><tr><th>Option</th><th>Cost</th><th>Audit Posture</th></tr></thead>",
            "    <tbody>",
        ])
        for opt in fa.get("formalization_options", []):
            html_parts.append(f"      <tr><td>{opt.get('option', '')}</td><td>{opt.get('cost', '')}</td><td>{opt.get('posture', '')}</td></tr>")
        html_parts.extend([
            "    </tbody>",
            "  </table>",
            "",
            "  <h3>Recommended Minimum</h3>",
            "  <ol>",
        ])
        for item in fa.get("recommended_minimum", []):
            html_parts.append(f"    <li>{item}</li>")
        html_parts.append("  </ol>")

    c = meta["contact"]
    html_parts.extend([
        "",
        "  <div class=\"contact-block\">",
        f"    <strong>Contact:</strong> {c['name']} — <a href=\"mailto:{c['email']}\">{c['email']}</a> | {c['phone']}",
        "  </div>",
        "",
        "  <p style=\"margin-top: 1.5rem; font-size: 0.8rem; color: #6b7280;\">Pre-meeting briefing for IRB reviewers. PRAMS: <a href=\"https://bayoupal.nicholls.edu/hsirb/\">bayoupal.nicholls.edu/hsirb/</a></p>",
        "",
        "</body>",
        "</html>",
    ])

    HTML_PATH.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"Generated: {HTML_PATH}")


if __name__ == "__main__":
    main()
