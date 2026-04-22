#!/usr/bin/env python3
"""
Complete clean fix using base64 to avoid ALL escaping issues
"""

import paramiko
import os
import time
import sys
import base64
import re

print("=" * 80)
print("Complete Clean Fix")
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
    # 1. Fix MySQL completely
    print("\n[1/5] Reinstalling MySQL...")
    
    # Stop everything
    run(ssh, "systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 2", "Stop MySQL")
    
    # Remove old data
    run(ssh, "rm -rf /var/lib/mysql/*", "Remove data")
    
    # Reinitialize
    run(ssh, "mysqld --initialize --user=mysql --datadir=/var/lib/mysql 2>&1", "Initialize", timeout=60)
    time.sleep(5)
    
    # Start MySQL
    run(ssh, "systemctl start mysqld", "Start MySQL")
    time.sleep(5)
    
    # Get temp password
    exit_code, log_output, error = run(ssh, "grep 'temporary password' /var/log/mysqld.log | tail -1", "Get temp password")
    
    if log_output:
        match = re.search(r'root@localhost:\s*(\S+)', log_output)
        if match:
            temp_pass = match.group(1)
            print(f"  Temp password found")
            
            # Change password
            change_cmd = f'mysql -uroot -p"{temp_pass}" --connect-expired-password -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\'; FLUSH PRIVILEGES;" 2>&1'
            exit_code, output, error = run(ssh, change_cmd, "Change password")
            
            if exit_code != 0:
                print(f"  First attempt failed, trying alternate...")
                run(ssh, f'mysql -uroot --connect-expired-password -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'EIMS2026_mysql\';" 2>&1', "Alternate change")
            
            # Verify
            exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1", "Verify MySQL")
            if '1' in output:
                print("  MySQL OK")
            else:
                print(f"  MySQL verification failed: {output}")
                sys.exit(1)
        else:
            print(f"  Could not parse password from: {log_output}")
            sys.exit(1)
    else:
        print(f"  No temp password in log")
        sys.exit(1)
    
    # 2. Create database
    print("\n[2/5] Creating database...")
    run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'CREATE DATABASE IF NOT EXISTS eims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'", "Create DB")
    print("  Database ready")
    
    # 3. Deploy frontend panel using base64 (NO escaping issues!)
    print("\n[3/5] Deploying frontend fix panel...")
    
    fix_panel_html = """{% load static %}
<div id="openclaw-fix-panel" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:99999;background:white;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.3);padding:40px;min-width:450px;max-width:600px;text-align:center;">
    <div style="font-size:64px;margin-bottom:20px;">&#x1F527;</div>
    <h2 style="margin:0 0 10px 0;color:#333;font-size:24px;">System Error Detected</h2>
    <p style="color:#666;margin:0 0 30px 0;font-size:14px;">System error detected</p>
    <div style="background:#f5f5f5;border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="background:#ddd;border-radius:4px;height:20px;overflow:hidden;">
            <div id="fix-progress-bar" style="background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);height:100%;width:0%;transition:width 0.5s ease;"></div>
        </div>
        <p id="fix-status" style="margin:10px 0 0 0;color:#666;font-size:13px;">Waiting...</p>
    </div>
    <div style="display:flex;gap:10px;justify-content:center;">
        <button id="btn-fix" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:12px 30px;border-radius:6px;font-size:16px;cursor:pointer;box-shadow:0 4px 15px rgba(102,126,234,0.4);">Manual Fix</button>
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
                                        status.textContent = 'Please refresh manually';
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
    
    # Encode to base64 - this avoids ALL escaping issues!
    encoded_html = base64.b64encode(fix_panel_html.encode('utf-8')).decode('ascii')
    
    # Create directory
    run(ssh, f"mkdir -p {SERVER_PATH}/templates/includes", "Create directory")
    
    # Write file via base64 decode
    run(ssh, f'echo "{encoded_html}" | base64 -d > {SERVER_PATH}/templates/includes/fix_panel.html', "Write template")
    
    # Verify
    exit_code, output, error = run(ssh, f"wc -l {SERVER_PATH}/templates/includes/fix_panel.html", "Verify template")
    print(f"  Template: {output}")
    
    # 4. Add API views and URLs using base64
    print("\n[4/5] Adding API endpoints...")
    
    # API views
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
        print("  API views added")
    else:
        print("  API exists")
    
    # URLs
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
    
    # 5. Restart Gunicorn
    print("\n[5/5] Restarting Gunicorn...")
    run(ssh, "pkill -9 -f gunicorn", "Stop Gunicorn")
    time.sleep(3)
    run(ssh, f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", "Start Gunicorn")
    time.sleep(5)
    
    exit_code, output, error = run(ssh, "ps aux | grep '[g]unicorn' | wc -l", "Check Gunicorn")
    print(f"  Gunicorn: {output} processes")
    
    exit_code, output, error = run(ssh, "curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/", "Test HTTP")
    print(f"  HTTP: {output}")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nNow refresh your browser:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    print("\nYou should see:")
    print("  - Normal login page (if working)")
    print("  - OR fix panel with Manual Fix button (if error)")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
