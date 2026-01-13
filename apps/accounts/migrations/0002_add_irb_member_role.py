from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrator'),
                    ('irb_member', 'IRB Committee Member'),
                    ('researcher', 'Researcher'),
                    ('instructor', 'Instructor'),
                    ('participant', 'Participant'),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
    ]



