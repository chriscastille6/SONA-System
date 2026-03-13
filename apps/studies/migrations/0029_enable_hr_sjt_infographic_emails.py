# Enable infographic email collection for HR SJT (lab-branded report signup)

from django.db import migrations


def enable_infographic_emails_for_hr_sjt(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='hr-sjt').update(collect_emails_for_infographics=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0028_rename_student_dat_study_i_consent_idx_student_dat_study_i_a198e7_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(enable_infographic_emails_for_hr_sjt, noop),
    ]
