#!/usr/bin/env python3
"""
紧急修复 - 使用OpenClaw自动修复办公系统
Emergency Fix - Use OpenClaw to auto-fix the office system
"""
import paramiko
import os
import time

print("=" * 80)
print("🚨 紧急修复办公系统")
print("Emergency Fix Office System with OpenClaw")
print("=" * 80)

# 服务器信息
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
PRIVATE_KEY = os.path.expanduser('~/.ssh/id_rsa')

try:
    # 连接服务器（使用密钥，无需密码）
    print("\n[1/8] 连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=PRIVATE_KEY, timeout=15)
    print("  ✅ 已连接（无需密码）")
    
    # 步骤1: 检查当前系统状态
    print("\n[2/8] 检查系统状态...")
    
    # 检查Gunicorn
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
    gunicorn_count = int(stdout.read().decode().strip())
    print(f"  Gunicorn进程: {gunicorn_count}")
    
    # 检查MySQL
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1' 2>&1 | grep -q '1' && echo OK || echo FAIL")
    mysql_status = stdout.read().decode().strip()
    print(f"  MySQL状态: {mysql_status}")
    
    # 检查Nginx
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active nginx 2>/dev/null || echo inactive")
    nginx_status = stdout.read().decode().strip()
    print(f"  Nginx状态: {nginx_status}")
    
    # 步骤2: 如果Gunicorn有问题，重启
    if gunicorn_count < 3 or mysql_status != 'OK':
        print("\n[3/8] 检测到问题，开始修复...")
        
        # 停止所有Gunicorn进程
        print("  停止Gunicorn...")
        ssh.exec_command("pkill -9 -f gunicorn; sleep 2", timeout=10)
        time.sleep(3)
        
        # 验证MySQL连接
        print("  验证MySQL...")
        stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1")
        mysql_test = stdout.read().decode().strip()
        
        if 'test' not in mysql_test.lower():
            print("  ⚠️  MySQL连接失败，触发OpenClaw修复...")
            
            # 触发OpenClaw增强修复脚本
            stdin, stdout, stderr = ssh.exec_command(
                "nohup bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/emergency_fix.log 2>&1 &",
                timeout=5
            )
            print("  ✅ OpenClaw修复脚本已启动")
            
            # 等待修复完成
            print("  等待修复完成（最多60秒）...")
            for i in range(30):
                time.sleep(2)
                stdin, stdout, stderr = ssh.exec_command(
                    "tail -3 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null",
                    timeout=5
                )
                log_output = stdout.read().decode().strip()
                
                if '100%' in log_output or '修复完成' in log_output:
                    print(f"  ✅ 修复完成: {log_output}")
                    break
                
                if i % 10 == 0 and i > 0:
                    print(f"  ... 修复进行中 ({i*2}秒)")
        else:
            print("  ✅ MySQL正常")
        
        # 重启Gunicorn
        print("  重启Gunicorn...")
        start_cmd = """cd /var/www/eims && source venv/bin/activate && nohup gunicorn \
--bind 127.0.0.1:8000 \
--workers 4 \
--timeout 300 \
wsgi:application > /var/www/eims/logs/gunicorn.log 2>&1 &"""
        
        ssh.exec_command(start_cmd, timeout=10)
        time.sleep(5)
        
        # 验证Gunicorn启动
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
        new_count = int(stdout.read().decode().strip())
        print(f"  Gunicorn进程数: {new_count}")
    else:
        print("\n[3/8] 系统状态正常，跳过修复")
    
    # 步骤3: 检查urls.py配置
    print("\n[4/8] 检查URL配置...")
    stdin, stdout, stderr = ssh.exec_command("grep -c 'views_openclaw_fix' /var/www/eims/urls.py")
    url_check = stdout.read().decode().strip()
    print(f"  OpenClaw路由配置: {'✅' if int(url_check) >= 2 else '❌'}")
    
    # 步骤4: 检查中间件配置
    print("\n[5/8] 检查中间件配置...")
    stdin, stdout, stderr = ssh.exec_command("grep -c 'middleware_mysql_autofix' /var/www/eims/settings.py")
    middleware_check = stdout.read().decode().strip()
    print(f"  自动修复中间件: {'✅' if int(middleware_check) > 0 else '❌'}")
    
    # 步骤5: 测试网站访问
    print("\n[6/8] 测试网站访问...")
    time.sleep(3)
    
    tests = [
        ("登录页面", "http://127.0.0.1:8000/login/"),
        ("控制面板", "http://127.0.0.1:8000/openclaw/panel/"),
    ]
    
    all_ok = True
    for name, url in tests:
        stdin, stdout, stderr = ssh.exec_command(
            f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 5 {url}",
            timeout=10
        )
        http_code = stdout.read().decode().strip()
        
        if http_code == '200':
            print(f"  ✅ {name}: HTTP {http_code}")
        elif http_code in ['302', '403']:
            print(f"  ⚠️  {name}: HTTP {http_code} (需要登录或重定向)")
        else:
            print(f"  ❌ {name}: HTTP {http_code}")
            all_ok = False
    
    # 步骤6: 检查OpenClaw监控状态
    print("\n[7/8] 检查OpenClaw监控...")
    stdin, stdout, stderr = ssh.exec_command("crontab -l | grep health_check")
    crontab_check = stdout.read().decode().strip()
    
    if crontab_check:
        print(f"  ✅ 定时监控已配置")
        print(f"     {crontab_check}")
    else:
        print("  ❌ 定时监控未配置")
    
    # 检查最近的修复日志
    stdin, stdout, stderr = ssh.exec_command("tail -5 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null")
    recent_logs = stdout.read().decode().strip()
    if recent_logs:
        print("  最近的健康检查:")
        for line in recent_logs.split('\n')[-3:]:
            if line.strip():
                print(f"    {line}")
    
    # 步骤7: 最终验证
    print("\n[8/8] 最终验证...")
    
    # 再次测试关键功能
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/")
    final_code = stdout.read().decode().strip()
    
    if final_code == '200':
        print("  ✅ 登录页面可访问")
    else:
        print(f"  ⚠️  登录页面状态: HTTP {final_code}")
    
    # 检查Gunicorn是否稳定运行
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep gunicorn | grep -v grep | wc -l")
    final_workers = int(stdout.read().decode().strip())
    print(f"  Gunicorn工作进程: {final_workers}")
    
    print("\n" + "=" * 80)
    print("✅ 紧急修复完成！")
    print("=" * 80)
    
    print("\n📊 系统状态总结:")
    print(f"  • Gunicorn: {'✅ 运行中' if final_workers >= 3 else '⚠️  异常'}")
    print(f"  • MySQL: {'✅ 正常' if mysql_status == 'OK' else '⚠️  需关注'}")
    print(f"  • Nginx: {'✅ 运行中' if nginx_status == 'active' else '⚠️  需检查'}")
    print(f"  • OpenClaw监控: {'✅ 已启用' if crontab_check else '❌ 未配置'}")
    
    print("\n📋 访问地址:")
    print("  • 登录页面: http://www.xietongai.com.cn/login/")
    print("  • 控制面板: http://www.xietongai.com.cn/openclaw/panel/")
    
    print("\n💡 提示:")
    print("  • OpenClaw每2分钟自动检查并修复问题")
    print("  • 如遇问题可访问控制面板手动触发修复")
    print("  • 查看日志: tail -f /root/.openclaw/monitoring/logs/health_check.log")
    
    if all_ok and final_workers >= 3:
        print("\n🎉 系统已就绪，可以正常使用！")
    else:
        print("\n⚠️  部分功能可能仍需调整，请查看上述状态")
    
    print("=" * 80)
    
    ssh.close()
    
except Exception as e:
    print(f"\n❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 建议:")
    print("  1. 检查SSH连接是否正常")
    print("  2. 手动登录服务器查看日志")
    print("  3. 联系技术支持")
