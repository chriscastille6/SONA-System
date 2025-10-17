"""
Admin configuration for prescreening app.
"""
from django.contrib import admin
from .models import PrescreenQuestion, PrescreenResponse


@admin.register(PrescreenQuestion)
class PrescreenQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'type', 'order', 'is_required', 'is_active']
    list_filter = ['type', 'is_required', 'is_active']
    search_fields = ['question_text']
    ordering = ['order', 'created_at']


@admin.register(PrescreenResponse)
class PrescreenResponseAdmin(admin.ModelAdmin):
    list_display = ['participant', 'submitted_at', 'updated_at']
    list_filter = ['submitted_at']
    search_fields = ['participant__email', 'participant__first_name', 'participant__last_name']
    raw_id_fields = ['participant']




