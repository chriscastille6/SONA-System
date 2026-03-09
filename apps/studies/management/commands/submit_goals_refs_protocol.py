"""
Submit the Goals as Reference Points (Decision Making Vignettes) draft protocol for IRB review.
Marks the draft as submitted, assigns college rep, routes, and notifies.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.studies.models import Study, ProtocolSubmission
from apps.studies.irb_utils import assign_college_rep, route_submission
from apps.studies.tasks import notify_college_rep_about_submission

User = get_user_model()


class Command(BaseCommand):
    help = "Submit the Goals as Reference Points draft protocol for IRB review"

    def handle(self, *args, **options):
        study = Study.objects.filter(slug='goals-refs').first()
        if not study:
            self.stdout.write(self.style.ERROR('Goals-refs study not found. Run add_goals_refs_study_online first.'))
            return

        draft = ProtocolSubmission.objects.filter(
            study=study,
            status='draft'
        ).order_by('-version').first()

        if not draft:
            self.stdout.write(self.style.ERROR('No draft protocol found for Goals as Reference Points. Run add_goals_refs_study_online first.'))
            return

        researcher = study.researcher
        if not researcher:
            researcher = User.objects.filter(email='christopher.castille@nicholls.edu').first()
        if not researcher:
            self.stdout.write(self.style.ERROR('No researcher found for submitted_by.'))
            return

        # Mark as submitted (triggers submission_number generation via save())
        draft.status = 'submitted'
        draft.submitted_by = researcher
        draft.review_type = draft.pi_suggested_review_type or 'exempt'
        draft.save()

        draft.refresh_from_db()

        # Update study deception flag
        study.involves_deception = draft.involves_deception
        study.save(update_fields=['involves_deception'])

        # Assign college rep and route
        assign_college_rep(draft)
        route_submission(draft)

        # Notify college rep
        try:
            result = notify_college_rep_about_submission(draft)
            if result and 'Failed' not in result:
                self.stdout.write(self.style.SUCCESS(f'  ✓ College rep notified: {result}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Email: {result}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  Email notification failed: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Protocol submitted successfully!'))
        self.stdout.write(f'  Submission #{draft.submission_number}')
        self.stdout.write(f'  Study: {study.title}')
        self.stdout.write(f'  College Rep: {draft.college_rep.get_full_name() if draft.college_rep else "Not assigned"}')
        self.stdout.write(f'  View: /studies/protocol/submissions/{draft.id}/')
