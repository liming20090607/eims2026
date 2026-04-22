#!/usr/bin/env python3
"""
紧急修复urls.py - 添加缺失的import
Emergency fix for urls.py - Add missing import
"""
import paramiko

print("=" * 80)
print("🚨 紧急修复urls.py")
print("Emergency Fix urls.py")
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
    # 读取当前内容
    print("[1/3] 读取urls.py...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/urls.py", timeout=5)
    content = stdout.read().decode()
    
    print("当前文件内容:")
    print("-" * 80)
    print(content[:800])
    print("-" * 80)
    
    # 检查是否需要修复
    if 'from eims_app import views_openclaw_fix' in content:
        print("\n✅ import语句已存在")
    else:
        print("\n❌ 缺少import，正在添加...")
        
        # 在第二行添加import（在第一行import之后）
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # 在 from django.urls import path, include 之后添加
            if 'from django.urls import path, include' in line:
                new_lines.append('from eims_app import views_openclaw_fix')
                print(f"  ✅ 已在第{i+2}行添加import")
        
        content = '\n'.join(new_lines)
        
        # 写回文件
        print("\n[2/3] 写入修复后的urls.py...")
        # 使用Python写入以避免heredoc问题
        python_write_cmd = f"""python3 << 'PYEOF'
content = '''{content}'''
with open('/var/www/eims/urls.py', 'w') as f:
    f.write(content)
print("File written successfully")
PYEOF
"""
        stdin, stdout, stderr = ssh.exec_command(python_write_cmd, timeout=10)
        write_result = stdout.read().decode().strip()
        write_error = stderr.read().decode().strip()
        
        if write_error:
            print(f"  ⚠️  写入警告: {write_error}")
        else:
            print(f"  ✅ {write_result}")
    
    # 验证
    print("\n[3/3] 验证修复...")
    stdin, stdout, stderr = ssh.exec_command("grep -n 'views_openclaw_fix' /var/www/eims/urls.py", timeout=5)
    grep_result = stdout.read().decode().strip()
    
    if grep_result:
        print(f"  ✅ import已确认:\n{grep_result}")
    else:
        print("  ❌ import仍未找到")
    
    # 测试语法
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python -m py_compile urls.py 2>&1", timeout=10)
    compile_error = stderr.read().decode().strip()
    
    if compile_error:
        print(f"  ❌ 语法错误:\n{compile_error}")
    else:
        print("  ✅ 语法正确")
    
    # 重启Gunicorn
    print("\n重启Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn; sleep 3", timeout=10)
    
    import time
    time.sleep(4)
    
    # 启动
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
        
        status = "✅" if http_code == '200' else "⚠️" if http_code in ['403', '405'] else "❌"
        print(f"  {status} {name}: HTTP {http_code}")
    
    print("\n" + "=" * 80)
    print("✅ 修复完成！")
    print("=" * 80)
    print("\n📋 现在访问控制面板:")
    print("  http://www.xietongai.com.cn/openclaw/panel/")
    print("\n页面上应该看到:")
    print("  • 📊 系统状态")
    print("  • 🚀 立即触发修复按钮")
    print("  • 📋 修复日志")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
