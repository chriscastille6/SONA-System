import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studies', '0004_irbreview_reviewdocument_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='IRBReviewerAssignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('receive_email_updates', models.BooleanField(default=True, help_text='Send email notifications when there are new reviews or updates.')),
                ('last_notified_at', models.DateTimeField(blank=True, help_text='Last time an automated notification was sent.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reviewer', models.ForeignKey(limit_choices_to={'role': 'irb_member'}, on_delete=django.db.models.deletion.CASCADE, related_name='irb_assignments', to=settings.AUTH_USER_MODEL)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer_assignments', to='studies.study')),
            ],
            options={
                'db_table': 'irb_reviewer_assignments',
                'ordering': ['-created_at'],
                'verbose_name': 'IRB Reviewer Assignment',
                'verbose_name_plural': 'IRB Reviewer Assignments',
                'unique_together': {('study', 'reviewer')},
            },
        ),
        migrations.AddField(
            model_name='study',
            name='irb_reviewers',
            field=models.ManyToManyField(blank=True, help_text='IRB members assigned to audit this study', related_name='assigned_irb_studies', through='studies.IRBReviewerAssignment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='irbreviewerassignment',
            index=models.Index(fields=['study', 'reviewer'], name='irb_assign_study_reviewer_idx'),
        ),
        migrations.AddIndex(
            model_name='irbreviewerassignment',
            index=models.Index(fields=['reviewer', 'created_at'], name='irb_assign_reviewer_created_idx'),
        ),
    ]



