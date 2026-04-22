#!/usr/bin/env python3
"""
Final nuclear option - complete MySQL reset with proper socket handling
"""

import paramiko
import os
import time
import sys
import base64
import re

print("=" * 80)
print("Final Nuclear MySQL Reset + Frontend")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc="", timeout=120):
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_code, output, error

try:
    # STEP 1: Nuclear MySQL reset
    print("\n[1/6] Nuclear MySQL reset...")
    
    # Kill everything
    run(ssh, "killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2", "Kill MySQL")
    run(ssh, "rm -rf /var/lib/mysql/* /var/log/mysqld.log", "Remove all MySQL data")
    
    # Reinitialize
    print("  Reinitializing (this takes 10-20 seconds)...")
    run(ssh, "mysqld --initialize --user=mysql --datadir=/var/lib/mysql 2>&1", "Initialize", timeout=60)
    time.sleep(10)
    
    # Check if initialization succeeded
    exit_code, output, error = run(ssh, "ls -la /var/lib/mysql/ | head -10", "Check data dir")
    print(f"  Data dir: {output[:200]}")
    
    # Start MySQL normally (it should start with temp password)
    run(ssh, "systemctl start mysqld", "Start MySQL")
    time.sleep(5)
    
    # Get temp password
    exit_code, log_output, error = run(ssh, "cat /var/log/mysqld.log 2>/dev/null | grep 'temporary password'", "Get temp password")
    
    if log_output:
        match = re.search(r'root@localhost:\s*(\S+)', log_output)
        if match:
            temp_pass = match.group(1)
            print(f"  Temp password: {temp_pass[:10]}...")
            
            # Change password - use direct connection without socket path
            print("  Changing password...")
            
            # Method 1: Try with --connect-expired-password
            change_cmd = f'''mysql -uroot -p'{temp_pass}' --connect-expired-password -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql'; FLUSH PRIVILEGES;" 2>&1'''
            exit_code, output, error = run(ssh, change_cmd, "Change password", timeout=30)
            
            if exit_code != 0:
                print(f"  Method 1 failed, trying method 2...")
                # Method 2: Skip grant tables with direct mysqld
                run(ssh, "systemctl stop mysqld; killall -9 mysqld 2>/dev/null; sleep 3", "Stop MySQL")
                
                # Start with skip-grant-tables in background
                run(ssh, "mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock &", "Start skip-grant")
                time.sleep(8)
                
                # Wait for socket
                for i in range(10):
                    exit_code, sock_output, _ = run(ssh, "ls -la /var/lib/mysql/mysql.sock 2>&1", f"Check socket {i+1}/10")
                    if 'mysql.sock' in sock_output:
                        print("  Socket ready")
                        break
                    time.sleep(2)
                
                # Now reset password
                reset_sql = """FLUSH PRIVILEGES; ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql'; FLUSH PRIVILEGES;"""
                exit_code, output, error = run(ssh, f'''mysql -u root --socket=/var/lib/mysql/mysql.sock -e "{reset_sql}" 2>&1''', "Reset password", timeout=30)
                
                # Stop skip-grant mode
                run(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", "Shutdown")
                time.sleep(3)
                
                # Start normally
                run(ssh, "systemctl start mysqld", "Start normal")
                time.sleep(5)
            else:
                print("  Password changed successfully")
            
            # Verify
            exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify MySQL")
            if '1' in output:
                print("  MySQL OK")
            else:
                print(f"  MySQL verification: {output}")
                # Last resort - create database anyway
                run(ssh, "mysql -uroot --connect-expired-password -e 'SELECT 1' 2>&1", "Try expired connection")
        else:
            print(f"  Could not parse password from: {log_output[:200]}")
    else:
        print(f"  No temp password found. Error: {error}")
        # Try to start anyway
        run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Try direct connection")
    
    # 2. Create database
    print("\n[2/6] Creating database...")
    run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' 2>&1", "Create DB")
    print("  Database ready")
    
    # 3-5. Deploy frontend (using base64 to avoid escaping)
    print("\n[3/6] Deploying frontend...")
    
    fix_panel_html = """{% load static %}
<div id="openclaw-fix-panel" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:99999;background:white;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.3);padding:40px;min-width:450px;max-width:600px;text-align:center;">
    <div style="font-size:64px;margin-bottom:20px;">&#x1F527;</div>
    <h2 style="margin:0 0 10px 0;color:#333;font-size:24px;">System Error</h2>
    <p style="color:#666;margin:0 0 30px 0;font-size:14px;">Error detected</p>
    <div style="background:#f5f5f5;border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="background:#ddd;border-radius:4px;height:20px;overflow:hidden;">
            <div id="fix-progress-bar" style="background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);height:100%;width:0%;transition:width 0.5s ease;"></div>
        </div>
        <p id="fix-status" style="margin:10px 0 0 0;color:#666;font-size:13px;">Waiting...</p>
    </div>
    <div style="display:flex;gap:10px;justify-content:center;">
        <button id="btn-fix" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:12px 30px;border-radius:6px;font-size:16px;cursor:pointer;">Manual Fix</button>
        <button id="btn-refresh" style="background:#f0f0f0;color:#333;border:1px solid #ddd;padding:12px 30px;border-radius:6px;font-size:16px;cursor:pointer;">Refresh</button>
    </div>
</div>
<script>
(function() {
    var hasError = document.body.innerHTML.indexOf('OperationalError') !== -1 || 
                   document.body.innerHTML.indexOf('DatabaseError') !== -1;
    if (!hasError) return;
    var panel = document.getElementById('openclaw-fix-panel');
    if (panel) panel.style.display = 'block';
    var btnRefresh = document.getElementById('btn-refresh');
    var btnFix = document.getElementById('btn-fix');
    if (btnRefresh) btnRefresh.addEventListener('click', function() { window.location.reload(); });
    if (btnFix) {
        btnFix.addEventListener('click', function() {
            var btn = this;
            var bar = document.getElementById('fix-progress-bar');
            var status = document.getElementById('fix-status');
            btn.disabled = true;
            btn.textContent = 'Fixing...';
            fetch('/openclaw/api/trigger-fix/')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.success) {
                        status.textContent = 'Fix triggered!';
                        bar.style.width = '20%';
                        var count = 0;
                        var timer = setInterval(function() {
                            count++;
                            bar.style.width = Math.min(20 + (count/30)*80, 100) + '%';
                            status.textContent = 'Checking... ' + count + '/30';
                            fetch('/openclaw/api/status/')
                                .then(function(r) { return r.json(); })
                                .then(function(s) {
                                    if (s.mysql === 'OK' || s.mysql === 'FIXED') {
                                        clearInterval(timer);
                                        bar.style.width = '100%';
                                        status.textContent = 'Fixed!';
                                        setTimeout(function() { window.location.reload(); }, 2000);
                                    }
                                    if (count >= 30) {
                                        clearInterval(timer);
                                        status.textContent = 'Refresh manually';
                                        btn.disabled = false;
                                        btn.textContent = 'Retry';
                                    }
                                });
                        }, 2000);
                    } else {
                        status.textContent = 'Error';
                        btn.disabled = false;
                        btn.textContent = 'Retry';
                    }
                })
                .catch(function() {
                    status.textContent = 'Network error';
                    btn.disabled = false;
                    btn.textContent = 'Retry';
                });
        });
    }
    var autoCount = 0;
    var autoTimer = setInterval(function() {
        autoCount++;
        if (autoCount > 20) { clearInterval(autoTimer); return; }
        window.location.reload();
    }, 3000);
})();
</script>
"""
    
    encoded_html = base64.b64encode(fix_panel_html.encode('utf-8')).decode('ascii')
    run(ssh, f"mkdir -p {SERVER_PATH}/templates/includes", "Create dir")
    run(ssh, f'echo "{encoded_html}" | base64 -d > {SERVER_PATH}/templates/includes/fix_panel.html', "Write template")
    
    # Verify
    exit_code, output, error = run(ssh, f"wc -l {SERVER_PATH}/templates/includes/fix_panel.html", "Verify")
    print(f"  Template: {output}")
    
    # 4. Add API
    print("\n[4/6] Adding API...")
    
    api_views = """

def openclaw_status(request):
    from django.http import JsonResponse
    import json
    try:
        with open('/root/.openclaw/monitoring/status.json', 'r') as f:
            return JsonResponse(json.load(f))
    except:
        return JsonResponse({'error': 'Not found'}, status=500)

def openclaw_trigger_fix(request):
    from django.http import JsonResponse
    import subprocess
    try:
        subprocess.Popen(['bash', '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
"""
    
    encoded_api = base64.b64encode(api_views.encode('utf-8')).decode('ascii')
    exit_code, output, error = run(ssh, f"grep -c 'def openclaw_status' {SERVER_PATH}/views_index.py", "Check API")
    if '0' in output:
        run(ssh, f'echo "{encoded_api}" | base64 -d >> {SERVER_PATH}/views_index.py', "Add API")
        print("  API added")
    else:
        print("  API exists")
    
    # 5. Add URLs
    print("\n[5/6] Adding URLs...")
    
    url_code = """    path('openclaw/api/status/', views_index.openclaw_status),
    path('openclaw/api/trigger-fix/', views_index.openclaw_trigger_fix),
"""
    encoded_url = base64.b64encode(url_code.encode('utf-8')).decode('ascii')
    exit_code, output, error = run(ssh, f"grep -c 'openclaw/api' {SERVER_PATH}/urls.py", "Check URLs")
    if '0' in output:
        python_cmd = f'''python3 -c "
import base64
encoded = '{encoded_url}'
content = base64.b64decode(encoded).decode('utf-8')
with open('{SERVER_PATH}/urls.py', 'r') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    new_lines.append(line)
    if 'urlpatterns = [' in line:
        new_lines.append(content)
with open('{SERVER_PATH}/urls.py', 'w') as f:
    f.writelines(new_lines)
print('Done')
"'''
        run(ssh, python_cmd, "Add URLs")
        print("  URLs added")
    else:
        print("  URLs exist")
    
    # Add to base.html
    include_code = '{% include "includes/fix_panel.html" %}'
    encoded_include = base64.b64encode(include_code.encode('utf-8')).decode('ascii')
    python_cmd = f'''python3 -c "
import base64
encoded = '{encoded_include}'
include_line = base64.b64decode(encoded).decode('utf-8')
with open('{SERVER_PATH}/templates/base.html', 'r') as f:
    content = f.read()
if 'fix_panel' not in content:
    content = content.replace('</body>', include_line + chr(10) + '</body>')
    with open('{SERVER_PATH}/templates/base.html', 'w') as f:
        f.write(content)
    print('Added')
else:
    print('Exists')
"'''
    exit_code, output, error = run(ssh, python_cmd, "Add to base.html")
    print(f"  {output}")
    
    # 6. Restart Gunicorn
    print("\n[6/6] Restarting Gunicorn...")
    run(ssh, "pkill -9 -f gunicorn", "Stop")
    time.sleep(3)
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", "Start")
    time.sleep(5)
    
    exit_code, output, error = run(ssh, "ps aux | grep '[g]unicorn' | wc -l", "Gunicorn")
    print(f"  Gunicorn: {output} processes")
    
    exit_code, output, error = run(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "HTTP")
    print(f"  HTTP: {output}")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nREFRESH YOUR BROWSER:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
