"""
Mark draft protocol submissions as submitted and generate submission numbers.

Use when protocols were created/assigned via management commands or admin
but never went through the normal submit flow (so they have no submission_number).
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.studies.models import ProtocolSubmission


class Command(BaseCommand):
    help = 'Mark draft protocol submissions as submitted and generate submission numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Backfill all drafts (default: only those with college_rep assigned)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        all_drafts = options['all']

        qs = ProtocolSubmission.objects.filter(status='draft')
        if not all_drafts:
            qs = qs.exclude(college_rep__isnull=True)

        drafts = list(qs.select_related('study', 'college_rep').order_by('study__title'))
        if not drafts:
            self.stdout.write(self.style.WARNING('No draft protocol submissions found.'))
            if not all_drafts:
                self.stdout.write('  (Use --all to include drafts without a college rep assigned)')
            return

        self.stdout.write(f'Found {len(drafts)} draft(s) to backfill:\n')
        for sub in drafts:
            study_title = sub.study.title if sub.study_id else '(no study)'
            rep = sub.college_rep.get_full_name() if sub.college_rep else 'Not assigned'
            self.stdout.write(f'  • {study_title[:50]}... (rep: {rep})')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] Would mark these as submitted. Run without --dry-run to apply.'))
            return

        self.stdout.write('')
        for sub in drafts:
            sub.status = 'submitted'
            if not sub.submitted_by and sub.study_id and sub.study.researcher_id:
                sub.submitted_by = sub.study.researcher
            sub.save()
            sub.refresh_from_db()
            study_title = sub.study.title if sub.study_id else '(no study)'
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ {sub.submission_number}: {study_title[:45]}...'
            ))

        self.stdout.write(self.style.SUCCESS(f'\nDone. {len(drafts)} protocol(s) marked as submitted.'))
