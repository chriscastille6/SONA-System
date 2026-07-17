"""
Compliance guardrail engine.

Evaluates an action context against principles and returns structured
warnings (soft) and blocks (hard) with authority citations so decision
making is explainable under administrative review.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from django.conf import settings

from .principles import PRINCIPLES, principle_citation
from .scanners import join_fields, scan_text_for_ipi_signals


class Severity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    BLOCK = 'block'


@dataclass
class ComplianceWarning:
    code: str
    severity: Severity
    principle_id: str
    title: str
    message: str
    remediation: str
    authority: str = ''

    def __post_init__(self):
        if not self.authority and self.principle_id in PRINCIPLES:
            self.authority = principle_citation(self.principle_id)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['severity'] = self.severity.value if isinstance(self.severity, Severity) else self.severity
        return d


@dataclass
class ComplianceReport:
    action: str
    warnings: List[ComplianceWarning] = field(default_factory=list)
    decision_rationale: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def blocks(self) -> List[ComplianceWarning]:
        return [w for w in self.warnings if w.severity == Severity.BLOCK]

    @property
    def soft_warnings(self) -> List[ComplianceWarning]:
        return [w for w in self.warnings if w.severity == Severity.WARNING]

    @property
    def is_blocked(self) -> bool:
        return bool(self.blocks)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action,
            'is_blocked': self.is_blocked,
            'has_warnings': self.has_warnings,
            'warnings': [w.to_dict() for w in self.warnings],
            'decision_rationale': list(self.decision_rationale),
            'metadata': dict(self.metadata),
            'principles_cited': sorted({w.principle_id for w in self.warnings}),
        }

    def explain(self) -> str:
        """Human-readable decision explanation for UI / audit."""
        lines = [f'Compliance evaluation for action: {self.action}']
        if not self.warnings:
            lines.append(
                'No automated principle warnings fired. Human judgment and institutional '
                'policy still apply (APA CPTA continuous improvement; CITI oversight).'
            )
        for w in self.warnings:
            lines.append(
                f'[{w.severity.value.upper()}] {w.code} — {w.title}: {w.message} '
                f'Authority: {w.authority}. Remediation: {w.remediation}'
            )
        if self.decision_rationale:
            lines.append('Decision rationale:')
            for r in self.decision_rationale:
                lines.append(f'  - {r}')
        return '\n'.join(lines)


def _enabled() -> bool:
    return bool(getattr(settings, 'COMPLIANCE_WARNINGS_ENABLED', True))


def evaluate_protocol_submission(submission, *, use_ai_review: bool = False) -> ComplianceReport:
    """
    Pre-submit / confirm-page checks for a ProtocolSubmission draft.
    """
    report = ComplianceReport(action='protocol_submit')
    if not _enabled():
        report.decision_rationale.append('Compliance warnings disabled by settings.')
        return report

    text = join_fields([
        getattr(submission, 'confidentiality_procedures', '') or '',
        getattr(submission, 'data_storage', '') or '',
        getattr(submission, 'data_sharing_plan', '') or '',
        getattr(submission, 'risk_statement', '') or '',
        getattr(submission, 'consent_procedures', '') or '',
        getattr(submission, 'methodology', '') or '',
        getattr(submission, 'purpose', '') or '',
    ])
    scan = scan_text_for_ipi_signals(text)
    report.metadata['ipi_scan'] = {
        'signal_categories': scan['signal_categories'],
        'counts': scan['counts'],
    }

    if not (getattr(submission, 'confidentiality_procedures', '') or '').strip():
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_MISSING_CONFIDENTIALITY',
            severity=Severity.WARNING,
            principle_id='IPI_VS_DEID',
            title='Missing confidentiality procedures',
            message='Protocol draft lacks confidentiality/anonymity procedures.',
            remediation='Document IPI handling, de-identification, access controls, and retention before submit.',
        ))

    if not (getattr(submission, 'data_storage', '') or '').strip():
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_MISSING_DATA_STORAGE',
            severity=Severity.WARNING,
            principle_id='LOCAL_CUSTODY',
            title='Missing data storage description',
            message='Protocol draft does not describe where data will be stored.',
            remediation='State university-managed storage (local/campus systems) and encryption controls.',
        ))

    if scan['has_cloud_ai_risk']:
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_PUBLIC_AI_LANGUAGE',
            severity=Severity.BLOCK if getattr(settings, 'COMPLIANCE_BLOCK_PUBLIC_AI_IN_PROTOCOL', True) else Severity.WARNING,
            principle_id='NO_PUBLIC_LLM_IPI',
            title='Public / consumer AI processing indicated',
            message=(
                'Protocol text appears to reference public/consumer generative AI for data handling. '
                'That creates unauthorized-disclosure risk under La. R.S. 17:3914 and FERPA.'
            ),
            remediation=(
                'Remove public-LLM processing of IPI. Use local/university-managed AI only, '
                'or confirm materials are fully de-identified with HITL attestation before any AI assist.'
            ),
        ))

    if scan['has_third_party_share_risk']:
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_THIRD_PARTY_SHARE',
            severity=Severity.WARNING,
            principle_id='LA_3914_NO_UNAUTHORIZED_DISCLOSURE',
            title='Third-party / external sharing language detected',
            message='Protocol mentions third-party or external data sharing.',
            remediation=(
                'Identify the recipient, legal authority, data minimization, DPA/BA if required, '
                'and HITL gate before any transfer.'
            ),
        ))

    if scan['has_mosaic_cue']:
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_MOSAIC_RISK',
            severity=Severity.WARNING,
            principle_id='MOSAIC_ATTACK',
            title='Mosaic / small-cell re-identification cue',
            message='Protocol language suggests small-n or individual-level release risk.',
            remediation='Plan k-anonymity / generalization and human audit before any external share.',
        ))

    if use_ai_review:
        _append_ai_provider_warnings(report, materials_may_contain_ipi=True)

    if not (getattr(submission, 'consent_procedures', '') or '').strip():
        report.warnings.append(ComplianceWarning(
            code='PROTOCOL_MISSING_CONSENT',
            severity=Severity.WARNING,
            principle_id='INFORMED_CONSENT_AI',
            title='Missing consent procedures',
            message='Consent procedures field is empty.',
            remediation='Document consent/assent language, privacy limits, and withdrawal rights.',
        ))

    report.decision_rationale.append(
        'Evaluated protocol draft against CITI IPI/de-id, La. R.S. 17:3914 non-disclosure, '
        'APA CPTA privacy/HITL, and SIOP CAPE public-AI privacy rules.'
    )
    if not report.is_blocked:
        report.decision_rationale.append(
            'No hard blocks remain (or only soft warnings). Submission may proceed with '
            'researcher acknowledgment of listed warnings; IRB determination remains independent.'
        )
    return report


def evaluate_ferpa_export(
    *,
    export_type: str,
    includes_direct_identifiers: bool = True,
    hitl_attested: bool = False,
    destination: str = 'download',
) -> ComplianceReport:
    """
    Guardrails for education-record / research exports.
    """
    report = ComplianceReport(
        action=f'export:{export_type}',
        metadata={
            'includes_direct_identifiers': includes_direct_identifiers,
            'hitl_attested': hitl_attested,
            'destination': destination,
        },
    )
    if not _enabled():
        report.decision_rationale.append('Compliance warnings disabled by settings.')
        return report

    if includes_direct_identifiers:
        report.warnings.append(ComplianceWarning(
            code='EXPORT_CONTAINS_IPI',
            severity=Severity.WARNING,
            principle_id='FERPA_EDUCATION_RECORDS',
            title='Export contains education-record identifiers',
            message=(
                'This export includes direct identifiers (e.g., name, email, student ID). '
                'It is an education record under FERPA and student PII under La. R.S. 17:3914.'
            ),
            remediation=(
                'Keep the file on university-managed systems. Do not upload to public AI, '
                'personal cloud, or unauthorized vendors. Prefer anonymized research exports '
                'when identifiers are not required.'
            ),
        ))
        report.warnings.append(ComplianceWarning(
            code='EXPORT_NO_PUBLIC_AI',
            severity=Severity.WARNING,
            principle_id='NO_PUBLIC_LLM_IPI',
            title='Do not paste export contents into public AI',
            message='Pasting identifiable export rows into consumer LLMs is an unauthorized disclosure risk.',
            remediation='Use local analysis tools only; strip identifiers or use salted anonymized IDs first.',
        ))

    require_hitl = bool(getattr(settings, 'COMPLIANCE_REQUIRE_HITL_FOR_EXPORT', False))
    if includes_direct_identifiers and require_hitl and not hitl_attested:
        report.warnings.append(ComplianceWarning(
            code='EXPORT_HITL_REQUIRED',
            severity=Severity.BLOCK,
            principle_id='HITL_BEFORE_SHARE',
            title='Human-in-the-loop attestation required',
            message='Settings require HITL attestation before identifiable exports.',
            remediation='Confirm review checkbox / attestation that this export will not leave authorized custody.',
        ))

    if destination not in ('download', 'local', 'university_managed'):
        report.warnings.append(ComplianceWarning(
            code='EXPORT_EXTERNAL_DESTINATION',
            severity=Severity.BLOCK,
            principle_id='LA_3914_NO_UNAUTHORIZED_DISCLOSURE',
            title='External export destination blocked',
            message=f'Export destination "{destination}" is not an approved local/university channel.',
            remediation='Use browser download to university-managed hardware only.',
        ))

    report.decision_rationale.append(
        'Export evaluated under FERPA education-records rules, La. R.S. 17:3914, '
        'and APA/SIOP prohibition on public-LLM processing of IPI.'
    )
    return report


def evaluate_ai_provider_use(
    *,
    provider: Optional[str] = None,
    materials_may_contain_ipi: bool = True,
) -> ComplianceReport:
    """Evaluate whether the configured AI provider is appropriate for materials."""
    report = ComplianceReport(action='ai_review')
    if not _enabled():
        report.decision_rationale.append('Compliance warnings disabled by settings.')
        return report
    _append_ai_provider_warnings(
        report,
        provider=provider,
        materials_may_contain_ipi=materials_may_contain_ipi,
    )
    return report


def _append_ai_provider_warnings(
    report: ComplianceReport,
    *,
    provider: Optional[str] = None,
    materials_may_contain_ipi: bool = True,
) -> None:
    provider = (provider or getattr(settings, 'IRB_AI_PROVIDER', 'openai') or 'openai').lower()
    report.metadata['ai_provider'] = provider
    local_providers = {'ollama'}
    cloud_providers = {'openai', 'anthropic', 'gemini'}

    if provider in local_providers:
        report.warnings.append(ComplianceWarning(
            code='AI_LOCAL_PROVIDER_OK',
            severity=Severity.INFO,
            principle_id='LOCAL_CUSTODY',
            title='Local / university-managed AI provider',
            message=f'AI provider "{provider}" keeps inference on a local/server endpoint you control.',
            remediation='Confirm the Ollama host is university-managed and not logging prompts externally.',
        ))
        report.decision_rationale.append(
            f'Provider {provider} aligns with local-custody preference (CITI InfoSec; La. R.S. 17:3914).'
        )
        return

    if provider in cloud_providers and materials_may_contain_ipi:
        block = bool(getattr(settings, 'COMPLIANCE_BLOCK_CLOUD_AI_WITH_IPI', False))
        report.warnings.append(ComplianceWarning(
            code='AI_CLOUD_PROVIDER_IPI_RISK',
            severity=Severity.BLOCK if block else Severity.WARNING,
            principle_id='NO_PUBLIC_LLM_IPI',
            title='Cloud AI provider with possible IPI in materials',
            message=(
                f'IRB AI provider is "{provider}". Protocol/consent materials may contain IPI. '
                'Cloud transmission can create third-party disclosure under FERPA / La. R.S. 17:3914 '
                'unless materials are confirmed de-identified and vendor terms prohibit training use.'
            ),
            remediation=(
                'Prefer IRB_AI_PROVIDER=ollama on university hardware; or strip IPI from materials '
                'before cloud AI; document HITL review of what was sent.'
            ),
        ))
        report.decision_rationale.append(
            'Cloud AI + possible IPI triggers APA CPTA §3 / SIOP public-AI privacy warning.'
        )
    elif provider in cloud_providers:
        report.warnings.append(ComplianceWarning(
            code='AI_CLOUD_PROVIDER_DEID_ASSUMED',
            severity=Severity.INFO,
            principle_id='IPI_VS_DEID',
            title='Cloud AI with de-identified materials assumed',
            message=f'Provider "{provider}" is cloud-hosted; ensure materials contain no IPI before send.',
            remediation='Re-scan materials; keep a human audit trail of de-identification.',
        ))


def evaluate_decision_rationale(notes: str, *, decision: str) -> ComplianceReport:
    """Require explainable rationale for IRB determinations when configured."""
    report = ComplianceReport(action=f'irb_decision:{decision}')
    if not _enabled():
        return report
    notes = (notes or '').strip()
    require = bool(getattr(settings, 'COMPLIANCE_REQUIRE_DECISION_RATIONALE', True))
    if require and len(notes) < 15:
        report.warnings.append(ComplianceWarning(
            code='DECISION_RATIONALE_REQUIRED',
            severity=Severity.BLOCK,
            principle_id='TRANSPARENCY_ACCOUNTABILITY',
            title='Decision rationale too short or missing',
            message=(
                'APA CPTA transparency/accountability and institutional auditability require a '
                'substantive written rationale for IRB determinations.'
            ),
            remediation='Enter at least a short paragraph explaining the determination basis.',
        ))
    else:
        report.decision_rationale.append(
            'Human decision rationale present; accountability principle satisfied at documentation level.'
        )
    return report
