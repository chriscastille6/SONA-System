"""
Assess protocol submissions and whether Jon Murphy and Juliann Allen can access each.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission


class Command(BaseCommand):
    help = 'Assess protocol submissions and access for Jon Murphy and Juliann Allen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Include archived and draft protocols (default: non-archived only)',
        )
        parser.add_argument(
            '--by-pi',
            type=str,
            metavar='EMAIL',
            help='Filter to protocols where study.researcher or submitted_by has this email',
        )

    def handle(self, *args, **options):
        jon = User.objects.filter(email='jonathan.murphy@nicholls.edu').first()
        juliann = User.objects.filter(email='juliann.allen@nicholls.edu').first()

        if not jon:
            self.stdout.write(self.style.ERROR('✗ Jon Murphy (jonathan.murphy@nicholls.edu) not found'))
        else:
            self.stdout.write(f'✓ Jon Murphy: {jon.get_full_name()} ({jon.email})')

        if not juliann:
            self.stdout.write(self.style.ERROR('✗ Juliann Allen (juliann.allen@nicholls.edu) not found'))
        else:
            self.stdout.write(f'✓ Juliann Allen: {juliann.get_full_name()} ({juliann.email})')

        if not jon or not juliann:
            return

        show_all = options.get('all', False)
        by_pi = options.get('by_pi', '').strip().lower()

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('PROTOCOL SUBMISSIONS – ACCESS ASSESSMENT')
        if show_all:
            self.stdout.write('(including archived and drafts)')
        if by_pi:
            self.stdout.write(f'(filtered by PI/submitted_by: {by_pi})')
        self.stdout.write('=' * 70)

        submissions = ProtocolSubmission.objects.all()
        if not show_all:
            submissions = submissions.filter(is_archived=False)
        if by_pi:
            submissions = submissions.filter(
                Q(study__researcher__email__iexact=by_pi) |
                Q(submitted_by__email__iexact=by_pi)
            )
        submissions = (
            submissions
            .select_related('study', 'study__researcher', 'college_rep', 'chair_reviewer', 'submitted_by')
            .prefetch_related('reviewers')
            .order_by('-submitted_at')
        )

        if not submissions.exists():
            scope = 'matching' if by_pi else 'non-archived'
            self.stdout.write(self.style.WARNING(f'\nNo {scope} protocol submissions found.'))
            return

        jon_count = 0
        juliann_count = 0

        for sub in submissions:
            # Safe study title (handle deleted study)
            try:
                study_title = sub.study.title if sub.study_id else '(no study)'
            except Exception:
                study_title = '(study deleted)'

            pi_name = '—'
            if sub.study_id:
                try:
                    r = sub.study.researcher
                    pi_name = r.get_full_name() if r else '—'
                except Exception:
                    pass

            status_label = sub.get_status_display()
            archived_label = ' [ARCHIVED]' if sub.is_archived else ''
            self.stdout.write(f'\n📋 {sub.submission_number or "Draft"}{archived_label}')
            self.stdout.write(f'   Status: {status_label}')
            self.stdout.write(f'   Study: {study_title}')
            self.stdout.write(f'   PI: {pi_name}')
            self.stdout.write(f'   Decision: {sub.get_decision_display()}')
            self.stdout.write(f'   Review type: {sub.get_review_type_display() or "—"}')

            # Assignments
            college_rep_name = sub.college_rep.get_full_name() if sub.college_rep else '—'
            chair_name = sub.chair_reviewer.get_full_name() if sub.chair_reviewer else '—'
            reviewer_names = [r.get_full_name() for r in sub.reviewers.all()]

            self.stdout.write(f'   College rep: {college_rep_name}')
            self.stdout.write(f'   Chair: {chair_name}')
            self.stdout.write(f'   Reviewers: {", ".join(reviewer_names) if reviewer_names else "—"}')

            # Jon Murphy access
            jon_can_access = sub.college_rep_id == jon.id
            if jon_can_access:
                jon_count += 1
                self.stdout.write(self.style.SUCCESS(f'   ✓ Jon Murphy: CAN ACCESS (college rep)'))
            else:
                reason = 'No college rep assigned' if not sub.college_rep else f'Assigned to {college_rep_name}'
                self.stdout.write(f'   ✗ Jon Murphy: No access ({reason})')

            # Juliann Allen access
            juliann_can_access = (
                sub.chair_reviewer_id == juliann.id or
                sub.reviewers.filter(id=juliann.id).exists()
            )
            if juliann_can_access:
                juliann_count += 1
                role = 'chair' if sub.chair_reviewer_id == juliann.id else 'reviewer'
                self.stdout.write(self.style.SUCCESS(f'   ✓ Juliann Allen: CAN ACCESS ({role})'))
            else:
                self.stdout.write(f'   ✗ Juliann Allen: No access')

        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 70)
        scope = 'all protocols' if show_all else 'non-archived protocols'
        if by_pi:
            scope = f"protocols for PI {by_pi}"
        self.stdout.write(f'Total {scope}: {submissions.count()}')
        self.stdout.write(f'Jon Murphy can access: {jon_count}')
        self.stdout.write(f'Juliann Allen can access: {juliann_count}')
        self.stdout.write('')
        self.stdout.write('Access rules:')
        self.stdout.write('  • Jon: protocols where he is college_rep')
        self.stdout.write('  • Juliann: protocols where she is chair_reviewer or in reviewers')
        self.stdout.write('  • To give Juliann access: assign her as reviewer on the protocol (college rep or chair uses "Assign Reviewers")')
