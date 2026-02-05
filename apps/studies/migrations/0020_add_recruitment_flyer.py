# Generated manually for recruitment flyer upload

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0019_add_protocol_amendment_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocolsubmission',
            name='recruitment_flyer',
            field=models.FileField(
                blank=True,
                help_text='Upload a recruitment flyer or poster if applicable (PDF or image)',
                null=True,
                upload_to='protocol_submissions/recruitment_flyers/%Y/%m/',
            ),
        ),
    ]
