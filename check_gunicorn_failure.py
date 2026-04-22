#!/usr/bin/env python3
"""
检查Gunicorn启动失败的详细原因
Check detailed reason for Gunicorn startup failure
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)
    
    print("=" * 80)
    print("🔍 检查Gunicorn启动失败原因")
    print("=" * 80)
    
    # 1. 查看完整错误日志
    print("\n[1/3] 查看Gunicorn错误日志...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/logs/gunicorn_error.log 2>/dev/null | tail -100", timeout=5)
    error_log = stdout.read().decode().strip()
    
    if error_log:
        print("\n错误日志内容:")
        print("-" * 80)
        # 找到Traceback部分
        lines = error_log.split('\n')
        traceback_start = -1
        for i, line in enumerate(lines):
            if 'Traceback' in line:
                traceback_start = i
                break
        
        if traceback_start >= 0:
            # 显示Traceback及之后的内容
            for line in lines[traceback_start:]:
                print(line)
        else:
            # 显示最后50行
            for line in lines[-50:]:
                print(line)
        print("-" * 80)
    else:
        print("无错误日志")
    
    # 2. 测试Django能否正常导入
    print("\n[2/3] 测试Django导入...")
    test_cmd = """cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c "
import django
django.setup()
print('Django setup OK')

# 测试URL配置
from django.urls import get_resolver
resolver = get_resolver()
print('URL resolver OK')

# 测试视图导入
from eims_app import views_openclaw_fix
print('views_openclaw_fix import OK')

print('All tests passed')
" 2>&1"""
    
    stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=15)
    test_output = stdout.read().decode().strip()
    test_error = stderr.read().decode().strip()
    
    if test_output:
        print(f"\n输出:\n{test_output}")
    
    if test_error:
        print(f"\n错误:\n{test_error}")
    
    # 3. 尝试手动启动Gunicorn并捕获输出
    print("\n[3/3] 尝试手动启动Gunicorn（前台模式）...")
    manual_cmd = """cd /var/www/eims && source venv/bin/activate && timeout 10 /var/www/eims/venv/bin/gunicorn \
--bind 127.0.0.1:8000 \
--workers 1 \
--timeout 5 \
wsgi:application 2>&1 || true"""
    
    stdin, stdout, stderr = ssh.exec_command(manual_cmd, timeout=20)
    manual_output = stdout.read().decode().strip()
    manual_error = stderr.read().decode().strip()
    
    if manual_output:
        print(f"\n输出:\n{manual_output[:1000]}")
    
    if manual_error:
        print(f"\n错误:\n{manual_error[:1000]}")
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
