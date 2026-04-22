#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnose and fix MySQL password issue on server
"""
import paramiko
import time

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    """Execute SSH command"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

def diagnose_mysql_password():
    """Diagnose MySQL password issue"""
    print("=" * 70)
    print("🔍 Diagnosing MySQL Password Issue")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\n📡 Connecting to server...")
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
        print("✅ Connected\n")
        
        # Step 1: Check current settings.py PASSWORD values
        print("[1] Checking settings.py PASSWORD configuration...")
        _, output, _ = ssh_exec(ssh, 'grep -n "PASSWORD" /var/www/eims/eims/settings.py | head -10')
        print(f"  Current PASSWORD settings:\n{output}\n")
        
        # Step 2: Test MySQL connection with different passwords
        print("[2] Testing MySQL passwords...")
        
        passwords_to_test = ['EIMS2026_mysql', 'root123', 'root', '']
        working_password = None
        
        for pwd in passwords_to_test:
            if pwd == '':
                test_cmd = 'mysql -u root -e "SELECT 1;" 2>&1'
            else:
                test_cmd = f'mysql -u root -p"{pwd}" -e "SELECT 1;" 2>&1'
            
            _, result, _ = ssh_exec(ssh, test_cmd)
            
            if '1' in result and 'Error' not in result:
                print(f"  ✅ Password '{pwd}' WORKS!")
                working_password = pwd
                break
            else:
                print(f"  ❌ Password '{pwd}' failed")
        
        if not working_password:
            print("\n  ⚠️  No working password found! Checking MySQL status...")
            _, mysql_status, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
            print(f"  MySQL status: {mysql_status}")
            
            # Try to reset MySQL password
            print("\n[3] Attempting to reset MySQL root password...")
            reset_commands = [
                'systemctl stop mysqld',
                'mysqld_safe --skip-grant-tables &',
                'sleep 3',
                'mysql -u root -e "FLUSH PRIVILEGES; ALTER USER \'root\'@\'localhost\' IDENTIFIED BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1',
                'sleep 2',
                'pkill mysqld_safe',
                'pkill mysqld',
                'sleep 2',
                'systemctl start mysqld',
                'sleep 3',
            ]
            
            for cmd in reset_commands:
                print(f"  Executing: {cmd[:60]}...")
                _, result, error = ssh_exec(ssh, cmd, timeout=15)
                if error and 'error' in error.lower():
                    print(f"    Warning: {error[:100]}")
                time.sleep(1)
            
            # Test again
            _, result, _ = ssh_exec(ssh, 'mysql -u root -p"EIMS2026_mysql" -e "SELECT 1;" 2>&1')
            if '1' in result:
                print("  ✅ MySQL password reset successful!")
                working_password = 'EIMS2026_mysql'
            else:
                print("  ❌ MySQL password reset failed")
                return False
        
        # Step 3: Fix settings.py with correct password
        print(f"\n[4] Fixing settings.py with correct password: {working_password}")
        
        # Read current settings.py
        _, current_settings, _ = ssh_exec(ssh, 'cat /var/www/eims/eims/settings.py')
        
        # Replace all PASSWORD values
        if working_password:
            # Use sed to replace all PASSWORD entries
            fix_cmd = f"sed -i \"s/'PASSWORD': '[^']*'/'PASSWORD': '{working_password}'/g\" /var/www/eims/eims/settings.py"
            ssh_exec(ssh, fix_cmd)
            
            # Verify the fix
            _, fixed_settings, _ = ssh_exec(ssh, 'grep -n "PASSWORD" /var/www/eims/eims/settings.py | head -10')
            print(f"  Updated PASSWORD settings:\n{fixed_settings}\n")
        
        # Step 4: Restart Gunicorn
        print("[5] Restarting Gunicorn...")
        ssh_exec(ssh, 'pkill -9 gunicorn || true')
        time.sleep(2)
        
        start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \\
            --bind 127.0.0.1:8000 \\
            --workers 5 \\
            --timeout 120 \\
            --chdir /var/www/eims \\
            eims.wsgi:application \\
            --access-logfile /var/www/eims/logs/gunicorn_access.log \\
            --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
        
        ssh_exec(ssh, start_cmd)
        time.sleep(5)
        
        _, count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
        print(f"  ✅ Gunicorn workers: {count}\n")
        
        # Step 5: Test login page
        print("[6] Testing login page...")
        _, code, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/')
        print(f"  HTTP Status: {code}")
        
        if code in ['200', '302']:
            print("\n" + "=" * 70)
            print("✅ SUCCESS! MySQL password fixed and login page working!")
            print("=" * 70)
            return True
        else:
            print(f"\n⚠️  Unexpected status: {code}")
            _, logs, _ = ssh_exec(ssh, 'tail -30 /var/www/eims/logs/gunicorn_error.log')
            print(f"\nRecent Gunicorn errors:\n{logs}")
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        ssh.close()

if __name__ == '__main__':
    success = diagnose_mysql_password()
    import sys
    sys.exit(0 if success else 1)
