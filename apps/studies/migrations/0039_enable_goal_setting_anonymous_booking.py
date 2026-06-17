# Enable anonymous public sign-up for the goal-setting study (no participant account).

from django.db import migrations


def enable_goal_setting_anonymous(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='goal-setting').update(allows_anonymous_booking=True)


def disable_goal_setting_anonymous(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='goal-setting').update(allows_anonymous_booking=False)


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0038_anonymous_signup'),
    ]

    operations = [
        migrations.RunPython(enable_goal_setting_anonymous, disable_goal_setting_anonymous),
    ]
