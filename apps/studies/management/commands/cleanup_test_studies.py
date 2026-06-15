from django.core.management.base import BaseCommand
from apps.studies.models import Study, ProtocolSubmission

class Command(BaseCommand):
    help = 'Clean up and delete distracting/test studies from the database by title or slug'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Auditing studies for test/distracting entries...")

        # Find studies with "asdf" or other test indicators in the title or slug
        test_queries = [
            Study.objects.filter(title__icontains="asdf"),
            Study.objects.filter(slug__icontains="asdf"),
            Study.objects.filter(description__icontains="asdf"),
        ]

        deleted_count = 0
        seen_ids = set()

        for queryset in test_queries:
            for study in queryset:
                if study.id in seen_ids:
                    continue
                seen_ids.add(study.id)
                self.stdout.write(self.style.WARNING(f"Found test study: '{study.title}' (ID: {study.id})"))
                
                # Delete related protocol submissions first if any
                ProtocolSubmission.objects.filter(study=study).delete()
                
                # Delete the study
                title = study.title
                study.delete()
                deleted_count += 1
                self.stdout.write(self.style.SUCCESS(f"Successfully deleted study: '{title}'"))

        if deleted_count == 0:
            self.stdout.write(self.style.NOTICE("No studies matching 'asdf' were found."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Cleaned up {deleted_count} study/studies."))
