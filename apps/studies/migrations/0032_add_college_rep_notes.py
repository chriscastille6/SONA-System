# Generated migration: store college rep notes when making determination

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0031_rename_conjoint_sona_irb_to_prams'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocolsubmission',
            name='college_rep_notes',
            field=models.TextField(blank=True, help_text="College rep's notes when making the determination (optional)"),
        ),
    ]
