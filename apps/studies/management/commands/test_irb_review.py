"""
Test IRB AI Review System

Creates a test review for the EI × DK study.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study, IRBReview
from apps.studies.tasks import run_irb_ai_review


class Command(BaseCommand):
    help = 'Create a test IRB review for the EI × DK study'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get the EI × DK study
        try:
            study = Study.objects.get(slug='ei-dk')
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR('EI × DK study not found. Create it first.'))
            return
        
        # Get researcher
        researcher = study.researcher
        if not researcher:
            researcher = User.objects.filter(email='researcher@example.com').first()
            if not researcher:
                self.stdout.write(self.style.ERROR('Researcher not found'))
                return
        
        # Create review
        review = IRBReview.objects.create(
            study=study,
            initiated_by=researcher,
            osf_repo_url='',  # Can add OSF URL if desired
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created IRB Review v{review.version}'))
        self.stdout.write(f'  Study: {study.title}')
        self.stdout.write(f'  Review ID: {review.id}')
        self.stdout.write(f'  Status: {review.status}')
        
        # Trigger review (synchronously for testing)
        self.stdout.write('\nTriggering AI review...')
        self.stdout.write(self.style.WARNING('Note: This requires ANTHROPIC_API_KEY to be configured'))
        
        # Run the task
        result = run_irb_ai_review(str(review.id))
        
        # Reload review to see results
        review.refresh_from_db()
        
        self.stdout.write(self.style.SUCCESS('\nReview Complete!'))
        self.stdout.write(f'  Status: {review.status}')
        self.stdout.write(f'  Risk Level: {review.overall_risk_level}')
        self.stdout.write(f'  Critical Issues: {len(review.critical_issues)}')
        self.stdout.write(f'  Moderate Issues: {len(review.moderate_issues)}')
        self.stdout.write(f'  Minor Issues: {len(review.minor_issues)}')
        
        if result.get('success'):
            self.stdout.write(f'\nView report at: http://localhost:8002/studies/{study.id}/irb-review/{review.version}/')
        else:
            self.stdout.write(self.style.ERROR(f'\nError: {result.get("error")}'))







