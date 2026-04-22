import os
import sys

sys.path.insert(0, 'e:\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS2026.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from eims_app.models import Tenant, UserProfile

print("=" * 60)
print("Testing admin login")
print("=" * 60)

# 1. Check if user exists
try:
    user = User.objects.get(username='admin')
    print(f"✅ User found: {user.username}")
    print(f"   - is_active: {user.is_active}")
    print(f"   - is_staff: {user.is_staff}")
    print(f"   - is_superuser: {user.is_superuser}")
    print(f"   - password hash: {user.password[:30]}...")
except User.DoesNotExist:
    print("❌ User 'admin' does not exist")
    sys.exit(1)

# 2. Test authentication
print("\nTesting authentication with 'Admin@123'...")
auth_user = authenticate(username='admin', password='Admin@123')
if auth_user:
    print(f"✅ Authentication successful: {auth_user.username}")
else:
    print("❌ Authentication failed")
    sys.exit(1)

# 3. Check UserProfile
print("\nChecking UserProfile...")
try:
    profile = UserProfile.objects.get(user=user)
    print(f"✅ UserProfile found")
    print(f"   - tenant: {profile.tenant}")
except UserProfile.DoesNotExist:
    print("⚠️ No UserProfile found (will be created on login)")

# 4. Check available tenants
print("\nAvailable tenants:")
tenants = Tenant.objects.filter(is_active=True)
if tenants.exists():
    for tenant in tenants:
        print(f"   - ID: {tenant.id}, Name: {tenant.name}, Code: {tenant.code}")
else:
    print("   ⚠️ No active tenants found!")
    print("   This will cause login to fail with '您还没有被分配到任何公司'")

print("\n" + "=" * 60)
print("Summary: Password is correct, check Tenant configuration")
print("=" * 60)
