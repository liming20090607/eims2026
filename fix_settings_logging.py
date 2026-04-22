#!/usr/bin/env python3
"""
修复settings.py - 移除错误的LOGGING配置
Fix settings.py - Remove incorrect LOGGING configuration
"""
import paramiko

print("=" * 80)
print("修复settings.py的LOGGING配置")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)
    print("\n已连接到服务器\n")
except Exception as e:
    print(f"\n连接失败: {e}")
    exit(1)

try:
    # 读取settings.py
    print("[1/3] 读取settings.py...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/settings.py", timeout=5)
    content = stdout.read().decode()
    
    # 检查是否有错误的LOGGING配置
    if 'MySQLAutoFixMiddleware' in content and 'LOGGING' in content:
        print("发现错误的LOGGING配置包含中间件")
        
        # 使用Python脚本清理
        fix_script = r"""
python3 << 'PYEOF'
import re

with open('/var/www/eims/settings.py', 'r') as f:
    lines = f.readlines()

# 找到并移除包含MySQLAutoFixMiddleware的LOGGING行
new_lines = []
skip_next = False
in_logging_block = False
brace_count = 0

for i, line in enumerate(lines):
    # 检查是否进入LOGGING配置块
    if 'LOGGING' in line and '=' in line and '{' in line:
        in_logging_block = True
        brace_count = line.count('{') - line.count('}')
        new_lines.append(line)
        continue
    
    if in_logging_block:
        brace_count += line.count('{') - line.count('}')
        
        # 如果这一行包含中间件路径，跳过它
        if 'MySQLAutoFixMiddleware' in line:
            print(f"Skipping line {i+1}: {line.strip()}")
            skip_next = True
            continue
        
        if skip_next and line.strip().startswith("'"):
            # 跳过下一行的引号
            skip_next = False
            continue
        
        skip_next = False
        
        if brace_count <= 0:
            in_logging_block = False
        
        new_lines.append(line)
    else:
        new_lines.append(line)

with open('/var/www/eims/settings.py', 'w') as f:
    f.writelines(new_lines)

print("Fixed settings.py")
PYEOF
"""
        stdin, stdout, stderr = ssh.exec_command(fix_script, timeout=10)
        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        print(f"结果: {result}")
        if error:
            print(f"错误: {error}")
    else:
        print("未发现错误的LOGGING配置")
    
    # 验证修复
    print("\n[2/3] 验证修复...")
    stdin, stdout, stderr = ssh.exec_command("grep -n 'MySQLAutoFixMiddleware' /var/www/eims/settings.py", timeout=5)
    grep_result = stdout.read().decode().strip()
    
    if grep_result:
        print(f"仍找到中间件引用:\n{grep_result}")
        
        # 显示上下文
        print("\n显示相关行:")
        for line_num in grep_result.split('\n'):
            if ':' in line_num:
                num = line_num.split(':')[0]
                stdin, stdout, stderr = ssh.exec_command(f"sed -n '{int(num)-2},{int(num)+2}p' /var/www/eims/settings.py", timeout=5)
                context = stdout.read().decode()
                print(f"\n行 {num}:")
                print(context)
    else:
        print("中间件已从错误位置移除")
    
    # 测试Django加载
    print("\n[3/3] 测试Django加载...")
    test_cmd = "cd /var/www/eims && source venv/bin/activate && DJANGO_SETTINGS_MODULE=settings python -c 'import django; django.setup(); print(\"Django OK\")' 2>&1"
    stdin, stdout, stderr = ssh.exec_command(test_cmd, timeout=15)
    test_output = stdout.read().decode().strip()
    test_error = stderr.read().decode().strip()
    
    if test_error and 'Traceback' in test_error:
        print(f"Django加载失败:\n{test_error[:500]}")
    else:
        print(f"Django加载成功: {test_output}")
    
    # 重启Gunicorn
    if 'Django OK' in test_output or not test_error:
        print("\n重启Gunicorn...")
        ssh.exec_command("pkill -9 -f gunicorn; sleep 3", timeout=10)
        
        import time
        time.sleep(4)
        
        start_cmd = "cd /var/www/eims && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 300 wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"
        ssh.exec_command(start_cmd, timeout=10)
        
        time.sleep(5)
        
        # 测试
        print("\n测试访问...")
        tests = [
            ("登录页面", "http://127.0.0.1:8000/login/"),
            ("控制面板", "http://127.0.0.1:8000/openclaw/panel/"),
        ]
        
        for name, url in tests:
            stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 5 {url}", timeout=10)
            http_code = stdout.read().decode().strip()
            
            status = "OK" if http_code == '200' else "WARN" if http_code in ['403', '405'] else "FAIL"
            print(f"  [{status}] {name}: HTTP {http_code}")
    
    print("\n" + "=" * 80)
    print("修复完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"\n修复失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
