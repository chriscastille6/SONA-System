"""
Ensure the Goals as Reference Points (goals-refs) protocol can be seen by
Jon Murphy (college rep) and Juliann Allen (reviewer).
Run after add_goals_refs_study_online to assign college rep and add Juliann as reviewer.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative
from apps.studies.irb_utils import assign_college_rep


class Command(BaseCommand):
    help = 'Assign Jon Murphy (CBA rep) and Juliann Allen (reviewer) to goals-refs protocol so both can see it'

    def handle(self, *args, **options):
        self.stdout.write('Assigning reviewers for Goals as Reference Points protocol...\n')

        study = Study.objects.filter(slug='goals-refs').first()
        if not study:
            self.stdout.write(self.style.ERROR('Goals-refs study not found. Run add_goals_refs_study_online first.'))
            return

        # Jon Murphy: from Business college rep
        jon = None
        biz = CollegeRepresentative.objects.filter(college='business', active=True).first()
        if biz and biz.representative_id:
            jon = biz.representative
        if not jon:
            jon = User.objects.filter(email__iexact='jonathan.murphy@nicholls.edu', role='irb_member').first()
        if not jon:
            self.stdout.write(self.style.WARNING('Jon Murphy (Business rep) not found. Run setup_college_reps / create his account.'))

        # Juliann Allen
        juliann = User.objects.filter(email__iexact='juliann.allen@nicholls.edu').first()
        if not juliann:
            juliann = User.objects.filter(
                first_name__icontains='juliann',
                last_name__icontains='allen',
                role='irb_member',
            ).first()
        if not juliann:
            self.stdout.write(self.style.WARNING('Juliann Allen not found. Run add_juliann_allen_irb if needed.'))

        submissions = ProtocolSubmission.objects.filter(study=study).order_by('-version')
        if not submissions.exists():
            self.stdout.write(self.style.WARNING('No protocol submissions for goals-refs. Run add_goals_refs_study_online first.'))
            return

        for sub in submissions:
            self.stdout.write(f'  Submission: {sub.submission_number or f"Draft v{sub.version}"} (status={sub.status})')
            if jon:
                if sub.college_rep_id != jon.id:
                    sub.college_rep = jon
                    sub.save(update_fields=['college_rep'])
                    self.stdout.write(self.style.SUCCESS(f'    Assigned college rep: {jon.get_full_name()}'))
                else:
                    self.stdout.write(f'    College rep already: {jon.get_full_name()}')
            if juliann:
                if not sub.reviewers.filter(id=juliann.id).exists():
                    sub.reviewers.add(juliann)
                    self.stdout.write(self.style.SUCCESS(f'    Added reviewer: {juliann.get_full_name()}'))
                else:
                    self.stdout.write(f'    Reviewer already: {juliann.get_full_name()}')

        self.stdout.write(self.style.SUCCESS('\nDone. Jon Murphy and Juliann Allen can view the protocol from their dashboards.'))
