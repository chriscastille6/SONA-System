"""
Middleware to set PostgreSQL session variables for RLS and audit logging.

Sets app.current_user_id and app.current_user_role at the start of each request
so that Row-Level Security policies and audit triggers can identify the acting user.
Uses SET LOCAL so values are transaction-scoped and do not leak across requests.
"""
from django.db import connection, transaction


class RLSUserContextMiddleware:
    """
    Set PostgreSQL session variables for the current request's user.

    Required for:
    - Row-Level Security policies (studies, signups)
    - irb_audit_logs trigger (changed_by_user_id)

    Wraps the request in a transaction so SET LOCAL persists for all view queries.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        cursor.execute(
                            "SET LOCAL app.current_user_id = %s",
                            [str(request.user.id)],
                        )
                        cursor.execute(
                            "SET LOCAL app.current_user_role = %s",
                            [request.user.role],
                        )
                    else:
                        cursor.execute(
                            "SET LOCAL app.current_user_id = %s",
                            [''],
                        )
                        cursor.execute(
                            "SET LOCAL app.current_user_role = %s",
                            ['anonymous'],
                        )
                return self.get_response(request)
        except Exception:
            return self.get_response(request)
