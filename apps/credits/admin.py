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
    list_display = ['created_at', 'actor', 'action', 'entity', 'entity_id', 'ip_address']
    list_filter = ['action', 'entity', 'created_at']
    search_fields = ['actor__email', 'actor__first_name', 'actor__last_name', 'action', 'entity']
    raw_id_fields = ['actor']
    readonly_fields = ['created_at', 'formatted_metadata']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('created_at', 'actor', 'action', 'entity', 'entity_id')
        }),
        ('Details', {
            'fields': ('formatted_metadata',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_metadata(self, obj):
        """Display metadata in a readable format."""
        from django.utils.html import format_html
        
        if not obj.metadata:
            return "No additional data"
        
        html = '<table style="border-collapse: collapse;">'
        for key, value in obj.metadata.items():
            html += f'<tr><td style="padding:5px; font-weight:bold; vertical-align:top;">{key}:</td>'
            html += f'<td style="padding:5px;">{value}</td></tr>'
        html += '</table>'
        return format_html(html)
    
    formatted_metadata.short_description = "Metadata"
    
    def has_add_permission(self, request):
        """Don't allow manual creation of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of audit logs."""
        return False




