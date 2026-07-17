# Optional lab mailing list — separate from formal study data collection

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0035_add_calendar_sync_and_sms_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabCommunityContact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('stay_informed', models.BooleanField(
                    default=True,
                    help_text='Receive updates about open lab studies and aggregate findings.',
                )),
                ('source', models.CharField(
                    blank=True,
                    default='lab-studies-page',
                    help_text='Where the signup originated (e.g. lab-studies-page).',
                    max_length=100,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Lab community contact',
                'verbose_name_plural': 'Lab community contacts',
                'db_table': 'lab_community_contacts',
                'ordering': ['-created_at'],
            },
        ),
    ]
