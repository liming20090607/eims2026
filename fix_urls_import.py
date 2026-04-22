#!/usr/bin/env python3
"""
修复urls.py中的import问题
Fix urls.py import issue
"""
import paramiko

print("=" * 80)
print("🔧 修复urls.py导入问题")
print("Fix urls.py Import Issue")
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
    # 读取当前urls.py
    print("[步骤 1/3] 读取urls.py...")
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/urls.py", timeout=5)
    urls_content = stdout.read().decode()
    
    print("当前内容（前40行）:")
    print('\n'.join(urls_content.split('\n')[:40]))
    
    # 检查是否已有import
    if 'views_openclaw_fix' in urls_content:
        print("\n✅ views_openclaw_fix已导入")
    else:
        print("\n❌ 缺少views_openclaw_fix导入")
        
        # 添加import
        print("\n[步骤 2/3] 添加import语句...")
        
        # 在文件开头添加import
        lines = urls_content.split('\n')
        new_lines = []
        import_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # 在from django.urls import path, include之后添加
            if not import_added and 'from django.urls import path, include' in line:
                new_lines.append('from eims_app import views_openclaw_fix')
                import_added = True
        
        urls_content = '\n'.join(new_lines)
        
        # 写回文件
        ssh.exec_command(f"cat > /var/www/eims/urls.py << 'URLEOF'\n{urls_content}\nURLEOF")
        print("  ✅ import语句已添加")
    
    # 验证语法
    print("\n[步骤 3/3] 验证Python语法...")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/eims && source venv/bin/activate && python -m py_compile urls.py 2>&1", timeout=10)
    compile_error = stderr.read().decode().strip()
    
    if compile_error:
        print(f"  ❌ 语法错误:\n{compile_error}")
    else:
        print("  ✅ 语法正确")
    
    # 重启Gunicorn
    print("\n重启Gunicorn...")
    ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
    
    start_cmd = """cd /var/www/eims && source venv/bin/activate && nohup gunicorn \
--bind 127.0.0.1:8000 \
--workers 4 \
--timeout 300 \
wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"""
    
    ssh.exec_command(start_cmd, timeout=10)
    
    import time
    time.sleep(5)
    
    # 测试访问
    print("\n测试访问...")
    tests = [
        ("登录页面", "http://127.0.0.1:8000/login/"),
        ("控制面板", "http://127.0.0.1:8000/openclaw/panel/"),
    ]
    
    for name, url in tests:
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", timeout=10)
        http_code = stdout.read().decode().strip()
        
        if http_code == '200':
            print(f"  ✅ {name}: HTTP {http_code}")
        else:
            print(f"  ⚠️  {name}: HTTP {http_code}")
    
    print("\n" + "=" * 80)
    print("✅ 修复完成！")
    print("=" * 80)
    
    print("\n📋 现在可以访问控制面板:")
    print("  http://www.xietongai.com.cn/openclaw/panel/")
    print("  或: http://39.106.41.239:8000/openclaw/panel/")
    
    print("\n💡 页面上应该有:")
    print("  • 📊 系统状态显示")
    print("  • 🚀 立即触发修复按钮")
    print("  • 📋 修复日志显示")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
