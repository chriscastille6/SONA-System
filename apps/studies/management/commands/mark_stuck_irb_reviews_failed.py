"""
Mark stuck IRB reviews (pending or in_progress for too long) as failed.

Use after restarting the Celery worker or when reviews never completed
so the UI shows "Failed" instead of "Pending" / "Queued".
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.studies.models import IRBReview


class Command(BaseCommand):
    help = 'Mark IRB reviews stuck in pending/in_progress (older than threshold) as failed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=float,
            default=1.0,
            help='Consider reviews stuck if initiated more than this many hours ago (default: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only print what would be updated; do not save',
        )
        parser.add_argument(
            '--study-id',
            type=str,
            default=None,
            help='Limit to reviews for this study (UUID)',
        )
        parser.add_argument(
            '--review-id',
            type=str,
            default=None,
            help='Limit to this single review (UUID)',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        study_id = options['study_id']
        review_id = options['review_id']

        cutoff = timezone.now() - timedelta(hours=hours)
        qs = IRBReview.objects.filter(
            status__in=['pending', 'in_progress'],
            initiated_at__lt=cutoff,
        )
        if study_id:
            qs = qs.filter(study_id=study_id)
        if review_id:
            qs = qs.filter(id=review_id)

        reviews = list(qs.select_related('study').order_by('study__slug', 'version'))
        if not reviews:
            self.stdout.write(
                self.style.SUCCESS(f'No stuck reviews found (status pending/in_progress, initiated before {cutoff.isoformat()}).')
            )
            return

        self.stdout.write(f'Found {len(reviews)} stuck review(s) to mark as failed.')
        for r in reviews:
            self.stdout.write(f'  v{r.version}  {r.study.title}  id={r.id}  initiated_at={r.initiated_at}')

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run: no changes saved.'))
            return

        updated = 0
        for r in reviews:
            r.status = 'failed'
            r.completed_at = timezone.now()
            r.save(update_fields=['status', 'completed_at'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Marked {updated} review(s) as failed.'))
