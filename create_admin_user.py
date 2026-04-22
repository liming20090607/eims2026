import os
import sys

sys.path.insert(0, 'e:\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS2026.settings')

import django
django.setup()

from django.contrib.auth.models import User

# Create or get admin user
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@eims.com',
        'is_staff': True,
        'is_superuser': True
    }
)

print(f'Admin user: {"created" if created else "exists"}')

# Set password
user.set_password('Admin@123')
user.save()

print('✅ Password set to Admin@123')
print(f'User: {user.username}, Active: {user.is_active}, Staff: {user.is_staff}')
