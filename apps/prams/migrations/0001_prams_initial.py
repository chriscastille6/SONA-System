# Generated migration for PRAMS (FERPA-compliant)

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PRAMSStudy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('datetime', models.DateTimeField(help_text='When the study takes place')),
                ('max_capacity', models.PositiveIntegerField(default=1, help_text='Maximum number of participants')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'prams_study',
                'ordering': ['datetime'],
                'verbose_name': 'PRAMS Study',
                'verbose_name_plural': 'PRAMS Studies',
            },
        ),
        migrations.CreateModel(
            name='PRAMSSignup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('participant_secure_id', models.CharField(db_index=True, help_text='Secure Participant ID from external system (no PII)', max_length=255)),
                ('cancellation_pin', models.CharField(help_text='4-digit PIN for cancellation', max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signups', to='prams.pramsstudy')),
            ],
            options={
                'db_table': 'prams_signup',
                'ordering': ['-created_at'],
                'verbose_name': 'PRAMS Signup',
                'verbose_name_plural': 'PRAMS Signups',
            },
        ),
        migrations.AddConstraint(
            model_name='pramssignup',
            constraint=models.UniqueConstraint(fields=('study', 'participant_secure_id'), name='prams_signup_unique_study_participant'),
        ),
    ]
