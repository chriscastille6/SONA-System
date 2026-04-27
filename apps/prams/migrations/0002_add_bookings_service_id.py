# Optional: Microsoft Bookings Service ID for flow mapping

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prams', '0001_prams_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pramsstudy',
            name='bookings_service_id',
            field=models.CharField(
                blank=True,
                help_text='Microsoft Bookings Service ID for flow mapping (optional)',
                max_length=255
            ),
        ),
    ]
