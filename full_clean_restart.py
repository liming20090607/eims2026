import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("完全清理缓存并重建 Gunicorn")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 杀掉所有占用 8000 端口的进程
    print("\n[1] 停止所有 Gunicorn 进程...")
    
    # 使用 fuser 命令更可靠地杀进程
    stdin, stdout, stderr = ssh.exec_command('fuser -k 8000/tcp 2>/dev/null || kill -9 $(lsof -t -i:8000) 2>/dev/null || true')
    time.sleep(3)
    
    # 再杀一次确保
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn 2>/dev/null || true')
    time.sleep(2)
    
    # 等待端口释放
    time.sleep(5)
    
    # 验证端口已释放
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 2>/dev/null | wc -l')
    port_count = stdout.read().decode('utf-8').strip()
    print(f"占用 8000 端口的进程数: {port_count}")
    
    # 2. 删除所有 Python 缓存文件
    print("\n[2] 删除所有 Python 缓存文件...")
    
    clean_cache_cmd = '''
cd /var/www/eims
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name "*.pyd" -delete 2>/dev/null
find . -name "*.class" -delete 2>/dev/null
echo "Cache cleaned"
'''
    
    stdin, stdout, stderr = ssh.exec_command(clean_cache_cmd)
    clean_output = stdout.read().decode('utf-8')
    print(clean_output.strip())
    
    # 3. 验证 settings.py 的实际内容
    print("\n[3] 验证 settings.py 数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('python3 -c "exec(open(\'/var/www/eims/settings.py\').read().split(\'DATABASES\')[0]); import re; content=open(\'/var/www/eims/settings.py\').read(); match=re.search(r"DATABASES\s*=\s*\{.*?\'PASSWORD\':\s*[\'"](.*?)[\'"]", content, re.DOTALL); print(\'PASSWORD:\', match.group(1) if match else \'NOT FOUND\')" 2>&1')
    pwd_check = stdout.read().decode('utf-8')
    print(pwd_check)
    
    # 直接用 grep 确认
    stdin, stdout, stderr = ssh.exec_command('grep -A 2 "PASSWORD" /var/www/eims/settings.py | grep -E "PASSWORD|DB_PASSWORD" | head -5')
    pwd_line = stdout.read().decode('utf-8')
    print("密码配置行:")
    print(pwd_line)
    
    # 4. 检查是否有其他配置文件覆盖
    print("\n[4] 检查是否有本地设置文件...")
    stdin, stdout, stderr = ssh.exec_command('find /var/www/eims -name "local_settings.py" -o -name "settings_local.py" -o -name ".env" 2>/dev/null | grep -v __pycache__')
    local_files = stdout.read().decode('utf-8')
    if local_files.strip():
        print("找到额外配置文件:")
        print(local_files)
        for f in local_files.strip().split('\n'):
            if f:
                print(f"\n{f} 内容:")
                stdin, stdout, stderr = ssh.exec_command(f'cat {f}')
                print(stdout.read().decode('utf-8'))
    else:
        print("[✓] 无额外配置文件")
    
    # 5. 创建新的 Gunicorn 启动脚本（带调试）
    print("\n[5] 创建新的 Gunicorn 启动脚本...")
    
    start_script = '''#!/bin/bash
cd /var/www/eims

# 激活虚拟环境
source venv/bin/activate

# 删除缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 清空日志
echo "" > logs/error.log
echo "" > logs/access.log

# 启动 Gunicorn
nohup gunicorn \\
    --bind 0.0.0.0:8000 \\
    --workers 3 \\
    --timeout 120 \\
    --access-logfile /var/www/eims/logs/access.log \\
    --error-logfile /var/www/eims/logs/error.log \\
    --capture-output \\
    --reload \\
    wsgi:application > /dev/null 2>&1 &

echo "Gunicorn started with PID: $!"
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/start_gunicorn.sh << "STARTEOF"\n{start_script}\nSTARTEOF')
    time.sleep(1)
    stdin, stdout, stderr = ssh.exec_command('chmod +x /tmp/start_gunicorn.sh')
    time.sleep(1)
    stdin, stdout, stderr = ssh.exec_command('bash /tmp/start_gunicorn.sh')
    start_output = stdout.read().decode('utf-8')
    print(start_output)
    
    # 6. 等待并验证
    print("\n[6] 等待 Gunicorn 启动...")
    time.sleep(10)
    
    # 检查进程
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    proc_info = stdout.read().decode('utf-8')
    print("Gunicorn 进程:")
    print(proc_info)
    
    # 检查日志
    print("\n[7] 检查启动日志...")
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    startup_log = stdout.read().decode('utf-8')
    if startup_log.strip():
        print("启动日志:")
        print(startup_log[-1000:] if len(startup_log) > 1000 else startup_log)
    else:
        print("[✓] 无启动错误")
    
    # 7. HTTP 测试
    print("\n[8] HTTP 测试...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    http_status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {http_status}")
    
    # 8. 等待并检查登录请求后的日志
    print("\n[9] 等待 10 秒后检查错误日志...")
    time.sleep(10)
    
    stdin, stdout, stderr = ssh.exec_command('tail -100 /var/www/eims/logs/error.log 2>&1')
    final_log = stdout.read().decode('utf-8')
    
    if 'Access denied' in final_log:
        print("\n[✗] 仍然有 Access denied 错误!")
        print("错误详情（最后 2000 字符）:")
        print(final_log[-2000:])
        print("\n" + "="*70)
        print("建议检查:")
        print("1. 登录 Baota 面板检查是否有其他服务配置")
        print("2. 检查 Nginx 配置是否指向正确的后端")
        print("3. 手动通过 SSH 测试 Django shell")
        print("="*70)
    else:
        print("\n[✓] 没有 Access denied 错误!")
        if final_log.strip():
            print("日志内容:")
            print(final_log[-500:])
        print("\n" + "="*70)
        print("✅ 系统已修复！")
        print("="*70)
        print("\n请登录:")
        print("  http://www.xietongai.com.cn/login/")
        print("  admin / admin123456")
        print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
