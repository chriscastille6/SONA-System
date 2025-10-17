"""
Admin configuration for studies app.
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from apps.credits.models import AuditLog
from .models import Study, Timeslot, Signup, Response


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'researcher', 'mode', 'credit_value', 'is_active', 'irb_status', 'irb_approved_by', 'monitoring_enabled', 'created_at']
    list_filter = ['mode', 'is_active', 'is_approved', 'irb_status', 'monitoring_enabled', 'created_at']
    search_fields = ['title', 'slug', 'researcher__email', 'researcher__first_name', 'researcher__last_name', 'irb_number']
    raw_id_fields = ['researcher', 'irb_approved_by', 'irb_last_reviewed_by']
    readonly_fields = ['created_at', 'updated_at', 'current_bf', 'irb_approved_at', 'irb_last_reviewed_at', 'view_audit_trail']
    actions = ['approve_studies', 'mark_irb_reviewed']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'mode', 'researcher', 'credit_value')
        }),
        ('Status', {
            'fields': ('is_active', 'is_approved')
        }),
        ('IRB Information', {
            'fields': ('irb_status', 'irb_number', 'irb_expiration')
        }),
        ('IRB Audit Trail', {
            'fields': ('irb_approved_by', 'irb_approved_at', 'irb_last_reviewed_by', 'irb_last_reviewed_at', 'irb_approval_notes', 'view_audit_trail'),
            'classes': ('collapse',)
        }),
        ('Open Science Framework', {
            'fields': ('osf_enabled', 'osf_project_id', 'osf_link')
        }),
        ('Bayesian Monitoring', {
            'fields': ('monitoring_enabled', 'min_sample_size', 'bf_threshold', 'analysis_plugin', 'current_bf', 'monitoring_notified')
        }),
        ('Study Details', {
            'fields': ('duration_minutes', 'max_participants', 'eligibility', 'consent_text', 'external_link')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def view_audit_trail(self, obj):
        """Display audit trail for this study."""
        if not obj.pk:
            return "N/A (study not saved yet)"
        
        logs = AuditLog.objects.filter(entity='study', entity_id=obj.id).order_by('-created_at')[:10]
        if not logs:
            return "No audit trail entries yet"
        
        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background:#f0f0f0;"><th>Date</th><th>Actor</th><th>Action</th><th>Details</th></tr>'
        
        for log in logs:
            actor = log.actor.get_full_name() if log.actor else "System"
            html += f'<tr style="border-bottom:1px solid #ddd;">'
            html += f'<td style="padding:5px;">{log.created_at.strftime("%Y-%m-%d %H:%M")}</td>'
            html += f'<td style="padding:5px;">{actor}</td>'
            html += f'<td style="padding:5px;"><strong>{log.action}</strong></td>'
            html += f'<td style="padding:5px; font-size:0.9em;">{log.metadata}</td>'
            html += f'</tr>'
        
        html += '</table>'
        return format_html(html)
    
    view_audit_trail.short_description = "Audit Trail (Last 10 entries)"
    
    def save_model(self, request, obj, form, change):
        """Track IRB approval when admin saves study."""
        if change:  # Existing study
            # Check if is_approved changed to True
            old_obj = Study.objects.get(pk=obj.pk)
            if not old_obj.is_approved and obj.is_approved:
                obj.irb_approved_by = request.user
                obj.irb_approved_at = timezone.now()
            
            # Track any IRB status change
            if old_obj.irb_status != obj.irb_status:
                obj.irb_last_reviewed_by = request.user
                obj.irb_last_reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def approve_studies(self, request, queryset):
        """Admin action to approve selected studies."""
        count = 0
        for study in queryset:
            if not study.is_approved:
                study.is_approved = True
                study.irb_approved_by = request.user
                study.irb_approved_at = timezone.now()
                study.save()
                count += 1
        
        self.message_user(request, f'Successfully approved {count} studies.')
    
    approve_studies.short_description = "Approve selected studies (IRB)"
    
    def mark_irb_reviewed(self, request, queryset):
        """Admin action to mark studies as reviewed."""
        count = queryset.update(
            irb_last_reviewed_by=request.user,
            irb_last_reviewed_at=timezone.now()
        )
        self.message_user(request, f'Marked {count} studies as reviewed.')
    
    mark_irb_reviewed.short_description = "Mark as IRB reviewed"


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ['study', 'starts_at', 'capacity', 'current_signups', 'is_cancelled']
    list_filter = ['is_cancelled', 'starts_at']
    search_fields = ['study__title']
    raw_id_fields = ['study']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ['participant', 'timeslot', 'status', 'booked_at']
    list_filter = ['status', 'booked_at']
    search_fields = ['participant__email', 'timeslot__study__title']
    raw_id_fields = ['timeslot', 'participant']
    readonly_fields = ['booked_at', 'consented_at']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['study', 'session_id', 'created_at', 'ip_address']
    list_filter = ['study', 'created_at']
    search_fields = ['study__title', 'session_id']
    raw_id_fields = ['study']
    readonly_fields = ['id', 'created_at', 'session_id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('study', 'session_id', 'created_at')
        }),
        ('Response Data', {
            'fields': ('payload',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )




