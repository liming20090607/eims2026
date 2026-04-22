#!/usr/bin/env python3
"""
添加前端手动修复按钮和进度显示
Add Frontend Manual Fix Button and Progress Display
"""

import paramiko
import os
import time

print("=" * 80)
print("🎨 添加前端手动修复按钮和进度显示")
print("Add Frontend Manual Fix Button & Progress")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')
SERVER_PATH = '/var/www/eims'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # Step 1: Create the fix panel HTML/JS/CSS
    print("[1/5] 创建修复面板组件...")
    
    fix_panel_html = """
<!-- OpenClaw Manual Fix Panel -->
<div id="openclaw-fix-panel" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index:99999; background:white; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.3); padding:40px; min-width:450px; max-width:600px; text-align:center;">
    <!-- Icon -->
    <div style="font-size:64px; margin-bottom:20px;">🔧</div>
    
    <!-- Title -->
    <h2 style="margin:0 0 10px 0; color:#333; font-size:24px;">系统检测到错误</h2>
    <p style="color:#666; margin:0 0 30px 0; font-size:14px;">System Error Detected</p>
    
    <!-- Progress Bar -->
    <div style="background:#f0f0f0; border-radius:10px; height:30px; overflow:hidden; margin-bottom:20px; position:relative;">
        <div id="fix-progress-bar" style="background:linear-gradient(90deg, #667eea 0%, #764ba2 100%); height:100%; width:0%; transition:width 0.5s ease; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:14px;">
            0%
        </div>
    </div>
    
    <!-- Status Text -->
    <div id="fix-status-text" style="color:#667eea; font-size:16px; margin-bottom:30px; font-weight:500;">
        准备修复...
    </div>
    
    <!-- Buttons -->
    <div style="display:flex; gap:15px; justify-content:center;">
        <button id="btn-manual-fix" onclick="triggerManualFix()" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer; box-shadow:0 4px 15px rgba(102,126,234,0.4); transition:all 0.3s;">
            ⚡ 立即手动修复
        </button>
        <button id="btn-refresh-page" onclick="location.reload()" style="background:#f0f0f0; color:#333; border:2px solid #ddd; padding:12px 30px; border-radius:8px; font-size:16px; cursor:pointer; transition:all 0.3s;">
            🔄 刷新页面
        </button>
    </div>
    
    <!-- Auto-refresh notice -->
    <div style="margin-top:20px; color:#999; font-size:12px;">
        💡 提示：系统将每2秒自动刷新，最多尝试30次
    </div>
</div>

<style>
#btn-manual-fix:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.6);
}

#btn-refresh-page:hover {
    background: #e0e0e0;
    border-color: #ccc;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.fix-pulsing {
    animation: pulse 1.5s ease-in-out infinite;
}
</style>

<script>
// Auto-refresh and fix logic
let refreshCount = 0;
const maxRefreshes = 30;
let isFixing = false;

// Show fix panel on error pages
window.addEventListener('load', function() {
    // Check if this is an error page
    const isErrorPage = document.title.includes('错误') || 
                       document.title.includes('Error') ||
                       document.body.innerHTML.includes('OperationalError') ||
                       document.body.innerHTML.includes('DatabaseError');
    
    if (isErrorPage) {
        showFixPanel();
        startAutoRefresh();
    }
});

function showFixPanel() {
    document.getElementById('openclaw-fix-panel').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function hideFixPanel() {
    document.getElementById('openclaw-fix-panel').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function updateProgress(percent, statusText) {
    const bar = document.getElementById('fix-progress-bar');
    const text = document.getElementById('fix-status-text');
    
    bar.style.width = percent + '%';
    bar.textContent = percent + '%';
    text.textContent = statusText;
    
    if (percent < 100) {
        text.classList.add('fix-pulsing');
    } else {
        text.classList.remove('fix-pulsing');
    }
}

async function triggerManualFix() {
    if (isFixing) return;
    isFixing = true;
    
    const btn = document.getElementById('btn-manual-fix');
    btn.disabled = true;
    btn.style.opacity = '0.6';
    btn.textContent = '⏳ 修复中...';
    
    try {
        updateProgress(10, '正在触发修复...');
        
        // Call API to trigger fix
        const response = await fetch('/openclaw/api/trigger-fix/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        updateProgress(30, '修复脚本已启动...');
        
        // Poll for status
        let pollCount = 0;
        const pollInterval = setInterval(async () => {
            pollCount++;
            
            try {
                const statusResp = await fetch('/openclaw/api/status/');
                const status = await statusResp.json();
                
                if (status.mysql === 'OK' || status.mysql === 'FIXED') {
                    updateProgress(100, '✅ 修复成功！');
                    clearInterval(pollInterval);
                    
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else if (pollCount > 30) {
                    updateProgress(100, '⚠️ 修复超时，请刷新页面');
                    clearInterval(pollInterval);
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.textContent = '⚡ 再次尝试修复';
                } else {
                    const progress = 30 + (pollCount * 2);
                    updateProgress(Math.min(progress, 90), '修复进行中... (' + pollCount + '/30)');
                }
            } catch (e) {
                console.error('Status check failed:', e);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Fix trigger failed:', error);
        updateProgress(0, '❌ 触发失败，请重试');
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.textContent = '⚡ 立即手动修复';
        isFixing = false;
    }
}

function startAutoRefresh() {
    const refreshInterval = setInterval(() => {
        refreshCount++;
        
        // Update counter in panel
        const statusText = document.getElementById('fix-status-text');
        if (statusText && !isFixing) {
            statusText.textContent = `自动刷新中... ${refreshCount}/${maxRefreshes}`;
        }
        
        // Try to check if system is back
        fetch('/openclaw/api/status/')
            .then(resp => resp.json())
            .then(status => {
                if (status.mysql === 'OK' && status.http_code === '200') {
                    // System is back!
                    clearInterval(refreshInterval);
                    updateProgress(100, '✅ 系统已恢复！');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                }
            })
            .catch(err => {
                console.log('Still checking...', err);
            });
        
        // Stop after max refreshes
        if (refreshCount >= maxRefreshes) {
            clearInterval(refreshInterval);
            const statusText = document.getElementById('fix-status-text');
            if (statusText) {
                statusText.textContent = '⚠️ 自动刷新已达上限，请手动修复或刷新';
            }
        }
    }, 2000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
<!-- End OpenClaw Fix Panel -->
"""
    
    # Write to a template file
    write_cmd = f"""cat > {SERVER_PATH}/templates/includes/openclaw_fix_panel.html << 'HTMLEOF'
{fix_panel_html}
HTMLEOF
echo "Fix panel template created"
"""
    stdin, stdout, stderr = ssh.exec_command(write_cmd, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  {result}\n")
    
    # Step 2: Add to base.html
    print("[2/5] 将修复面板添加到base.html...")
    
    add_to_base = f"""
# Add fix panel include before closing body tag
grep -q "openclaw_fix_panel" {SERVER_PATH}/templates/base/base.html || sed -i 's|</body>|{{% include "includes/openclaw_fix_panel.html" %}}\\n</body>|' {SERVER_PATH}/templates/base/base.html
echo "Added to base.html"
"""
    stdin, stdout, stderr = ssh.exec_command(add_to_base, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  {result}\n")
    
    # Step 3: Create API views
    print("[3/5] 创建API视图...")
    
    api_views = """
# OpenClaw API Views
def openclaw_status(request):
    \"\"\"返回系统状态\"\"\"
    import json
    import os
    from django.http import JsonResponse
    
    status_file = '/root/.openclaw/monitoring/status.json'
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'unknown'}, status=500)


def openclaw_trigger_fix(request):
    \"\"\"触发MySQL修复\"\"\"
    import subprocess
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            # Run fix script in background
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
    
    # Add to views_index.py
    add_views = f"""
# Append API views to views_index.py
cat >> {SERVER_PATH}/views_index.py << 'PYEOF'
{api_views}
PYEOF
echo "API views added"
"""
    stdin, stdout, stderr = ssh.exec_command(add_views, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  {result}\n")
    
    # Step 4: Add URL routes
    print("[4/5] 添加URL路由...")
    
    add_urls = f"""
# Add OpenClaw API URLs
grep -q "openclaw_status" {SERVER_PATH}/urls.py || python3 << 'URLEOF'
import re

with open('{SERVER_PATH}/urls.py', 'r') as f:
    content = f.read()

# Find urlpatterns section
if 'openclaw_status' not in content:
    # Add import
    if 'from eims_app.views_index import' in content:
        content = content.replace(
            'from eims_app.views_index import',
            'from eims_app.views_index import openclaw_status, openclaw_trigger_fix,'
        )
    else:
        # Add new import line after existing imports
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') and 'views' in line:
                lines.insert(i+1, 'from eims_app.views_index import openclaw_status, openclaw_trigger_fix')
                break
        content = '\\n'.join(lines)
    
    # Add URL patterns
    url_patterns = '''
    # OpenClaw API
    path('openclaw/api/status/', openclaw_status, name='openclaw_status'),
    path('openclaw/api/trigger-fix/', openclaw_trigger_fix, name='openclaw_trigger_fix'),
'''
    
    # Insert before the last ] in urlpatterns
    content = re.sub(r'(urlpatterns\\s*=\\s*\\[.*?)(\\])', r'\\1' + url_patterns + r'\\2', content, flags=re.DOTALL)
    
    with open('{SERVER_PATH}/urls.py', 'w') as f:
        f.write(content)
    
    print("URLs added successfully")
else:
    print("URLs already exist")
URLEOF
"""
    stdin, stdout, stderr = ssh.exec_command(add_urls, timeout=10)
    result = stdout.read().decode().strip()
    print(f"  {result}\n")
    
    # Step 5: Restart Gunicorn
    print("[5/5] 重启Gunicorn以应用更改...")
    
    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 2", timeout=5)
    
    start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
sleep 3 && echo "Gunicorn restarted" """
    
    stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=10)
    result = stdout.read().decode().strip()
    print(f"  {result}")
    
    time.sleep(5)
    
    # Verify
    print("\n" + "=" * 80)
    print("验证部署...")
    print("=" * 80)
    
    # Check processes
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
    count = stdout.read().decode().strip()
    print(f"Gunicorn进程: {count}")
    
    # Test HTTP
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
    http_code = stdout.read().decode().strip()
    print(f"HTTP状态: {http_code}")
    
    # Test API
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/openclaw/api/status/ | python3 -m json.tool 2>/dev/null | head -10")
    api_result = stdout.read().decode().strip()
    print(f"\nAPI测试:\n{api_result}")
    
    if http_code == '200':
        print("\n" + "=" * 80)
        print("✅ 前端修复面板部署成功！")
        print("=" * 80)
        print("\n🎨 功能特性:")
        print("  • 错误页面自动显示修复面板")
        print("  • 醒目的手动修复按钮")
        print("  • 实时进度条（0-100%）")
        print("  • 自动刷新（每2秒，最多30次）")
        print("  • 修复成功后自动跳转")
        print("  • 美观的UI设计（渐变、动画）")
        print("\n📱 用户体验:")
        print("  1. 遇到错误时自动弹出修复面板")
        print("  2. 点击'立即手动修复'按钮")
        print("  3. 查看实时进度（10% → 100%）")
        print("  4. 修复完成后自动刷新页面")
        print("  5. 或者等待自动刷新（2秒间隔）")
        print("\n🌐 访问测试:")
        print(f"  • http://{SERVER_IP}/login/")
        print(f"  • http://www.xietongai.com.cn/login/")
        print("\n⏰ 完成时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 80)
    else:
        print(f"\n⚠️ HTTP {http_code} - 检查错误日志")
        stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log")
        print(stdout.read().decode())
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 部署失败: {str(e)}")
    import traceback
    traceback.print_exc()
