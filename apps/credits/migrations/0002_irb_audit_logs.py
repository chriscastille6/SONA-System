# Generated for OHRP/IRB compliance - immutable database-level audit log

from django.db import migrations


def apply_irb_audit_logs(apps, schema_editor):
    """Apply only on PostgreSQL (uses JSONB, RLS, triggers)."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(CREATE_SQL)


def reverse_irb_audit_logs(apps, schema_editor):
    """Reverse only on PostgreSQL."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(REVERSE_SQL)


CREATE_SQL = """
-- OHRP/IRB compliant immutable audit log
CREATE TABLE irb_audit_logs (
    log_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    action_type text NOT NULL CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data jsonb,
    new_data jsonb,
    changed_by_user_id uuid,
    changed_at timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX irb_audit_logs_table_record_idx ON irb_audit_logs (table_name, record_id);
CREATE INDEX irb_audit_logs_changed_at_idx ON irb_audit_logs (changed_at DESC);

-- Append-only: block UPDATE and DELETE
ALTER TABLE irb_audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY irb_audit_logs_insert_policy ON irb_audit_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY irb_audit_logs_select_policy ON irb_audit_logs
    FOR SELECT USING (true);

CREATE POLICY irb_audit_logs_no_update ON irb_audit_logs
    FOR UPDATE USING (false);

CREATE POLICY irb_audit_logs_no_delete ON irb_audit_logs
    FOR DELETE USING (false);

-- Generic trigger function
CREATE OR REPLACE FUNCTION irb_audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id uuid;
    v_record_id uuid;
BEGIN
    v_user_id := NULL;
    BEGIN
        v_user_id := NULLIF(trim(current_setting('app.current_user_id', true)), '')::uuid;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;

    v_record_id := CASE TG_OP
        WHEN 'INSERT' THEN NEW.id
        WHEN 'UPDATE' THEN NEW.id
        WHEN 'DELETE' THEN OLD.id
    END;

    INSERT INTO irb_audit_logs (table_name, record_id, action_type, old_data, new_data, changed_by_user_id)
    VALUES (
        TG_TABLE_NAME,
        v_record_id,
        TG_OP,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD)::jsonb ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW)::jsonb ELSE NULL END,
        v_user_id
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply to studies (maps to irb_protocols)
DROP TRIGGER IF EXISTS irb_audit_studies_trigger ON studies;
CREATE TRIGGER irb_audit_studies_trigger
    AFTER INSERT OR UPDATE OR DELETE ON studies
    FOR EACH ROW EXECUTE FUNCTION irb_audit_trigger_func();

-- Apply to credit_transactions (maps to participant_credits)
DROP TRIGGER IF EXISTS irb_audit_credit_transactions_trigger ON credit_transactions;
CREATE TRIGGER irb_audit_credit_transactions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON credit_transactions
    FOR EACH ROW EXECUTE FUNCTION irb_audit_trigger_func();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS irb_audit_studies_trigger ON studies;
DROP TRIGGER IF EXISTS irb_audit_credit_transactions_trigger ON credit_transactions;
DROP FUNCTION IF EXISTS irb_audit_trigger_func();
DROP TABLE IF EXISTS irb_audit_logs;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0001_initial'),
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_irb_audit_logs, reverse_irb_audit_logs),
    ]
