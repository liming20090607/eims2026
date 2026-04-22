"""
Create Superuser for Root Admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if User.objects.filter(username='root_admin').exists():
    print("Superuser 'root_admin' already exists!")
else:
    # Create superuser
    user = User.objects.create_superuser(
        username='root_admin',
        email='admin@eims.com',
        password='admin123456'
    )
    print(f"✓ Superuser created successfully!")
    print(f"  Username: root_admin")
    print(f"  Email: admin@eims.com")
    print(f"  Password: admin123456")
    print(f"\n⚠️  Please change the password after first login!")
