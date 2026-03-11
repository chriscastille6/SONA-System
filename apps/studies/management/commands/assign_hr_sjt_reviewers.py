"""
Ensure the HR Situational Judgment Test (hr-sjt) protocol can be seen by
Jon Murphy (college rep) and Juliann Allen (reviewer).
Run after add_hr_sjt_study_online so both can access the protocol and documentation.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative
from apps.studies.irb_utils import assign_college_rep


class Command(BaseCommand):
    help = 'Assign Jon Murphy (CBA rep) and Juliann Allen (reviewer) to hr-sjt protocol'

    def handle(self, *args, **options):
        self.stdout.write('Assigning reviewers for HR Situational Judgment Test protocol...\n')

        study = Study.objects.filter(slug='hr-sjt').first()
        if not study:
            self.stdout.write(self.style.ERROR('hr-sjt study not found. Run add_hr_sjt_study_online first.'))
            return

        jon = None
        biz = CollegeRepresentative.objects.filter(college='business', active=True).first()
        if biz and biz.representative_id:
            jon = biz.representative
        if not jon:
            jon = User.objects.filter(email__iexact='jonathan.murphy@nicholls.edu', role='irb_member').first()

        juliann = User.objects.filter(email__iexact='juliann.allen@nicholls.edu').first()
        if not juliann:
            juliann = User.objects.filter(
                first_name__icontains='juliann',
                last_name__icontains='allen',
                role='irb_member',
            ).first()

        submissions = ProtocolSubmission.objects.filter(study=study).order_by('-version')
        if not submissions.exists():
            self.stdout.write(self.style.WARNING('No protocol submissions for hr-sjt. Run add_hr_sjt_study_online first.'))
            return

        for sub in submissions:
            self.stdout.write(f'  Submission: {sub.submission_number or f"Draft v{sub.version}"} (status={sub.status})')
            assign_college_rep(sub)
            if jon and sub.college_rep_id != jon.id:
                sub.college_rep = jon
                sub.save(update_fields=['college_rep'])
                self.stdout.write(self.style.SUCCESS(f'    Assigned college rep: {jon.get_full_name()}'))
            elif jon:
                self.stdout.write(f'    College rep: {jon.get_full_name()}')
            if juliann:
                if not sub.reviewers.filter(id=juliann.id).exists():
                    sub.reviewers.add(juliann)
                    self.stdout.write(self.style.SUCCESS(f'    Added reviewer: {juliann.get_full_name()}'))
                else:
                    self.stdout.write(f'    Reviewer: {juliann.get_full_name()}')

        self.stdout.write(self.style.SUCCESS('\nDone. Juliann Allen and Jon Murphy can view the protocol and documentation.'))
