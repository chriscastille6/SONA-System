"""
Admin configuration for credits app.
"""
from django.contrib import admin
from .models import CreditTransaction, AuditLog


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['participant', 'study', 'course', 'amount', 'created_by', 'created_at']
    list_filter = ['created_at', 'amount']
    search_fields = ['participant__email', 'participant__first_name', 'participant__last_name', 
                     'study__title', 'course__code']
    raw_id_fields = ['participant', 'study', 'course', 'created_by']
    readonly_fields = ['created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'entity', 'created_at']
    list_filter = ['action', 'entity', 'created_at']
    search_fields = ['actor__email', 'action', 'entity']
    raw_id_fields = ['actor']
    readonly_fields = ['created_at']




