# IRB hard-stop expiration enforcement: PostgreSQL view for active approved studies

from django.db import migrations


def apply_view(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(CREATE_VIEW_SQL)


def reverse_view(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(DROP_VIEW_SQL)


CREATE_VIEW_SQL = """
CREATE OR REPLACE VIEW active_approved_studies AS
SELECT * FROM studies
WHERE is_active = true
  AND is_approved = true
  AND is_classroom_based = false
  AND irb_status IN ('approved', 'exempt', 'not_required')
  AND (irb_expiration IS NULL OR irb_expiration >= CURRENT_DATE);
"""

DROP_VIEW_SQL = """
DROP VIEW IF EXISTS active_approved_studies;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0021_add_protocol_submission_archived'),
    ]

    operations = [
        migrations.RunPython(apply_view, reverse_view),
    ]
