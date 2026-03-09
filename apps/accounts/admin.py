"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, Profile, EmailVerificationToken, CITICertificate


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    actions = ['mark_email_verified']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('email_verified_at', 'last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login']
    
    @admin.action(description="Mark email as verified")
    def mark_email_verified(self, request, queryset):
        updated = queryset.filter(email_verified_at__isnull=True).update(email_verified_at=timezone.now())
        self.message_user(request, f'{updated} user(s) marked as email verified.')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model."""
    
    list_display = ['user', 'student_id', 'department', 'no_show_count', 'is_banned']
    list_filter = ['is_banned', 'gender']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    raw_id_fields = ['user']


@admin.register(CITICertificate)
class CITICertificateAdmin(admin.ModelAdmin):
    """Admin interface for CITI certificates. Add certificates for researchers to enable protocol submission."""

    list_display = ['user', 'completion_date', 'expiration_date', 'is_valid', 'course_name', 'record_id']
    list_filter = ['expiration_date', 'completion_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'record_id']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    date_hierarchy = 'expiration_date'

    @admin.display(boolean=True)
    def is_valid(self, obj):
        return obj.is_valid if obj else False


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin interface for email verification tokens."""
    
    list_display = ['user', 'created_at', 'expires_at', 'used_at', 'is_valid']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__email']
    readonly_fields = ['token', 'created_at']




