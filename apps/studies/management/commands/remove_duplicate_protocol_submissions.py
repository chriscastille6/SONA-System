"""
Remove duplicate draft protocol submissions when an approved submission exists for the same study.

Use when multiple protocol submissions exist for one study (e.g. a draft created alongside
an approved submission). Keeps the approved/submitted one and archives or deletes drafts.
"""
from django.core.management.base import BaseCommand

from apps.studies.models import ProtocolSubmission


class Command(BaseCommand):
    help = 'Remove duplicate draft protocol submissions (keep approved/submitted)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be removed without making changes',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete duplicates instead of archiving (default: archive)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete = options['delete']

        # Find studies with multiple protocol submissions
        from django.db.models import Count
        from django.db.models import Q

        dupes = (
            ProtocolSubmission.objects.values('study_id')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if not dupes:
            self.stdout.write(self.style.SUCCESS('No duplicate protocol submissions found.'))
            return

        removed = 0
        for row in dupes:
            study_id = row['study_id']
            subs = list(
                ProtocolSubmission.objects.filter(study_id=study_id)
                .select_related('study', 'submitted_by', 'college_rep')
            )
            # Keep: approved first, then submitted with number, then most recent by submitted_at
            keep = None
            for s in subs:
                if s.decision == 'approved' or (s.status == 'submitted' and s.submission_number):
                    keep = s
                    break
            if not keep:
                keep = subs[0]  # Keep first if none approved/submitted

            for s in subs:
                if s.id == keep.id:
                    continue
                # Remove draft or older duplicate
                study_title = s.study.title[:50] if s.study_id else '(no study)'
                pi = s.submitted_by.get_full_name() if s.submitted_by else '—'
                if dry_run:
                    self.stdout.write(
                        f'  Would remove: {s.id} — {study_title}... (PI: {pi}, status={s.status})'
                    )
                else:
                    if delete:
                        s.delete()
                        self.stdout.write(self.style.WARNING(f'  Deleted: {study_title}... (was draft)'))
                    else:
                        s.is_archived = True
                        s.save(update_fields=['is_archived'])
                        self.stdout.write(self.style.WARNING(f'  Archived: {study_title}... (was draft)'))
                removed += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n[DRY RUN] Would remove {removed} duplicate(s).'))
            self.stdout.write('Run without --dry-run to apply. Use --delete to delete instead of archive.')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nDone. {"Deleted" if delete else "Archived"} {removed} duplicate(s).'))
