"""
Migrate user data from SQLite backup to MySQL multi-database architecture

This script will:
1. Extract users, groups, profiles, and tenant relations from SQLite backup
2. Create/update tenants in eims_root database
3. Migrate auth users to eims_root (auth tables are shared)
4. Distribute user profiles and tenant relations to appropriate company databases
5. Preserve user-group relationships
"""
import os
import sys
import django
import sqlite3
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from eims_app.models.model_user import UserProfile, UserTenantRelation
from eims_app.models.model_tenant import Tenant

User = get_user_model()

# Find the most recent backup
backup_dir = 'backup'
backups = [f for f in os.listdir(backup_dir) if f.endswith('.sqlite3')]
backups.sort(reverse=True)
latest_backup = os.path.join(backup_dir, backups[0])

print(f"{'='*70}")
print(f"Migrating user data from SQLite backup")
print(f"Source: {latest_backup}")
print(f"{'='*70}\n")

# Connect to SQLite
sqlite_conn = sqlite3.connect(latest_backup)
sqlite_cursor = sqlite_conn.cursor()

# Statistics
stats = {
    'tenants_created': 0,
    'tenants_skipped': 0,
    'users_migrated': 0,
    'users_skipped': 0,
    'profiles_created': 0,
    'relations_created': 0,
    'groups_migrated': 0,
    'errors': []
}

def migrate_tenants():
    """Migrate tenant/company data to eims_root database"""
    print("[1/5] Migrating tenants...")
    
    sqlite_cursor.execute("SELECT * FROM eims_app_tenant;")
    tenants = sqlite_cursor.fetchall()
    
    # Get column names
    sqlite_cursor.execute("PRAGMA table_info(eims_app_tenant);")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in tenants:
        tenant_data = dict(zip(columns, row))
        
        try:
            # Map old codes to new codes
            code_mapping = {
                'COMPANY_A': 'dingce',
                'COMPANY_B': 'shengchang', 
                'COMPANY_C': 'jiachengda'
            }
            
            new_code = code_mapping.get(tenant_data['code'], tenant_data['code'].lower())
            
            tenant, created = Tenant.objects.using('default').get_or_create(
                code=new_code,
                defaults={
                    'name': tenant_data['name'],
                    'short_name': tenant_data.get('short_name', ''),
                    'contact_person': tenant_data.get('contact_person', ''),
                    'contact_phone': tenant_data.get('contact_phone', ''),
                    'contact_email': tenant_data.get('contact_email', ''),
                    'address': tenant_data.get('address', ''),
                    'is_active': tenant_data.get('is_active', True),
                    'remark': tenant_data.get('remark', '')
                }
            )
            
            if created:
                stats['tenants_created'] += 1
                print(f"  ✓ Created tenant: {tenant.name} ({tenant.code})")
            else:
                stats['tenants_skipped'] += 1
                # Update existing tenant info
                tenant.name = tenant_data['name']
                tenant.short_name = tenant_data.get('short_name', '')
                tenant.save()
                print(f"  ~ Updated tenant: {tenant.name} ({tenant.code})")
                
        except Exception as e:
            error_msg = f"Error migrating tenant {tenant_data.get('code')}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
    
    print(f"  Total: {stats['tenants_created']} created, {stats['tenants_skipped']} updated\n")


def migrate_groups():
    """Migrate user groups"""
    print("[2/5] Migrating user groups...")
    
    sqlite_cursor.execute("SELECT * FROM auth_group;")
    groups = sqlite_cursor.fetchall()
    
    for group_row in groups:
        group_id, group_name = group_row
        
        try:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                stats['groups_migrated'] += 1
                print(f"  ✓ Created group: {group_name}")
            else:
                print(f"  ~ Group exists: {group_name}")
        except Exception as e:
            error_msg = f"Error migrating group {group_name}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
    
    print(f"  Total: {stats['groups_migrated']} groups migrated\n")


def migrate_users():
    """Migrate users to eims_root database"""
    print("[3/5] Migrating users...")
    
    sqlite_cursor.execute("SELECT * FROM auth_user;")
    users = sqlite_cursor.fetchall()
    
    # Get column names
    sqlite_cursor.execute("PRAGMA table_info(auth_user);")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in users:
        user_data = dict(zip(columns, row))
        
        try:
            # Check if user already exists
            if User.objects.using('default').filter(username=user_data['username']).exists():
                stats['users_skipped'] += 1
                print(f"  ~ User exists: {user_data['username']}")
                continue
            
            # Create user
            user = User(
                username=user_data['username'],
                password=user_data['password'],  # Keep hashed password
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                email=user_data.get('email', ''),
                is_staff=user_data.get('is_staff', False),
                is_active=user_data.get('is_active', True),
                is_superuser=user_data.get('is_superuser', False),
                date_joined=user_data.get('date_joined'),
                last_login=user_data.get('last_login')
            )
            user.save(using='default')
            
            stats['users_migrated'] += 1
            print(f"  ✓ Migrated user: {user.username} ({'Superuser' if user.is_superuser else 'User'})")
            
        except Exception as e:
            error_msg = f"Error migrating user {user_data.get('username')}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
    
    print(f"  Total: {stats['users_migrated']} migrated, {stats['users_skipped']} skipped\n")


def migrate_user_groups():
    """Migrate user-group relationships"""
    print("[3.5/5] Migrating user-group relationships...")
    
    sqlite_cursor.execute("SELECT * FROM auth_user_groups;")
    user_groups = sqlite_cursor.fetchall()
    
    # Get column names to understand structure
    sqlite_cursor.execute("PRAGMA table_info(auth_user_groups);")
    ug_columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    count = 0
    for row in user_groups:
        # Handle different table structures (2 or 3 columns)
        if len(row) == 2:
            user_id, group_id = row
        elif len(row) == 3:
            # Has an id column: id, user_id, group_id
            _, user_id, group_id = row
        else:
            continue
        try:
            # Get original username from SQLite
            sqlite_cursor.execute("SELECT username FROM auth_user WHERE id=?", (user_id,))
            result = sqlite_cursor.fetchone()
            if not result:
                continue
            username = result[0]
            
            # Get original group name from SQLite
            sqlite_cursor.execute("SELECT name FROM auth_group WHERE id=?", (group_id,))
            result = sqlite_cursor.fetchone()
            if not result:
                continue
            group_name = result[0]
            
            # Find user and group in MySQL
            try:
                user = User.objects.using('default').get(username=username)
                group = Group.objects.get(name=group_name)
                
                if group not in user.groups.all():
                    user.groups.add(group)
                    count += 1
                    
            except User.DoesNotExist:
                pass  # User might not have been migrated
                
        except Exception as e:
            error_msg = f"Error linking user ID {user_id} to group ID {group_id}: {e}"
            stats['errors'].append(error_msg)
    
    print(f"  Total: {count} user-group relationships established\n")


def migrate_profiles_and_relations():
    """Migrate user profiles and tenant relations"""
    print("[4/5] Migrating user profiles and tenant relations...")
    
    # NOTE: Since company databases don't have tables yet, we'll store everything in default
    # Later, you can run a distribution script to move data to appropriate company databases
    db_alias = 'default'
    
    # Migrate user profiles
    sqlite_cursor.execute("SELECT * FROM eims_app_userprofile;")
    profiles = sqlite_cursor.fetchall()
    
    sqlite_cursor.execute("PRAGMA table_info(eims_app_userprofile);")
    profile_columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in profiles:
        profile_data = dict(zip(profile_columns, row))
        user_id = profile_data['user_id']
        
        try:
            # Get username from SQLite
            sqlite_cursor.execute("SELECT username FROM auth_user WHERE id=?", (user_id,))
            result = sqlite_cursor.fetchone()
            if not result:
                continue
            username = result[0]
            
            # Find user in MySQL
            try:
                user = User.objects.using('default').get(username=username)
            except User.DoesNotExist:
                continue
            
            # Determine target tenant
            tenant_id = profile_data.get('tenant_id')
            tenant_obj = None
            
            if tenant_id:
                # Get tenant code from SQLite
                sqlite_cursor.execute("SELECT code FROM eims_app_tenant WHERE id=?", (tenant_id,))
                result = sqlite_cursor.fetchone()
                if result:
                    old_code = result[0]
                    code_mapping = {
                        'COMPANY_A': 'dingce',
                        'COMPANY_B': 'shengchang',
                        'COMPANY_C': 'jiachengda'
                    }
                    new_code = code_mapping.get(old_code, old_code.lower())
                    
                    try:
                        tenant_obj = Tenant.objects.using('default').get(code=new_code)
                    except Tenant.DoesNotExist:
                        pass
            
            # Create or update profile
            profile, created = UserProfile.objects.using(db_alias).get_or_create(
                user=user,
                defaults={
                    'real_name': profile_data.get('real_name', ''),
                    'gender': profile_data.get('gender', ''),
                    'birthday': profile_data.get('birthday'),
                    'phone': profile_data.get('phone', ''),
                    'wechat': profile_data.get('wechat', ''),
                    'tenant': tenant_obj  # Set tenant if found
                }
            )
            
            if created:
                stats['profiles_created'] += 1
                tenant_info = f" -> {tenant_obj.name}" if tenant_obj else ""
                print(f"  ✓ Created profile for {username}{tenant_info}")
            
        except Exception as e:
            error_msg = f"Error migrating profile for user ID {user_id}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
    
    # Migrate user-tenant relations
    sqlite_cursor.execute("SELECT * FROM eims_app_usertenantrelation;")
    relations = sqlite_cursor.fetchall()
    
    sqlite_cursor.execute("PRAGMA table_info(eims_app_usertenantrelation);")
    relation_columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in relations:
        relation_data = dict(zip(relation_columns, row))
        user_id = relation_data['user_id']
        tenant_id = relation_data['tenant_id']
        
        try:
            # Get username from SQLite
            sqlite_cursor.execute("SELECT username FROM auth_user WHERE id=?", (user_id,))
            result = sqlite_cursor.fetchone()
            if not result:
                continue
            username = result[0]
            
            # Get tenant code from SQLite
            sqlite_cursor.execute("SELECT code FROM eims_app_tenant WHERE id=?", (tenant_id,))
            result = sqlite_cursor.fetchone()
            if not result:
                continue
            old_code = result[0]
            
            # Map to new code
            code_mapping = {
                'COMPANY_A': 'dingce',
                'COMPANY_B': 'shengchang',
                'COMPANY_C': 'jiachengda'
            }
            new_code = code_mapping.get(old_code, old_code.lower())
            
            # Find user and tenant in MySQL
            try:
                user = User.objects.using('default').get(username=username)
                tenant = Tenant.objects.using('default').get(code=new_code)
            except (User.DoesNotExist, Tenant.DoesNotExist):
                continue
            
            # Store in default database for now
            relation, created = UserTenantRelation.objects.using(db_alias).get_or_create(
                user=user,
                tenant=tenant,
                defaults={
                    'is_primary': relation_data.get('is_primary', False),
                    'remark': relation_data.get('remark', ''),
                }
            )
            
            if created:
                stats['relations_created'] += 1
                print(f"  ✓ Created relation: {username} <-> {tenant.name} ({'Primary' if relation.is_primary else 'Secondary'})")
            
        except Exception as e:
            error_msg = f"Error migrating relation for user ID {user_id}, tenant ID {tenant_id}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
    
    print(f"  Total: {stats['profiles_created']} profiles, {stats['relations_created']} relations\n")


def print_summary():
    """Print migration summary"""
    print(f"\n{'='*70}")
    print(f"Migration Summary")
    print(f"{'='*70}")
    print(f"Tenants:        {stats['tenants_created']} created, {stats['tenants_skipped']} updated")
    print(f"User Groups:    {stats['groups_migrated']} migrated")
    print(f"Users:          {stats['users_migrated']} migrated, {stats['users_skipped']} skipped")
    print(f"Profiles:       {stats['profiles_created']} created")
    print(f"Relations:      {stats['relations_created']} created")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")
    
    print(f"{'='*70}\n")


if __name__ == '__main__':
    try:
        migrate_tenants()
        migrate_groups()
        migrate_users()
        migrate_user_groups()
        migrate_profiles_and_relations()
        print_summary()
        
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Verify users can login with their original passwords")
        print("2. Check that users are properly assigned to companies")
        print("3. Test root admin can view all users across all companies")
        
    except Exception as e:
        print(f"\n✗ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sqlite_conn.close()
