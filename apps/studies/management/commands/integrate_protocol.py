"""
Management command to integrate HTML protocols from the Psychological Assessments folder.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study
import os
import shutil
from pathlib import Path

User = get_user_model()


class Command(BaseCommand):
    help = 'Integrate a protocol from Psychological Assessments folder'

    def add_arguments(self, parser):
        parser.add_argument('protocol_name', type=str, help='Protocol folder name (e.g., emotional-intelligence-assessment)')
        parser.add_argument('html_file', type=str, help='HTML file to use (e.g., comprehensive-cat-assessment.html)')
        parser.add_argument('--title', type=str, help='Study title', required=True)
        parser.add_argument('--slug', type=str, help='Study slug (auto-generated if not provided)')
        parser.add_argument('--description', type=str, help='Study description')
        parser.add_argument('--min-n', type=int, default=20, help='Minimum sample size')
        parser.add_argument('--bf-threshold', type=float, default=10.0, help='BF threshold')

    def handle(self, *args, **options):
        protocol_name = options['protocol_name']
        html_file = options['html_file']
        title = options['title']
        slug = options.get('slug')
        description = options.get('description', '')
        min_n = options['min_n']
        bf_threshold = options['bf_threshold']
        
        # Paths
        psych_assessments = Path('/Users/ccastille/Documents/GitHub/Psychological Assessments')
        source_dir = psych_assessments / protocol_name
        source_html = source_dir / html_file
        
        # Check source exists
        if not source_html.exists():
            self.stdout.write(self.style.ERROR(f'Source HTML not found: {source_html}'))
            return
        
        # Get researcher
        researcher = User.objects.filter(role='researcher').first()
        if not researcher:
            self.stdout.write(self.style.ERROR('No researcher user found. Create one first.'))
            return
        
        # Check if study exists
        if slug and Study.objects.filter(slug=slug).exists():
            self.stdout.write(self.style.WARNING(f'Study with slug "{slug}" already exists'))
            return
        
        # Create study
        study = Study.objects.create(
            title=title,
            slug=slug or '',  # Auto-generated in save()
            description=description or f'Protocol for {title}',
            mode='online',
            researcher=researcher,
            credit_value=1.0,
            duration_minutes=30,
            is_active=True,
            is_approved=True,
            irb_status='not_required',
            osf_enabled=False,
            monitoring_enabled=True,
            min_sample_size=min_n,
            bf_threshold=bf_threshold,
            analysis_plugin='apps.studies.analysis.placeholder:compute_bf',
            consent_text='I consent to participate in this research study.',
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created study: {study.title} (slug: {study.slug})'))
        
        # Create project directory
        project_dir = Path('/Users/ccastille/Documents/GitHub/SONA System/templates/projects') / study.slug
        protocol_dir = project_dir / 'protocol'
        protocol_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy HTML file
        dest_html = protocol_dir / 'index.html'
        shutil.copy2(source_html, dest_html)
        self.stdout.write(self.style.SUCCESS(f'Copied HTML to: {dest_html}'))
        
        # Copy any related JS/JSON files
        related_files = []
        html_content = source_html.read_text()
        
        # Look for related files mentioned in HTML
        for pattern in ['.js', '.json', '-engine.js', '-analysis.js']:
            base_name = html_file.replace('.html', '')
            for file in source_dir.glob(f'{base_name}*{pattern}'):
                related_files.append(file)
            for file in source_dir.glob(f'*{pattern}'):
                if file.name in html_content:
                    related_files.append(file)
        
        # Copy related files
        for file in related_files:
            dest_file = protocol_dir / file.name
            shutil.copy2(file, dest_file)
            self.stdout.write(self.style.SUCCESS(f'Copied: {file.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Integration complete!'))
        self.stdout.write(self.style.SUCCESS(f'Protocol URL: /studies/{study.slug}/run/'))
        self.stdout.write(self.style.SUCCESS(f'Status URL: /studies/{study.slug}/status/'))
        self.stdout.write(self.style.SUCCESS(f'API Submit URL: /api/studies/{study.id}/submit/'))
        self.stdout.write(self.style.WARNING('\nNext step: Modify the HTML to submit data to the API'))

