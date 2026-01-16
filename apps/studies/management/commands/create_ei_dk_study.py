"""
Management command to create the EI × Dunning-Kruger study.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study

User = get_user_model()


class Command(BaseCommand):
    help = 'Create EI × Dunning-Kruger study'

    def handle(self, *args, **options):
        # Get the current user (you) as researcher
        # This will use the first admin/researcher user found
        researcher = User.objects.filter(
            role__in=['researcher', 'admin', 'instructor']
        ).first()
        
        if not researcher:
            self.stdout.write(self.style.ERROR(
                'No researcher/admin user found. Please create a user account first.'
            ))
            return
        
        # Check if EI DK study already exists
        if Study.objects.filter(slug='ei-dk').exists():
            study = Study.objects.get(slug='ei-dk')
            self.stdout.write(self.style.WARNING(
                f'EI × Dunning-Kruger study already exists (ID: {study.id})'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Study URL: https://bayoupal.nicholls.edu/hsirb/studies/{study.slug}/run/'
            ))
            return
        
        # Create EI × Dunning-Kruger study
        study = Study.objects.create(
            title='EI × Dunning-Kruger Study',
            slug='ei-dk',
            description='''
This study examines the relationship between emotional intelligence (EI) and the Dunning-Kruger effect. 
Participants will complete self-assessments of their EI abilities and then take an actual EI test to 
compare their self-perceptions with their actual performance.

The study involves:
- Self-estimates of EI abilities
- Video-based EI assessment (36 items across 3 workplace scenarios)
- Immediate feedback on performance
- Questions about interest in EI training

Duration: Approximately 20-25 minutes
            '''.strip(),
            mode='online',
            researcher=researcher,
            credit_value=1.0,
            duration_minutes=25,
            is_active=True,
            is_approved=False,  # Will need IRB approval
            
            # IRB fields
            irb_status='pending',
            
            # Deception flag
            involves_deception=False,
            
            # OSF fields  
            osf_enabled=False,
            
            # Bayesian monitoring
            monitoring_enabled=True,
            min_sample_size=20,
            bf_threshold=10.0,
            analysis_plugin='apps.studies.analysis.placeholder:compute_bf',
            
            # Consent
            consent_text='''
I understand that this study examines emotional intelligence and self-assessment accuracy. 
I will be asked to estimate my EI abilities, complete an EI assessment, and receive feedback 
on my performance. My responses will be kept confidential and used only for research purposes.

I understand that:
- Participation is voluntary
- I can withdraw at any time
- My data will be anonymized
- The study takes approximately 20-25 minutes

By clicking "Yes, I consent to participate", I agree to participate in this study.
            '''.strip(),
            
            external_link='',
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Created study: {study.title} (slug: {study.slug})'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Study ID: {study.id}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Protocol URL: https://bayoupal.nicholls.edu/hsirb/studies/{study.slug}/run/'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Status URL: https://bayoupal.nicholls.edu/hsirb/studies/{study.slug}/status/'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   API Submit URL: https://bayoupal.nicholls.edu/hsirb/api/studies/{study.id}/submit/'
        ))
        self.stdout.write(self.style.WARNING(
            '\n⚠️  Next Steps:'
        ))
        self.stdout.write(
            '   1. Go to: https://bayoupal.nicholls.edu/hsirb/studies/researcher/'
        )
        self.stdout.write(
            '   2. Find your study and click "Submit Protocol"'
        )
        self.stdout.write(
            '   3. Fill out the IRB protocol submission form'
        )
