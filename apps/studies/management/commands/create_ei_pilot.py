"""
Management command to create the EI Pilot study.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study

User = get_user_model()


class Command(BaseCommand):
    help = 'Create EI Pilot study for demonstration'

    def handle(self, *args, **options):
        # Get or create a researcher user
        researcher = User.objects.filter(role='researcher').first()
        
        if not researcher:
            self.stdout.write(self.style.WARNING(
                'No researcher users found. Creating a demo researcher...'
            ))
            researcher = User.objects.create_user(
                email='researcher@example.com',
                password='demo123',
                first_name='Demo',
                last_name='Researcher',
                role='researcher'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Created researcher: {researcher.email}'
            ))
        
        # Check if EI Pilot already exists
        if Study.objects.filter(slug='ei-pilot').exists():
            self.stdout.write(self.style.WARNING(
                'EI Pilot study already exists'
            ))
            return
        
        # Create EI Pilot study
        study = Study.objects.create(
            title='EI Pilot - Emotional Intelligence Measurement Protocol',
            slug='ei-pilot',
            description='''
This is a pilot test of an emotional intelligence measurement protocol.
This study is NOT approved by the IRB as it is for pilot testing purposes only.
Data collected will not be used for research purposes.

The study involves completing a series of emotional intelligence assessments
and questionnaires. Your responses will help us refine the measurement protocol
before seeking IRB approval for a full research study.
            '''.strip(),
            mode='online',
            researcher=researcher,
            credit_value=1.0,
            duration_minutes=30,
            is_active=True,
            is_approved=True,
            
            # IRB fields
            irb_status='not_required',
            
            # OSF fields  
            osf_enabled=False,
            
            # Bayesian monitoring
            monitoring_enabled=True,
            min_sample_size=20,
            bf_threshold=10.0,
            analysis_plugin='apps.studies.analysis.placeholder:compute_bf',
            
            # Consent
            consent_text='''
I understand that this is a pilot test and my data will not be used for research purposes.
I consent to participate in this protocol development study.
            '''.strip(),
            
            external_link='',
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'Created study: {study.title} (slug: {study.slug})'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Protocol URL: /studies/{study.slug}/run/'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Status URL: /studies/{study.slug}/status/'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'API Submit URL: /api/studies/{study.id}/submit/'
        ))


