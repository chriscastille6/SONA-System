# Infographic email signup: separate dataset for participants who want to receive infographics

from django.db import migrations, models
import django.db.models.deletion
import uuid


def enable_infographic_emails_for_goal_setting(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='goal-setting').update(collect_emails_for_infographics=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0024_add_post_decision_analysis_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='collect_emails_for_infographics',
            field=models.BooleanField(
                default=False,
                help_text='Allow participants to optionally share their email to receive study infographics (stored separately from response data)',
            ),
        ),
        migrations.CreateModel(
            name='StudyEmailContact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('session_id', models.UUIDField(blank=True, db_index=True, help_text='Optional link to response session if submitted in same flow', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='infographic_contacts', to='studies.study')),
            ],
            options={
                'verbose_name': 'Study infographic contact',
                'verbose_name_plural': 'Study infographic contacts',
                'db_table': 'study_email_contacts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='studyemailcontact',
            index=models.Index(fields=['study', 'created_at'], name='study_email_study_i_8a1b2c_idx'),
        ),
        migrations.RunPython(enable_infographic_emails_for_goal_setting, noop),
    ]
