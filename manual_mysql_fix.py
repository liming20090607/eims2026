#!/usr/bin/env python3
"""
Manual MySQL Fix + Frontend Panel
"""

import paramiko
import os
import time
import sys
import base64

print("=" * 80)
print("Manual MySQL Fix + Frontend")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

def run(ssh, cmd, desc=""):
    """Run command and return output"""
    print(f"  {desc}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    return exit_code, output, error

try:
    print("\n[1/7] Stopping MySQL completely...")
    run(ssh, "systemctl stop mysqld 2>/dev/null; killall -9 mysqld mysqld_safe 2>/dev/null; sleep 3", "Stop MySQL")
    
    print("\n[2/7] Cleaning up...")
    run(ssh, "rm -f /var/lib/mysql/mysql.sock /var/lib/mysql/*.lock", "Remove socket files")
    run(ssh, "mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld", "Fix permissions")
    
    print("\n[3/7] Starting MySQL in recovery mode...")
    run(ssh, "mysqld_safe --user=mysql --skip-grant-tables --skip-networking &", "Start recovery mode")
    time.sleep(10)
    
    # Check if socket exists
    exit_code, output, error = run(ssh, "ls -la /var/lib/mysql/mysql.sock 2>&1", "Check socket")
    if 'mysql.sock' not in output:
        print(f"  ERROR: Socket not created: {output}")
        sys.exit(1)
    print("  Socket created")
    
    print("\n[4/7] Resetting root password...")
    reset_sql = """
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
FLUSH PRIVILEGES;
"""
    exit_code, output, error = run(ssh, f"mysql -u root --socket=/var/lib/mysql/mysql.sock -e \"{reset_sql}\"", "Reset password")
    if exit_code != 0:
        print(f"  Password reset output: {output}")
        print(f"  Error: {error}")
    
    print("\n[5/7] Restarting MySQL normally...")
    run(ssh, "mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown 2>/dev/null || killall mysqld", "Shutdown recovery")
    time.sleep(3)
    run(ssh, "systemctl start mysqld 2>/dev/null || service mysql start", "Start MySQL")
    time.sleep(5)
    
    # Verify
    exit_code, output, error = run(ssh, "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1", "Verify MySQL")
    if '1' in output:
        print("  MySQL OK")
    else:
        print(f"  MySQL still failed: {output}")
        sys.exit(1)
    
    print("\n[6/7] Deploying frontend fix panel...")
    
    # Create fix panel HTML using base64
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
    print("\n[7/7] Adding API and restarting...")
    
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
    
    # Check if API exists
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
        python_cmd = f'python3 -c "\nimport base64\nencoded = \'{url_encoded}\'\ncontent = base64.b64decode(encoded).decode(\'utf-8\')\nwith open(\'{SERVER_PATH}/urls.py\', \'r\') as f:\n    lines = f.readlines()\nnew_lines = []\nfor line in lines:\n    new_lines.append(line)\n    if \'urlpatterns = [\' in line:\n        new_lines.append(content)\nwith open(\'{SERVER_PATH}/urls.py\', \'w\') as f:\n    f.writelines(new_lines)\n"'
        run(ssh, python_cmd, "Add URLs")
        print("  URLs added")
    else:
        print("  URLs already exist")
    
    # Add to base.html
    include_code = '{% include "includes/fix_panel.html" %}'
    include_encoded = base64.b64encode(include_code.encode('utf-8')).decode('ascii')
    
    python_cmd = f'python3 -c "\nimport base64\nencoded = \'{include_encoded}\'\ninclude_line = base64.b64decode(encoded).decode(\'utf-8\')\nwith open(\'{SERVER_PATH}/templates/base.html\', \'r\') as f:\n    content = f.read()\nif \'fix_panel\' not in content:\n    content = content.replace(\'</body>\', include_line + chr(10) + \'</body>\')\n    with open(\'{SERVER_PATH}/templates/base.html\', \'w\') as f:\n        f.write(content)\n    print(\'Added\')\nelse:\n    print(\'Exists\')\n"'
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
    print("COMPLETE")
    print("=" * 80)
    print("\nNow refresh your browser:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    print("\nYou should see the fix panel with Manual Fix button if there's an error!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
