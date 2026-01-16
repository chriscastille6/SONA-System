"""
Management command to update the EI × RPM study with DK content.
"""
from django.core.management.base import BaseCommand
from apps.studies.models import Study


class Command(BaseCommand):
    help = 'Update EI × RPM study with Dunning-Kruger content'

    def handle(self, *args, **options):
        try:
            study = Study.objects.get(slug='ei-rpm')
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'EI × RPM study (ei-rpm) does not exist. Create it first.'
            ))
            return
        
        # Update description with DK content
        study.description = '''This study examines the relationship between emotional intelligence (EI) and fluid intelligence as measured by Raven's Progressive Matrices (RPM). We are testing whether there is a fluid emotional intelligence that is separate and distinct from crystallized IQ.

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

Duration: Approximately 30-40 minutes'''
        
        # Update consent text with DK content
        study.consent_text = '''I understand that this study examines emotional intelligence and cognitive abilities. I will be asked to:
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

By clicking "Yes, I consent to participate", I agree to participate in this study.'''
        
        study.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Updated study: {study.title} (slug: {study.slug})'
        ))
        self.stdout.write(self.style.SUCCESS(
            '   Description and consent text updated with Dunning-Kruger content.'
        ))
