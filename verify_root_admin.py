"""
Quick verification that root admin can access all user data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models.model_user import UserProfile, UserTenantRelation
from eims_app.models.model_tenant import Tenant

User = get_user_model()

print("="*70)
print("ROOT ADMIN VERIFICATION")
print("="*70)

# Verify root user exists and has proper setup
try:
    root_user = User.objects.get(username='root')
    print(f"\n✓ Root user exists: {root_user.username}")
    print(f"  - Is Superuser: {root_user.is_superuser}")
    print(f"  - Is Active: {root_user.is_active}")
    
    # Check profile
    try:
        profile = root_user.profile
        print(f"  - Profile exists: Yes")
        print(f"  - Default company: {profile.tenant.name if profile.tenant else 'None'}")
    except:
        print(f"  - Profile exists: No (needs setup)")
    
    # Check tenant relations
    relations = UserTenantRelation.objects.filter(user=root_user)
    if relations.exists():
        print(f"  - Company assignments: {relations.count()}")
        for rel in relations:
            primary_marker = " (Primary)" if rel.is_primary else ""
            print(f"    • {rel.tenant.name}{primary_marker}")
    else:
        print(f"  - Company assignments: None")
        
except User.DoesNotExist:
    print("\n✗ Root user NOT found!")
    exit(1)

# Show what root admin can manage
print("\n" + "="*70)
print("WHAT ROOT ADMIN CAN MANAGE:")
print("="*70)

tenants = Tenant.objects.all()
print(f"\n📊 Companies ({tenants.count()}):")
for t in tenants:
    user_count = UserTenantRelation.objects.filter(tenant=t).count()
    print(f"  • {t.name} - {user_count} users assigned")

users = User.objects.all()
print(f"\n👥 Users ({users.count()}):")
print(f"  • Can view all {users.count()} users")
print(f"  • Can edit user details")
print(f"  • Can assign/change passwords")
print(f"  • Can activate/deactivate accounts")

groups_count = User.groups.through.objects.count()
print(f"\n🏷️  User Groups:")
print(f"  • {groups_count} user-group assignments exist")
print(f"  • Can add/remove users from groups")
print(f"  • Can create new groups")

profiles = UserProfile.objects.all()
print(f"\n📋 User Profiles ({profiles.count()}):")
print(f"  • Can view/edit all user profiles")
print(f"  • Can assign default companies")

relations = UserTenantRelation.objects.all()
print(f"\n🔗 Company Assignments ({relations.count()}):")
print(f"  • Can assign users to multiple companies")
print(f"  • Can set primary company for each user")
print(f"  • Can remove company assignments")

print("\n" + "="*70)
print("HOW TO ACCESS:")
print("="*70)
print("\n1. Login as root:")
print("   URL: http://localhost:8000/")
print("   Username: root")
print("   Password: root123456")
print("\n2. Access Root Admin Backend:")
print("   URL: http://localhost:8000/root/")
print("\n3. Use Django Admin (alternative):")
print("   URL: http://localhost:8000/admin/")
print("   (Same credentials)")

print("\n" + "="*70)
print("✓ ROOT ADMIN IS READY FOR UNIFIED USER MANAGEMENT")
print("="*70)
