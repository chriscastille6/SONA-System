"""
Management command to create the EI × RPM (Fluid Intelligence) study.
Tests whether there is a fluid emotional intelligence separate and distinct from crystallized IQ.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study

User = get_user_model()


class Command(BaseCommand):
    help = 'Create EI × RPM (Fluid Intelligence) study'

    def handle(self, *args, **options):
        # Get the current user (you) as researcher
        researcher = User.objects.filter(
            role__in=['researcher', 'admin', 'instructor']
        ).first()
        
        if not researcher:
            self.stdout.write(self.style.ERROR(
                'No researcher/admin user found. Please create a user account first.'
            ))
            return
        
        # Check if EI RPM study already exists
        if Study.objects.filter(slug='ei-rpm').exists():
            study = Study.objects.get(slug='ei-rpm')
            self.stdout.write(self.style.WARNING(
                f'EI × RPM study already exists (ID: {study.id})'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Study URL: https://bayoupal.nicholls.edu/hsirb/studies/{study.slug}/run/'
            ))
            return
        
        # Create EI × RPM (Fluid Intelligence) study
        study = Study.objects.create(
            title='Emotional Intelligence and Fluid Intelligence Study',
            slug='ei-rpm',
            description='''
This study examines the relationship between emotional intelligence (EI) and fluid intelligence 
as measured by Raven's Progressive Matrices (RPM). We are testing whether there is a fluid 
emotional intelligence that is separate and distinct from crystallized IQ.

The study involves:
- Self-estimates of EI abilities (pre-test assessments)
- Emotional Intelligence assessment (video-based scenarios)
- Raven's Progressive Matrices (fluid intelligence test)
- Comparison of self-perceptions with actual performance
- Demographic and background questions

This research aims to understand:
1. Whether emotional intelligence represents a distinct form of fluid intelligence separate from crystallized IQ
2. The relationship between self-assessed EI abilities and actual EI performance
3. How fluid intelligence (RPM) relates to emotional intelligence abilities

Duration: Approximately 30-40 minutes
            '''.strip(),
            mode='online',
            researcher=researcher,
            credit_value=1.0,
            duration_minutes=35,
            is_active=True,
            is_approved=False,  # Will need IRB approval
            
            # IRB fields
            irb_status='pending',
            
            # Deception flag (may involve some deception about study purpose)
            involves_deception=False,
            
            # OSF fields  
            osf_enabled=False,
            
            # Bayesian monitoring
            monitoring_enabled=True,
            min_sample_size=30,
            bf_threshold=10.0,
            analysis_plugin='apps.studies.analysis.placeholder:compute_bf',
            
            # Consent
            consent_text='''
I understand that this study examines emotional intelligence and cognitive abilities. 
I will be asked to:
- Estimate my emotional intelligence abilities before testing
- Complete an emotional intelligence assessment (video-based scenarios)
- Complete a fluid intelligence test (Raven's Progressive Matrices)
- Receive feedback comparing my self-estimates with my actual performance
- Provide demographic and background information

My responses will be kept confidential and used only for research purposes.

I understand that:
- Participation is voluntary
- I can withdraw at any time without penalty
- My data will be anonymized and kept confidential
- The study takes approximately 30-40 minutes
- I will receive course credit for participation

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
