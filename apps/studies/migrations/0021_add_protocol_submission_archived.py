# Generated migration for archive option on protocol submissions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0020_add_recruitment_flyer'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocolsubmission',
            name='is_archived',
            field=models.BooleanField(db_index=True, default=False, help_text='If True, submission is archived (e.g. duplicate); hidden from default lists but preserved.'),
        ),
    ]
