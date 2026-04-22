"""
Check existing users in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*80)
print("Existing Users in Database:")
print("="*80)

users = User.objects.all()
if users.exists():
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Is Active: {user.is_active}")
        print(f"Date Joined: {user.date_joined}")
        print("-" * 80)
else:
    print("\nNo users found in database!")

print("\n" + "="*80)
print("To login, use one of the usernames listed above")
print("="*80)
