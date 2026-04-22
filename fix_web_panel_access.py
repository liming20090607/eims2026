#!/usr/bin/env python3
"""
修复Web控制面板访问问题
Fix Web Control Panel Access Issue
"""
import paramiko
import time

print("=" * 80)
print("🔧 修复Web控制面板访问问题")
print("Fix Web Control Panel Access Issue")
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
    # 1. 检查Gunicorn状态
    print("[步骤 1/5] 检查Gunicorn状态...")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep", timeout=5)
    gunicorn_processes = stdout.read().decode().strip()
    
    if gunicorn_processes:
        print(f"  ✅ Gunicorn正在运行:\n{gunicorn_processes[:200]}")
    else:
        print("  ❌ Gunicorn未运行")
    
    # 2. 检查urls.py的import语句
    print("\n[步骤 2/5] 检查urls.py的import语句...")
    stdin, stdout, stderr = ssh.exec_command("head -30 /var/www/eims/urls.py", timeout=5)
    urls_head = stdout.read().decode()
    print(urls_head)
    
    # 3. 检查views_openclaw_fix.py是否存在语法错误
    print("\n[步骤 3/5] 检查视图文件语法...")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python -m py_compile eims_app/views_openclaw_fix.py 2>&1", timeout=10)
    compile_output = stdout.read().decode().strip()
    compile_error = stderr.read().decode().strip()
    
    if compile_error:
        print(f"  ❌ 语法错误:\n{compile_error}")
    else:
        print("  ✅ 视图文件语法正确")
    
    # 4. 检查中间件是否有问题
    print("\n[步骤 4/5] 检查中间件语法...")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python -m py_compile eims_app/middleware_mysql_autofix.py 2>&1", timeout=10)
    compile_output = stdout.read().decode().strip()
    compile_error = stderr.read().decode().strip()
    
    if compile_error:
        print(f"  ❌ 语法错误:\n{compile_error}")
    else:
        print("  ✅ 中间件语法正确")
    
    # 5. 重启Gunicorn
    print("\n[步骤 5/5] 重启Gunicorn...")
    
    # 停止所有Gunicorn进程
    print("  停止Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn", timeout=5)
    time.sleep(3)
    
    # 确认已停止
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep", timeout=5)
    remaining = stdout.read().decode().strip()
    if not remaining:
        print("  ✅ Gunicorn已停止")
    else:
        print(f"  ⚠️  仍有进程: {remaining[:100]}")
        ssh.exec_command("killall -9 gunicorn", timeout=5)
        time.sleep(2)
    
    # 启动Gunicorn
    print("  启动Gunicorn...")
    start_cmd = """cd /var/www/eims && source venv/bin/activate && nohup gunicorn \
--bind 127.0.0.1:8000 \
--workers 4 \
--timeout 300 \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn_error.log \
wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"""
    
    ssh.exec_command(start_cmd, timeout=10)
    time.sleep(5)
    
    # 验证启动
    print("  验证启动...")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l", timeout=5)
    worker_count = stdout.read().decode().strip()
    print(f"  Gunicorn工作进程数: {worker_count}")
    
    # 测试访问
    print("\n  测试访问...")
    time.sleep(2)
    
    tests = [
        ("登录页面", "http://127.0.0.1:8000/login/"),
        ("控制面板", "http://127.0.0.1:8000/openclaw/panel/"),
        ("API接口", "http://127.0.0.1:8000/api/openclaw/check-status/"),
    ]
    
    for name, url in tests:
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", timeout=10)
        http_code = stdout.read().decode().strip()
        
        if http_code == '200':
            print(f"    ✅ {name}: HTTP {http_code}")
        elif http_code == '403':
            print(f"    ⚠️  {name}: HTTP {http_code} (需要CSRF token)")
        elif http_code == '405':
            print(f"    ⚠️  {name}: HTTP {http_code} (方法不允许)")
        elif http_code == '000':
            print(f"    ❌ {name}: HTTP {http_code} (连接失败)")
        else:
            print(f"    ⚠️  {name}: HTTP {http_code}")
    
    # 查看错误日志
    print("\n  查看Gunicorn错误日志（最后20行）:")
    stdin, stdout, stderr = ssh.exec_command("tail -20 /var/www/eims/logs/gunicorn_error.log 2>/dev/null || echo '无错误日志'", timeout=5)
    error_log = stdout.read().decode().strip()
    if error_log and error_log != '无错误日志':
        print(error_log)
    else:
        print("  (无错误)")
    
    print("\n" + "=" * 80)
    print("✅ 修复完成！")
    print("=" * 80)
    
    print("\n📋 现在可以访问:")
    print("  • 控制面板: http://www.xietongai.com.cn/openclaw/panel/")
    print("  • 或: http://39.106.41.239:8000/openclaw/panel/")
    
    print("\n💡 如果仍然无法访问:")
    print("  1. 等待10秒让Gunicorn完全启动")
    print("  2. 清除浏览器缓存")
    print("  3. 检查Nginx配置")
    print("  4. 查看错误日志: tail -f /var/www/eims/logs/gunicorn_error.log")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
