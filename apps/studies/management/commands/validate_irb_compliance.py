"""
Synthetic data validation for IRB/FERPA compliance measures.

Creates test data, exercises compliance features, verifies behavior, then rolls back.
Run: python manage.py validate_irb_compliance
On PostgreSQL: also validates audit triggers and RLS.
"""
import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.studies.models import Study
from apps.credits.models import CreditTransaction


class Command(BaseCommand):
    help = "Validate IRB/FERPA compliance with synthetic data (rolls back)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--persist',
            action='store_true',
            help='Keep test data (default: roll back)',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("IRB/FERPA Compliance Synthetic Validation")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        results = []
        use_transaction = not options['persist']

        if use_transaction:
            with transaction.atomic():
                sid = transaction.savepoint()
                try:
                    self._run_checks(results)
                finally:
                    transaction.savepoint_rollback(sid)
        else:
            self._run_checks(results)

        self._print_results(results)

    def _run_checks(self, results):
        """Run all validation checks."""
        # 1. active_approved excludes expired studies
        self._check_active_approved(results)

        # 2. irb_audit_logs trigger (PostgreSQL only)
        self._check_audit_triggers(results)

        # 3. RLS policies (PostgreSQL only)
        self._check_rls(results)

    def _check_active_approved(self, results):
        """Verify active_approved excludes expired/pending studies."""
        self.stdout.write("1. Active Approved Filter (Prompt 3)...")

        researcher = User.objects.filter(role='researcher').first()
        if not researcher:
            results.append(("active_approved", False, "No researcher user found"))
            return

        today = timezone.now().date()
        past = today - timedelta(days=30)
        future = today + timedelta(days=90)

        suffix = str(uuid.uuid4())[:8]
        # Create test studies
        expired_study = Study.objects.create(
            title="[VALIDATION] Expired Study",
            slug="validation-expired-" + suffix,
            description="Should NOT appear in active_approved",
            mode="online",
            researcher=researcher,
            is_active=True,
            is_approved=True,
            is_classroom_based=False,
            irb_status="expired",
            irb_expiration=past,
            consent_text="Test consent",
        )
        approved_study = Study.objects.create(
            title="[VALIDATION] Approved Study",
            slug="validation-approved-" + suffix,
            description="Should appear in active_approved",
            mode="online",
            researcher=researcher,
            is_active=True,
            is_approved=True,
            is_classroom_based=False,
            irb_status="approved",
            irb_expiration=future,
            consent_text="Test consent",
        )
        pending_study = Study.objects.create(
            title="[VALIDATION] Pending Study",
            slug="validation-pending-" + suffix,
            description="Should NOT appear in active_approved",
            mode="online",
            researcher=researcher,
            is_active=True,
            is_approved=True,
            is_classroom_based=False,
            irb_status="pending",
            irb_expiration=future,
            consent_text="Test consent",
        )

        active_ids = set(Study.active_approved.values_list('id', flat=True))

        expired_excluded = expired_study.id not in active_ids
        approved_included = approved_study.id in active_ids
        pending_excluded = pending_study.id not in active_ids

        ok = expired_excluded and approved_included and pending_excluded
        msg = (
            f"expired excluded={expired_excluded}, approved included={approved_included}, "
            f"pending excluded={pending_excluded}"
        )
        results.append(("active_approved filter", ok, msg))
        self.stdout.write(f"   {msg} -> {'PASS' if ok else 'FAIL'}")

    def _check_audit_triggers(self, results):
        """Verify irb_audit_logs receives INSERT/UPDATE/DELETE (PostgreSQL)."""
        self.stdout.write("2. Audit Log Triggers (Prompt 1)...")

        if connection.vendor != 'postgresql':
            results.append(("irb_audit_logs triggers", None, "SKIP (not PostgreSQL)"))
            self.stdout.write("   SKIP (not PostgreSQL)")
            return

        researcher = User.objects.filter(role='researcher').first()
        participant = User.objects.filter(role='participant').first()
        if not researcher or not participant:
            results.append(("irb_audit_logs triggers", False, "Missing researcher/participant"))
            return

        with connection.cursor() as c:
            c.execute("SELECT COUNT(*) FROM irb_audit_logs")
            count_before = c.fetchone()[0]

        # Trigger: create study
        study = Study.objects.create(
            title="[VALIDATION] Audit Test Study",
            slug="validation-audit-" + str(timezone.now().timestamp()),
            description="Audit trigger test",
            mode="online",
            researcher=researcher,
            consent_text="Test",
        )
        study.title = "[VALIDATION] Audit Test Study Updated"
        study.save()
        study.delete()

        # Trigger: create credit transaction
        CreditTransaction.objects.create(
            participant=participant,
            amount=Decimal("1.00"),
            reason="[VALIDATION] Audit test",
            created_by=researcher,
        )

        with connection.cursor() as c:
            c.execute("SELECT COUNT(*) FROM irb_audit_logs")
            count_after = c.fetchone()[0]
            c.execute(
                "SELECT table_name, action_type FROM irb_audit_logs "
                "ORDER BY changed_at DESC LIMIT 5"
            )
            recent = c.fetchall()

        # Expect: 3 study ops (insert, update, delete) + 1 credit insert = 4 new rows
        new_rows = count_after - count_before
        has_studies = any(r[0] == 'studies' for r in recent)
        has_credits = any(r[0] == 'credit_transactions' for r in recent)

        ok = new_rows >= 4 and has_studies and has_credits
        msg = f"new_rows={new_rows}, studies={has_studies}, credits={has_credits}"
        results.append(("irb_audit_logs triggers", ok, msg))
        self.stdout.write(f"   {msg} -> {'PASS' if ok else 'FAIL'}")

    def _check_rls(self, results):
        """Verify RLS is enabled (PostgreSQL)."""
        self.stdout.write("3. Row-Level Security (Prompt 2)...")

        if connection.vendor != 'postgresql':
            results.append(("RLS policies", None, "SKIP (not PostgreSQL)"))
            self.stdout.write("   SKIP (not PostgreSQL)")
            return

        with connection.cursor() as c:
            c.execute(
                "SELECT relname, relrowsecurity FROM pg_class "
                "WHERE relname IN ('studies', 'signups') AND relkind = 'r'"
            )
            rows = dict(c.fetchall())

        studies_rls = rows.get('studies', False)
        signups_rls = rows.get('signups', False)
        ok = studies_rls and signups_rls
        msg = f"studies={studies_rls}, signups={signups_rls}"
        results.append(("RLS policies", ok, msg))
        self.stdout.write(f"   {msg} -> {'PASS' if ok else 'FAIL'}")

    def _print_results(self, results):
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("Summary")
        self.stdout.write("=" * 60)
        passed = sum(1 for _, ok, _ in results if ok is True)
        failed = sum(1 for _, ok, _ in results if ok is False)
        skipped = sum(1 for _, ok, _ in results if ok is None)
        for name, ok, msg in results:
            status = "PASS" if ok is True else ("FAIL" if ok is False else "SKIP")
            self.stdout.write(f"  {name}: {status}")
        self.stdout.write("")
        self.stdout.write(f"  Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        if failed > 0:
            self.stdout.write(self.style.ERROR("\n  Some checks FAILED."))
        else:
            self.stdout.write(self.style.SUCCESS("\n  All applicable checks PASSED."))
