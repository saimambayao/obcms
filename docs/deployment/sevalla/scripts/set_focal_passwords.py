#!/usr/bin/env python3
"""
Set passwords for all MOA focal users.
Run from project root: python3 set_focal_passwords.py
"""
import os
import sys
import django

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from coordination.models import Organization

User = get_user_model()

print("=" * 80)
print("Setting passwords for MOA focal users")
print("=" * 80)

# Get all focal users
focal_users = User.objects.filter(username__startswith='focal.')
print(f"\nFound {focal_users.count()} focal users")

updated_count = 0
for user in focal_users:
    # Extract acronym from username (e.g., "focal.MAFAR" -> "MAFAR")
    acronym = user.username.replace('focal.', '')
    password = f"{acronym}.focal123"

    # Set password using Django's password hashing
    user.set_password(password)
    user.save(update_fields=['password'])

    print(f"✓ {user.username} | Password: {password}")
    updated_count += 1

print("\n" + "=" * 80)
print(f"Successfully updated {updated_count} focal user passwords!")
print("=" * 80)
print("\nYou can now log in with:")
print("  Username: focal.[ACRONYM]")
print("  Password: [ACRONYM].focal123")
print("\nExample: focal.MAFAR / MAFAR.focal123")
