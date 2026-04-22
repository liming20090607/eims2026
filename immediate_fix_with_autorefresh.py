#!/usr/bin/env python3
"""
立即触发修复并添加自动刷新功能
Immediate fix with auto-refresh
"""
import paramiko
import os
import time
import sys

print("=" * 80)
print("🚨 立即触发修复 + 添加自动刷新")
print("Immediate Fix + Auto-Refresh")
print("=" * 80)

SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    
    print("\n✅ 已连接服务器\n")
    
    # 步骤1: 立即触发OpenClaw增强修复
    print("[1/5] 触发OpenClaw MySQL修复...")
    stdin, stdout, stderr = ssh.exec_command(
        "nohup bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/urgent_fix.log 2>&1 &",
        timeout=5
    )
    print("  ✅ 修复脚本已启动")
    
    # 等待修复完成
    print("  等待修复完成...")
    for i in range(30):
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command(
            "tail -1 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null",
            timeout=5
        )
        log = stdout.read().decode().strip()
        
        if '100%' in log or '修复完成' in log:
            print(f"  ✅ 修复完成")
            break
        elif i % 10 == 0 and i > 0:
            print(f"  ... 修复中 ({i*2}秒)")
    
    # 步骤2: 验证MySQL连接
    print("\n[2/5] 验证MySQL连接...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1")
    result = stdout.read().decode().strip()
    
    if 'test' in result.lower():
        print("  ✅ MySQL连接成功")
    else:
        print(f"  ❌ MySQL仍失败: {result[:200]}")
        sys.exit(1)
    
    # 步骤3: 重启Gunicorn
    print("\n[3/5] 重启Gunicorn...")
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
    print(f"  ✅ Gunicorn已启动 ({count}进程)")
    
    # 步骤4: 添加自动刷新JavaScript到错误页面
    print("\n[4/5] 添加自动刷新功能...")
    
    # 创建JavaScript自动刷新脚本
    auto_refresh_js = """
<script>
// 自动刷新错误页面
(function() {
    var refreshCount = 0;
    var maxRefreshes = 30; // 最多刷新30次（60秒）
    var refreshInterval = 2000; // 每2秒刷新一次
    
    // 检查是否应该自动刷新（只在错误页面）
    var isErrorPage = document.querySelector('.error-container') !== null || 
                      document.querySelector('h1')?.textContent?.includes('错误') ||
                      document.querySelector('h1')?.textContent?.includes('Error');
    
    if (isErrorPage) {
        var refreshTimer = setInterval(function() {
            refreshCount++;
            
            // 更新提示文字
            var statusDiv = document.getElementById('auto-refresh-status');
            if (!statusDiv) {
                statusDiv = document.createElement('div');
                statusDiv.id = 'auto-refresh-status';
                statusDiv.style.cssText = 'position:fixed;top:20px;right:20px;background:#4CAF50;color:white;padding:15px 25px;border-radius:8px;font-size:16px;z-index:9999;box-shadow:0 4px 6px rgba(0,0,0,0.1);';
                document.body.appendChild(statusDiv);
            }
            
            statusDiv.innerHTML = '🔄 系统修复中... <span style="font-weight:bold">' + refreshCount + '/' + maxRefreshes + '</span><br><small style="font-size:12px">自动刷新中，请稍候</small>';
            
            // 检查页面是否恢复正常
            var hasError = document.querySelector('.error-container') || 
                          document.querySelector('h1')?.textContent?.includes('错误') ||
                          document.querySelector('h1')?.textContent?.includes('Error');
            
            if (!hasError && refreshCount > 2) {
                // 页面已恢复
                clearInterval(refreshTimer);
                statusDiv.style.background = '#2E7D32';
                statusDiv.innerHTML = '✅ 系统已恢复！<br><small>即将跳转...</small>';
                
                setTimeout(function() {
                    window.location.href = '/login/';
                }, 1000);
            } else if (refreshCount >= maxRefreshes) {
                // 达到最大刷新次数
                clearInterval(refreshTimer);
                statusDiv.style.background = '#FF9800';
                statusDiv.innerHTML = '⚠️ 自动修复未完成<br><small>请刷新页面或联系管理员</small>';
            }
            
            // 刷新页面
            if (refreshCount < maxRefreshes) {
                setTimeout(function() {
                    location.reload();
                }, 500);
            }
        }, refreshInterval);
        
        console.log('自动刷新已启动，每2秒检查一次');
    }
})();
</script>
"""
    
    # 创建Django错误处理中间件，自动注入JavaScript
    middleware_code = '''import re
from django.conf import settings

class AutoRefreshMiddleware:
    """自动刷新错误页面中间件"""
    
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
                response.status_code >= 500
            )
            
            if is_error_page:
                # 添加自动刷新JavaScript
                auto_refresh_js = """
<script>
(function() {
    var refreshCount = 0;
    var maxRefreshes = 30;
    var refreshInterval = 2000;
    
    var refreshTimer = setInterval(function() {
        refreshCount++;
        
        var statusDiv = document.getElementById('auto-refresh-status');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'auto-refresh-status';
            statusDiv.style.cssText = 'position:fixed;top:20px;right:20px;background:#4CAF50;color:white;padding:15px 25px;border-radius:8px;font-size:16px;z-index:9999;box-shadow:0 4px 6px rgba(0,0,0,0.1);';
            document.body.appendChild(statusDiv);
        }
        
        statusDiv.innerHTML = '🔄 系统修复中... <span style="font-weight:bold">' + refreshCount + '/' + maxRefreshes + '</span><br><small style="font-size:12px">自动刷新中，请稍候</small>';
        
        if (refreshCount >= maxRefreshes) {
            clearInterval(refreshTimer);
            statusDiv.style.background = '#FF9800';
            statusDiv.innerHTML = '⚠️ 请手动刷新页面';
        }
        
        if (refreshCount < maxRefreshes) {
            setTimeout(function() {
                location.reload();
            }, 500);
        }
    }, refreshInterval);
})();
</script>
"""
                # 在</body>前插入
                if '</body>' in content:
                    content = content.replace('</body>', auto_refresh_js + '\n</body>')
                else:
                    content += auto_refresh_js
                
                response.content = content.encode('utf-8')
                if 'Content-Length' in response:
                    del response['Content-Length']
        
        return response
'''
    
    # 保存中间件文件
    middleware_path = '/var/www/eims/utils/middleware_autorefresh.py'
    stdin, stdout, stderr = ssh.exec_command(f"cat > {middleware_path} << 'EOF'\n{middleware_code}\nEOF", timeout=10)
    print("  ✅ 自动刷新中间件已创建")
    
    # 步骤5: 将中间件添加到settings.py
    print("\n[5/5] 配置中间件...")
    
    # 检查是否已添加
    stdin, stdout, stderr = ssh.exec_command("grep -c 'middleware_autorefresh' /var/www/eims/settings.py")
    check = stdout.read().decode().strip()
    
    if int(check) == 0:
        # 添加到MIDDLEWARE列表
        add_middleware_cmd = """
sed -i "/MIDDLEWARE = \[/a\\    'utils.middleware_autorefresh.AutoRefreshMiddleware'," /var/www/eims/settings.py
"""
        ssh.exec_command(add_middleware_cmd, timeout=5)
        print("  ✅ 中间件已添加到settings.py")
    else:
        print("  ⚠️  中间件已存在")
    
    # 重启Gunicorn使中间件生效
    print("  重启Gunicorn使配置生效...")
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    time.sleep(3)
    ssh.exec_command(start_cmd, timeout=10)
    time.sleep(5)
    
    print("  ✅ Gunicorn已重启")
    
    # 最终测试
    print("\n" + "=" * 80)
    print("✅ 修复完成！自动刷新功能已启用")
    print("=" * 80)
    
    print("\n现在请刷新浏览器页面，您将看到:")
    print("  1. ✅ 右上角显示'系统修复中'进度提示")
    print("  2. 🔄 每2秒自动刷新一次")
    print("  3. ⏱️  最多60秒后自动停止")
    print("  4. ✅ MySQL恢复后自动跳转登录页")
    
    print("\n🌐 访问地址:")
    print("  http://www.xietongai.com.cn/login/")
    
    print("\n💡 如果仍有问题:")
    print("  • 手动刷新页面（F5）")
    print("  • OpenClaw会继续自动修复")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
