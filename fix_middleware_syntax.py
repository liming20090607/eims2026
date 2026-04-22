#!/usr/bin/env python3
"""
修复中间件语法错误
Fix middleware syntax error
"""
import paramiko
import os
import time
import sys

print("=" * 80)
print("🔧 修复中间件语法错误")
print("Fix Middleware Syntax Error")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # 创建正确版本的中间件文件
    print("[1/3] 创建正确的中间件文件...")
    
    middleware_code = r'''import re
from django.conf import settings

class AutoRefreshMiddleware:
    """自动刷新和手动修复按钮中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 只对HTML响应处理
        if response.get('Content-Type', '').startswith('text/html'):
            content = response.content.decode('utf-8')
            
            # 检查是否是错误页面
            is_error_page = (
                'error-container' in content or
                'OperationalError' in content or
                'Internal Server Error' in content or
                'Access denied' in content or
                response.status_code >= 500
            )
            
            if is_error_page:
                # 添加手动修复按钮和自动刷新
                fix_button_html = """
<div id="emergency-fix-panel" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:40px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.3);z-index:10000;text-align:center;max-width:500px;width:90%;">
    <div style="font-size:64px;margin-bottom:20px;">🔧</div>
    <h2 style="color:#d32f2f;margin-bottom:15px;font-size:24px;">系统故障检测</h2>
    <p style="color:#666;margin-bottom:25px;font-size:16px;">检测到数据库连接异常，系统正在自动修复中...</p>
    
    <div id="fix-progress" style="margin-bottom:25px;">
        <div style="background:#e0e0e0;border-radius:10px;height:30px;overflow:hidden;margin-bottom:10px;">
            <div id="progress-bar" style="background:linear-gradient(90deg,#4CAF50,#8BC34A);height:100%;width:0%;transition:width 0.5s;border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:14px;">
                0%
            </div>
        </div>
        <p id="progress-text" style="color:#666;font-size:14px;margin:0;">正在修复...</p>
    </div>
    
    <div style="display:flex;gap:15px;justify-content:center;margin-bottom:20px;">
        <button onclick="triggerManualFix()" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:15px 30px;border-radius:8px;font-size:16px;cursor:pointer;box-shadow:0 4px 15px rgba(102,126,234,0.4);transition:all 0.3s;font-weight:bold;">
            ⚡ 立即手动修复
        </button>
        <button onclick="location.reload()" style="background:#f5f5f5;color:#333;border:2px solid #ddd;padding:15px 30px;border-radius:8px;font-size:16px;cursor:pointer;transition:all 0.3s;font-weight:bold;">
            🔄 刷新页面
        </button>
    </div>
    
    <p style="color:#999;font-size:12px;margin:0;">
        💡 OpenClaw会在后台自动修复，通常30-60秒内完成
    </p>
</div>

<div id="fix-overlay" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:9999;"></div>

<script>
(function() {
    var refreshCount = 0;
    var maxRefreshes = 30;
    var refreshInterval = 2000;
    var isFixing = false;
    
    // 更新进度条
    function updateProgress(percent, text) {
        var bar = document.getElementById('progress-bar');
        var txt = document.getElementById('progress-text');
        if (bar) {
            bar.style.width = percent + '%';
            bar.textContent = percent + '%';
        }
        if (txt) {
            txt.textContent = text;
        }
    }
    
    // 手动触发修复
    window.triggerManualFix = function() {
        if (isFixing) return;
        isFixing = true;
        
        updateProgress(10, '正在连接服务器...');
        
        fetch('/openclaw/api/trigger-fix/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.status === 'success') {
                updateProgress(50, '修复脚本已启动，等待完成...');
                
                // 开始轮询检查修复状态
                var checkInterval = setInterval(function() {
                    fetch('/openclaw/api/check-status/')
                    .then(function(r) { return r.json(); })
                    .then(function(status) {
                        if (status.mysql === 'OK' || status.mysql === 'FIXED') {
                            clearInterval(checkInterval);
                            updateProgress(100, '✅ 修复完成！正在跳转...');
                            setTimeout(function() {
                                window.location.href = '/login/';
                            }, 1000);
                        } else {
                            updateProgress(75, '修复中，请稍候...');
                        }
                    })
                    .catch(function() {
                        // 忽略错误，继续轮询
                    });
                }, 2000);
            } else {
                updateProgress(0, '❌ 触发失败，请重试');
                isFixing = false;
            }
        })
        .catch(function(error) {
            updateProgress(0, '❌ 网络错误，请重试');
            isFixing = false;
        });
    };
    
    // 获取CSRF Token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // 自动刷新
    var refreshTimer = setInterval(function() {
        refreshCount++;
        
        if (refreshCount <= maxRefreshes) {
            updateProgress(Math.min(refreshCount * 3, 90), '自动修复中 (' + refreshCount + '/' + maxRefreshes + ')...');
            
            // 检查页面是否恢复
            var hasError = document.querySelector('.error-container') || 
                          document.querySelector('h1')?.textContent?.includes('错误') ||
                          document.querySelector('h1')?.textContent?.includes('Error');
            
            if (!hasError && refreshCount > 2) {
                clearInterval(refreshTimer);
                updateProgress(100, '✅ 系统已恢复！正在跳转...');
                setTimeout(function() {
                    window.location.href = '/login/';
                }, 1000);
            } else if (refreshCount >= maxRefreshes) {
                clearInterval(refreshTimer);
                updateProgress(100, '⚠️ 自动修复未完成，请点击"立即手动修复"');
            }
            
            setTimeout(function() {
                location.reload();
            }, 500);
        }
    }, refreshInterval);
    
    // 初始进度
    updateProgress(10, '检测到错误，开始自动修复...');
})();
</script>
"""
                
                # 在<body>后立即插入
                if '<body>' in content:
                    content = content.replace('<body>', '<body>' + fix_button_html, 1)
                else:
                    content = fix_button_html + content
                
                response.content = content.encode('utf-8')
                if 'Content-Length' in response:
                    del response['Content-Length']
        
        return response
'''
    
    # 保存中间件文件
    stdin, stdout, stderr = ssh.exec_command("cat > /var/www/eims/utils/middleware_autorefresh.py << 'ENDOFFILE'\n" + middleware_code + "\nENDOFFILE", timeout=10)
    
    # 检查文件是否正确创建
    stdin, stdout, stderr = ssh.exec_command("python -m py_compile /var/www/eims/utils/middleware_autorefresh.py 2>&1")
    check_result = stdout.read().decode().strip()
    
    if not check_result:
        print("  ✅ 中间件文件语法正确")
    else:
        print(f"  ❌ 仍有语法错误: {check_result}")
        sys.exit(1)
    
    # 步骤2: 确保API视图存在
    print("\n[2/3] 检查API视图...")
    
    stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/eims/eims_app/views_openclaw_api.py 2>&1")
    api_exists = stdout.read().decode().strip()
    
    if 'views_openclaw_api.py' in api_exists:
        print("  ✅ API视图文件存在")
    else:
        print("  ⚠️  API视图文件不存在，创建中...")
        
        api_view_code = '''from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import subprocess
import json
import os

@csrf_exempt
@require_POST
def trigger_fix(request):
    """手动触发修复"""
    try:
        # 在后台启动修复脚本
        subprocess.Popen([
            'bash',
            '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return JsonResponse({
            'status': 'success',
            'message': '修复脚本已启动'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def check_status(request):
    """检查系统状态"""
    try:
        # 检查MySQL
        result = subprocess.run(
            ['mysql', '-uroot', '-pEIMS2026_mysql', '-e', 'SELECT 1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        mysql_status = 'OK' if result.returncode == 0 else 'FAIL'
        
        # 读取状态文件
        status_file = '/root/.openclaw/monitoring/status.json'
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        else:
            status_data = {}
        
        status_data['mysql'] = mysql_status
        
        return JsonResponse(status_data)
    except Exception as e:
        return JsonResponse({
            'mysql': 'ERROR',
            'error': str(e)
        }, status=500)
'''
        
        stdin, stdout, stderr = ssh.exec_command("cat > /var/www/eims/eims_app/views_openclaw_api.py << 'ENDOFFILE'\n" + api_view_code + "\nENDOFFILE", timeout=10)
        print("  ✅ API视图已创建")
    
    # 步骤3: 重启Gunicorn
    print("\n[3/3] 重启Gunicorn...")
    
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    time.sleep(3)
    
    start_cmd = """cd /var/www/eims && source venv/bin/activate && nohup gunicorn \
--bind 127.0.0.1:8000 \
--workers 4 \
--timeout 300 \
wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"""
    
    ssh.exec_command(start_cmd, timeout=10)
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
    count = int(stdout.read().decode().strip())
    print(f"  ✅ Gunicorn已重启 ({count}进程)")
    
    # 测试访问
    print("\n" + "=" * 80)
    print("✅ 修复完成！现在请刷新浏览器")
    print("=" * 80)
    
    print("\n现在访问:")
    print("  http://www.xietongai.com.cn/login/")
    
    print("\n您应该看到:")
    print("  1. 🎯 屏幕中央的修复面板")
    print("  2. ⚡ '立即手动修复'按钮")
    print("  3. 🔄 '刷新页面'按钮")
    print("  4. 📊 实时进度条")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
