"""
Decision explainability helpers.

Persists structured decision traces to AuditLog so researchers and reviewers
can later explain *why* an action was allowed, warned, or blocked — with
principle citations baked into metadata.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .guardrails import ComplianceReport


def build_decision_trace(
    report: ComplianceReport,
    *,
    outcome: str,
    actor_note: str = '',
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a JSON-serializable decision trace.

    outcome: one of allow | allow_with_warnings | block | attested
    """
    trace = {
        'outcome': outcome,
        'action': report.action,
        'explanation': report.explain(),
        'principles_cited': sorted({w.principle_id for w in report.warnings}),
        'warning_codes': [w.code for w in report.warnings],
        'block_codes': [w.code for w in report.blocks],
        'decision_rationale': list(report.decision_rationale),
        'report': report.to_dict(),
        'actor_note': (actor_note or '')[:2000],
    }
    if extra:
        # Avoid nesting raw PII; callers must scrub first.
        trace['extra'] = extra
    return trace


def log_compliance_decision(
    *,
    actor,
    action: str,
    entity: str,
    entity_id=None,
    report: ComplianceReport,
    outcome: str,
    request=None,
    actor_note: str = '',
    extra: Optional[Dict[str, Any]] = None,
):
    """
    Write an AuditLog row for a compliance-evaluated decision.

    Failures are swallowed at the call site if needed; this function raises
    so callers can choose. Prefer try/except in views to avoid blocking UX
    when audit DB write fails unexpectedly.
    """
    from apps.credits.models import AuditLog

    ip = None
    ua = ''
    if request is not None:
        ip = request.META.get('REMOTE_ADDR')
        if ip and len(str(ip)) >= 45:
            ip = None
        ua = (request.META.get('HTTP_USER_AGENT') or '')[:500]

    metadata = build_decision_trace(
        report,
        outcome=outcome,
        actor_note=actor_note,
        extra=extra,
    )
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip,
        user_agent=ua,
        metadata=metadata,
    )


def outcome_from_report(report: ComplianceReport, *, proceeded: bool) -> str:
    if report.is_blocked and not proceeded:
        return 'block'
    if report.is_blocked and proceeded:
        return 'override_block'  # should be rare / admin-only
    if report.soft_warnings and proceeded:
        return 'allow_with_warnings'
    if proceeded:
        return 'allow'
    return 'cancelled'
