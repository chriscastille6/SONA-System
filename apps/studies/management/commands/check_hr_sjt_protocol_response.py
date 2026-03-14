"""
Check whether the HR-SJT protocol submission has stored reviewer/college rep responses.
Useful to verify if Juliann Allen's (or any reviewer's) response was saved online.

Run: python manage.py check_hr_sjt_protocol_response
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.studies.models import Study, ProtocolSubmission


class Command(BaseCommand):
    help = 'Show HR-SJT protocol submission(s) and whether reviewer/college rep responses are stored'

    def handle(self, *args, **options):
        study = Study.objects.filter(slug='hr-sjt').first()
        if not study:
            self.stdout.write(self.style.ERROR('Study hr-sjt not found.'))
            return

        submissions = ProtocolSubmission.objects.filter(study=study).select_related(
            'college_rep', 'chair_reviewer', 'decided_by', 'submitted_by'
        ).prefetch_related('reviewers').order_by('-version')

        if not submissions.exists():
            self.stdout.write(self.style.WARNING('No protocol submissions for hr-sjt.'))
            return

        self.stdout.write(f'HR-SJT protocol submission(s) for study: {study.title}\n')
        for sub in submissions:
            self.stdout.write('-' * 60)
            self.stdout.write(f'Submission: {sub.display_submission_number} (v{sub.version})')
            self.stdout.write(f'  Status: {sub.status}  |  Decision: {sub.decision}')
            self.stdout.write(f'  Submitted: {sub.submitted_at or "—"} by {sub.submitted_by or "—"}')

            # College rep and determination
            rep = sub.college_rep
            self.stdout.write(f'\n  College rep: {rep.get_full_name() if rep else "—"} ({getattr(rep, "email", "") or ""})')
            self.stdout.write(f'  College rep determination: {sub.college_rep_determination or "—"}')
            self.stdout.write(f'  Reviewed at: {sub.reviewed_at or "—"}')

            # Reviewers
            revs = list(sub.reviewers.all())
            if revs:
                self.stdout.write(f'  Reviewers: {", ".join(r.get_full_name() for r in revs)}')
            else:
                self.stdout.write('  Reviewers: —')

            # Decision (this is where reviewer/college rep "options and text box" are stored)
            self.stdout.write(f'\n  Decided by: {sub.decided_by.get_full_name() if sub.decided_by else "—"} ({getattr(sub.decided_by, "email", "") or ""})')
            self.stdout.write(f'  Decided at: {sub.decided_at or "—"}')
            if sub.approval_notes:
                self.stdout.write(f'  Approval notes: {sub.approval_notes[:200]}{"..." if len(sub.approval_notes) > 200 else ""}')
            if sub.rnr_notes:
                self.stdout.write(f'  Revise & resubmit notes: {sub.rnr_notes[:200]}{"..." if len(sub.rnr_notes) > 200 else ""}')
            if sub.rejection_grounds:
                self.stdout.write(f'  Rejection grounds: {sub.rejection_grounds[:200]}{"..." if len(sub.rejection_grounds) > 200 else ""}')

            # Check for Juliann
            juliann_emails = ('juliann.allen@nicholls.edu',)
            is_rep = rep and getattr(rep, 'email', '').lower() in juliann_emails
            is_reviewer = any(getattr(r, 'email', '').lower() in juliann_emails for r in revs)
            is_decider = sub.decided_by and getattr(sub.decided_by, 'email', '').lower() in juliann_emails
            if is_rep or is_reviewer or is_decider:
                self.stdout.write(self.style.SUCCESS('\n  >>> Juliann Allen is assigned (college rep / reviewer / decider).'))
            if sub.decision != 'pending' and (sub.decided_at or sub.approval_notes or sub.rnr_notes or sub.rejection_grounds):
                self.stdout.write(self.style.SUCCESS('  >>> A response (decision + notes) is stored for this submission.'))
            elif sub.college_rep_determination and sub.reviewed_at:
                self.stdout.write(self.style.SUCCESS('  >>> College rep determination and reviewed_at are stored (options saved).'))
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('Done. If "Decided by" or "Approval/RNR/Rejection notes" show data, the response was stored.'))

