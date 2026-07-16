# HSIRB FAQ: AI Tools, Local Analysis, and Education Records

This FAQ states how PRAMS / HSIRB-related work should treat **AI coding assistants** (for example Cursor), **R/Python analysis**, and **FERPA-covered education records**. It is meant to close a common open question for IT and IRB reviewers: *how do we get help analyzing data without putting student-level files in the cloud?*

This page describes **policy posture and proportionate controls**. It does not claim that any tool makes re-identification risk zero.

## Short answer

**Default: local-first.**  
Row-level student or participant data stays on an approved local or campus system. AI assistants and cloud agents receive **research questions, analysis plans, and code**, plus **synthetic or dummy data** when a dry-run is needed. They do **not** receive identifiable education records.

**Only when a table must leave the device** do we use a documented de-identification and release path (human attestation, and optional mosaic / DCR / distractor controls). Analytic work that needs outliers, multilevel models, or interaction tests should run on the **local analytic frame**, not on a diluted cloud export.

## FAQ

### 1. Can I paste student-level CSVs into Cursor (cloud) or another AI chat?

**No** for identifiable or readily linkable education records, unless IT and IRB have explicitly approved that path for that project.

Use one of these instead:

1. **Local-first (preferred):** Keep the real file on your machine or campus host. Ask the AI for code and model specifications. Run R/Python locally. Bring back only **non-identifying** outputs (coefficients, fit stats, plots without row IDs, aggregated tables).
2. **Synthetic dry-run:** Give the AI a dummy or synthetic schema (for example clearly fake Disney-named rows) so it can draft and test code. Swap in the real local file only on your machine.
3. **Release-minimized export (exception path):** If a file must leave the device, follow the de-identification gate below. Do not treat this as the daily workflow for multilevel or outlier analysis.

### 2. What is the difference between “local-first” and “release-minimized”?

| Pattern | Where the real rows live | What the AI / cloud may see | Use when |
|--------|---------------------------|-----------------------------|----------|
| Local-first | Approved local or campus system | Questions, code, dummy/synthetic stand-ins; later, non-identifying results | Almost all HSIRB analysis support |
| Release-minimized | Real rows stay local; only a controlled table may leave | De-identified / synthetic / diluted table **without** local linkage keys | A partner, vendor, or off-device tool truly requires a file |

### 3. Does using AI for code review or model design require sending my dataset?

**No.** For most meeting concerns (main effects, interactions, multilevel structure, outlier diagnostics), the AI needs the **hypothesis, variable dictionary, and design**, not the student file. Code can be validated on synthetic data, then executed locally on the real extract.

### 4. What if IT’s concern is specifically “Cursor cannot touch our data”?

That concern is usually solved by **local-first**, not by building a perfect cloud-safe research extract.

- Push the **question and a tested script** to the researcher’s computer.
- Run analysis **on-device** (R or Python).
- Return **summaries only**.

Heavy de-identification, distance-to-closest-record (DCR) gates, and distractor dilution are for **off-device release**, and are often overkill for “help me write the multilevel model.”

### 5. When we do release a table, what gates are expected?

At minimum:

1. **No direct identifiers** in the release file (names, emails, SSNs, institutional mailbox strings, etc.).
2. **Institutional brand stripping** when brand leakage is a stated risk.
3. **Human attestation** (who approved, when, decision, integrity hash of the reviewed file).
4. **No upload of local-only keys** that would reveal which rows or columns are analytic versus decoy.

Optional hardening for higher scrutiny (documented in the local PoC tooling):

- Exact clone checks against the scrubbed source.
- Quasi-identifier uniqueness reporting (k-map style).
- DCR near-match culls (reject synthetic rows too close to real scrubbed rows).
- Distractor **variables** and distractor **cases** in the cloud-facing file, with an **on-device encrypted linkage key** used only locally to cut/keep.

### 5a. What technical enforcement exists beyond “please follow the FAQ”?

The local PoC adds **enforcement gates** (still not a full campus DLP/HSM program):

| Control | What it does |
|--------|----------------|
| **`.cursorignore`** | Keeps local audit CSVs, linkage keys, identifiable drop folders, and env secrets out of default Cursor indexing / cloud-agent context |
| **Mandatory APPROVE check** | Refuses to write the cloud-candidate CSV unless the attestation log contains a human `APPROVE` |
| **Outbound DLP scan** | Blocks export if emails, SSN-shaped values, institutional brand strings, or non-token identifier columns remain |
| **Encrypted linkage key** | Stores the cut/keep map as `local_only_linkage_key.json.enc` with a local Fernet key file; plaintext key beside the release is a hard fail |
| **Packaging rule** | Cloud bundle = diluted CSV only; never the `.enc` / `.key` / attestation / audit sample |

Campus production should still add network DLP, approved storage paths, and secrets-manager/HSM key custody. The PoC demonstrates enforceable local gates; it does not replace those controls.

### 6. Will distractors or privacy filters break outlier and multilevel analyses?

**They must not enter the analytic model.**

- **Cloud-facing diluted files** may contain decoy rows and decoy columns to reduce re-identification utility.
- **Local analysis** uses the on-device linkage key to keep analytic rows and true analysis columns only, then runs outliers, multilevel models, and interaction tests on that frame.
- Privacy filters that thin neighborhoods (for example aggressive DCR culling) can still change tails. For outlier-focused work, prefer **local-first on the real approved extract** when policy allows, rather than analyzing the diluted release file.

### 7. Do we claim “zero re-identification risk”?

**No.** HSIRB language should say **risk reduction with documented gates**, not absolute elimination. Mosaic / linkage risk can remain if an attacker knows the true quasi-identifier set and has strong auxiliary data. Controls reduce that risk; they do not magically erase it.

### 8. What may be returned from a local run into an AI chat or ticket?

Allowed examples: model formulas, anonymized coefficient tables, fit indices, methodology notes, error messages with **no** student names/emails/IDs, and plots that do not label individuals.

Not allowed: row-level dumps, identifiable logs, grade rosters, or files that still contain direct identifiers.

### 9. How does this relate to PRAMS study data exports?

PRAMS research exports should remain consistent with existing platform rules: opaque participant IDs where used, role-based access, and no unnecessary direct identifiers in researcher downloads. This FAQ adds the **AI-tooling** rule: cloud assistants are not an alternate export channel for education records.

### 10. What should PIs write in a protocol about AI analysis support?

A proportionate statement is enough, for example:

> Identifiable education records and participant-level analysis files remain on approved local or campus systems. AI coding assistants may be used for analysis planning and code generation with synthetic or de-identified stand-in data only. Any off-device dataset follows institutional de-identification and human attestation requirements. Analytic models for hypotheses, interactions, and outliers are executed locally on the approved analysis file.

## Related local tooling (optional)

- `scripts/ferpa_local_deid_synthesis_poc.py` — full local release pipeline with enforcement gates  
- `scripts/ferpa_release_enforcement.py` — reusable outbound DLP / encrypted-key helpers (`scan <file.csv>`)  
- `.cursorignore` — path blocks for local sensitive artifacts  

These are control patterns for IT review—not a requirement for every multilevel analysis request. Daily work should remain **local-first**.

### 11. Does NIST CAISI change our local-first data rules?

**Not directly.** NIST’s [Center for AI Standards and Innovation (CAISI)](https://www.nist.gov/caisi) focuses on measuring and securing **commercial AI systems**, voluntary standards, and evaluations of AI capabilities that may pose national-security-relevant risks. It is not a FERPA handbook and does not replace campus IT rules for education records.

What *is* useful to borrow for PRAMS / HSIRB AI use:

1. **Pre-deployment testing is not enough.** CAISI’s NIST AI 800-4 work on [post-deployment monitoring of AI systems](https://www.nist.gov/news-events/news/2026/03/new-report-challenges-monitoring-deployed-ai-systems) stresses that AI behavior in real use can differ from lab checks. For us, that means AI IRB helpers and coding assistants need ongoing review after they are turned on—not a one-time demo.
2. **Monitor more than “did the model answer?”** Useful monitoring buckets from that CAISI/NIST framing include: functionality, operations, **human factors** (over-trust, unclear AI advice), **security/misuse**, **compliance** (FERPA / protocol scope), and broader impacts. Human-factors and compliance are the gaps most likely to matter in an IRB setting.
3. **Treat AI evaluation results carefully.** CAISI has also highlighted that models can “cheat” or look stronger than they are on agentic evaluations. Do not treat a green AI IRB score as an audit sign-off.
4. **Supply-chain / model provenance awareness.** If campus tools call external model APIs, know which vendor/model is used and that identifiable education records must not be the prompt payload (same local-first rule).

**Bottom line:** Keep CAISI as an AI-*system* measurement lens. Keep FERPA local-first as the *data* rule. They complement each other; CAISI does not authorize sending student rows to cloud AI.

## Revision note

This FAQ is intended for the HSIRB / PRAMS public guidance surface so “AI + student data + Cursor/R/Python” is no longer an undocumented open issue. Update this document when campus IT issues a more specific AI or data-handling standard. References to NIST CAISI / NIST AI 800-4 should be refreshed if NIST revises that monitoring guidance.
