"""
Assign college reps to protocol submissions that don't have one.
Useful for protocols created via add_*_study_online (e.g. whole-person-fit, hr-sjt)
that were loaded from JSON before assign_college_rep was called.
"""
from django.core.management.base import BaseCommand
from apps.studies.models import ProtocolSubmission
from apps.studies.irb_utils import assign_college_rep


class Command(BaseCommand):
    help = 'Assign college reps to protocol submissions that have none'

    def handle(self, *args, **options):
        unassigned = ProtocolSubmission.objects.filter(college_rep__isnull=True)
        count = unassigned.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All protocol submissions already have a college rep.'))
            return

        self.stdout.write(f'Found {count} protocol(s) without college rep. Assigning...\n')
        assigned = 0
        for sub in unassigned.select_related('study', 'study__researcher', 'submitted_by'):
            try:
                study_title = sub.study.title if sub.study_id else '(no study)'
            except Exception:
                study_title = '(study deleted)'
            result = assign_college_rep(sub)
            if result:
                assigned += 1
                rep_name = result.representative.get_full_name()
                self.stdout.write(self.style.SUCCESS(f'  ✓ {sub.submission_number or "Draft"}: {study_title} → {rep_name}'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ✗ {sub.submission_number or "Draft"}: {study_title} (could not assign: need researcher profile with department, or pi_department on protocol)'
                ))

        self.stdout.write(f'\nAssigned {assigned} of {count}.')
