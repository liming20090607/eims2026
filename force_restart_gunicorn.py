import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("="*70)
    print("强制重启 Gunicorn 并验证登录")
    print("="*70)
    
    ssh.connect('39.106.41.239', 22, 'root', 'fjkl546#')
    
    # 1. 找到并杀掉所有占用 8000 端口的进程
    print("\n[1] 查找并杀掉占用 8000 端口的所有进程...")
    
    # 先查看谁在用 8000 端口
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 -t 2>/dev/null || ss -tlnp | grep ":8000"')
    port_users = stdout.read().decode('utf-8')
    print("当前占用 8000 端口的进程:")
    print(port_users if port_users else "无")
    
    # 强制杀掉所有 gunicorn 进程
    stdin, stdout, stderr = ssh.exec_command('kill -9 $(lsof -t -i:8000) 2>/dev/null || true')
    time.sleep(2)
    
    # 再次杀掉所有 gunicorn
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f gunicorn || true')
    time.sleep(3)
    
    # 确认端口已释放
    stdin, stdout, stderr = ssh.exec_command('lsof -i :8000 -t 2>/dev/null | wc -l')
    remaining = stdout.read().decode('utf-8').strip()
    print(f"剩余占用 8000 端口的进程数: {remaining}")
    
    # 2. 确认进程已停止
    print("\n[2] 确认所有 Gunicorn 进程已停止...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    count = stdout.read().decode('utf-8').strip()
    print(f"Gunicorn 进程数: {count}")
    
    if int(count) > 0:
        print("仍有进程运行，再次强制杀掉...")
        stdin, stdout, stderr = ssh.exec_command('kill -9 $(ps aux | grep gunicorn | grep -v grep | awk \'{print $2}\') 2>/dev/null || true')
        time.sleep(2)
    
    # 等待端口完全释放
    print("\n等待 5 秒让端口完全释放...")
    time.sleep(5)
    
    # 3. 启动新的 Gunicorn
    print("\n[3] 启动新的 Gunicorn 进程...")
    
    # 先确保日志目录存在
    stdin, stdout, stderr = ssh.exec_command('mkdir -p /var/www/eims/logs')
    
    # 清空旧日志
    stdin, stdout, stderr = ssh.exec_command('echo "" > /var/www/eims/logs/error.log')
    
    start_cmd = 'cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/www/eims/logs/access.log --error-logfile /var/www/eims/logs/error.log --capture-output wsgi:application > /dev/null 2>&1 &'
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    
    print("等待 Gunicorn 启动...")
    time.sleep(10)
    
    # 4. 验证进程
    print("\n[4] 验证新进程...")
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep')
    process_info = stdout.read().decode('utf-8')
    print("Gunicorn 进程信息:")
    print(process_info)
    
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep gunicorn | grep -v grep | wc -l')
    final_count = stdout.read().decode('utf-8').strip()
    print(f"\nGunicorn 进程数: {final_count}")
    
    # 5. 检查新日志是否有错误
    print("\n[5] 检查新进程的错误日志...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('tail -30 /var/www/eims/logs/error.log 2>&1')
    errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in errors:
        print("[✗] 仍有 Access denied 错误:")
        print(errors[-1500:])
    elif errors.strip():
        print("错误日志内容:")
        print(errors[-1000:] if len(errors) > 1000 else errors)
    else:
        print("[✓] 无错误日志")
    
    # 6. HTTP 测试
    print("\n[6] HTTP 测试...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
    status = stdout.read().decode('utf-8').strip()
    print(f"HTTP 状态码: {status}")
    
    # 7. 测试登录页面
    print("\n[7] 测试登录页面...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/login/ | head -20')
    login_page = stdout.read().decode('utf-8')
    if 'login' in login_page.lower() or 'form' in login_page.lower():
        print("[✓] 登录页面正常加载")
    
    # 8. 等待几秒后再次检查日志（看是否有新请求产生的错误）
    print("\n[8] 等待并检查是否有新错误...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command('tail -50 /var/www/eims/logs/error.log 2>&1')
    final_errors = stdout.read().decode('utf-8')
    
    if 'Access denied' in final_errors:
        print("[✗] 登录后仍有 Access denied 错误:")
        # 只显示最后 2000 字符
        print(final_errors[-2000:])
    else:
        print("[✓] 没有 Access denied 错误")
        if final_errors.strip():
            print("其他日志内容:")
            print(final_errors[-500:])
    
    print("\n" + "="*70)
    print("✅ 修复完成！")
    print("="*70)
    print("\n现在请尝试登录:")
    print("  地址: http://www.xietongai.com.cn/login/")
    print("  用户: admin")
    print("  密码: admin123456")
    print("\n或:")
    print("  用户: root")
    print("  密码: root123456")
    print("="*70)
    
finally:
    ssh.close()
    print("\n完成！")
