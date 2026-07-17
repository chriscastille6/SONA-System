# Institutional & State Authorities (PPM + JML 25-109)

These authorities are cited by `apps/compliance` guardrails alongside CITI, FERPA, La. R.S. 17:3914, and APA/SIOP guidance.

## Nicholls Policy & Procedure Manual

- **Portal:** https://www.nicholls.edu/policy-procedure-manual/
- **§5.3.5 Information Technology Policy**  
  Users of Nicholls IT resources (faculty, staff, students) must know and follow campus IT policies. Security and privacy policies protect data and IP. Violations may trigger university penalties.  
  Full IT policy database: https://www.nicholls.edu/information-tech/policyandprocedure/
- **§2.7.1 AI Use Policy (syllabi)**  
  Generative AI tools (e.g., ChatGPT) used for student course credit require instructor permission and attribution; misuse is plagiarism. Research/admin AI remains governed by IT policy + student-data law + JML 25-109.
- **§5.7 Academic Affairs / Records**  
  Office of Records and Registration monitors FERPA compliance.

## Louisiana Executive Order JML 25-109

- **Title:** Amended State Government's Use of AI  
- **PDF:** https://www.doa.la.gov/media/tzqptbak/jml-25-109-amended-state-government-s-use-of-ai.pdf  
- **Key operational sections for PRAMS workflows:**
  - **§2** — AI source use must be approved (CIO / agency head outside OTS) as secure and reliable.
  - **§6** — Until mandated AI policies are implemented, **do not input** into any AI system: public PII; property-specific info; proprietary info; confidential data; restricted data; cybersecurity/physical-security-sensitive info.
  - **§7** — Review/cleanse datasets before AI use (data quality / “garbage in, garbage out”).
  - **WHEREAS / university warning** — Hostile foreign AI (e.g., DeepSeek) has no place in Louisiana universities.
  - **§8** — State entities and political subdivisions directed to cooperate.

## How PRAMS uses these

| Workflow | Citation used |
|----------|----------------|
| Protocol submit (public AI / DeepSeek language) | JML 25-109 §6; PPM §5.3.5 |
| Cloud AI IRB preflight with possible IPI | JML 25-109 §§2/6; PPM §5.3.5 |
| Local Ollama preference | PPM §5.3.5 / IT Policies; JML 25-109 risk reduction |
| FERPA credit export | FERPA; PPM §5.7; La. R.S. 17:3914; JML 25-109 §6 (no paste into AI) |

This document is an operational map for explainability—not legal advice and not a substitute for official PPM text or the signed Executive Order.

## Cursor agent enforcement

The same authorities are mirrored for local/cloud agent work via:

- `.cursor/rules/nicholls-research-compliance.mdc` (always apply)
- `.cursor/rules/ferpa-image-pii.mdc` (always apply)
- `.cursor/hooks.json` → `beforeSubmitPrompt` + `beforeReadFile`

See `docs/COMPLIANCE_GUARDRAILS.md` § Cursor rules & hooks.
