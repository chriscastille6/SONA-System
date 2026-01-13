import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studies', '0005_irb_reviewer_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyUpdate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('visibility', models.CharField(choices=[('irb', 'IRB Reviewers'), ('team', 'Research Team Only')], db_index=True, default='irb', help_text='Choose who should see this update.', max_length=20)),
                ('message', models.TextField(blank=True)),
                ('attachment', models.FileField(blank=True, upload_to='study_updates/%Y/%m/')),
                ('attachment_name', models.CharField(blank=True, max_length=255)),
                ('attachment_size', models.IntegerField(default=0)),
                ('notified_at', models.DateTimeField(blank=True, help_text='Last time IRB reviewers were emailed about this update.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='study_updates', to=settings.AUTH_USER_MODEL)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='studies.study')),
            ],
            options={
                'db_table': 'study_updates',
                'ordering': ['-created_at'],
                'verbose_name': 'Study Update',
                'verbose_name_plural': 'Study Updates',
            },
        ),
        migrations.AddIndex(
            model_name='studyupdate',
            index=models.Index(fields=['study', 'visibility', '-created_at'], name='study_upda_study_v_1a55b4_idx'),
        ),
    ]



