#!/usr/bin/env python3
"""
检查Web控制面板部署状态
Check Web Control Panel Deployment Status
"""
import paramiko

print("=" * 80)
print("🔍 检查Web控制面板部署状态")
print("Check Web Control Panel Deployment Status")
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
    # 1. 检查视图文件
    print("[1/6] 检查视图文件...")
    stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/eims/eims_app/views_openclaw_fix.py", timeout=5)
    output = stdout.read().decode().strip()
    if output:
        print(f"  ✅ 视图文件存在: {output}")
    else:
        print("  ❌ 视图文件不存在")
    
    # 2. 检查模板文件
    print("\n[2/6] 检查模板文件...")
    stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/eims/templates/openclaw/control_panel.html", timeout=5)
    output = stdout.read().decode().strip()
    if output:
        print(f"  ✅ 模板文件存在: {output}")
    else:
        print("  ❌ 模板文件不存在")
    
    # 3. 检查URL路由
    print("\n[3/6] 检查URL路由配置...")
    stdin, stdout, stderr = ssh.exec_command("grep -n 'openclaw\|control_panel' /var/www/eims/urls.py", timeout=5)
    output = stdout.read().decode().strip()
    if output:
        print(f"  ✅ URL路由配置:\n{output}")
    else:
        print("  ❌ URL路由未配置")
        
        # 显示urls.py的内容
        print("\n  查看urls.py内容:")
        stdin, stdout, stderr = ssh.exec_command("cat /var/www/eims/urls.py", timeout=5)
        urls_content = stdout.read().decode()
        print(urls_content[:500])
    
    # 4. 检查中间件
    print("\n[4/6] 检查中间件配置...")
    stdin, stdout, stderr = ssh.exec_command("grep -n 'middleware_mysql_autofix' /var/www/eims/settings.py", timeout=5)
    output = stdout.read().decode().strip()
    if output:
        print(f"  ✅ 中间件已配置:\n{output}")
    else:
        print("  ❌ 中间件未配置")
    
    # 5. 测试API接口
    print("\n[5/6] 测试API接口...")
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/api/openclaw/check-status/ -X POST", timeout=10)
    http_code = stdout.read().decode().strip()
    print(f"  API状态码: {http_code}")
    if http_code in ['200', '403', '405']:
        print("  ✅ API接口可访问")
    else:
        print(f"  ⚠️  API接口返回异常状态码: {http_code}")
    
    # 6. 测试控制面板页面
    print("\n[6/6] 测试控制面板页面...")
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/openclaw/panel/", timeout=10)
    http_code = stdout.read().decode().strip()
    print(f"  页面状态码: {http_code}")
    if http_code == '200':
        print("  ✅ 控制面板页面可访问")
    else:
        print(f"  ❌ 控制面板页面无法访问 (HTTP {http_code})")
        
        # 尝试获取错误信息
        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/openclaw/panel/ 2>&1 | head -20", timeout=10)
        error_output = stdout.read().decode().strip()
        if error_output:
            print(f"\n  错误信息:\n{error_output[:300]}")
    
    print("\n" + "=" * 80)
    print("📋 诊断结果")
    print("=" * 80)
    
    # 总结问题
    issues = []
    
    stdin, stdout, stderr = ssh.exec_command("test -f /var/www/eims/eims_app/views_openclaw_fix.py && echo 'OK' || echo 'MISSING'", timeout=5)
    if 'MISSING' in stdout.read().decode():
        issues.append("❌ 视图文件缺失")
    
    stdin, stdout, stderr = ssh.exec_command("test -f /var/www/eims/templates/openclaw/control_panel.html && echo 'OK' || echo 'MISSING'", timeout=5)
    if 'MISSING' in stdout.read().decode():
        issues.append("❌ 模板文件缺失")
    
    stdin, stdout, stderr = ssh.exec_command("grep -q 'openclaw' /var/www/eims/urls.py && echo 'OK' || echo 'MISSING'", timeout=5)
    if 'MISSING' in stdout.read().decode():
        issues.append("❌ URL路由未配置")
    
    if issues:
        print("\n发现的问题:")
        for issue in issues:
            print(f"  {issue}")
        print("\n💡 建议: 重新运行 deploy_web_trigger.py 部署脚本")
    else:
        print("\n✅ 所有组件都已正确部署")
        print("\n📋 访问地址:")
        print("  • 控制面板: http://www.xietongai.com.cn/openclaw/panel/")
        print("  • 或: http://39.106.41.239:8000/openclaw/panel/")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
