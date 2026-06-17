# Rename public study slug so signup URLs do not expose "goal-setting" to participants.

from django.db import migrations


def rename_slug_forward(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='goal-setting').update(slug='decision-making')


def rename_slug_backward(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    Study.objects.filter(slug='decision-making').update(slug='goal-setting')


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0039_enable_goal_setting_anonymous_booking'),
    ]

    operations = [
        migrations.RunPython(rename_slug_forward, rename_slug_backward),
    ]
