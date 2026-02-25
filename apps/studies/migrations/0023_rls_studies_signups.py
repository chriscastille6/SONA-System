# FERPA Row-Level Security for studies and signups

from django.db import migrations


def apply_rls(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        for sql, reverse_sql in _RLS_OPERATIONS:
            if sql:
                cursor.execute(sql)


def reverse_rls(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        for sql, reverse_sql in reversed(_RLS_OPERATIONS):
            if reverse_sql and reverse_sql is not migrations.RunSQL.noop:
                cursor.execute(reverse_sql)


# UUID cast helper - CAST avoids :: parsing issues on some PostgreSQL versions
_U = "CAST(NULLIF(trim(current_setting('app.current_user_id', true)), '') AS uuid)"

# (forward_sql, reverse_sql)
# Use separate policies per role to avoid complex nesting that fails on some PostgreSQL versions
_RLS_OPERATIONS = [
    ("ALTER TABLE studies ENABLE ROW LEVEL SECURITY", "ALTER TABLE studies DISABLE ROW LEVEL SECURITY"),
    ("ALTER TABLE studies FORCE ROW LEVEL SECURITY", migrations.RunSQL.noop),
    (
        "CREATE POLICY studies_select_admin ON studies FOR SELECT USING (current_setting('app.current_user_role', true) = 'admin')",
        "DROP POLICY IF EXISTS studies_select_admin ON studies",
    ),
    (
        "CREATE POLICY studies_select_researcher ON studies FOR SELECT USING (current_setting('app.current_user_role', true) IN ('researcher', 'irb_member', 'instructor') AND researcher_id IS NOT NULL AND researcher_id = " + _U + ")",
        "DROP POLICY IF EXISTS studies_select_researcher ON studies",
    ),
    (
        "CREATE POLICY studies_select_participant ON studies FOR SELECT USING (current_setting('app.current_user_role', true) IN ('participant', 'anonymous', '') AND is_active = true AND is_approved = true AND irb_status IN ('approved', 'exempt', 'not_required') AND (irb_expiration IS NULL OR irb_expiration >= CURRENT_DATE))",
        "DROP POLICY IF EXISTS studies_select_participant ON studies",
    ),
    (
        "CREATE POLICY studies_insert_policy ON studies FOR INSERT WITH CHECK "
        "(current_setting('app.current_user_role', true) IN ('admin', 'researcher', 'irb_member', 'instructor'))",
        "DROP POLICY IF EXISTS studies_insert_policy ON studies",
    ),
    (
        "CREATE POLICY studies_update_policy ON studies FOR UPDATE USING ("
        "(current_setting('app.current_user_role', true) = 'admin') "
        "OR ((current_setting('app.current_user_role', true) IN ('researcher', 'irb_member', 'instructor') "
        "AND researcher_id IS NOT NULL AND researcher_id = " + _U + "))",
        "DROP POLICY IF EXISTS studies_update_policy ON studies",
    ),
    (
        "CREATE POLICY studies_delete_policy ON studies FOR DELETE USING "
        "(current_setting('app.current_user_role', true) = 'admin')",
        "DROP POLICY IF EXISTS studies_delete_policy ON studies",
    ),
    ("ALTER TABLE signups ENABLE ROW LEVEL SECURITY", "ALTER TABLE signups DISABLE ROW LEVEL SECURITY"),
    ("ALTER TABLE signups FORCE ROW LEVEL SECURITY", migrations.RunSQL.noop),
    (
        "CREATE POLICY signups_select_policy ON signups FOR SELECT USING ("
        "(current_setting('app.current_user_role', true) = 'admin') "
        "OR (participant_id = " + _U + ") "
        "OR EXISTS (SELECT 1 FROM timeslots t JOIN studies s ON t.study_id = s.id "
        "WHERE t.id = signups.timeslot_id AND s.researcher_id = " + _U + ")",
        "DROP POLICY IF EXISTS signups_select_policy ON signups",
    ),
    ("CREATE POLICY signups_insert_policy ON signups FOR INSERT WITH CHECK (true)", "DROP POLICY IF EXISTS signups_insert_policy ON signups"),
    ("CREATE POLICY signups_update_policy ON signups FOR UPDATE USING (true)", "DROP POLICY IF EXISTS signups_update_policy ON signups"),
    ("CREATE POLICY signups_delete_policy ON signups FOR DELETE USING (true)", "DROP POLICY IF EXISTS signups_delete_policy ON signups"),
]


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0022_active_approved_studies_view'),
    ]

    operations = [
        migrations.RunPython(apply_rls, reverse_rls),
    ]
