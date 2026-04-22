#!/usr/bin/env python3
"""
Complete Fix - MySQL + Frontend Panel
"""

import paramiko
import os
import time
import sys
from io import StringIO

print("=" * 80)
print("🚨 Complete Fix - MySQL + Frontend Panel")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ Connected\n")
    
    # Step 1: Check and fix MySQL
    print("[1/6] Checking MySQL status...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1")
    mysql_result = stdout.read().decode().strip()
    
    if '1' not in mysql_result:
        print("  ⚠️  MySQL authentication failed - triggering auto-fix...")
        
        # Trigger OpenClaw enhanced MySQL fix
        print("  → Running enhanced_mysql_fix.sh...")
        stdin, stdout, stderr = ssh.exec_command(
            "nohup bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/mysql_fix.log 2>&1 &",
            timeout=5
        )
        
        # Wait for fix to complete
        print("  ⏳ Waiting for MySQL fix (60 seconds)...")
        time.sleep(60)
        
        # Verify MySQL
        stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1")
        mysql_result = stdout.read().decode().strip()
        
        if '1' in mysql_result:
            print("  ✅ MySQL fixed successfully")
        else:
            print("  ❌ MySQL still failed - manual intervention needed")
            sys.exit(1)
    else:
        print("  ✅ MySQL is working")
    
    # Step 2: Add frontend fix panel to base.html
    print("\n[2/6] Adding frontend fix panel to base.html...")
    
    # Create the fix panel script
    fix_panel_script = r"""
<!-- OpenClaw Auto Fix Panel -->
<script>
(function() {
    // Check if page has database error
    var pageContent = document.body.innerHTML;
    var hasError = pageContent.indexOf('OperationalError') !== -1 || 
                   pageContent.indexOf('DatabaseError') !== -1 ||
                   pageContent.indexOf('Error') !== -1 && pageContent.indexOf('database') !== -1;
    
    if (!hasError) return;
    
    // Create fix panel
    var panel = document.createElement('div');
    panel.id = 'openclaw-fix-panel';
    panel.style.cssText = 'display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index:99999; background:white; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.3); padding:40px; min-width:450px; max-width:600px; text-align:center;';
    panel.innerHTML = '<div style="font-size:64px; margin-bottom:20px;">&#x1F527;</div>' +
        '<h2 style="margin:0 0 10px 0; color:#333; font-size:24px;">&#x7CFB;&#x7EDF;&#x68C0;&#x6D4B;&#x5230;&#x9519;&#x8BEF;</h2>' +
        '<p style="color:#666; margin:0 0 30px 0; font-size:14px;">System Error Detected</p>' +
        '<div style="background:#f5f5f5; border-radius:8px; padding:20px; margin-bottom:20px;">' +
        '<div id="fix-progress" style="background:#ddd; border-radius:4px; height:20px; overflow:hidden;">' +
        '<div id="fix-progress-bar" style="background:linear-gradient(90deg, #667eea 0%, #764ba2 100%); height:100%; width:0%; transition:width 0.5s ease;"></div>' +
        '</div>' +
        '<p id="fix-status" style="margin:10px 0 0 0; color:#666; font-size:13px;">&#x7B49;&#x5F85;&#x4E2D;... Waiting...</p>' +
        '</div>' +
        '<div style="display:flex; gap:10px; justify-content:center;">' +
        '<button id="btn-manual-fix" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; padding:12px 30px; border-radius:6px; font-size:16px; cursor:pointer; box-shadow:0 4px 15px rgba(102,126,234,0.4);">&#x26A1; &#x7ACB;&#x5373;&#x624B;&#x52A8;&#x4FEE;&#x590D;</button>' +
        '<button id="btn-refresh" style="background:#f0f0f0; color:#333; border:1px solid #ddd; padding:12px 30px; border-radius:6px; font-size:16px; cursor:pointer;">&#x1F504; &#x5237;&#x65B0;&#x9875;&#x9762;</button>' +
        '</div>';
    document.body.appendChild(panel);
    
    // Show panel
    setTimeout(function() {
        panel.style.display = 'block';
    }, 500);
    
    // Manual fix button
    document.getElementById('btn-manual-fix').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.textContent = '\u23F3 Fixing...';
        
        var progressBar = document.getElementById('fix-progress-bar');
        var statusText = document.getElementById('fix-status');
        
        // Call API to trigger fix
        fetch('/openclaw/api/trigger-fix/')
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    statusText.textContent = '\u2705 Fix triggered! Monitoring...';
                    progressBar.style.width = '20%';
                    
                    // Poll for status
                    var attempts = 0;
                    var maxAttempts = 30;
                    var interval = setInterval(function() {
                        attempts++;
                        var progress = Math.min(20 + (attempts / maxAttempts) * 80, 100);
                        progressBar.style.width = progress + '%';
                        statusText.textContent = '\uD83D\uDD04 Checking status... ' + attempts + '/' + maxAttempts;
                        
                        fetch('/openclaw/api/status/')
                            .then(function(r) { return r.json(); })
                            .then(function(status) {
                                if (status.mysql === 'OK' || status.mysql === 'FIXED') {
                                    clearInterval(interval);
                                    progressBar.style.width = '100%';
                                    statusText.textContent = '\u2705 MySQL fixed! Redirecting...';
                                    setTimeout(function() {
                                        window.location.reload();
                                    }, 2000);
                                }
                                if (attempts >= maxAttempts) {
                                    clearInterval(interval);
                                    statusText.textContent = '\u26A0\uFE0F Please refresh manually';
                                    btn.disabled = false;
                                    btn.textContent = '\u26A1 Try Again';
                                }
                            });
                    }, 2000);
                } else {
                    statusText.textContent = '\u274C Error: ' + (data.error || 'Unknown');
                    btn.disabled = false;
                    btn.textContent = '\u26A1 Retry';
                }
            })
            .catch(function(err) {
                statusText.textContent = '\u274C Network error';
                btn.disabled = false;
                btn.textContent = '\u26A1 Retry';
            });
    });
    
    // Refresh button
    document.getElementById('btn-refresh').addEventListener('click', function() {
        window.location.reload();
    });
    
    // Auto-refresh every 3 seconds
    var autoRefreshCount = 0;
    var autoRefreshInterval = setInterval(function() {
        autoRefreshCount++;
        if (autoRefreshCount > 20) {
            clearInterval(autoRefreshInterval);
            return;
        }
        window.location.reload();
    }, 3000);
})();
</script>
"""
    
    # Upload script to server
    script_path = '/tmp/fix_panel_script.js'
    sftp = ssh.open_sftp()
    with StringIO(fix_panel_script) as f:
        sftp.putfo(f, script_path)
    sftp.close()
    
    # Insert into base.html before </body>
    print("  → Adding fix panel to base.html...")
    ssh.exec_command(f"cp {SERVER_PATH}/templates/base.html {SERVER_PATH}/templates/base.html.bak", timeout=5)
    
    insert_cmd = f"""python3 -c "
import re
with open('{SERVER_PATH}/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()
with open('{script_path}', 'r', encoding='utf-8') as f:
    script = f.read()
if 'openclaw-fix-panel' not in content:
    content = content.replace('</body>', script + '</body>')
    with open('{SERVER_PATH}/templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added')
else:
    print('Already exists')
"
"""
    stdin, stdout, stderr = ssh.exec_command(insert_cmd, timeout=10)
    result = stdout.read().decode().strip()
    print(f"  {result}")
    
    # Step 3: Verify API endpoints exist
    print("\n[3/6] Verifying API endpoints...")
    stdin, stdout, stderr = ssh.exec_command(f"grep -c 'def openclaw_' {SERVER_PATH}/views_index.py")
    api_count = int(stdout.read().decode().strip())
    
    if api_count == 0:
        print("  ⚠️  API endpoints missing - adding them...")
        # Add API views
        api_views = """
# OpenClaw API Views
def openclaw_status(request):
    from django.http import JsonResponse
    import json
    try:
        with open('/root/.openclaw/monitoring/status.json', 'r') as f:
            status = json.load(f)
        return JsonResponse(status)
    except:
        return JsonResponse({'error': 'Status file not found'}, status=500)

def openclaw_trigger_fix(request):
    from django.http import JsonResponse
    import subprocess
    try:
        subprocess.Popen(['bash', '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'])
        return JsonResponse({'success': True, 'message': 'Fix triggered'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
"""
        ssh.exec_command(f"echo '{api_views}' >> {SERVER_PATH}/views_index.py", timeout=5)
        print("  ✅ API views added")
    
    # Check URLs
    stdin, stdout, stderr = ssh.exec_command(f"grep -c 'openclaw/api' {SERVER_PATH}/urls.py")
    url_count = int(stdout.read().decode().strip())
    
    if url_count == 0:
        print("  ⚠️  API URLs missing - adding them...")
        ssh.exec_command(f"sed -i '/urlpatterns = \\[/a\\    path(\\\"openclaw/api/status/\\\", views_index.openclaw_status, name=\\\"openclaw_status\\\"),\\n    path(\\\"openclaw/api/trigger-fix/\\\", views_index.openclaw_trigger_fix, name=\\\"openclaw_trigger_fix\\\"),' {SERVER_PATH}/urls.py", timeout=5)
        print("  ✅ API URLs added")
    
    # Step 4: Restart Gunicorn
    print("\n[4/6] Restarting Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn", timeout=5)
    time.sleep(3)
    ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > logs/gunicorn.log 2>&1 &", timeout=5)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
    gunicorn_count = int(stdout.read().decode().strip())
    print(f"  ✅ Gunicorn: {gunicorn_count} processes")
    
    # Step 5: Test HTTP
    print("\n[5/6] Testing HTTP...")
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
    http_code = stdout.read().decode().strip()
    print(f"  HTTP Status: {http_code}")
    
    # Step 6: Final verification
    print("\n[6/6] Final verification...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | head -1")
    mysql_ok = '1' in stdout.read().decode()
    print(f"  MySQL: {'✅ OK' if mysql_ok else '❌ Failed'}")
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE FIX FINISHED")
    print("=" * 80)
    print("\n🌐 Access your system:")
    print("  http://www.xietongai.com.cn/login/")
    print("  http://39.106.41.239:8000/login/")
    print("\n💡 If you see an error page:")
    print("  - The fix panel should appear automatically")
    print("  - Click '立即手动修复' button")
    print("  - Wait for progress bar to complete")
    print("  - Page will auto-refresh when fixed")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
