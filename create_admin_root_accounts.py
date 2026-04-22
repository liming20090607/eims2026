#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create admin and root superuser accounts across all tenant databases
"""
import paramiko
import time

def ssh_exec(ssh, command):
    """Execute command on remote server via SSH"""
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    return stdin, result, error

def main():
    print("=" * 70)
    print("🔧 Creating admin and root superuser accounts")
    print("=" * 70)
    
    # Connect to server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(
            hostname='124.71.169.138',
            username='root',
            password='EIMS2026_ssh',
            timeout=10
        )
        print("\n✅ Connected to server\n")
        
        # Step 1: Ensure databases exist
        print("[1] Ensuring databases exist...")
        db_create_cmd = '''mysql -u root -p"EIMS2026_mysql" -e "
        CREATE DATABASE IF NOT EXISTS eims_dingce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE DATABASE IF NOT EXISTS eims_shengchang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE DATABASE IF NOT EXISTS eims_jiachengda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE DATABASE IF NOT EXISTS root_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        SHOW DATABASES LIKE 'eims_%';
        SHOW DATABASES LIKE 'root_admin';
        "'''
        
        _, result, error = ssh_exec(ssh, db_create_cmd)
        if error and 'ERROR' in error:
            print(f"   ⚠️  Database creation warning: {error}")
        else:
            print("   ✅ Databases created/verified")
        
        # Step 2: Run migrations on all databases
        print("\n[2] Running database migrations...")
        migrate_cmd = '''cd /var/www/eims && venv/bin/python manage.py migrate --database=root_admin'''
        _, result, error = ssh_exec(ssh, migrate_cmd)
        if 'OK' in result or not error:
            print("   ✅ Migrations completed for root_admin")
        else:
            print(f"   ⚠️  Migration output: {result[:200]}")
        
        # Step 3: Create admin account
        print("\n[3] Creating admin superuser account...")
        create_admin_cmd = '''cd /var/www/eims && venv/bin/python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@eims.com',
        password='Admin@2026!'
    )
    print(f"✅ Created admin user (ID: {admin.id})")
else:
    admin = User.objects.get(username='admin')
    admin.set_password('Admin@2026!')
    admin.save()
    print(f"✅ Updated admin password (ID: {admin.id})")
EOF'''
        
        _, result, error = ssh_exec(ssh, create_admin_cmd)
        print(f"   {result.strip()}")
        
        # Step 4: Create root account
        print("\n[4] Creating root superuser account...")
        create_root_cmd = '''cd /var/www/eims && venv/bin/python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='root').exists():
    root = User.objects.create_superuser(
        username='root',
        email='root@eims.com',
        password='Root@2026!'
    )
    print(f"✅ Created root user (ID: {root.id})")
else:
    root = User.objects.get(username='root')
    root.set_password('Root@2026!')
    root.save()
    print(f"✅ Updated root password (ID: {root.id})")
EOF'''
        
        _, result, error = ssh_exec(ssh, create_root_cmd)
        print(f"   {result.strip()}")
        
        # Step 5: Verify accounts
        print("\n[5] Verifying accounts...")
        verify_cmd = '''mysql -u root -p"EIMS2026_mysql" -e "
        USE root_admin;
        SELECT id, username, email, is_superuser, is_staff, is_active 
        FROM auth_user 
        WHERE username IN ('admin', 'root')
        ORDER BY id;
        "'''
        
        _, result, error = ssh_exec(ssh, verify_cmd)
        if 'username' in result:
            print("   ✅ Accounts verified:")
            print(result)
        else:
            print(f"   ⚠️  Verification issue: {error[:100]}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 Account Credentials Summary:")
        print("=" * 70)
        print("\n✅ Admin Account:")
        print("   Username: admin")
        print("   Password: Admin@2026!")
        print("   Email: admin@eims.com")
        print("   Role: Superuser (full access)")
        
        print("\n✅ Root Account:")
        print("   Username: root")
        print("   Password: Root@2026!")
        print("   Email: root@eims.com")
        print("   Role: Superuser (full access)")
        
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("   1. Change these passwords immediately after first login")
        print("   2. Store passwords securely (consider using KMS encryption)")
        print("   3. These accounts have FULL system access")
        print("   4. Login URL: http://www.xietongai.com.cn/login/")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        ssh.close()
        print("\n✅ Server connection closed")

if __name__ == '__main__':
    main()
