import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserProfile, Tenant

print("="*80)
print("Checking Chen Lianhua's account status")
print("="*80)

# Check if user exists
user = User.objects.filter(username='jcdry001').first()
if user:
    print(f"\n✓ User account found:")
    print(f"  Username: {user.username}")
    print(f"  Name: {user.get_full_name()}")
    print(f"  Active: {user.is_active}")
    
    # Check UserProfile
    profile = UserProfile.objects.filter(user=user).first()
    if profile:
        print(f"\n✓ UserProfile found:")
        if profile.tenant:
            print(f"  Tenant: {profile.tenant.name} (ID: {profile.tenant.id})")
            print(f"\n✓ Login should work now!")
        else:
            print(f"  ⚠ WARNING: No tenant assigned!")
    else:
        print(f"\n⚠ WARNING: No UserProfile found!")
else:
    print(f"\n⚠ User account 'jcdry001' NOT found!")
    print(f"  Need to run fix_chenlianhua_login.py script")

print("\n" + "="*80)
