#!/usr/bin/env python3
"""
完整诊断并修复Gunicorn启动问题
Complete diagnosis and fix for Gunicorn startup issues
"""
import paramiko
import time

print("=" * 80)
print("🔍 完整诊断Gunicorn问题")
print("Complete Gunicorn Diagnosis")
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
    # 1. 检查所有Python进程
    print("[1/8] 检查所有相关进程...")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'gunicorn|python' | grep -v grep", timeout=5)
    processes = stdout.read().decode().strip()
    if processes:
        print(f"运行中的进程:\n{processes}\n")
    else:
        print("没有运行中的进程\n")
    
    # 2. 检查端口占用
    print("[2/8] 检查端口8000...")
    stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep 8000 || ss -tlnp | grep 8000", timeout=5)
    port_info = stdout.read().decode().strip()
    if port_info:
        print(f"端口8000被占用:\n{port_info}\n")
    else:
        print("端口8000空闲\n")
    
    # 3. 测试Django配置
    print("[3/8] 测试Django配置...")
    stdin, stdout, stderr = ssh.exec_command(
        "cd /var/www/eims && source venv/bin/activate && python manage.py check 2>&1 | head -30",
        timeout=15
    )
    check_output = stdout.read().decode().strip()
    check_error = stderr.read().decode().strip()
    
    if check_error and 'Traceback' in check_error:
        print(f"Django配置错误:\n{check_error[:500]}\n")
    elif check_output:
        print(f"Django检查结果:\n{check_output[:500]}\n")
    else:
        print("Django配置正常\n")
    
    # 4. 检查urls.py的完整内容
    print("[4/8] 检查urls.py...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/urls.py", timeout=5)
    urls_content = stdout.read().decode()
    
    # 查找问题
    issues = []
    if 'views_openclaw_fix' not in urls_content.split('urlpatterns')[0]:
        issues.append("缺少 views_openclaw_fix 导入")
    
    if 'from eims_app import views_openclaw_fix' not in urls_content:
        issues.append("导入语句格式可能不正确")
    
    if issues:
        print(f"urls.py问题:\n")
        for issue in issues:
            print(f"  ❌ {issue}")
        print()
    else:
        print("urls.py看起来正常\n")
    
    # 5. 检查视图文件
    print("[5/8] 检查视图文件...")
    stdin, stdout, stderr = ssh.exec_command(
        "cd /var/www/eims && source venv/bin/activate && python -c 'from eims_app import views_openclaw_fix; print(\"OK\")' 2>&1",
        timeout=10
    )
    import_test = stdout.read().decode().strip()
    import_error = stderr.read().decode().strip()
    
    if import_error:
        print(f"视图导入错误:\n{import_error[:500]}\n")
    else:
        print(f"视图导入成功: {import_test}\n")
    
    # 6. 清理并重启
    print("[6/8] 清理旧进程...")
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    time.sleep(3)
    
    # 确认清理
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep", timeout=5)
    remaining = stdout.read().decode().strip()
    if remaining:
        print(f"仍有残留进程，强制清理...")
        ssh.exec_command("killall -9 gunicorn; sleep 2", timeout=10)
        time.sleep(3)
    else:
        print("所有Gunicorn进程已清理\n")
    
    # 7. 使用不同方式启动
    print("[7/8] 尝试启动Gunicorn（方法1：直接启动）...")
    
    start_cmd = """cd /var/www/eims && \
source venv/bin/activate && \
python -m gunicorn \
--bind 127.0.0.1:8000 \
--workers 3 \
--timeout 300 \
--preload \
wsgi:application \
--daemon \
--access-logfile /var/www/eims/logs/gunicorn_access.log \
--error-logfile /var/www/eims/logs/gunicorn_error.log \
--pid /var/www/eims/gunicorn.pid"""
    
    stdin, stdout, stderr = ssh.exec_command(start_cmd, timeout=15)
    start_error = stderr.read().decode().strip()
    
    if start_error:
        print(f"启动错误:\n{start_error[:500]}\n")
        print("尝试方法2...")
        
        # 方法2：简化启动
        simple_cmd = "cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 3 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"
        ssh.exec_command(simple_cmd, timeout=10)
    else:
        print("Gunicorn启动命令已执行\n")
    
    time.sleep(5)
    
    # 8. 验证
    print("[8/8] 验证启动...")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l", timeout=5)
    worker_count = stdout.read().decode().strip()
    print(f"Gunicorn进程数: {worker_count}\n")
    
    # 测试HTTP
    print("测试HTTP访问...")
    time.sleep(3)
    
    tests = [
        ("登录页面", "http://127.0.0.1:8000/login/"),
        ("控制面板", "http://127.0.0.1:8000/openclaw/panel/"),
        ("API接口", "http://127.0.0.1:8000/api/openclaw/check-status/"),
    ]
    
    success_count = 0
    for name, url in tests:
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 5 {url}", timeout=10)
        http_code = stdout.read().decode().strip()
        
        if http_code == '200':
            print(f"  ✅ {name}: HTTP {http_code}")
            success_count += 1
        elif http_code in ['403', '405']:
            print(f"  ⚠️  {name}: HTTP {http_code} (可接受)")
            success_count += 1
        elif http_code == '000':
            print(f"  ❌ {name}: HTTP {http_code} (连接失败)")
        else:
            print(f"  ⚠️  {name}: HTTP {http_code}")
    
    print("\n" + "=" * 80)
    
    if success_count > 0:
        print("✅ Gunicorn已成功启动！")
        print("\n📋 访问地址:")
        print("  • 控制面板: http://www.xietongai.com.cn/openclaw/panel/")
        print("  • 或: http://39.106.41.239:8000/openclaw/panel/")
    else:
        print("⚠️  Gunicorn启动可能有问题")
        print("\n🔍 请查看日志:")
        print("  tail -f /var/www/eims/logs/gunicorn_error.log")
        print("  tail -f /var/www/eims/logs/gunicorn.log")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 诊断失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
