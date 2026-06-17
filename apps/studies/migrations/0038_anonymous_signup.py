# Generated manually for anonymous timeslot booking

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0037_student_data_consent_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='allows_anonymous_booking',
            field=models.BooleanField(
                default=False,
                help_text='Allow public sign-up without a participant account (token + PIN only)',
            ),
        ),
        migrations.CreateModel(
            name='AnonymousSignup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('booking_reference', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Reference shown to participant for cancellation', unique=True)),
                ('cancellation_pin', models.CharField(help_text='4-digit PIN for cancellation', max_length=4)),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('cancelled', 'Cancelled')], db_index=True, default='booked', max_length=20)),
                ('consent_text_version', models.TextField(help_text='Copy of consent text at time of signup')),
                ('booked_at', models.DateTimeField(auto_now_add=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('timeslot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anonymous_signups', to='studies.timeslot')),
            ],
            options={
                'verbose_name': 'Anonymous Signup',
                'verbose_name_plural': 'Anonymous Signups',
                'db_table': 'anonymous_signups',
                'ordering': ['-booked_at'],
                'indexes': [
                    models.Index(fields=['timeslot', 'status'], name='anonymous_s_timeslo_6a8f2d_idx'),
                    models.Index(fields=['booking_reference'], name='anonymous_s_booking_4c1e9a_idx'),
                ],
            },
        ),
    ]
