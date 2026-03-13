# Student data consent: record consent for secondary use of course data (e.g. HR SJT MNGT 425)

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0026_study_post_decision_r_script'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentDataConsent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(help_text='Student email; used to match consent to course data and for withdrawal requests', max_length=254)),
                ('consented_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('consent_text_version', models.TextField(help_text='Copy of consent form text at time of consent')),
                ('withdrawn_at', models.DateTimeField(blank=True, help_text='When participant withdrew consent, if applicable', null=True)),
                ('study', models.ForeignKey(help_text='Study for which secondary data consent is given (e.g. hr-sjt)', on_delete=django.db.models.deletion.CASCADE, related_name='student_data_consents', to='studies.study')),
            ],
            options={
                'verbose_name': 'Student data consent',
                'verbose_name_plural': 'Student data consents',
                'db_table': 'student_data_consents',
                'ordering': ['-consented_at'],
            },
        ),
        migrations.AddIndex(
            model_name='studentdataconsent',
            index=models.Index(fields=['study', 'consented_at'], name='student_dat_study_i_consent_idx'),
        ),
        migrations.AddConstraint(
            model_name='studentdataconsent',
            constraint=models.UniqueConstraint(fields=('study', 'email'), name='unique_study_student_data_consent'),
        ),
    ]
