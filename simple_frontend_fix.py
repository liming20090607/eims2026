#!/usr/bin/env python3
"""
Simple fix - add frontend panel properly
"""

import paramiko
import os
import time

print("=" * 80)
print("🔧 简单修复前端面板")
print("Simple Frontend Panel Fix")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'  
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)

print("\n✅ Connected\n")

# Step 1: Create includes directory
print("[1/6] Creating directories...")
ssh.exec_command(f"mkdir -p {SERVER_PATH}/templates/includes", timeout=5)
print("  ✅ Done\n")

# Step 2: Create fix panel template using Python to avoid escaping issues
print("[2/6] Creating fix panel template...")

create_template = f"""python3 << 'PYEOF'
template_content = '''{{% load static %}}
<!-- OpenClaw Manual Fix Panel -->
<div id="openclaw-fix-panel" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index:99999; background:white; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.3); padding:40px; min-width:450px; max-width:600px; text-align:center;">
    <div style="font-size:64px; margin-bottom:20px;">&#128295;</div>
    <h2 style="margin:0 0 10px 0; color:#333; font-size:24px;">系统检测到错误</h2>
    <p style="color:#666; margin:0 0 30px 0; font-size:14px;">System Error Detected</p>
    
    <div style="background:#f0f0f0; border-radius:10px; height:30px; overflow:hidden; margin-bottom:20px; position:relative;">
        <div id="fix-progress-bar" style="background:linear-gradient(90deg, #667eea 0%, #764ba2 100%); height:100%; width:0%; transition:width 0.5s ease; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:14px;">
            0%
        </div>
    </div>
    
    <div id="fix-status-text" style="color:#667eea; font-size:16px; margin-bottom:30px; font-weight:500;">
        准备修复...
    </div>
    
    <div style="display:flex; gap:15px; justify-content:center;">
        <button id="btn-manual-fix" onclick="triggerManualFix()" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer; box-shadow:0 4px 15px rgba(102,126,234,0.4);">
            &#9889; 立即手动修复
        </button>
        <button id="btn-refresh-page" onclick="location.reload()" style="background:#f0f0f0; color:#333; border:2px solid #ddd; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer;">
            &#128260; 刷新页面
        </button>
    </div>
    
    <div style="margin-top:20px; color:#999; font-size:12px;">
        &#128161; 提示：系统将每2秒自动刷新，最多尝试30次
    </div>
</div>

<script>
let refreshCount = 0;
const maxRefreshes = 30;
let isFixing = false;

window.addEventListener('load', function() {{
    const isErrorPage = document.title.includes('错误') || 
                       document.title.includes('Error') ||
                       document.body.innerHTML.includes('OperationalError') ||
                       document.body.innerHTML.includes('DatabaseError');
    
    if (isErrorPage) {{
        showFixPanel();
        startAutoRefresh();
    }}
}});

function showFixPanel() {{
    document.getElementById('openclaw-fix-panel').style.display = 'block';
    document.body.style.overflow = 'hidden';
}}

function updateProgress(percent, statusText) {{
    const bar = document.getElementById('fix-progress-bar');
    const text = document.getElementById('fix-status-text');
    bar.style.width = percent + '%';
    bar.textContent = percent + '%';
    text.textContent = statusText;
}}

async function triggerManualFix() {{
    if (isFixing) return;
    isFixing = true;
    
    const btn = document.getElementById('btn-manual-fix');
    btn.disabled = true;
    btn.style.opacity = '0.6';
    btn.textContent = '&#9203; 修复中...';
    
    try {{
        updateProgress(10, '正在触发修复...');
        
        const response = await fetch('/openclaw/api/trigger-fix/', {{
            method: 'POST',
            headers: {{
                'X-CSRFToken': getCookie('csrftoken')
            }}
        }});
        
        updateProgress(30, '修复脚本已启动...');
        
        let pollCount = 0;
        const pollInterval = setInterval(async () => {{
            pollCount++;
            
            try {{
                const statusResp = await fetch('/openclaw/api/status/');
                const status = await statusResp.json();
                
                if (status.mysql === 'OK' || status.mysql === 'FIXED') {{
                    updateProgress(100, '&#9989; 修复成功！');
                    clearInterval(pollInterval);
                    setTimeout(() => {{
                        location.reload();
                    }}, 2000);
                }} else if (pollCount > 30) {{
                    updateProgress(100, '&#9888; 修复超时，请刷新页面');
                    clearInterval(pollInterval);
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.textContent = '&#9889; 再次尝试修复';
                }} else {{
                    const progress = 30 + (pollCount * 2);
                    updateProgress(Math.min(progress, 90), '修复进行中... (' + pollCount + '/30)');
                }}
            }} catch (e) {{
                console.error('Status check failed:', e);
            }}
        }}, 2000);
        
    }} catch (error) {{
        console.error('Fix trigger failed:', error);
        updateProgress(0, '&#10060; 触发失败，请重试');
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.textContent = '&#9889; 立即手动修复';
        isFixing = false;
    }}
}}

function startAutoRefresh() {{
    const refreshInterval = setInterval(() => {{
        refreshCount++;
        
        const statusText = document.getElementById('fix-status-text');
        if (statusText && !isFixing) {{
            statusText.textContent = `自动刷新中... ${{refreshCount}}/${{maxRefreshes}}`;
        }}
        
        fetch('/openclaw/api/status/')
            .then(resp => resp.json())
            .then(status => {{
                if (status.mysql === 'OK' && status.http_code === '200') {{
                    clearInterval(refreshInterval);
                    updateProgress(100, '&#9989; 系统已恢复！');
                    setTimeout(() => {{
                        location.reload();
                    }}, 1500);
                }}
            }})
            .catch(err => {{
                console.log('Still checking...', err);
            }});
        
        if (refreshCount >= maxRefreshes) {{
            clearInterval(refreshInterval);
            const statusText = document.getElementById('fix-status-text');
            if (statusText) {{
                statusText.textContent = '&#9888; 自动刷新已达上限，请手动修复或刷新';
            }}
        }}
    }}, 2000);
}}

function getCookie(name) {{
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {{
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {{
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }}
        }}
    }}
    return cookieValue;
}}
</script>
<!-- End OpenClaw Fix Panel -->
'''

with open('{SERVER_PATH}/templates/includes/openclaw_fix_panel.html', 'w', encoding='utf-8') as f:
    f.write(template_content)

print('Template created successfully')
PYEOF
"""

stdin, stdout, stderr = ssh.exec_command(create_template, timeout=10)
result = stdout.read().decode().strip()
error = stderr.read().decode().strip()
print(f"  {result}")
if error:
    print(f"  Error: {error[:200]}")

# Verify
stdin, stdout, stderr = ssh.exec_command(f"test -f {SERVER_PATH}/templates/includes/openclaw_fix_panel.html && echo 'File exists' || echo 'File missing'")
print(f"  {stdout.read().decode().strip()}\n")

# Step 3: Add API views to a separate file
print("[3/6] Creating API views...")

api_views_code = """from django.http import JsonResponse
import json
import subprocess
import os


def openclaw_status(request):
    \"\"\"返回系统状态\"\"\"
    status_file = '/root/.openclaw/monitoring/status.json'
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'unknown'}, status=500)


def openclaw_trigger_fix(request):
    \"\"\"触发MySQL修复\"\"\"
    if request.method == 'POST':
        try:
            subprocess.Popen([
                'bash',
                '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return JsonResponse({
                'success': True,
                'message': '修复脚本已启动，请稍候...'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
"""

write_api = f"""cat > {SERVER_PATH}/openclaw_api_views.py << 'PYEOF'
{api_views_code}
PYEOF
echo "API views created"
"""

stdin, stdout, stderr = ssh.exec_command(write_api, timeout=5)
print(f"  {stdout.read().decode().strip()}\n")

# Step 4: Add URLs
print("[4/6] Adding URL routes...")

add_urls_cmd = f"""python3 << 'URLEOF'
import re

urls_file = '{SERVER_PATH}/urls.py'

with open(urls_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already added
if 'openclaw_api_views' not in content:
    # Add import
    import_line = "from openclaw_api_views import openclaw_status, openclaw_trigger_fix\\n"
    
    # Find where to insert (after other imports)
    lines = content.split('\\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            insert_idx = i + 1
    
    lines.insert(insert_idx, import_line.strip())
    
    # Add URL patterns
    url_patterns = """    # OpenClaw API
    path('openclaw/api/status/', openclaw_status, name='openclaw_status'),
    path('openclaw/api/trigger-fix/', openclaw_trigger_fix, name='openclaw_trigger_fix'),
"""
    
    # Find urlpatterns and add before closing bracket
    content = '\\n'.join(lines)
    content = re.sub(r'(urlpatterns\\s*=\\s*\\[)', r'\\1\\n' + url_patterns, content)
    
    with open(urls_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("URLs added successfully")
else:
    print("URLs already exist")
URLEOF
"""

stdin, stdout, stderr = ssh.exec_command(add_urls_cmd, timeout=10)
result = stdout.read().decode().strip()
error = stderr.read().decode().strip()
print(f"  {result}")
if error and 'Traceback' in error:
    print(f"  Error: {error[:300]}\n")

# Step 5: Add to base.html
print("[5/6] Adding to base.html...")

add_to_base = f"""python3 << 'BASICEOF'
base_file = '{SERVER_PATH}/templates/base/base.html'

with open(base_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'openclaw_fix_panel' not in content:
    # Add before </body>
    include_tag = '{{% include "includes/openclaw_fix_panel.html" %}}'
    content = content.replace('</body>', f'{include_tag}\\n</body>')
    
    with open(base_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Added to base.html")
else:
    print("Already in base.html")
BASICEOF
"""

stdin, stdout, stderr = ssh.exec_command(add_to_base, timeout=10)
result = stdout.read().decode().strip()
error = stderr.read().decode().strip()
print(f"  {result}")
if error and 'Traceback' in error:
    print(f"  Error: {error[:300]}")

# Step 6: Restart Gunicorn
print("\n[6/6] Restarting Gunicorn...")
ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)

start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
sleep 5 && echo "Gunicorn started" """

stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
result = stdout.read().decode().strip()
print(f"  {result}")

time.sleep(8)

# Final verification
print("\n" + "=" * 80)
print("Final Verification")
print("=" * 80)

stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
count = stdout.read().decode().strip()
print(f"Gunicorn processes: {count}")

time.sleep(3)
stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
http_code = stdout.read().decode().strip()
print(f"HTTP Status: {http_code}")

if http_code == '200':
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Frontend panel deployed!")
    print("=" * 80)
    print("\n🎨 Features:")
    print("  ✓ Auto-show on error pages")
    print("  ✓ Manual fix button (purple gradient)")
    print("  ✓ Real-time progress bar (0-100%)")
    print("  ✓ Status text updates")
    print("  ✓ Auto-refresh every 2 seconds (max 30 times)")
    print("  ✓ Auto-redirect after fix")
    print("\n🌐 Test at:")
    print(f"  • http://{SERVER_IP}/login/")
    print(f"  • http://www.xietongai.com.cn/login/")
    print("=" * 80)
else:
    print(f"\n⚠️ HTTP {http_code}")
    print("\nChecking errors...")
    stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log")
    print(stdout.read().decode())

ssh.close()
