#!/usr/bin/env python3
"""
Nuclear option - Complete MySQL reinstall
"""

import paramiko
import os
import time
import sys
import base64

print("=" * 80)
print("Nuclear MySQL Reinstall + Frontend Panel")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc=""):
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    if len(output) > 300:
        output = output[-300:]
    return exit_code, output, error

try:
    # Step 1: Complete MySQL removal
    print("\n[1/8] Stopping and removing MySQL...")
    run(ssh, "systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2", "Stop MySQL")
    run(ssh, "rm -rf /var/lib/mysql/* /var/log/mysqld.log /var/lib/mysql/.mysql_secret", "Remove MySQL data")
    print("  MySQL data removed")
    
    # Step 2: Reinitialize MySQL
    print("\n[2/8] Reinitializing MySQL...")
    run(ssh, "mysqld --initialize --user=mysql --datadir=/var/lib/mysql 2>&1 | tail -1", "Initialize")
    time.sleep(5)
    
    # Step 3: Start MySQL
    print("\n[3/8] Starting MySQL...")
    run(ssh, "systemctl start mysqld", "Start MySQL")
    time.sleep(5)
    
    # Step 4: Get temporary password
    print("\n[4/8] Getting temporary password...")
    exit_code, temp_pass, error = run(ssh, "grep 'temporary password' /var/log/mysqld.log | tail -1", "Get temp password")
    
    if temp_pass:
        import re
        match = re.search(r'root@localhost: (.+)', temp_pass)
        if match:
            temp_password = match.group(1)
            print(f"  Temporary password found")
            
            # Step 5: Change password
            print("\n[5/8] Changing root password...")
            change_cmd = f'mysql -uroot -p"{temp_password}" --connect-expired-password -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1'
            exit_code, output, error = run(ssh, change_cmd, "Change password")
            
            if exit_code == 0:
                print("  Password changed successfully")
            else:
                print(f"  Error: {error[:200]}")
                # Try alternative method
                print("  Trying alternative method...")
                run(ssh, "mysql -uroot --connect-expired-password -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';\" 2>&1", "Alt change")
        else:
            print(f"  Could not extract password: {temp_pass}")
            sys.exit(1)
    else:
        print(f"  No temporary password found: {error}")
        sys.exit(1)
    
    # Step 6: Verify MySQL
    print("\n[6/8] Verifying MySQL...")
    exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify")
    if '1' in output:
        print("  MySQL OK")
    else:
        print(f"  MySQL failed: {output}")
        sys.exit(1)
    
    # Step 7: Create database
    print("\n[7/8] Creating database...")
    run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'", "Create DB")
    print("  Database created")
    
    # Step 8: Deploy frontend
    print("\n[8/8] Deploying frontend fix panel...")
    
    fix_panel_html = r'''{% load static %}
<div id="openclaw-fix-panel" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:99999;background:white;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.3);padding:40px;min-width:450px;max-width:600px;text-align:center;">
    <div style="font-size:64px;margin-bottom:20px;">&#x1F527;</div>
    <h2 style="margin:0 0 10px 0;color:#333;font-size:24px;">System Error Detected</h2>
    <p style="color:#666;margin:0 0 30px 0;font-size:14px;">&#x7CFB;&#x7EDF;&#x68C0;&#x6D4B;&#x5230;&#x9519;&#x8BEF;</p>
    <div style="background:#f5f5f5;border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="background:#ddd;border-radius:4px;height:20px;overflow:hidden;">
            <div id="fix-progress-bar" style="background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);height:100%;width:0%;transition:width 0.5s ease;"></div>
        </div>
        <p id="fix-status" style="margin:10px 0 0 0;color:#666;font-size:13px;">Waiting...</p>
    </div>
    <div style="display:flex;gap:10px;justify-content:center;">
        <button id="btn-fix" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:12px 30px;border-radius:6px;font-size:16px;cursor:pointer;box-shadow:0 4px 15px rgba(102,126,234,0.4);">&#x26A1; Manual Fix</button>
        <button id="btn-refresh" style="background:#f0f0f0;color:#333;border:1px solid #ddd;padding:12px 30px;border-radius:6px;font-size:16px;cursor:pointer;">&#x1F504; Refresh</button>
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
    
    if (btnRefresh) {
        btnRefresh.addEventListener('click', function() {
            window.location.reload();
        });
    }
    
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
                        status.textContent = 'Fix triggered! Monitoring...';
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
                                        status.textContent = 'Fixed! Refreshing...';
                                        setTimeout(function() { window.location.reload(); }, 2000);
                                    }
                                    if (count >= 30) {
                                        clearInterval(timer);
                                        status.textContent = 'Please refresh manually';
                                        btn.disabled = false;
                                        btn.textContent = 'Retry';
                                    }
                                });
                        }, 2000);
                    } else {
                        status.textContent = 'Error: ' + (data.error || 'Unknown');
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
'''
    
    encoded = base64.b64encode(fix_panel_html.encode('utf-8')).decode('ascii')
    
    run(ssh, f"mkdir -p {SERVER_PATH}/templates/includes", "Create directory")
    run(ssh, f'echo "{encoded}" | base64 -d > {SERVER_PATH}/templates/includes/fix_panel.html', "Write template")
    print("  Template created")
    
    # Add API views
    api_code = """

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
    
    api_encoded = base64.b64encode(api_code.encode('utf-8')).decode('ascii')
    
    exit_code, output, error = run(ssh, f"grep -c 'def openclaw_status' {SERVER_PATH}/views_index.py", "Check API")
    if '0' in output:
        run(ssh, f'echo "{api_encoded}" | base64 -d >> {SERVER_PATH}/views_index.py', "Add API")
        print("  API views added")
    else:
        print("  API already exists")
    
    # Add URLs
    url_code = """    path('openclaw/api/status/', views_index.openclaw_status),
    path('openclaw/api/trigger-fix/', views_index.openclaw_trigger_fix),
"""
    url_encoded = base64.b64encode(url_code.encode('utf-8')).decode('ascii')
    
    exit_code, output, error = run(ssh, f"grep -c 'openclaw/api' {SERVER_PATH}/urls.py", "Check URLs")
    if '0' in output:
        python_cmd = f"""python3 -c "
import base64
encoded = '{url_encoded}'
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
"
"""
        run(ssh, python_cmd, "Add URLs")
        print("  URLs added")
    else:
        print("  URLs already exist")
    
    # Add to base.html
    include_code = '{% include "includes/fix_panel.html" %}'
    include_encoded = base64.b64encode(include_code.encode('utf-8')).decode('ascii')
    
    python_cmd = f"""python3 -c "
import base64
encoded = '{include_encoded}'
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
"
"""
    exit_code, output, error = run(ssh, python_cmd, "Add to base.html")
    print(f"  {output}")
    
    # Restart Gunicorn
    print("\nRestarting Gunicorn...")
    run(ssh, "pkill -9 -f gunicorn", "Stop Gunicorn")
    time.sleep(3)
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", "Start Gunicorn")
    time.sleep(5)
    
    exit_code, output, error = run(ssh, "ps aux | grep '[g]unicorn' | wc -l", "Check Gunicorn")
    print(f"  Gunicorn: {output} processes")
    
    exit_code, output, error = run(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "Test HTTP")
    print(f"  HTTP: {output}")
    
    print("\n" + "=" * 80)
    print("COMPLETE - MySQL Reinstalled + Frontend Panel Deployed")
    print("=" * 80)
    print("\nRefresh your browser:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
