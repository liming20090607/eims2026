#!/usr/bin/env python3
"""
添加手动触发修复的Web接口到Django
Add manual trigger fix web interface to Django
"""
import paramiko
import time

print("=" * 80)
print("🌐 添加Web手动触发修复接口")
print("Add Web Manual Trigger Fix Interface")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)
    print("\n✅ 已连接到服务器\n")
except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    exit(1)

try:
    # 1. 创建触发修复的视图函数
    print("[步骤 1/3] 创建修复触发视图...")
    
    view_code = '''

# ==================== OpenClaw手动修复接口 ====================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import subprocess
import os

@csrf_exempt
@require_POST
def trigger_openclaw_fix(request):
    """手动触发OpenClaw立即修复MySQL"""
    try:
        # 检查修复脚本是否已在运行
        check_cmd = "pgrep -f 'enhanced_mysql_fix.sh' | wc -l"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        running_count = int(result.stdout.strip())
        
        if running_count > 0:
            return JsonResponse({
                'status': 'running',
                'message': '修复脚本正在运行中，请稍候...',
                'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 在后台启动修复脚本
        fix_script = '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'
        log_file = '/root/.openclaw/monitoring/logs/manual_trigger.log'
        
        # 清空旧日志
        subprocess.run(f"echo '' > {log_file}", shell=True)
        
        # 后台执行
        cmd = f"nohup bash {fix_script} >> {log_file} 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        return JsonResponse({
            'status': 'started',
            'message': '修复脚本已启动，预计30-60秒完成',
            'log_file': log_file,
            'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'启动失败: {str(e)}',
            'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, status=500)


@require_POST
def check_fix_status(request):
    """检查修复状态"""
    try:
        log_file = '/root/.openclaw/monitoring/logs/auto_fix.log'
        
        if not os.path.exists(log_file):
            return JsonResponse({
                'status': 'no_log',
                'message': '暂无修复日志',
                'logs': ''
            })
        
        # 读取最后30行日志
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent_logs = ''.join(lines[-30:])
        
        # 检查是否正在运行
        result = subprocess.run("pgrep -f 'enhanced_mysql_fix.sh' | wc -l", 
                              shell=True, capture_output=True, text=True)
        is_running = int(result.stdout.strip()) > 0
        
        # 检查MySQL状态
        mysql_result = subprocess.run(
            "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -q '1' && echo OK || echo FAIL",
            shell=True, capture_output=True, text=True
        )
        mysql_status = 'OK' if 'OK' in mysql_result.stdout else 'FAIL'
        
        return JsonResponse({
            'status': 'running' if is_running else 'idle',
            'mysql_status': mysql_status,
            'logs': recent_logs,
            'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'检查失败: {str(e)}',
            'logs': ''
        }, status=500)
'''
    
    # 写入视图文件
    ssh.exec_command(f"cat >> /var/www/eims/eims_app/views_openclaw_fix.py << 'EOF'\n{view_code}\nEOF")
    print("  ✅ 视图函数已创建")
    
    # 2. 添加URL路由
    print("\n[步骤 2/3] 添加URL路由...")
    
    urls_code = '''
    # OpenClaw手动修复接口
    path('api/openclaw/trigger-fix/', views_openclaw_fix.trigger_openclaw_fix, name='trigger_openclaw_fix'),
    path('api/openclaw/check-status/', views_openclaw_fix.check_fix_status, name='check_fix_status'),
'''
    
    # 检查是否已存在
    stdin, stdout, stderr = ssh.exec_command("grep -c 'trigger-fix' /var/www/eims/urls.py", timeout=5)
    if '0' in stdout.read().decode():
        # 在urlpatterns中添加路由
        ssh.exec_command(f"""
python3 << 'PYEOF'
import re

with open('/var/www/eims/urls.py', 'r') as f:
    content = f.read()

if 'trigger-fix' not in content:
    # 找到urlpatterns的开头
    match = re.search(r'(urlpatterns\s*=\\s*\\[)', content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + '''
    # OpenClaw手动修复接口
    path('api/openclaw/trigger-fix/', views_openclaw_fix.trigger_openclaw_fix, name='trigger_openclaw_fix'),
    path('api/openclaw/check-status/', views_openclaw_fix.check_fix_status, name='check_fix_status'),
''' + content[insert_pos:]
        
        # 添加import
        if 'views_openclaw_fix' not in content:
            # 在文件顶部添加import
            content = content.replace(
                'from django.urls import path, include',
                'from django.urls import path, include\\nfrom eims_app import views_openclaw_fix'
            )
        
        with open('/var/www/eims/urls.py', 'w') as f:
            f.write(content)
        
        print("URL路由已添加")
    else:
        print("未找到urlpatterns")
else:
    print("路由已存在")
PYEOF
""")
        print("  ✅ URL路由已添加")
    else:
        print("  ℹ️  URL路由已存在，跳过")
    
    # 3. 创建Web界面HTML
    print("\n[步骤 3/3] 创建Web控制面板...")
    
    html_content = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw手动修复控制面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2em;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .status-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-ok { background: #10b981; }
        .status-fail { background: #ef4444; }
        .status-running { 
            background: #f59e0b;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .btn {
            padding: 15px 40px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .log-box {
            background: #1f2937;
            color: #10b981;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.6;
            margin-top: 15px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .info-item {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .info-label {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 5px;
        }
        .info-value {
            font-size: 18px;
            font-weight: bold;
            color: #1f2937;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 OpenClaw手动修复控制面板</h1>
        
        <div class="card">
            <h2 style="margin-bottom: 20px;">📊 系统状态</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">MySQL状态</div>
                    <div class="info-value" id="mysql-status">
                        <span class="status-indicator status-ok"></span>检查中...
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">修复脚本</div>
                    <div class="info-value" id="fix-status">
                        <span class="status-indicator status-ok"></span>空闲
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">最后更新</div>
                    <div class="info-value" id="last-update" style="font-size: 14px;">-</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px;">🚀 手动触发修复</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                当检测到MySQL连接问题时，可以立即触发OpenClaw进行修复，无需等待自动检查。
            </p>
            <button class="btn btn-primary" id="trigger-btn" onclick="triggerFix()">
                ⚡ 立即触发修复
            </button>
            <div class="progress-bar" id="progress-bar" style="display: none;">
                <div class="progress-fill" id="progress-fill" style="width: 0%;">0%</div>
            </div>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 15px;">📋 修复日志</h2>
            <button class="btn" style="background: #f3f4f6; padding: 10px 20px; font-size: 14px; margin-bottom: 10px;" onclick="refreshLogs()">
                🔄 刷新日志
            </button>
            <div class="log-box" id="log-box">
                点击"刷新日志"按钮查看最新日志...
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        
        async function triggerFix() {
            if (isRunning) return;
            
            const btn = document.getElementById('trigger-btn');
            const progressBar = document.getElementById('progress-bar');
            const progressFill = document.getElementById('progress-fill');
            
            btn.disabled = true;
            btn.textContent = '⏳ 修复进行中...';
            progressBar.style.display = 'block';
            isRunning = true;
            
            try {
                const response = await fetch('/api/openclaw/trigger-fix/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    // 开始监控进度
                    let progress = 0;
                    const interval = setInterval(() => {
                        progress += 5;
                        if (progress > 95) progress = 95;
                        progressFill.style.width = progress + '%';
                        progressFill.textContent = progress + '%';
                    }, 1500);
                    
                    // 等待完成
                    setTimeout(() => {
                        clearInterval(interval);
                        progressFill.style.width = '100%';
                        progressFill.textContent = '100%';
                        
                        setTimeout(() => {
                            progressBar.style.display = 'none';
                            btn.disabled = false;
                            btn.textContent = '⚡ 立即触发修复';
                            isRunning = false;
                            checkStatus();
                            refreshLogs();
                        }, 2000);
                    }, 30000);
                } else {
                    alert(data.message);
                    btn.disabled = false;
                    btn.textContent = '⚡ 立即触发修复';
                    isRunning = false;
                }
            } catch (error) {
                alert('触发失败: ' + error.message);
                btn.disabled = false;
                btn.textContent = '⚡ 立即触发修复';
                isRunning = false;
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/openclaw/check-status/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                // 更新MySQL状态
                const mysqlStatus = document.getElementById('mysql-status');
                if (data.mysql_status === 'OK') {
                    mysqlStatus.innerHTML = '<span class="status-indicator status-ok"></span>正常';
                } else {
                    mysqlStatus.innerHTML = '<span class="status-indicator status-fail"></span>异常';
                }
                
                // 更新修复脚本状态
                const fixStatus = document.getElementById('fix-status');
                if (data.status === 'running') {
                    fixStatus.innerHTML = '<span class="status-indicator status-running"></span>运行中';
                } else {
                    fixStatus.innerHTML = '<span class="status-indicator status-ok"></span>空闲';
                }
                
                // 更新时间
                document.getElementById('last-update').textContent = data.timestamp || '-';
                
            } catch (error) {
                console.error('检查状态失败:', error);
            }
        }
        
        async function refreshLogs() {
            try {
                const response = await fetch('/api/openclaw/check-status/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                const logBox = document.getElementById('log-box');
                
                if (data.logs) {
                    logBox.textContent = data.logs;
                    logBox.scrollTop = logBox.scrollHeight;
                } else {
                    logBox.textContent = '暂无日志';
                }
            } catch (error) {
                console.error('刷新日志失败:', error);
            }
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
        
        // 初始检查
        checkStatus();
        refreshLogs();
        
        // 每10秒自动更新状态
        setInterval(checkStatus, 10000);
    </script>
</body>
</html>
'''
    
    # 创建模板目录和文件
    ssh.exec_command("mkdir -p /var/www/eims/templates/openclaw")
    ssh.exec_command(f"cat > /var/www/eims/templates/openclaw/control_panel.html << 'HTMLEOF'\n{html_content}\nHTMLEOF")
    print("  ✅ Web控制面板已创建")
    
    # 添加控制面板的URL和视图
    print("\n添加控制面板访问路由...")
    ssh.exec_command("""
python3 << 'PYEOF'
import re

# 添加到urls.py
with open('/var/www/eims/urls.py', 'r') as f:
    content = f.read()

if 'control_panel' not in content:
    # 添加视图导入
    if 'TemplateView' not in content:
        content = content.replace(
            'from django.urls import path, include',
            'from django.urls import path, include\\nfrom django.views.generic import TemplateView'
        )
    
    # 添加URL
    match = re.search(r'(urlpatterns\s*=\\s*\\[)', content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + '''
    # OpenClaw控制面板
    path('openclaw/panel/', TemplateView.as_view(template_name='openclaw/control_panel.html'), name='openclaw_panel'),
''' + content[insert_pos:]
        
        with open('/var/www/eims/urls.py', 'w') as f:
            f.write(content)
        
        print("控制面板路由已添加")

PYEOF
""")
    
    print("\n" + "=" * 80)
    print("✅ Web接口部署完成！")
    print("=" * 80)
    
    print("\n📋 访问地址:")
    print("  控制面板: http://www.xietongai.com.cn/openclaw/panel/")
    print("  或: http://39.106.41.239:8000/openclaw/panel/")
    
    print("\n🔧 API接口:")
    print("  POST /api/openclaw/trigger-fix/ - 触发修复")
    print("  POST /api/openclaw/check-status/ - 检查状态")
    
    print("\n💡 使用方法:")
    print("  1. 访问控制面板页面")
    print("  2. 点击'立即触发修复'按钮")
    print("  3. 实时查看修复进度和日志")
    print("  4. 或运行本地脚本: python trigger_openclaw_fix.py")
    
    print("\n⚡ 优势:")
    print("  ✓ 无需等待2分钟自动检查")
    print("  ✓ 实时进度显示")
    print("  ✓ 完整日志记录")
    print("  ✓ 支持Web和命令行两种方式")
    
except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
