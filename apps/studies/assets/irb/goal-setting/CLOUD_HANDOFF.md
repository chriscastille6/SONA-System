# Goal-setting HSIRB packet — Cursor Cloud handoff

Development / protocol packaging only. Synthetic and IRB materials; no student PII.

## Purpose

Keep the Nicholls goal-setting (public title: **A Study in Decision Making**) exempt HSIRB packet and rebuild tooling available so follow-up agents can regenerate PDFs and so **IRB reviewers see the familiar Nicholls-branded packet** (cover + project information form + narrative + appendices), not ad-hoc form overlays.

**Reviewer-facing output (PRAMS):** Protocol Submissions → goal-setting / decision-making → **HSIRB application packet (PDF)**  
Also: `/studies/<slug>/protocol/documentation/` for `goal-setting` or `decision-making`.

Rebuild attaches the packet to `ProtocolSubmission.full_protocol_pdf` via `add_goal_setting_study_online`.

## Canonical packet files

| Path | Role |
|------|------|
| `apps/studies/assets/irb/goal-setting/materials/pdf/HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf` | Full exempt application + appendices A–H (current) |
| `apps/studies/assets/irb/goal-setting/materials/pdf/HSIRB_Application_A_Study_in_Decision_Making_with_signup_qr.pdf` | Same packet variant refreshed from the full packet (main flyer already includes signup QR) |
| `apps/studies/assets/irb/goal-setting/HSIRB_EXEMPT_REVIEW_REQUEST.pdf` | Official rev9 2019 form overlay (pages 1–4) + Attachment A narrative + CITI |
| `apps/studies/assets/irb/goal-setting/HSIRB_EXEMPT_REVIEW_REQUEST.md` | Field map for the rev9 draft |
| `apps/studies/assets/irb/goal-setting/HSIRB-exempt_review_request.rev9_2019.v2_BLANK.pdf` | Official blank used by the filler |
| `apps/studies/assets/irb/goal-setting/chris_castille_irb_approval_july_2024.pdf` | Prior local approval PDF on file |
| `apps/studies/assets/irb/goal-setting/addendum_1_procedural_modifications.pdf` | Procedural addendum on file |
| `apps/studies/assets/irb/goal-setting/materials/` | Editable `.txt` / `.docx` sources + `admin/` print masters |
| `apps/studies/assets/irb/goal-setting/materials/pdf/` | Participant appendix PDFs (consent, flyers, workbook sample, Waterloo protocol, RR manuscript, IPA letter) |

## Rebuild commands (technical)

Requires `pymupdf` and `reportlab` (`pip install pymupdf reportlab`).

```bash
# Official rev9 exempt form draft (overlay + Attachment A + CITI)
python3 scripts/fill_decision_making_hsirb_exempt_form.py

# Rebuild full packet narrative + appendices from current materials/pdf sources
python scripts/rebuild_goal_setting_hsirb_packet.py --no-tmp-copy

# Refresh with_signup_qr variant from the repo full packet (auto-finds main flyer page)
python scripts/embed_goal_setting_hsirb_packet_qr.py

# Optional: regenerate branded flyers (includes signup QR on main flyer)
python scripts/generate_goal_setting_flyer.py

# Optional: rebuild consent .docx from .txt, then PDF via LibreOffice helper
python scripts/build_goal_setting_consent_docx.py
./scripts/build_consent_from_docx.sh
```

DB narrative seed (PRAMS protocol fields):  
`python manage.py populate_goal_setting_protocol_details`

## Packet structure (current)

1. Exempt request cover + project information form  
2. Narrative sections (two-phase pilot → main; payment main-only; repeat-participation disclosure)  
3. List of appendices  
4. Appendices A / A2 (pilot & main flyers), B / B2 (pilot & main consent), C (workbook sample), D (productivity report), E / E2 (pilot appreciation & main debrief), F (UWaterloo master protocol), G (Psych Science RR manuscript), H (Stage 1 IPA letter)

## Do not invent

- Do not change exemption category, protocol numbers, approval status, risk language, or Waterloo claims unless the human PI supplies updated source text.  
- Prefer packaging/rebuild/docs fixes over rewriting consent or protocol substance.  
- Participant materials already state titles **Assistant Professor of Marketing** for Gravois and Maught; the rebuild script must stay aligned with those sources.

## Human remaining (not agent work)

- Confirm CITI certificates are attached/submitted (packet text still notes certificates pending / upon request).  
- PI review of rebuilt PDFs before HSIRB submission or amendment filing.  
- Any formal HSIRB submission / amendment through PRAMS or board channels.  
- Production deploy of study/protocol DB fields if needed (separate from this packaging branch).
