"""
Management command to reassign EI protocol to Business college rep (Jon Murphy).
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Reassign EI protocol submission to Business college rep (Jon Murphy)'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Reassigning EI Protocol to Business College Rep...\n')

        # Find EI study
        study = Study.objects.filter(slug='ei-rpm').first()
        if not study:
            self.stdout.write(self.style.ERROR('✗ EI study (ei-rpm) not found'))
            return

        self.stdout.write(f'✓ Found study: {study.title}')

        # Find Jon Murphy (Business college rep)
        jon_murphy = User.objects.filter(email='jonathan.murphy@nicholls.edu').first()
        if not jon_murphy:
            # Try alternative email
            jon_murphy = User.objects.filter(email__icontains='murphy', role='irb_member').first()
        
        if not jon_murphy:
            # Get from college rep
            biz_rep = CollegeRepresentative.objects.filter(college='business', active=True).first()
            if biz_rep and biz_rep.representative:
                jon_murphy = biz_rep.representative
        
        if not jon_murphy:
            self.stdout.write(self.style.ERROR('✗ Jon Murphy (Business college rep) not found'))
            return

        self.stdout.write(f'✓ Found Business college rep: {jon_murphy.get_full_name()} ({jon_murphy.email})')

        # Find all protocol submissions for EI study
        submissions = ProtocolSubmission.objects.filter(study=study).order_by('-version')
        
        if not submissions.exists():
            self.stdout.write(self.style.WARNING('⚠ No protocol submissions found for EI study'))
            return

        self.stdout.write(f'\nFound {submissions.count()} protocol submission(s):')
        
        for submission in submissions:
            old_rep = submission.college_rep
            self.stdout.write(f'\n  Submission: {submission.submission_number or f"Draft v{submission.version}"}')
            self.stdout.write(f'    Status: {submission.get_status_display()}')
            self.stdout.write(f'    Decision: {submission.get_decision_display()}')
            if old_rep:
                self.stdout.write(f'    Current college rep: {old_rep.get_full_name()} ({old_rep.email})')
            else:
                self.stdout.write(f'    Current college rep: None')
            
            # Reassign to Jon Murphy
            submission.college_rep = jon_murphy
            submission.save(update_fields=['college_rep'])
            
            self.stdout.write(self.style.SUCCESS(
                f'    ✓ Reassigned to: {jon_murphy.get_full_name()} (Business)'
            ))

        self.stdout.write(self.style.SUCCESS('\n✅ EI protocol(s) reassigned to Business college rep!'))
        self.stdout.write(f'\nJon Murphy can now review and approve the EI protocol.')
