"""
Set the college representative on protocol submission(s) so they can make IRB decisions.

For **exempt** protocols, only `college_rep` may approve / revise-resubmit / reject
(see protocol_make_decision). Assigned reviewers alone cannot decide on exempt submissions.

Typical use: make Juliann Allen the decision-maker for HR-SJT after Jon was college rep.

  python manage.py set_protocol_college_rep --slug hr-sjt --email juliann.allen@nicholls.edu

Optional: target one submission by UUID:

  python manage.py set_protocol_college_rep --submission-id <uuid> --email juliann.allen@nicholls.edu
"""
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission, Study


class Command(BaseCommand):
    help = 'Set college_rep on protocol submission(s) so that user can make IRB decisions (required for exempt).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            default='hr-sjt',
            help='Study slug (default: hr-sjt). Ignored if --submission-id is set.',
        )
        parser.add_argument(
            '--email',
            default='juliann.allen@nicholls.edu',
            help='User email to set as college_rep (default: juliann.allen@nicholls.edu).',
        )
        parser.add_argument(
            '--submission-id',
            default=None,
            help='Single ProtocolSubmission UUID to update.',
        )
        parser.add_argument(
            '--include-decided',
            action='store_true',
            help='Also update submissions that already have a decision (default: pending only).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would change without saving.',
        )

    def handle(self, *args, **options):
        email = (options['email'] or '').strip().lower()
        slug = (options['slug'] or '').strip()
        submission_id = options.get('submission_id')
        include_decided = options['include_decided']
        dry_run = options['dry_run']

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stdout.write(
                self.style.ERROR(f'No user found with email {email!r}. Run add_juliann_allen_irb if needed.')
            )
            return

        if submission_id:
            qs = ProtocolSubmission.objects.filter(id=submission_id)
            if not qs.exists():
                self.stdout.write(self.style.ERROR(f'No submission with id {submission_id!r}.'))
                return
        else:
            study = Study.objects.filter(slug=slug).first()
            if not study:
                self.stdout.write(self.style.ERROR(f'No study with slug {slug!r}.'))
                return
            qs = ProtocolSubmission.objects.filter(study=study)
            if not include_decided:
                qs = qs.filter(decision='pending')

        count = qs.count()
        if count == 0:
            self.stdout.write(
                self.style.WARNING('No matching submissions. Try --include-decided or check slug/submission-id.')
            )
            return

        self.stdout.write(
            f'{"Would set" if dry_run else "Setting"} college_rep to {user.get_full_name()} <{user.email}> '
            f'on {count} submission(s).\n'
        )

        for sub in qs.select_related('study'):
            old = sub.college_rep
            old_label = f'{old.get_full_name()} <{old.email}>' if old else '(none)'
            self.stdout.write(
                f'  {sub.id} | {sub.study.slug} | v{sub.version} | decision={sub.decision} | '
                f'review_type={sub.review_type} | college_rep: {old_label} -> {user.email}'
            )
            if not dry_run:
                sub.college_rep = user
                sub.save(update_fields=['college_rep'])

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run — no changes saved.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nDone. That user can now submit decisions on exempt protocols.'))
