#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-refresh and debug until login page is accessible
Automatically detects issues and fixes them
"""
import paramiko
import time
import sys

SSH_HOST = '39.106.41.239'
SSH_USER = 'root'
SSH_PASS = 'EIMS2026_root'

def ssh_exec(ssh, command, timeout=10):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_status, output, error

def check_login_page(ssh):
    """Check if login page is accessible"""
    try:
        # Test via Nginx (port 80)
        _, output, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/')
        nginx_code = output.strip()
        
        # Test via Gunicorn directly (port 8000)
        _, output, _ = ssh_exec(ssh, 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8000/login/')
        gunicorn_code = output.strip()
        
        return nginx_code, gunicorn_code
    except Exception as e:
        return None, str(e)

def fix_gunicorn_module_error(ssh):
    """Fix ModuleNotFoundError: No module named 'eims.wsgi'"""
    print("\n🔧 Fixing Gunicorn module error...")
    
    # Check current directory structure
    _, output, _ = ssh_exec(ssh, 'ls -la /var/www/eims/')
    print(f"  Directory listing:\n{output}")
    
    # Check if wsgi.py exists
    _, wsgi_exists, _ = ssh_exec(ssh, 'test -f /var/www/eims/eims/wsgi.py && echo "EXISTS" || echo "MISSING"')
    print(f"  wsgi.py status: {wsgi_exists}")
    
    # Check __init__.py
    _, init_exists, _ = ssh_exec(ssh, 'test -f /var/www/eims/eims/__init__.py && echo "EXISTS" || echo "MISSING"')
    print(f"  __init__.py status: {init_exists}")
    
    # The issue is likely that Gunicorn is running from wrong directory
    # Let's restart it with correct working directory
    print("  Restarting Gunicorn with correct configuration...")
    
    # Kill existing Gunicorn
    ssh_exec(ssh, 'pkill -9 gunicorn || true')
    time.sleep(2)
    
    # Start Gunicorn from correct directory
    start_cmd = '''cd /var/www/eims && nohup /var/www/eims/venv/bin/gunicorn \
        --bind 127.0.0.1:8000 \
        --workers 5 \
        --timeout 120 \
        --chdir /var/www/eims \
        eims.wsgi:application \
        --access-logfile /var/www/eims/logs/gunicorn_access.log \
        --error-logfile /var/www/eims/logs/gunicorn_error.log > /dev/null 2>&1 &'''
    
    ssh_exec(ssh, start_cmd)
    time.sleep(5)
    
    # Verify Gunicorn started
    _, count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
    print(f"  ✅ Gunicorn workers: {count}")
    
    return int(count) > 0

def fix_nginx(ssh):
    """Restart Nginx if needed"""
    print("\n🔧 Checking Nginx...")
    
    _, output, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
    nginx_count = int(output.strip())
    
    if nginx_count == 0:
        print("  Starting Nginx...")
        ssh_exec(ssh, 'nginx')
        time.sleep(2)
        _, output, _ = ssh_exec(ssh, 'pgrep -c nginx || echo "0"')
        print(f"  ✅ Nginx processes: {output.strip()}")
    else:
        print(f"  ✅ Nginx already running ({nginx_count} processes)")

def fix_mysql(ssh):
    """Ensure MySQL is running"""
    print("\n🔧 Checking MySQL...")
    
    _, output, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
    if output.strip() != 'active':
        print("  Starting MySQL...")
        ssh_exec(ssh, 'systemctl start mysqld')
        time.sleep(3)
        _, output, _ = ssh_exec(ssh, 'systemctl is-active mysqld')
        print(f"  ✅ MySQL status: {output.strip()}")
    else:
        print("  ✅ MySQL already running")

def auto_refresh_until_login(max_attempts=10):
    """Main function: Auto-refresh and debug until login page works"""
    print("=" * 70)
    print("🔄 Auto-Refresh & Debug System")
    print("   Target: Make login page accessible")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\n📡 Connecting to server {SSH_HOST}...")
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
        print("✅ Connected successfully\n")
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n{'='*70}")
            print(f"📊 Attempt {attempt}/{max_attempts}")
            print(f"{'='*70}")
            
            # Check services
            fix_mysql(ssh)
            fix_nginx(ssh)
            
            # Check Gunicorn
            _, gunicorn_count, _ = ssh_exec(ssh, 'pgrep -c gunicorn || echo "0"')
            gunicorn_workers = int(gunicorn_count.strip())
            
            if gunicorn_workers < 2:
                print(f"\n⚠️  Gunicorn has only {gunicorn_workers} workers")
                success = fix_gunicorn_module_error(ssh)
                if not success:
                    print("  ❌ Failed to fix Gunicorn, checking logs...")
                    _, logs, _ = ssh_exec(ssh, 'tail -20 /var/www/eims/logs/gunicorn_error.log')
                    print(f"  Recent errors:\n{logs}")
            else:
                print(f"  ✅ Gunicorn healthy ({gunicorn_workers} workers)")
            
            # Test login page
            print(f"\n🧪 Testing login page...")
            nginx_code, gunicorn_code = check_login_page(ssh)
            
            print(f"  Nginx (port 80): HTTP {nginx_code}")
            print(f"  Gunicorn (port 8000): HTTP {gunicorn_code}")
            
            # Check if successful
            if nginx_code in ['200', '302']:
                print(f"\n{'='*70}")
                print("✅ SUCCESS! Login page is accessible!")
                print(f"{'='*70}")
                
                # Get page content to verify
                _, html, _ = ssh_exec(ssh, 'curl -s http://127.0.0.1:80/login/ | head -50')
                if '登录' in html or 'Login' in html:
                    print("✅ Login page content verified")
                
                print(f"\n🌐 You can now access:")
                print(f"   http://{SSH_HOST}/login/")
                print(f"   http://www.xietongai.com.cn/login/")
                return True
            
            elif nginx_code == '502':
                print("  ⚠️  502 Bad Gateway - Gunicorn issue detected")
                fix_gunicorn_module_error(ssh)
            
            elif nginx_code in ['000', None]:
                print("  ⚠️  Connection refused - Service not responding")
            
            else:
                print(f"  ⚠️  Unexpected status code: {nginx_code}")
            
            # Wait before next attempt
            if attempt < max_attempts:
                wait_time = 5
                print(f"\n⏳ Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)
        
        print(f"\n{'='*70}")
        print(f"❌ Failed after {max_attempts} attempts")
        print(f"{'='*70}")
        print("\nPlease check server manually or contact support.")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        ssh.close()
        print("\n🔒 SSH connection closed")

if __name__ == '__main__':
    success = auto_refresh_until_login(max_attempts=10)
    sys.exit(0 if success else 1)
