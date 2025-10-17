"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model."""
    
    list_display = ['user', 'student_id', 'department', 'no_show_count', 'is_banned']
    list_filter = ['is_banned', 'gender']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    raw_id_fields = ['user']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin interface for email verification tokens."""
    
    list_display = ['user', 'created_at', 'expires_at', 'used_at', 'is_valid']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__email']
    readonly_fields = ['token', 'created_at']




