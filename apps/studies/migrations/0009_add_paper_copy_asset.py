import shutil
from pathlib import Path

from django.conf import settings
from django.db import migrations


def add_paper_copy(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    asset = Path(__file__).resolve().parents[1] / 'assets' / 'irb' / 'conjoint-analysis' / 'Conjoint_Analysis_Paper_Copy.pdf'
    if not asset.exists():
        return

    media_dir = Path(settings.MEDIA_ROOT) / 'irb' / 'conjoint-analysis'
    media_dir.mkdir(parents=True, exist_ok=True)
    dest = media_dir / 'Conjoint_Analysis_Paper_Copy.pdf'
    shutil.copyfile(asset, dest)

    author = getattr(study, 'researcher', None)
    relative_path = 'irb/conjoint-analysis/Conjoint_Analysis_Paper_Copy.pdf'

    update, created = StudyUpdate.objects.get_or_create(
        study=study,
        attachment_name='Conjoint_Analysis_Paper_Copy.pdf',
        defaults={
            'author': author,
            'visibility': 'irb',
            'message': 'Signed paper consent packet (scanned copy)',
        },
    )
    if not created:
        update.author = author
        update.visibility = 'irb'
        update.message = 'Signed paper consent packet (scanned copy)'

    update.attachment.name = relative_path
    update.attachment_name = 'Conjoint_Analysis_Paper_Copy.pdf'
    try:
        update.attachment_size = dest.stat().st_size
    except OSError:
        update.attachment_size = 0
    update.save()


def remove_paper_copy(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    StudyUpdate.objects.filter(
        study=study,
        attachment_name='Conjoint_Analysis_Paper_Copy.pdf',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0008_seed_conjoint_irb_assets'),
    ]

    operations = [
        migrations.RunPython(add_paper_copy, remove_paper_copy),
    ]


