import datetime
from pathlib import Path

from django.conf import settings
from django.db import migrations
from django.utils import timezone


def create_conjoint_study(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    User = apps.get_model('accounts', 'User')
    IRBReviewerAssignment = apps.get_model('studies', 'IRBReviewerAssignment')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    researcher = User.objects.filter(email='christopher.castille@nicholls.edu').first()
    if not researcher:
        return

    consent_text = (
        "I have reviewed the paper consent form for the Theory of Optimal Fringe Benefits "
        "Using Conjoint Analysis classroom exercise. I understand participation is voluntary, "
        "anonymized, and I may skip any questions. By signing the paper consent or continuing "
        "with the survey, I acknowledge my agreement to participate."
    )

    study_defaults = {
        'title': 'Conjoint Analysis Study',
        'description': (
            "Educational conjoint-analysis exercise for Labor Economics students. "
            "Participants review consent materials, complete an intake survey, work "
            "through eight job-package choice tasks, and collaborate on designing an "
            "optimal fringe benefits package under budget constraints."
        ),
        'mode': 'online',
        'researcher': researcher,
        'credit_value': 0,
        'is_active': True,
        'is_approved': True,
        'eligibility': {
            'courses': ['Labor Economics'],
            'age_min': 18,
        },
        'consent_text': consent_text,
        'irb_status': 'approved',
        'irb_number': 'NSU-IRB-2025-CONJOINT',
        'irb_approved_at': timezone.make_aware(datetime.datetime(2025, 10, 30, 12, 0, 0)),
        'irb_approval_notes': (
            'IRB approval packet stored under media/irb/conjoint-analysis/. '
            'See SONA_IRB_Summary.md for protocol details.'
        ),
        'monitoring_enabled': False,
        'analysis_plugin': 'apps.studies.analysis.placeholder:compute_bf',
        'min_sample_size': 20,
        'bf_threshold': 10.0,
        'external_link': '',
    }

    study, created = Study.objects.get_or_create(
        slug='conjoint-analysis',
        defaults=study_defaults
    )

    if not created:
        return

    reviewer = User.objects.filter(email='jonathan.murphy@nicholls.edu').first()
    if reviewer:
        IRBReviewerAssignment.objects.get_or_create(
            study=study,
            reviewer=reviewer,
            defaults={'receive_email_updates': True}
        )

    media_base = Path(settings.MEDIA_ROOT) / 'irb' / 'conjoint-analysis'
    attachments = [
        ('IRB approval packet (PDF)', 'Conjoint_Analysis_NonExempt_IRB_Application.pdf'),
        ('IRB approval packet (DOCX)', 'Conjoint_Analysis_NonExempt_IRB_Application.docx'),
        ('SONA-facing protocol summary', 'SONA_IRB_Summary.md'),
    ]

    for message, filename in attachments:
        file_path = media_base / filename
        if not file_path.exists():
            continue

        update = StudyUpdate.objects.create(
            study=study,
            author=researcher,
            visibility='irb',
            message=message,
        )
        relative_name = f'irb/conjoint-analysis/{filename}'
        update.attachment.name = relative_name
        update.attachment_name = filename
        try:
            update.attachment_size = file_path.stat().st_size
        except OSError:
            update.attachment_size = 0
        update.save(update_fields=['attachment', 'attachment_name', 'attachment_size'])


def delete_conjoint_study(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    IRBReviewerAssignment = apps.get_model('studies', 'IRBReviewerAssignment')
    StudyUpdate = apps.get_model('studies', 'StudyUpdate')

    try:
        study = Study.objects.get(slug='conjoint-analysis')
    except Study.DoesNotExist:
        return

    IRBReviewerAssignment.objects.filter(study=study).delete()
    StudyUpdate.objects.filter(study=study).delete()
    study.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0006_studyupdate'),
        ('accounts', '0002_add_irb_member_role'),
    ]

    operations = [
        migrations.RunPython(create_conjoint_study, delete_conjoint_study),
    ]


