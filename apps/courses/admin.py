"""
Admin configuration for courses app.
"""
from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'term', 'section', 'instructor', 'credits_required', 'is_active']
    list_filter = ['term', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'instructor__email']
    raw_id_fields = ['instructor']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['participant', 'course', 'enrolled_at']
    list_filter = ['enrolled_at', 'course__term']
    search_fields = ['participant__email', 'participant__first_name', 'participant__last_name', 'course__code']
    raw_id_fields = ['course', 'participant']




