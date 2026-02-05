"""
Quick command to update the co_investigators field for the TRO study protocol submission.
"""
from django.core.management.base import BaseCommand
from apps.studies.models import Study, ProtocolSubmission
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Update co_investigators field for TRO study protocol submission'

    def handle(self, *args, **options):
        # Get the study
        study = Study.objects.filter(slug='conjoint-analysis').first()
        if not study:
            self.stdout.write(self.style.ERROR('TRO study not found'))
            return
        
        # Get the protocol submission
        submission = ProtocolSubmission.objects.filter(
            study=study,
            protocol_number='IRBE20251031-005CBA'
        ).first()
        
        if not submission:
            self.stdout.write(self.style.ERROR('Protocol submission not found'))
            return
        
        # Get Christopher Castille
        co_i = User.objects.filter(email='christopher.castille@nicholls.edu').first()
        if not co_i:
            self.stdout.write(self.style.ERROR('Christopher Castille not found'))
            return
        
        # Update co_investigators field
        submission.co_investigators = f'Dr. Christopher Castille, {co_i.email}'
        submission.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Updated co_investigators field: {submission.co_investigators}'
        ))
        
        # Verify the query works
        co_i_studies = Study.objects.filter(
            protocol_submissions__co_investigators__icontains=co_i.email
        ).distinct()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Studies where Christopher Castille is Co-I: {co_i_studies.count()}'
        ))
        for s in co_i_studies:
            self.stdout.write(f'  - {s.title}')
