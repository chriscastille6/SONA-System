"""
Management command to delete the EI × Dunning-Kruger study.
This study's content has been merged into the EI × RPM study.
"""
from django.core.management.base import BaseCommand
from apps.studies.models import Study


class Command(BaseCommand):
    help = 'Delete EI × Dunning-Kruger study (content merged into EI × RPM study)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        try:
            study = Study.objects.get(slug='ei-dk')
        except Study.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                'EI × Dunning-Kruger study (ei-dk) does not exist.'
            ))
            return
        
        if not options['force']:
            self.stdout.write(self.style.WARNING(
                f'This will delete the study: {study.title} (ID: {study.id})'
            ))
            self.stdout.write(self.style.WARNING(
                'This action cannot be undone. Use --force to proceed.'
            ))
            return
        
        # Delete the study
        study_id = study.id
        study_title = study.title
        study.delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Deleted study: {study_title} (ID: {study_id})'
        ))
        self.stdout.write(self.style.SUCCESS(
            '   Content has been merged into the EI × RPM study.'
        ))
