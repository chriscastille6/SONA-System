"""
Admin configuration for studies app.
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from apps.credits.models import AuditLog
from .models import (
    Study,
    Timeslot,
    Signup,
    Response,
    IRBReview,
    ReviewDocument,
    IRBReviewerAssignment,
    StudyUpdate,
)


class IRBReviewerAssignmentInline(admin.TabularInline):
    model = IRBReviewerAssignment
    extra = 0
    raw_id_fields = ['reviewer']
    fields = ['reviewer', 'receive_email_updates', 'last_notified_at', 'created_at', 'updated_at']
    readonly_fields = ['last_notified_at', 'created_at', 'updated_at']


class StudyUpdateInline(admin.StackedInline):
    model = StudyUpdate
    extra = 0
    fields = [
        'author',
        'visibility',
        'message',
        'attachment',
        'attachment_name',
        'attachment_size',
        'notified_at',
        'created_at',
        'updated_at',
    ]
    readonly_fields = [
        'author',
        'attachment_name',
        'attachment_size',
        'notified_at',
        'created_at',
        'updated_at',
    ]


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'researcher', 'mode', 'credit_value', 'is_active', 'irb_status', 'irb_approved_by', 'monitoring_enabled', 'created_at']
    list_filter = ['mode', 'is_active', 'is_approved', 'irb_status', 'monitoring_enabled', 'created_at']
    search_fields = ['title', 'slug', 'researcher__email', 'researcher__first_name', 'researcher__last_name', 'irb_number']
    raw_id_fields = ['researcher', 'irb_approved_by', 'irb_last_reviewed_by']
    readonly_fields = ['created_at', 'updated_at', 'current_bf', 'irb_approved_at', 'irb_last_reviewed_at', 'view_audit_trail']
    actions = ['approve_studies', 'mark_irb_reviewed']
    inlines = [IRBReviewerAssignmentInline, StudyUpdateInline]
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


@admin.register(IRBReview)
class IRBReviewAdmin(admin.ModelAdmin):
    list_display = ['study', 'version', 'status', 'overall_risk_level', 'initiated_by', 'initiated_at', 'critical_count', 'moderate_count']
    list_filter = ['status', 'overall_risk_level', 'initiated_at']
    search_fields = ['study__title', 'study__slug', 'initiated_by__email']
    raw_id_fields = ['study', 'initiated_by']
    readonly_fields = [
        'id', 'version', 'initiated_at', 'completed_at', 'processing_time_seconds',
        'ethics_analysis', 'privacy_analysis', 'vulnerability_analysis',
        'data_security_analysis', 'consent_analysis', 'critical_issues',
        'moderate_issues', 'minor_issues', 'recommendations', 'ai_model_versions',
        'uploaded_files', 'view_documents', 'view_summary'
    ]
    actions = ['trigger_committee_review']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('study', 'version', 'status', 'initiated_by', 'initiated_at', 'completed_at')
        }),
        ('Materials', {
            'fields': ('osf_repo_url', 'uploaded_files', 'view_documents')
        }),
        ('Overall Assessment', {
            'fields': ('overall_risk_level', 'view_summary', 'processing_time_seconds')
        }),
        ('Findings by Severity', {
            'fields': ('critical_issues', 'moderate_issues', 'minor_issues')
        }),
        ('Agent-Specific Analysis', {
            'fields': ('ethics_analysis', 'privacy_analysis', 'vulnerability_analysis', 
                      'data_security_analysis', 'consent_analysis'),
            'classes': ('collapse',)
        }),
        ('Recommendations', {
            'fields': ('recommendations',)
        }),
        ('Researcher Response', {
            'fields': ('researcher_notes', 'issues_addressed')
        }),
        ('Audit Trail', {
            'fields': ('ai_model_versions',),
            'classes': ('collapse',)
        }),
    )
    
    def critical_count(self, obj):
        """Display count of critical issues."""
        count = len(obj.critical_issues)
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', count)
        return count
    critical_count.short_description = 'Critical'
    
    def moderate_count(self, obj):
        """Display count of moderate issues."""
        count = len(obj.moderate_issues)
        if count > 0:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', count)
        return count
    moderate_count.short_description = 'Moderate'
    
    def view_documents(self, obj):
        """Display list of uploaded documents."""
        if not obj.pk:
            return "N/A (review not saved yet)"
        
        docs = obj.documents.all()
        if not docs:
            return "No documents uploaded"
        
        html = '<ul>'
        for doc in docs:
            html += f'<li>{doc.filename} ({doc.get_file_type_display()}) - {doc.file_size_bytes:,} bytes</li>'
        html += '</ul>'
        return format_html(html)
    view_documents.short_description = 'Uploaded Documents'
    
    def view_summary(self, obj):
        """Display a summary of the review."""
        if obj.status != 'completed':
            return f"Status: {obj.get_status_display()}"
        
        risk_colors = {
            'minimal': 'green',
            'low': 'lightgreen',
            'moderate': 'orange',
            'high': 'red'
        }
        color = risk_colors.get(obj.overall_risk_level, 'gray')
        
        html = f'<div style="background: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;">'
        html += f'{obj.get_overall_risk_level_display()}'
        html += '</div>'
        html += f'<p><strong>Total Issues:</strong> {len(obj.critical_issues) + len(obj.moderate_issues) + len(obj.minor_issues)}</p>'
        html += f'<p><strong>Recommendations:</strong> {len(obj.recommendations)}</p>'
        
        return format_html(html)
    view_summary.short_description = 'Review Summary'
    
    def trigger_committee_review(self, request, queryset):
        """Admin action to trigger AI review for selected studies."""
        from .tasks import run_irb_ai_review
        
        count = 0
        for review in queryset.filter(status='pending'):
            run_irb_ai_review.delay(str(review.id))
            count += 1
        
        self.message_user(request, f'Triggered AI review for {count} studies.')
    trigger_committee_review.short_description = "Trigger AI review (committee)"


@admin.register(StudyUpdate)
class StudyUpdateAdmin(admin.ModelAdmin):
    list_display = ['study', 'visibility', 'author', 'created_at', 'notified_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['study__title', 'author__email', 'message']
    raw_id_fields = ['study', 'author']
    readonly_fields = ['attachment_name', 'attachment_size', 'created_at', 'updated_at', 'notified_at']


@admin.register(ReviewDocument)
class ReviewDocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file_type', 'review', 'uploaded_at', 'file_size_kb']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['filename', 'review__study__title']
    raw_id_fields = ['review']
    readonly_fields = ['id', 'uploaded_at', 'file_hash', 'file_size_bytes']
    
    def file_size_kb(self, obj):
        """Display file size in KB."""
        return f"{obj.file_size_bytes / 1024:.1f} KB"
    file_size_kb.short_description = 'File Size'



