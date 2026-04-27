# StudentDataConsent: separate HR SJT vs MNGT 425 teaching portfolio (Exhibits A–C)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0035_add_calendar_sync_and_sms_flags"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="studentdataconsent",
            name="unique_study_student_data_consent",
        ),
        migrations.AddField(
            model_name="studentdataconsent",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("hr_sjt_secondary", "HR SJT — secondary use of course/assignment data"),
                    (
                        "mngt425_teaching_portfolio",
                        "MNGT 425 — teaching portfolio research (Exhibits A–C)",
                    ),
                ],
                db_index=True,
                default="hr_sjt_secondary",
                help_text="Which consent the student agreed to; same email may consent separately to each purpose.",
                max_length=40,
            ),
        ),
        migrations.AddConstraint(
            model_name="studentdataconsent",
            constraint=models.UniqueConstraint(
                fields=("study", "email", "purpose"),
                name="unique_study_email_purpose_student_data_consent",
            ),
        ),
    ]
