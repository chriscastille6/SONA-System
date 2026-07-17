"""Unit tests for compliance guardrails (synthetic data only)."""

from django.test import SimpleTestCase, override_settings

from apps.compliance.guardrails import (
    Severity,
    evaluate_ai_provider_use,
    evaluate_decision_rationale,
    evaluate_ferpa_export,
    evaluate_protocol_submission,
)
from apps.compliance.scanners import scan_text_for_ipi_signals
from apps.compliance.explainability import build_decision_trace, outcome_from_report


class FakeSubmission:
    def __init__(self, **kwargs):
        self.confidentiality_procedures = kwargs.get('confidentiality_procedures', '')
        self.data_storage = kwargs.get('data_storage', '')
        self.data_sharing_plan = kwargs.get('data_sharing_plan', '')
        self.risk_statement = kwargs.get('risk_statement', '')
        self.consent_procedures = kwargs.get('consent_procedures', '')
        self.methodology = kwargs.get('methodology', '')
        self.purpose = kwargs.get('purpose', '')


class ScannerTests(SimpleTestCase):
    def test_detects_email_without_logging_raw_value(self):
        scan = scan_text_for_ipi_signals('Contact participant@example.edu for follow-up')
        self.assertTrue(scan['has_ipi_like_signals'])
        self.assertEqual(scan['counts']['email'], 1)
        # Ensure we only expose categories/counts, not the address itself
        blob = str(scan)
        self.assertNotIn('participant@example.edu', blob)

    def test_detects_public_ai_phrase(self):
        scan = scan_text_for_ipi_signals('We will analyze open responses with ChatGPT.')
        self.assertTrue(scan['has_cloud_ai_risk'])


@override_settings(COMPLIANCE_WARNINGS_ENABLED=True, COMPLIANCE_BLOCK_PUBLIC_AI_IN_PROTOCOL=True)
class ProtocolGuardrailTests(SimpleTestCase):
    def test_missing_confidentiality_warns(self):
        sub = FakeSubmission(
            consent_procedures='Written consent obtained.',
            data_storage='Campus encrypted server.',
        )
        report = evaluate_protocol_submission(sub)
        codes = {w.code for w in report.warnings}
        self.assertIn('PROTOCOL_MISSING_CONFIDENTIALITY', codes)
        self.assertFalse(report.is_blocked)

    def test_chatgpt_in_protocol_blocks(self):
        sub = FakeSubmission(
            confidentiality_procedures='Data stored locally.',
            data_storage='University laptop.',
            consent_procedures='Consent form used.',
            data_sharing_plan='Transcripts will be uploaded to ChatGPT for thematic coding.',
        )
        report = evaluate_protocol_submission(sub)
        self.assertTrue(report.is_blocked)
        self.assertTrue(any(w.code == 'PROTOCOL_PUBLIC_AI_LANGUAGE' for w in report.blocks))

    def test_clean_local_protocol_minimal_warnings(self):
        sub = FakeSubmission(
            confidentiality_procedures='No direct identifiers; SONA codes only; local encrypted disk.',
            data_storage='University-managed laptop; BitLocker; no cloud sync.',
            consent_procedures='Online consent with withdrawal rights.',
            data_sharing_plan='Aggregated results only after human review; no third-party processors.',
        )
        report = evaluate_protocol_submission(sub)
        self.assertFalse(report.is_blocked)
        self.assertNotIn('PROTOCOL_PUBLIC_AI_LANGUAGE', {w.code for w in report.warnings})


@override_settings(COMPLIANCE_WARNINGS_ENABLED=True, COMPLIANCE_BLOCK_CLOUD_AI_WITH_IPI=False)
class AIProviderGuardrailTests(SimpleTestCase):
    def test_ollama_is_info_not_block(self):
        report = evaluate_ai_provider_use(provider='ollama', materials_may_contain_ipi=True)
        self.assertFalse(report.is_blocked)
        self.assertTrue(any(w.code == 'AI_LOCAL_PROVIDER_OK' for w in report.warnings))

    def test_openai_warns_when_ipi_possible(self):
        report = evaluate_ai_provider_use(provider='openai', materials_may_contain_ipi=True)
        self.assertTrue(any(w.code == 'AI_CLOUD_PROVIDER_IPI_RISK' for w in report.warnings))


@override_settings(COMPLIANCE_WARNINGS_ENABLED=True, COMPLIANCE_REQUIRE_HITL_FOR_EXPORT=True)
class ExportGuardrailTests(SimpleTestCase):
    def test_identifiable_export_warns_and_requires_hitl(self):
        report = evaluate_ferpa_export(
            export_type='course_credits_csv',
            includes_direct_identifiers=True,
            hitl_attested=False,
        )
        self.assertTrue(report.is_blocked)
        codes = {w.code for w in report.warnings}
        self.assertIn('EXPORT_CONTAINS_IPI', codes)
        self.assertIn('EXPORT_HITL_REQUIRED', codes)

    def test_hitl_attestation_clears_block(self):
        report = evaluate_ferpa_export(
            export_type='course_credits_csv',
            includes_direct_identifiers=True,
            hitl_attested=True,
        )
        self.assertFalse(report.is_blocked)


@override_settings(COMPLIANCE_REQUIRE_DECISION_RATIONALE=True)
class DecisionRationaleTests(SimpleTestCase):
    def test_short_notes_block(self):
        report = evaluate_decision_rationale('ok', decision='approved')
        self.assertTrue(report.is_blocked)

    def test_substantive_notes_allow(self):
        report = evaluate_decision_rationale(
            'Exempt Category D: anonymous educational survey; minimal risk; consent adequate.',
            decision='approved',
        )
        self.assertFalse(report.is_blocked)


class ExplainabilityTests(SimpleTestCase):
    def test_trace_includes_principles(self):
        report = evaluate_ferpa_export(
            export_type='course_credits_csv',
            includes_direct_identifiers=True,
            hitl_attested=True,
        )
        trace = build_decision_trace(report, outcome=outcome_from_report(report, proceeded=True))
        self.assertEqual(trace['outcome'], 'allow_with_warnings')
        self.assertIn('FERPA_EDUCATION_RECORDS', trace['principles_cited'])
        self.assertIn('explanation', trace)
