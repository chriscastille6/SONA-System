"""
Management command to update Jon Murphy's email address.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Update Jon Murphy email to jonathan.murphy@nicholls.edu'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Updating Jon Murphy email address...\n')
        
        # Find Jon Murphy by various possible emails
        jon_murphy = User.objects.filter(
            email__icontains='murphy'
        ).filter(role='irb_member').first()
        
        if not jon_murphy:
            self.stdout.write(self.style.ERROR('✗ Jon Murphy account not found'))
            return
        
        old_email = jon_murphy.email
        new_email = 'jonathan.murphy@nicholls.edu'
        
        if old_email == new_email:
            self.stdout.write(self.style.SUCCESS(f'✓ Email is already correct: {new_email}'))
            return
        
        # Check if new email already exists
        if User.objects.filter(email=new_email).exclude(id=jon_murphy.id).exists():
            self.stdout.write(self.style.ERROR(f'✗ Email {new_email} already exists for another user'))
            return
        
        jon_murphy.email = new_email
        jon_murphy.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Updated email from {old_email} to {new_email}'))
        self.stdout.write(f'\nJon Murphy can now log in with:')
        self.stdout.write(f'  Email: {new_email}')
        self.stdout.write(f'  Password: temp_password_change_me')
