"""
Data migration: rename conjoint IRB summary from SONA_IRB_Summary.md to PRAMS_IRB_Summary.md.
Updates existing StudyUpdate rows and renames the media file so existing deployments stay consistent.
"""
import os
from django.db import migrations


def rename_sona_to_prams(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    updates = StudyUpdate.objects.filter(
        study=study,
        attachment_name='SONA_IRB_Summary.md',
    )
    for update in updates:
        update.attachment_name = 'PRAMS_IRB_Summary.md'
        update.message = 'PRAMS-facing protocol summary'
        if update.attachment:
            old_name = update.attachment.name
            if old_name and 'SONA_IRB_Summary.md' in old_name:
                from django.conf import settings
                old_path = os.path.join(settings.MEDIA_ROOT, old_name)
                new_name = old_name.replace('SONA_IRB_Summary.md', 'PRAMS_IRB_Summary.md')
                new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                if os.path.isfile(old_path):
                    try:
                        os.rename(old_path, new_path)
                    except OSError:
                        pass
                update.attachment.name = new_name
        update.save()


def noop_reverse(apps, schema_editor):
    """No reverse: we do not rename back to SONA."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0030_add_full_protocol_pdf'),
    ]

    operations = [
        migrations.RunPython(rename_sona_to_prams, noop_reverse),
    ]
