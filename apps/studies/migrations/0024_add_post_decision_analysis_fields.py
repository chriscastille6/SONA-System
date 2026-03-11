# Post-decision analysis: run analysis when BF threshold is reached

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0023_rls_studies_signups'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='run_analysis_on_threshold',
            field=models.BooleanField(
                default=False,
                help_text='When True, run post-decision analysis task when BF threshold is reached',
            ),
        ),
        migrations.AddField(
            model_name='study',
            name='post_decision_analysis_run_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the post-decision analysis task last ran (set when threshold reached)',
                null=True,
            ),
        ),
    ]
