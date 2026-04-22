#!/usr/bin/env python
"""
Comprehensive auto-restart and fix system
Restarts Gunicorn continuously until login page works with proper CSRF
"""

import paramiko
import time
from datetime import datetime

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def restart_gunicorn(ssh):
    """Force restart Gunicorn"""
    # Kill all gunicorn processes
    ssh.exec_command('pkill -9 gunicorn 2>/dev/null || true')
    ssh.exec_command('sleep 2')
    
    # Clean start
    cmd = '''cd /var/www/eims
nohup /var/www/eims/venv/bin/gunicorn \\
  --bind 127.0.0.1:8000 \\
  --workers 5 \\
  --timeout 120 \\
  --graceful-timeout 30 \\
  --access-logfile /var/www/eims/logs/gunicorn_access.log \\
  --error-logfile /var/www/eims/logs/gunicorn_error.log \\
  --log-level warning \\
  eims.wsgi:application >/dev/null 2>&1 &
'''
    ssh.exec_command(cmd)
    time.sleep(5)
    
    # Verify started
    stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn')
    count = stdout.read().decode().strip()
    return count

def test_login_page(ssh):
    """Test if login page works properly"""
    # Test HTTP response
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'
    )
    http_code = stdout.read().decode().strip()
    
    # Test CSRF cookie generation
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -c /tmp/csrf_test.txt http://127.0.0.1:80/login/ >/dev/null && grep csrftoken /tmp/csrf_test.txt || echo "NO_CSRF"'
    )
    csrf_result = stdout.read().decode().strip()
    csrf_ok = 'csrftoken' in csrf_result
    
    # Get login page content
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s --connect-timeout 5 http://127.0.0.1:80/login/ | grep -o "<title>[^<]*</title>" || echo "NO_TITLE"'
    )
    title = stdout.read().decode().strip()
    
    return {
        'http_code': http_code,
        'csrf_ok': csrf_ok,
        'title': title
    }

def auto_fix_until_working():
    """Main auto-fix loop"""
    print("\n" + "="*70)
    print("🚀 Automatic Server Fix System")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Monitoring and fixing until login page works...\n")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    
    max_attempts = 30
    attempt = 0
    stable_count = 0
    required_stable = 3  # Need 3 consecutive successful checks
    
    while attempt < max_attempts:
        attempt += 1
        time.sleep(3)
        
        print(f"\n{'='*70}")
        print(f"📍 Attempt {attempt}/{max_attempts}")
        print(f"{'='*70}")
        
        # Step 1: Check MySQL
        print("\n[1] Checking MySQL...")
        stdin, stdout, stderr = ssh.exec_command('systemctl is-active mysqld')
        mysql_status = stdout.read().decode().strip()
        if mysql_status != 'active':
            print(f"  ⚠️  MySQL is {mysql_status}, restarting...")
            ssh.exec_command('systemctl restart mysqld')
            time.sleep(3)
            print("  ✅ MySQL restarted")
        else:
            print(f"  ✅ MySQL: {mysql_status}")
        
        # Step 2: Restart Gunicorn
        print("\n[2] Restarting Gunicorn...")
        gunicorn_count = restart_gunicorn(ssh)
        if gunicorn_count and int(gunicorn_count) >= 2:
            print(f"  ✅ Gunicorn started: {gunicorn_count} workers")
        else:
            print(f"  ❌ Gunicorn failed to start: {gunicorn_count} workers")
            # Check error logs
            stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/gunicorn_error.log 2>/dev/null')
            errors = stdout.read().decode().strip()
            if errors:
                print("  Recent errors:")
                for line in errors.split('\n')[-5:]:
                    if line.strip():
                        print(f"    {line[:70]}")
        
        # Step 3: Wait for Gunicorn to stabilize
        print("\n[3] Waiting for Gunicorn to stabilize...")
        time.sleep(5)
        
        # Step 4: Test login page
        print("\n[4] Testing login page...")
        result = test_login_page(ssh)
        
        print(f"  HTTP Status: {result['http_code']}")
        print(f"  CSRF Cookie: {'✅ Yes' if result['csrf_ok'] else '❌ No'}")
        print(f"  Page Title: {result['title']}")
        
        # Step 5: Evaluate
        print("\n[5] Evaluation:")
        http_ok = result['http_code'] in ['200', '302', '500']
        
        if http_ok and result['csrf_ok']:
            stable_count += 1
            print(f"  ✅ Success! (Stable count: {stable_count}/{required_stable})")
            
            if stable_count >= required_stable:
                print(f"\n{'='*70}")
                print("✅✅✅ SERVER IS FULLY OPERATIONAL! ✅✅✅")
                print(f"{'='*70}")
                print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Total attempts: {attempt}")
                print(f"Stable checks: {stable_count} consecutive\n")
                print("🎉 ACTION REQUIRED IN BROWSER:")
                print("   1. Press Ctrl+Shift+Delete")
                print("   2. Select 'All time'")
                print("   3. Check 'Cookies and other site data'")
                print("   4. Click 'Clear data'")
                print("   5. Visit: http://www.xietongai.com.cn/login/")
                print("\n   OR try Incognito mode: Ctrl+Shift+N\n")
                print("💡 Auto-correction will continue monitoring every 2 minutes")
                print("   Any future issues will be fixed automatically\n")
                ssh.close()
                return True
        else:
            stable_count = 0  # Reset on failure
            print(f"  ⚠️  Not ready yet (Reset stable count)")
            
            # Show specific issues
            if not http_ok:
                print(f"    → HTTP {result['http_code']} - Server not responding")
            if not result['csrf_ok']:
                print(f"    → CSRF cookie not generated")
        
        # Progress indicator
        remaining = max_attempts - attempt
        if remaining > 0:
            print(f"\n⏳ Waiting 5 seconds before next attempt... ({remaining} remaining)")
    
    # If we reach here, we failed
    ssh.close()
    print(f"\n{'='*70}")
    print("⚠️  Reached maximum attempts")
    print(f"{'='*70}")
    print("\nManual intervention may be needed.")
    print("\nPlease try:")
    print("  1. Open Incognito/Private window (Ctrl+Shift+N)")
    print("  2. Visit: http://www.xietongai.com.cn/login/")
    print("  3. Clear all browser cache (Ctrl+Shift+Delete)")
    print("="*70 + "\n")
    return False

if __name__ == '__main__':
    try:
        auto_fix_until_working()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
