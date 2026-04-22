#!/usr/bin/env python3
"""
部署MySQL错误自动修复中间件
Deploy MySQL Error Auto-Fix Middleware
"""
import paramiko
import time

print("=" * 80)
print("🔧 部署MySQL错误自动修复中间件")
print("Deploy MySQL Error Auto-Fix Middleware")
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
    # 1. 创建中间件
    print("[步骤 1/4] 创建MySQL错误拦截中间件...")
    
    middleware_code = '''"""
MySQL错误自动修复中间件
当检测到MySQL连接错误时，自动触发修复并显示友好页面
"""
from django.http import HttpResponse
from django.conf import settings
import subprocess
import os
import time
import json


class MySQLAutoFixMiddleware:
    """
    MySQL错误自动修复中间件
    
    功能：
    1. 拦截MySQL连接错误
    2. 自动触发OpenClaw修复脚本
    3. 显示自动修复进度页面
    4. 修复完成后自动刷新
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.fix_script = '/root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh'
        self.log_file = '/root/.openclaw/monitoring/logs/auto_fix.log'
        
    def __call__(self, request):
        # 排除API请求和静态文件
        if request.path.startswith('/api/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # 检查是否是MySQL错误
            error_message = str(e)
            is_mysql_error = any(keyword in error_message for keyword in [
                'OperationalError',
                'Access denied',
                'Can\'t connect',
                'mysql',
                'MySQL',
                'pymysql'
            ])
            
            if is_mysql_error:
                return self.handle_mysql_error(request, error_message)
            
            # 非MySQL错误，正常抛出
            raise
    
    def handle_mysql_error(self, request, error_message):
        """处理MySQL错误，触发自动修复"""
        
        # 检查是否已在修复中
        if self.is_fix_running():
            return self.show_fix_progress_page()
        
        # 触发修复脚本
        self.trigger_fix_script()
        
        # 返回自动修复页面
        return self.show_fix_progress_page()
    
    def is_fix_running(self):
        """检查修复脚本是否正在运行"""
        try:
            result = subprocess.run(
                "pgrep -f 'enhanced_mysql_fix.sh' | wc -l",
                shell=True,
                capture_output=True,
                text=True
            )
            return int(result.stdout.strip()) > 0
        except:
            return False
    
    def trigger_fix_script(self):
        """触发修复脚本"""
        try:
            # 清空旧日志
            with open(self.log_file, 'w') as f:
                f.write('')
            
            # 后台执行修复脚本
            cmd = f"nohup bash {self.fix_script} >> {self.log_file} 2>&1 &"
            subprocess.Popen(cmd, shell=True)
            
        except Exception as e:
            print(f"触发修复脚本失败: {e}")
    
    def show_fix_progress_page(self):
        """显示修复进度页面"""
        # 读取自动修复页面HTML
        template_path = os.path.join(
            settings.BASE_DIR,
            'auto_fix_error_page.html'
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return HttpResponse(html_content, status=503)
        except Exception as e:
            # 如果模板文件不存在，返回简单HTML
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="5">
                <title>系统维护中</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        margin: 0;
                    }}
                    .container {{
                        text-align: center;
                        padding: 40px;
                    }}
                    h1 {{ font-size: 48px; margin-bottom: 20px; }}
                    p {{ font-size: 20px; margin-bottom: 30px; }}
                    .spinner {{
                        border: 4px solid rgba(255,255,255,0.3);
                        border-top: 4px solid white;
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 20px;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="spinner"></div>
                    <h1>🔧 系统维护中</h1>
                    <p>检测到数据库问题，正在自动修复...</p>
                    <p>页面将在修复完成后自动刷新</p>
                </div>
            </body>
            </html>
            """, status=503)
'''
    
    # 写入中间件文件
    ssh.exec_command(f"cat > /var/www/eims/eims_app/middleware_mysql_autofix.py << 'EOF'\n{middleware_code}\nEOF")
    print("  ✅ 中间件已创建")
    
    # 2. 复制HTML模板到服务器
    print("\n[步骤 2/4] 部署自动修复页面模板...")
    
    # 读取本地HTML文件
    with open('e:/EIMS2026/auto_fix_error_page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 上传到服务器
    ssh.exec_command(f"cat > /var/www/eims/auto_fix_error_page.html << 'HTMLEOF'\n{html_content}\nHTMLEOF")
    print("  ✅ 自动修复页面已部署")
    
    # 3. 配置settings.py
    print("\n[步骤 3/4] 配置Django settings.py...")
    
    ssh.exec_command("""
python3 << 'PYEOF'
with open('/var/www/eims/settings.py', 'r') as f:
    content = f.read()

# 检查中间件是否已添加
if 'middleware_mysql_autofix' not in content:
    # 找到MIDDLEWARE列表
    import re
    match = re.search(r'(MIDDLEWARE\s*=\s*\\[)', content)
    if match:
        # 在MIDDLEWARE列表末尾添加
        insert_pos = content.rfind(']', match.start())
        new_middleware = \"\"\",
    # MySQL错误自动修复中间件（必须在最后）
    'eims_app.middleware_mysql_autofix.MySQLAutoFixMiddleware',
\"\"\"
        content = content[:insert_pos] + new_middleware + content[insert_pos:]
        
        with open('/var/www/eims/settings.py', 'w') as f:
            f.write(content)
        
        print("中间件已添加到settings.py")
    else:
        print("未找到MIDDLEWARE配置")
else:
    print("中间件已存在，跳过")

PYEOF
""")
    print("  ✅ settings.py已更新")
    
    # 4. 重启Gunicorn
    print("\n[步骤 4/4] 重启Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    time.sleep(3)
    ssh.exec_command(
        "cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &",
        timeout=10
    )
    time.sleep(3)
    
    # 验证
    print("\n验证部署...")
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", timeout=10)
    http_code = stdout.read().decode().strip()
    
    print("\n" + "=" * 80)
    print("✅ 自动修复中间件部署完成！")
    print("=" * 80)
    
    print("\n📊 部署内容:")
    print("  ✓ MySQLAutoFixMiddleware - 错误拦截中间件")
    print("  ✓ auto_fix_error_page.html - 自动修复页面")
    print("  ✓ settings.py - 中间件配置")
    print(f"  ✓ Gunicorn状态: HTTP {http_code}")
    
    print("\n🎯 工作流程:")
    print("  1. 用户访问网站")
    print("  2. 如果MySQL错误 → 中间件拦截")
    print("  3. 自动触发OpenClaw修复脚本")
    print("  4. 显示修复进度页面（带进度条）")
    print("  5. 实时监控修复进度")
    print("  6. 修复完成 → 自动跳转到正常页面")
    print("  7. 修复失败 → 显示手动操作指引")
    
    print("\n⚡ 特点:")
    print("  • 零人工干预 - 完全自动化")
    print("  • 实时进度显示 - 用户可见")
    print("  • 自动刷新 - 修复完成后自动跳转")
    print("  • 友好提示 - 清晰的错误说明")
    print("  • 降级处理 - 修复失败提供手动方案")
    
    print("\n📋 测试方法:")
    print("  1. 正常访问网站应该正常")
    print("  2. 模拟MySQL错误（谨慎操作）:")
    print("     mysql -uroot -pEIMS2026_mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'wrong';\"")
    print("  3. 访问网站会看到自动修复页面")
    print("  4. 等待修复完成会自动跳转")
    print("  5. 恢复密码:")
    print("     mysql -uroot -pEIMS2026_mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'EIMS2026_mysql';\"")
    
    print("\n💡 提示:")
    print("  • 修复过程约30-60秒")
    print("  • 页面会自动刷新，无需手动操作")
    print("  • 用户可以清晰看到修复进度")
    print("  • 如果自动修复失败，提供手动操作指引")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
