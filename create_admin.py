#!/usr/bin/env python
"""
Quick script to create admin user for Railway deployment.
Run with: railway run python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Create admin if doesn't exist
email = 'admin@nicholls.edu'
if not User.objects.filter(email=email).exists():
    admin = User.objects.create_superuser(
        email=email,
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role='admin'
    )
    print(f'✅ Created superuser: {email}')
    print(f'   Password: admin123')
    print(f'   Access at: https://nichollsirb.up.railway.app/admin/')
else:
    print(f'⚠️  Admin user {email} already exists')

