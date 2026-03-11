# Post-decision R script: optional path to run R analysis when threshold reached

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0025_add_infographic_email_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='post_decision_r_script',
            field=models.CharField(
                blank=True,
                help_text='Path to R script to run when threshold is reached (relative to project root or absolute). Leave blank to skip R analysis.',
                max_length=500,
            ),
        ),
    ]
