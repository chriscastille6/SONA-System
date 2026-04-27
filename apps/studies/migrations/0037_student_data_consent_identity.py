# StudentDataConsent: legal name + explicit consent / decline for IRB audit trail

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0036_student_data_consent_purpose"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentdataconsent",
            name="first_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Participant first name (signed/typed) for consent records; optional for legacy rows.",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="studentdataconsent",
            name="last_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Participant last name (signed/typed) for consent records; optional for legacy rows.",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="studentdataconsent",
            name="consent_given",
            field=models.BooleanField(
                default=True,
                help_text="False when the participant explicitly declined on this form (IRB audit).",
            ),
        ),
    ]
