import shutil
from pathlib import Path

from django.conf import settings
from django.db import migrations


def seed_conjoint_irb_assets(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    # Ensure OSF metadata is present
    updated_fields = []
    if not study.osf_enabled:
        study.osf_enabled = True
        updated_fields.append('osf_enabled')
    if study.osf_project_id != 'j9ghr':
        study.osf_project_id = 'j9ghr'
        updated_fields.append('osf_project_id')
    if study.osf_link != 'https://osf.io/j9ghr/':
        study.osf_link = 'https://osf.io/j9ghr/'
        updated_fields.append('osf_link')
    if updated_fields:
        study.save(update_fields=updated_fields)

    asset_dir = Path(__file__).resolve().parents[1] / 'assets' / 'irb' / 'conjoint-analysis'
    media_dir = Path(settings.MEDIA_ROOT) / 'irb' / 'conjoint-analysis'
    media_dir.mkdir(parents=True, exist_ok=True)

    author = getattr(study, 'researcher', None)

    attachments = [
        ('IRB approval packet (PDF)', 'Conjoint_Analysis_NonExempt_IRB_Application.pdf'),
        ('Meder and Castille approval document', 'meder_and_castille_approval.pdf'),
        ('SONA-facing protocol summary', 'SONA_IRB_Summary.md'),
    ]

    for message, filename in attachments:
        src = asset_dir / filename
        if not src.exists():
            continue

        dest = media_dir / filename
        shutil.copyfile(src, dest)

        relative_path = f'irb/conjoint-analysis/{filename}'
        defaults = {
            'author': author,
            'visibility': 'irb',
            'message': message,
        }
        update, created = StudyUpdate.objects.get_or_create(
            study=study,
            attachment_name=filename,
            defaults=defaults,
        )
        if not created:
            update.message = message
            update.author = author
            update.visibility = 'irb'
        update.attachment.name = relative_path
        update.attachment_name = filename
        try:
            update.attachment_size = dest.stat().st_size
        except OSError:
            update.attachment_size = 0
        update.save()


def unseed_conjoint_irb_assets(apps, schema_editor):
    """Best-effort cleanup – only remove StudyUpdate records we created."""
    Study = apps.get_model('studies', 'Study')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    StudyUpdate.objects.filter(
        study=study,
        attachment_name__in=[
            'Conjoint_Analysis_NonExempt_IRB_Application.pdf',
            'meder_and_castille_approval.pdf',
            'SONA_IRB_Summary.md',
        ],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0007_conjoint_study'),
    ]

    operations = [
        migrations.RunPython(seed_conjoint_irb_assets, unseed_conjoint_irb_assets),
    ]

