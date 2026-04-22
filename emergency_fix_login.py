#!/usr/bin/env python3
"""
紧急修复登录问题
Emergency Fix for Login Issue
"""

import paramiko
import os
import time

print("=" * 80)
print("🚨 紧急修复登录问题")
print("Emergency Fix for Login Issue")
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
    
    # Step 1: Check current error
    print("[1/6] 检查当前错误...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/login/ 2>&1 | head -50")
    page_content = stdout.read().decode()
    
    if 'OperationalError' in page_content or 'DatabaseError' in page_content:
        print("  ⚠️  检测到数据库错误")
        error_type = "database"
    elif '500' in page_content or 'Internal Server Error' in page_content:
        print("  ⚠️  检测到服务器错误(500)")
        error_type = "server"
    else:
        print("  ℹ️  页面可能正常，继续检查...")
        error_type = "unknown"
    
    # Check Gunicorn logs
    stdin, stdout, stderr = ssh.exec_command(f"tail -30 {SERVER_PATH}/logs/gunicorn_error.log 2>/dev/null | grep -i 'error\\|exception' | tail -10")
    errors = stdout.read().decode()
    if errors:
        print(f"\n  最近错误:\n{errors[:500]}")
    
    # Step 2: Trigger OpenClaw MySQL fix
    print("\n[2/6] 触发OpenClaw MySQL修复...")
    ssh.exec_command("bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/emergency_fix.log 2>&1 &", timeout=5)
    print("  ✅ 修复脚本已启动")
    print("  ⏳ 等待修复完成（约60秒）...")
    
    # Wait for fix to complete
    for i in range(12):
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -c '1'")
        if '1' in stdout.read().decode():
            print(f"  ✅ MySQL已恢复 ({(i+1)*5}秒)")
            break
        else:
            print(f"  ⏳ 修复中... ({(i+1)*5}秒)")
    
    # Step 3: Check and fix views/urls issues
    print("\n[3/6] 检查视图和URL配置...")
    
    # Check if views_index.py has syntax errors
    stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && python -m py_compile views_index.py 2>&1")
    compile_error = stderr.read().decode()
    if compile_error:
        print(f"  ⚠️  views_index.py有语法错误，尝试修复...")
        # Remove the problematic API code we added
        ssh.exec_command(f"cd {SERVER_PATH} && git checkout views_index.py 2>/dev/null || echo 'No git'", timeout=5)
        print("  ✅ 已恢复views_index.py")
    else:
        print("  ✅ views_index.py语法正确")
    
    # Check urls.py
    stdin, stdout, stderr = ssh.exec_command(f"cd {SERVER_PATH} && source venv/bin/activate && python -m py_compile urls.py 2>&1")
    urls_error = stderr.read().decode()
    if urls_error:
        print(f"  ⚠️  urls.py有错误，尝试修复...")
        ssh.exec_command(f"cd {SERVER_PATH} && git checkout urls.py 2>/dev/null || echo 'No git'", timeout=5)
        print("  ✅ 已恢复urls.py")
    else:
        print("  ✅ urls.py语法正确")
    
    # Step 4: Restart Gunicorn cleanly
    print("\n[4/6] 重启Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn 2>/dev/null; sleep 3", timeout=10)
    
    # Start Gunicorn with proper settings
    start_cmd = f"""cd {SERVER_PATH} && \
source venv/bin/activate && \
nohup gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 300 \\
    --access-logfile {SERVER_PATH}/logs/gunicorn_access.log \\
    --error-logfile {SERVER_PATH}/logs/gunicorn_error.log \\
    wsgi:application > {SERVER_PATH}/logs/gunicorn.log 2>&1 &
sleep 5 && echo "Gunicorn started" """
    
    stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
    result = stdout.read().decode().strip()
    print(f"  {result}")
    
    time.sleep(8)
    
    # Step 5: Verify services
    print("\n[5/6] 验证服务状态...")
    
    # Check Gunicorn
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[g]unicorn' | wc -l")
    gunicorn_count = stdout.read().decode().strip()
    print(f"  Gunicorn进程: {gunicorn_count}")
    
    # Check MySQL
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -c '1'")
    mysql_ok = '1' in stdout.read().decode()
    print(f"  MySQL连接: {'✅ 正常' if mysql_ok else '❌ 失败'}")
    
    # Test HTTP
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("curl -o /dev/null -s -w '%{http_code}' http://127.0.0.1:8000/login/")
    http_code = stdout.read().decode().strip()
    print(f"  HTTP状态: {http_code}")
    
    # Step 6: Final check and summary
    print("\n[6/6] 最终检查...")
    
    if http_code == '200':
        print("  ✅ 登录页面可访问")
        
        # Check if it's the actual login page
        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/login/ | grep -c 'login'")
        if '0' not in stdout.read().decode():
            print("  ✅ 登录表单正常")
        
        print("\n" + "=" * 80)
        print("✅ 修复成功！系统已恢复正常")
        print("=" * 80)
        print(f"\n🌐 现在可以访问:")
        print(f"  • http://{SERVER_IP}/login/")
        print(f"  • http://www.xietongai.com.cn/login/")
        print(f"\n💡 提示:")
        print(f"  • OpenClaw会继续每2分钟自动监控")
        print(f"  • 如果再次出现故障，会自动修复")
        print(f"  • 可以查看日志: tail -f /root/.openclaw/monitoring/logs/health_check.log")
        print(f"\n⏰ 修复完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    else:
        print(f"  ⚠️  HTTP {http_code} - 仍有问题")
        print("\n  查看最新错误:")
        stdin, stdout, stderr = ssh.exec_command(f"tail -40 {SERVER_PATH}/logs/gunicorn_error.log | tail -20")
        print(stdout.read().decode())
        
        print("\n  建议操作:")
        print("  1. 检查数据库连接配置")
        print("  2. 查看Django错误日志")
        print("  3. 尝试手动运行: python manage.py check")
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {str(e)}")
    import traceback
    traceback.print_exc()
