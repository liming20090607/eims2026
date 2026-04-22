import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 CSRF 验证失败问题")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 检查当前 settings.py 中的 ALLOWED_HOSTS 和 CSRF_TRUSTED_ORIGINS
    print("\n[1] 检查当前配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 3 "ALLOWED_HOSTS" /var/www/eims/settings.py | head -10')
    allowed_hosts = stdout.read().decode('utf-8')
    print("ALLOWED_HOSTS:")
    print(allowed_hosts)
    
    stdin, stdout, stderr = ssh.exec_command('grep -A 3 "CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py | head -10')
    csrf_origins = stdout.read().decode('utf-8')
    print("\nCSRF_TRUSTED_ORIGINS:")
    print(csrf_origins)
    
    # 2. 检查 settings.py 中是否有 os.environ.get 用于这些配置
    print("\n[2] 检查是否使用环境变量...")
    stdin, stdout, stderr = ssh.exec_command('grep -n "ALLOWED_HOSTS\|CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py')
    config_lines = stdout.read().decode('utf-8')
    print(config_lines)
    
    # 3. 更新 settings.py 配置
    print("\n[3] 更新 ALLOWED_HOSTS 和 CSRF_TRUSTED_ORIGINS...")
    
    update_settings = r'''
import re

# 读取 settings.py
with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新 ALLOWED_HOSTS
old_allowed = re.search(r"ALLOWED_HOSTS\s*=\s*\[.*?\]", content, re.DOTALL)
if old_allowed:
    new_allowed = """ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '39.106.41.239',
    'www.xietongai.com.cn',
    'xietongai.com.cn',
]"""
    content = content[:old_allowed.start()] + new_allowed + content[old_allowed.end():]
    print("✓ 已更新 ALLOWED_HOSTS")
else:
    print("✗ 未找到 ALLOWED_HOSTS")

# 更新或添加 CSRF_TRUSTED_ORIGINS
old_csrf = re.search(r"CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]", content, re.DOTALL)
new_csrf = """CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'http://39.106.41.239',
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'https://www.xietongai.com.cn',
    'https://xietongai.com.cn',
]"""

if old_csrf:
    content = content[:old_csrf.start()] + new_csrf + content[old_csrf.end():]
    print("✓ 已更新 CSRF_TRUSTED_ORIGINS")
else:
    # 在 ALLOWED_HOSTS 后面添加
    content = content.replace(
        new_allowed,
        new_allowed + "\n\n" + new_csrf
    )
    print("✓ 已添加 CSRF_TRUSTED_ORIGINS")

# 保存 settings.py
with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ settings.py 已更新")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/update_settings.py << "UPDATEEOF"\n{update_settings}\nUPDATEEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/update_settings.py 2>&1')
    update_output = stdout.read().decode('utf-8')
    update_error = stderr.read().decode('utf-8')
    print(update_output)
    if update_error:
        print("错误:", update_error)
    
    # 4. 验证更新后的配置
    print("\n[4] 验证更新后的配置...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 8 "ALLOWED_HOSTS" /var/www/eims/settings.py | head -12')
    new_allowed = stdout.read().decode('utf-8')
    print("新的 ALLOWED_HOSTS:")
    print(new_allowed)
    
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "CSRF_TRUSTED_ORIGINS" /var/www/eims/settings.py | head -15')
    new_csrf = stdout.read().decode('utf-8')
    print("\n新的 CSRF_TRUSTED_ORIGINS:")
    print(new_csrf)
    
    # 5. 清空缓存
    print("\n[5] 清空 Python 缓存...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/eims && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "✓ 缓存已清空"')
    print(stdout.read().decode('utf-8').strip())
    
    # 6. 重启 Gunicorn
    print("\n[6] 重启 Gunicorn...")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f "gunicorn.*eims" || true')
    time.sleep(3)
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 Gunicorn 启动...")
    time.sleep(8)
    
    # 验证进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {count}")
    
    # 7. HTTP 测试
    print("\n[7] HTTP 测试...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status}")
    
    # 8. 测试登录页面
    print("\n[8] 测试登录页面...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ | grep -i "csrf" | head -5')
    csrf_check = stdout.read().decode('utf-8')
    if csrf_check:
        print("[✓] 登录页面包含 CSRF token")
    
    # 9. 检查错误日志
    print("\n[9] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'CSRF' in errors or 'Forbidden' in errors:
        print("[✗] 仍有 CSRF 错误:")
        print(errors[-1000:])
    else:
        print("[✓] 无 CSRF 错误")
        if errors.strip():
            print("其他日志:")
            print(errors[-500:])
    
    print("\n" + "="*70)
    print("✅ CSRF 配置已更新！")
    print("="*70)
    print("\n配置说明:")
    print("  ALLOWED_HOSTS 已添加:")
    print("    - localhost")
    print("    - 127.0.0.1")
    print("    - 39.106.41.239")
    print("    - www.xietongai.com.cn")
    print("    - xietongai.com.cn")
    print("\n  CSRF_TRUSTED_ORIGINS 已添加:")
    print("    - http://www.xietongai.com.cn")
    print("    - https://www.xietongai.com.cn")
    print("    - 以及其他相关域名")
    print("\n现在请:")
    print("1. 清除浏览器缓存和 Cookie")
    print("2. 刷新登录页面")
    print("3. 重新尝试登录")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
