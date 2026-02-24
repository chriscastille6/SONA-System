"""
Test IRB AI Review System

Creates a test review for any study in the database.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study, IRBReview
from apps.studies.tasks import run_irb_ai_review


class Command(BaseCommand):
    help = 'Create a test IRB review for any study (use --slug to pick one)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Study slug to use (default: most recently created study)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        slug = options.get('slug')
        if slug:
            try:
                study = Study.objects.get(slug=slug)
            except Study.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Study with slug "{slug}" not found.'))
                return
        else:
            study = Study.objects.order_by('-created_at').first()
            if not study:
                self.stdout.write(self.style.ERROR('No studies in database. Create a study first.'))
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
        self.stdout.write(self.style.WARNING('Note: Requires OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, or Ollama'))
        
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







