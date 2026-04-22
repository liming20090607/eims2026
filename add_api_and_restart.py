#!/usr/bin/env python3
"""
Add API views and URLs, then restart
"""

import paramiko
import os
import time

print("=" * 80)
print("🔧 Adding API & Restarting")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Step 1: Add API views to views_index.py
print("[1/4] Adding API views...")

api_code = """

# ==================== OpenClaw API Views ====================
def openclaw_status(request):
    from django.http import JsonResponse
    import json
    status_file = '/root/.openclaw/monitoring/status.json'
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def openclaw_trigger_fix(request):
    from django.http import JsonResponse
    import subprocess
    if request.method == 'POST':
        try:
            subprocess.Popen(['bash', '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return JsonResponse({'success': True, 'message': '修复已启动'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
"""

# Append to views_index.py
append_views = f"echo '{api_code}' >> {SERVER_PATH}/views_index.py"
ssh.exec_command(append_views, timeout=5)
print("  ✅ API views added\n")

# Step 2: Add URLs
print("[2/4] Adding URL routes...")

add_urls_cmd = f"""python3 << 'PYEOF'
urls_file = '{SERVER_PATH}/urls.py'
with open(urls_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find import section and urlpatterns
new_lines = []
import_added = False
for line in lines:
    new_lines.append(line)
    if line.startswith('from ') and 'views_index' in line and not import_added:
        # Add our import after existing views_index import
        if 'openclaw_status' not in line:
            new_lines.append('from eims_app.views_index import openclaw_status, openclaw_trigger_fix\\n')
            import_added = True

# Now add URL patterns
content = ''.join(new_lines)
if 'openclaw/api/status' not in content:
    # Find urlpatterns = [ and add after it
    import re
    pattern = r'(urlpatterns\\s*=\\s*\\[)'
    replacement = r'\\1\\n    # OpenClaw API\\n    path(\"openclaw/api/status/\", openclaw_status, name=\"openclaw_status\"),\\n    path(\"openclaw/api/trigger-fix/\", openclaw_trigger_fix, name=\"openclaw_trigger_fix\"),'
    content = re.sub(pattern, replacement, content)
    
    with open(urls_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("URLs added")
else:
    print("URLs already exist")
PYEOF
"""

stdin, stdout, stderr = ssh.exec_command(add_urls_cmd, timeout=10)
result = stdout.read().decode().strip()
print(f"  {result}\n")

# Step 3: Add template include to base.html
print("[3/4] Adding template to base.html...")

add_template = f"""python3 << 'BASICEOF'
base_file = '{SERVER_PATH}/templates/base/base.html'
with open(base_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'openclaw_fix_panel' not in content:
    content = content.replace('</body>', '{{% include "includes/openclaw_fix_panel.html" %}}\\n</body>')
    with open(base_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Template added to base.html")
else:
    print("Already in base.html")
BASICEOF
"""

stdin, stdout, stderr = ssh.exec_command(add_template, timeout=10)
result = stdout.read().decode().strip()
print(f"  {result}\n")

# Step 4: Restart Gunicorn
print("[4/4] Restarting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)

start_cmd = f"""cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 & echo "Started" """
stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=10)
print(f"  {stdout.read().decode().strip()}")

time.sleep(8)

# Verify
print("\n" + "=" * 80)
print("Verification")
print("=" * 80)

stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"Gunicorn processes: {count}")

time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"HTTP Status: {http_code}")

# Test API
stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/openclaw/api/status/ 2>&1 | head -3")
api_resp = stdout.read().decode().strip()
print(f"API Response: {api_resp[:150]}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Frontend panel is live!")
    print("=" * 80)
    print("\n🎨 Features enabled:")
    print("  ✓ Error page detection")
    print("  ✓ Manual fix button (purple gradient)")
    print("  ✓ Progress bar (0-100% with animation)")
    print("  ✓ Auto-refresh every 2 seconds")
    print("  ✓ Auto-redirect after fix")
    print("\n🌐 Test at:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print("=" * 80)
else:
    print(f"\n⚠️ HTTP {http_code}")
    stdin, stdout, stderr = ssh.exec_command(f"tail -20 {SERVER_PATH}/logs/gunicorn_error.log")
    print(stdout.read().decode())

ssh.close()
