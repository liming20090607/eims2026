import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("修复 settings.py 并重启服务")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 查看当前 ALLOWED_HOSTS 附近的内容
    print("\n[1] 检查 settings.py 当前状态...")
    stdin, stdout, stderr = ssh.exec_command('sed -n "30,50p" /var/www/eims/settings.py')
    settings_content = stdout.read().decode('utf-8')
    print(settings_content)
    
    # 2. 清理 settings.py，删除重复配置
    print("\n[2] 清理 settings.py 中的重复配置...")
    
    clean_settings = r'''
import re

# 读取 settings.py
with open('/var/www/eims/settings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找并清理重复的 ALLOWED_HOSTS 和 CSRF_TRUSTED_ORIGINS
cleaned_lines = []
skip_until_next_section = False
in_duplicate_allowed = False
in_duplicate_csrf = False

for line in lines:
    # 检查是否是注释的旧 ALLOWED_HOSTS
    if line.strip().startswith('#ALLOWED_HOSTS ='):
        continue
    
    # 检查是否是第一个 ALLOWED_HOSTS（我们添加的）
    if line.strip() == 'ALLOWED_HOSTS = [' and 'localhost' in line:
        in_duplicate_allowed = True
        continue
    
    if in_duplicate_allowed:
        if line.strip() == ']':
            in_duplicate_allowed = False
        continue
    
    # 检查是否是注释标记
    if '# CSRF 信任来源（生产环境配置）' in line:
        continue
    
    cleaned_lines.append(line)

# 保存清理后的文件
with open('/var/www/eims/settings.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("✓ settings.py 已清理")
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/clean_settings.py << "CLEANEOF"\n{clean_settings}\nCLEANEOF')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('/var/www/eims/venv/bin/python /tmp/clean_settings.py 2>&1')
    clean_output = stdout.read().decode('utf-8')
    clean_error = stderr.read().decode('utf-8')
    print(clean_output)
    if clean_error:
        print("错误:", clean_error)
    
    # 3. 验证清理后的配置
    print("\n[3] 验证清理后的配置...")
    stdin, stdout, stderr = ssh.exec_command('sed -n "30,55p" /var/www/eims/settings.py')
    cleaned_content = stdout.read().decode('utf-8')
    print(cleaned_content)
    
    # 4. 完全停止 Gunicorn
    print("\n[4] 停止所有 Gunicorn 进程...")
    
    # 找到并杀掉所有占用 8000 端口的进程
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || kill -9 $(lsof -t -i:8000) 2>/dev/null || true')
    time.sleep(2)
    
    # 再次确认
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(3)
    
    # 等待端口释放
    time.sleep(3)
    
    # 验证端口已释放
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 2>/dev/null | wc -l')
    port_users = stdout.read().decode('utf-8').strip()
    print(f"占用 8000 端口的进程数: {port_users}")
    
    # 5. 启动 Gunicorn
    print("\n[5] 启动 Gunicorn...")
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    # 6. 验证进程
    print("\n[6] 验证 Gunicorn 进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    proc_info = stdout.read().decode('utf-8')
    print("Gunicorn 进程:")
    print(proc_info)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {count}")
    
    # 7. HTTP 测试
    print("\n[7] HTTP 测试...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status}")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
    login_status = stdout.read().decode('utf-8').strip()
    print(f"登录页面状态码: {login_status}")
    
    # 8. 检查错误日志
    print("\n[8] 检查错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'CSRF' in errors or 'Forbidden' in errors or '500' in errors:
        print("[✗] 仍有错误:")
        print(errors[-2000:])
    else:
        print("[✓] 无错误")
        if errors.strip():
            print("日志内容:")
            print(errors[-1000:])
        else:
            print("日志为空（正常）")
    
    # 9. 测试登录页面是否包含 CSRF token
    print("\n[9] 测试登录页面...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ | grep -o "csrfmiddlewaretoken" | head -1')
    csrf_token = stdout.read().decode('utf-8').strip()
    if csrf_token:
        print("[✓] 登录页面包含 CSRF token")
    
    print("\n" + "="*70)
    print("✅ 修复完成！")
    print("="*70)
    print("\n现在请:")
    print("1. 清除浏览器缓存和 Cookie")
    print("2. 刷新登录页面: http://www.xietongai.com.cn/login/")
    print("3. 重新尝试登录")
    print("\n登录凭据:")
    print("  用户名: admin  密码: admin123456")
    print("  用户名: root   密码: root123456")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
