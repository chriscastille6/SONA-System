"""
Admin configuration for studies app.
"""
from django.contrib import admin
from .models import Study, Timeslot, Signup, Response


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'researcher', 'mode', 'credit_value', 'is_active', 'irb_status', 'monitoring_enabled', 'created_at']
    list_filter = ['mode', 'is_active', 'is_approved', 'irb_status', 'monitoring_enabled', 'created_at']
    search_fields = ['title', 'slug', 'researcher__email', 'researcher__first_name', 'researcher__last_name']
    raw_id_fields = ['researcher']
    readonly_fields = ['created_at', 'updated_at', 'current_bf']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'mode', 'researcher', 'credit_value')
        }),
        ('Status', {
            'fields': ('is_active', 'is_approved')
        }),
        ('IRB', {
            'fields': ('irb_status', 'irb_number', 'irb_expiration')
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




