#!/usr/bin/env python3
"""
Simple Complete Fix
"""

import paramiko
import os
import time
import sys

print("=" * 80)
print("Complete Fix - MySQL + Frontend")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\nConnected\n")

# 1. Check MySQL
print("[1/5] Check MySQL...")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1")
mysql_result = stdout.read().decode().strip()

if '1' not in mysql_result:
    print("  MySQL failed - triggering auto-fix...")
    ssh.exec_command("bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/mysql_fix.log 2>&1", timeout=120)
    time.sleep(65)
    
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1")
    if '1' in stdout.read().decode():
        print("  MySQL fixed")
    else:
        print("  MySQL still failed")
        sys.exit(1)
else:
    print("  MySQL OK")

# 2. Create fix panel HTML file
print("\n[2/5] Create fix panel template...")

create_panel_cmd = f"""cat > {SERVER_PATH}/templates/includes/fix_panel.html << 'EOF'
<!-- OpenClaw Fix Panel -->
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
    panel.style.display = 'block';
    
    document.getElementById('btn-refresh').addEventListener('click', function() {
        window.location.reload();
    });
    
    document.getElementById('btn-fix').addEventListener('click', function() {
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
    
    var autoCount = 0;
    var autoTimer = setInterval(function() {
        autoCount++;
        if (autoCount > 20) { clearInterval(autoTimer); return; }
        window.location.reload();
    }, 3000);
})();
</script>
EOF
"""

ssh.exec_command(create_panel_cmd, timeout=10)
time.sleep(2)
print("  Template created")

# 3. Add API views to views_index.py
print("\n[3/5] Add API views...")

add_api_cmd = f"""
grep -q 'def openclaw_status' {SERVER_PATH}/views_index.py || cat >> {SERVER_PATH}/views_index.py << 'EOF'

# OpenClaw API
def openclaw_status(request):
    from django.http import JsonResponse
    import json
    try:
        with open('/root/.openclaw/monitoring/status.json', 'r') as f:
            return JsonResponse(json.load(f))
    except:
        return JsonResponse({{'error': 'Not found'}}, status=500)

def openclaw_trigger_fix(request):
    from django.http import JsonResponse
    import subprocess
    try:
        subprocess.Popen(['bash', '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'])
        return JsonResponse({{'success': True}})
    except Exception as e:
        return JsonResponse({{'success': False, 'error': str(e)}}, status=500)
EOF
"""

ssh.exec_command(add_api_cmd, timeout=10)
time.sleep(2)
print("  API views added")

# 4. Add URLs
print("\n[4/5] Add URLs...")

add_urls_cmd = f"""
grep -q 'openclaw/api' {SERVER_PATH}/urls.py || sed -i '/urlpatterns = \[/a\\    path(\"openclaw/api/status/\", views_index.openclaw_status),\\n    path(\"openclaw/api/trigger-fix/\", views_index.openclaw_trigger_fix),' {SERVER_PATH}/urls.py
"""

ssh.exec_command(add_urls_cmd, timeout=10)
time.sleep(2)
print("  URLs added")

# 5. Add to base.html and restart
print("\n[5/5] Add to base.html and restart...")

# Backup base.html
ssh.exec_command(f"cp {SERVER_PATH}/templates/base.html {SERVER_PATH}/templates/base.html.bak", timeout=5)

# Add fix panel include before </body>
add_to_base_cmd = f"""
grep -q 'fix_panel' {SERVER_PATH}/templates/base.html || sed -i 's|</body>|{{% include "includes/fix_panel.html" %}}\n</body>|' {SERVER_PATH}/templates/base.html
"""

ssh.exec_command(add_to_base_cmd, timeout=10)
time.sleep(2)

# Restart Gunicorn
ssh.exec_command("pkill -9 -f gunicorn", timeout=5)
time.sleep(3)
ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", timeout=5)
time.sleep(5)

# Check
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
gunicorn_count = int(stdout.read().decode().strip())

stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()

print(f"  Gunicorn: {gunicorn_count} processes")
print(f"  HTTP: {http_code}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
print("\nAccess:")
print("  http://www.xietongai.com.cn/login/")
print("  http://39.106.41.239:8000/login/")
print("\nFix panel should appear automatically on error pages!")

ssh.close()
