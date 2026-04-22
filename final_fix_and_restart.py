import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 settings.py 配置并重启服务")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 完全重写 settings.py 的安全配置部分
    print("\n[1] 修复 settings.py 配置...")
    
    fix_script = r'''
# 读取完整文件
with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换整个安全配置部分
import re

# 匹配从 SECRET_KEY 到 INSTALLED_APPS 之前的所有内容
pattern = r'# -------------------------- 安全配置 --------------------------.*?# -------------------------- 应用配置 --------------------------'

replacement = """# -------------------------- 安全配置 --------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-aos-development-key-2026')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = ['*']  # 开发阶段允许所有主机访问（生产环境请务必修改）

# CSRF 信任来源
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'http://39.106.41.239',
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'https://www.xietongai.com.cn',
    'https://xietongai.com.cn',
]

# -------------------------- 应用配置 --------------------------"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content != content:
    with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ settings.py 配置已修复")
else:
    print("✗ 未找到匹配的配置部分，尝试其他方法...")
    
    # 备用方案：手动清理
    lines = content.split('\n')
    cleaned_lines = []
    skip = False
    in_allowed_hosts = False
    
    for line in lines:
        # 跳过注释的 ALLOWED_HOSTS
        if line.strip().startswith('#ALLOWED_HOSTS') or line.strip().startswith('# CSRF 信任来源'):
            continue
        
        # 检测孤立的列表项（没有前面的 ALLOWED_HOSTS = [）
        if in_allowed_hosts:
            if line.strip() == ']':
                in_allowed_hosts = False
            continue
        
        # 如果是孤立的主机名（在方括号内但前面没有 ALLOWED_HOSTS = [）
        stripped = line.strip()
        if stripped in ["'localhost',", "'127.0.0.1',", "'39.106.41.239',", "'www.xietongai.com.cn',", "'xietongai.com.cn',"]:
            continue
        
        cleaned_lines.append(line)
    
    new_content = '\n'.join(cleaned_lines)
    with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ settings.py 已清理（备用方案）")

# 验证修复结果
with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n当前配置:")
for i, line in enumerate(lines[31:50], start=32):
    print(f"{i}: {line}", end='')
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/fix_settings.py << "FIXEOF"\n{fix_script}\nFIXEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/fix_settings.py 2>&1')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error)
    
    # 2. 测试 Django 配置是否有效
    print("\n[2] 测试 Django 配置...")
    test_config = r'''
import os
import sys
sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
try:
    django.setup()
    from django.conf import settings
    print("✓ Django 配置加载成功")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"DEBUG: {settings.DEBUG}")
except Exception as e:
    print(f"✗ Django 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_config.py << "TESTEOF"\n{test_config}\nTESTEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/test_config.py 2>&1')
    test_output = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print(test_output)
    if test_error and 'Traceback' in test_error:
        print("配置错误详情:")
        print(test_error)
    
    # 3. 强制停止所有 Gunicorn 进程
    print("\n[3] 停止所有 Gunicorn 进程...")
    
    # 使用多种方式确保完全停止
    stop_commands = [
        'fuser -k 8000/tcp 2>/dev/null || true',
        'sleep 2',
        'pkill -9 -f "gunicorn.*wsgi" 2>/dev/null || true',
        'sleep 2',
        'kill -9 $(lsof -t -i:8000) 2>/dev/null || true',
        'sleep 3',
    ]
    
    for cmd in stop_commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(1 if 'sleep' not in cmd else 2)
    
    # 验证端口已释放
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 2>/dev/null | grep LISTEN || echo "端口已释放"')
    port_status = stdout.read().decode('utf-8').strip()
    print(f"端口状态: {port_status}")
    
    # 4. 清空 Python 缓存
    print("\n[4] 清空 Python 缓存...")
    stdin, stdout, stderr = ssh.exec_command('''
cd /var/www/eims
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
echo "✓ 缓存已清空"
''')
    print(stdout.read().decode('utf-8').strip())
    
    # 5. 启动 Gunicorn
    print("\n[5] 启动 Gunicorn...")
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 Gunicorn 启动...")
    time.sleep(12)
    
    # 6. 验证服务
    print("\n[6] 验证服务状态...")
    
    # 检查进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    proc_info = stdout.read().decode('utf-8')
    print("Gunicorn 进程:")
    for line in proc_info.strip().split('\n')[:5]:
        print(f"  {line}")
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {count}")
    
    # HTTP 测试
    print("\n[7] HTTP 测试...")
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态码: {login_status}")
    
    # 检查错误日志
    print("\n[8] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -20 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    has_errors = any(keyword in errors for keyword in ['Error', 'Exception', 'Traceback', 'CSRF', 'Forbidden'])
    
    if has_errors:
        print("[!] 发现错误日志:")
        print(errors[-2000:])
    else:
        print("[✓] 无错误")
        if errors.strip():
            print("日志内容:")
            print(errors[-1000:])
    
    # 检查 CSRF token
    print("\n[9] 检查登录页面 CSRF token...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ | grep -c "csrfmiddlewaretoken"')
    csrf_count = stdout.read().decode('utf-8').strip()
    print(f"CSRF token 数量: {csrf_count}")
    
    print("\n" + "="*70)
    if login_status == '200' and csrf_count != '0':
        print("✅ 修复成功！系统已正常运行")
        print("="*70)
        print("\n现在请:")
        print("1. 清除浏览器缓存和 Cookie")
        print("2. 访问: http://www.xietongai.com.cn/login/")
        print("3. 使用以下凭据登录:")
        print("   用户名: admin  密码: admin123456")
        print("   用户名: root   密码: root123456")
    else:
        print("⚠️  服务已启动但可能需要进一步检查")
        print("="*70)
        print(f"登录页面状态: {login_status}")
        print(f"CSRF token: {csrf_count}")
        print("\n建议:")
        print("1. 检查浏览器控制台是否有错误")
        print("2. 清除浏览器缓存后重试")
        print("3. 使用无痕模式访问")
    
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
