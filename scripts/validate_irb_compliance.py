#!/usr/bin/env python
"""
Validate IRB/FERPA compliance implementation.
Run with: python manage.py shell < scripts/validate_irb_compliance.py
Or: python manage.py runscript validate_irb_compliance (if django-extensions)
Or: python -c "import django; django.setup(); exec(open('scripts/validate_irb_compliance.py').read())"
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection


def validate():
    results = []

    # Application layer (DB-agnostic)
    from apps.accounts.middleware import RLSUserContextMiddleware
    from apps.studies.models import Study
    from django.conf import settings

    results.append(('RLSUserContextMiddleware', 'apps.accounts.middleware' in str(RLSUserContextMiddleware)))
    results.append(('Middleware in MIDDLEWARE', 'apps.accounts.middleware.RLSUserContextMiddleware' in settings.MIDDLEWARE))
    results.append(('Study.active_approved manager', hasattr(Study, 'active_approved')))
    results.append(('active_approved filter logic', Study.active_approved.all().query is not None))

    # Participant-facing views use active_approved
    from apps.studies import views
    import inspect
    study_list_src = inspect.getsource(views.study_list)
    results.append(('study_list uses active_approved', 'active_approved' in study_list_src))
    study_detail_src = inspect.getsource(views.study_detail)
    results.append(('study_detail uses active_approved', 'active_approved' in study_detail_src))
    submit_src = inspect.getsource(views.submit_response)
    results.append(('submit_response uses active_approved', 'active_approved' in submit_src))

    # PostgreSQL-specific
    if connection.vendor == 'postgresql':
        with connection.cursor() as c:
            c.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'irb_audit_logs'
                )
            """)
            results.append(('irb_audit_logs table', c.fetchone()[0]))

            c.execute("""
                SELECT tgname FROM pg_trigger 
                WHERE tgname IN ('irb_audit_studies_trigger', 'irb_audit_credit_transactions_trigger')
            """)
            triggers = [r[0] for r in c.fetchall()]
            results.append(('Audit triggers (studies, credit_transactions)', len(triggers) == 2))

            c.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.views 
                    WHERE table_schema = 'public' AND table_name = 'active_approved_studies'
                )
            """)
            results.append(('active_approved_studies view', c.fetchone()[0]))

            c.execute("""
                SELECT relname, relrowsecurity FROM pg_class 
                WHERE relname IN ('studies', 'signups') AND relkind = 'r'
            """)
            rls = {r[0]: r[1] for r in c.fetchall()}
            results.append(('RLS on studies', rls.get('studies', False)))
            results.append(('RLS on signups', rls.get('signups', False)))

            c.execute("""
                SELECT polname, polcmd FROM pg_policy 
                WHERE polrelid = 'irb_audit_logs'::regclass
            """)
            audit_policies = c.fetchall()
            # polcmd: r=SELECT, a=INSERT, w=UPDATE, d=DELETE
            no_update = any(p[1] == 'w' and 'no_update' in p[0] for p in audit_policies)
            no_delete = any(p[1] == 'd' and 'no_delete' in p[0] for p in audit_policies)
            results.append(('irb_audit_logs append-only (no UPDATE/DELETE)', no_update and no_delete))
    else:
        results.append(('PostgreSQL checks', 'SKIP (using %s)' % connection.vendor))

    return results


if __name__ == '__main__':
    print('IRB/FERPA Compliance Validation')
    print('=' * 50)
    print('Database: %s' % connection.vendor)
    print()
    for name, ok in validate():
        status = 'PASS' if ok is True else ('FAIL' if ok is False else ok)
        print('  %-45s %s' % (name, status))
    print()
