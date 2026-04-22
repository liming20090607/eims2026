#!/usr/bin/env python3
"""
手动触发OpenClaw立即修复MySQL
Manual trigger for OpenClaw to immediately fix MySQL
"""
import paramiko
import time
import sys

print("=" * 80)
print("🚨 手动触发OpenClaw立即修复MySQL")
print("Manually Trigger OpenClaw Immediate MySQL Fix")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('39.106.41.239', username='root', password='fjkl546#', timeout=15)
    print("\n✅ 已连接到服务器\n")
except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    sys.exit(1)

try:
    # 步骤1: 检查当前MySQL状态
    print("[步骤 1/4] 检查MySQL当前状态...")
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1", timeout=10)
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    error = stderr.read().decode('utf-8', errors='ignore').strip()
    
    if 'test' in output.lower() or '1' in output:
        print("  ℹ️  MySQL连接正常，但仍将执行修复以确保稳定性")
    else:
        print("  ❌ MySQL连接失败，立即开始修复...")
    
    # 步骤2: 立即执行增强版修复脚本
    print("\n[步骤 2/4] 执行OpenClaw增强修复脚本...")
    print("  这将在后台运行，请稍候...\n")
    
    # 在后台执行修复脚本
    stdin, stdout, stderr = ssh.exec_command(
        "nohup bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh > /tmp/manual_fix.log 2>&1 &",
        timeout=5
    )
    
    print("  ✅ 修复脚本已在后台启动")
    print("  脚本PID: " + stdout.read().decode().strip())
    
    # 步骤3: 监控修复进度
    print("\n[步骤 3/4] 监控修复进度...")
    print("  " + "-" * 70)
    
    for i in range(30):  # 最多等待60秒（30次 * 2秒）
        time.sleep(2)
        
        # 读取日志
        stdin, stdout, stderr = ssh.exec_command("tail -5 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null", timeout=5)
        log_output = stdout.read().decode('utf-8', errors='ignore').strip()
        
        if log_output:
            lines = log_output.split('\n')
            for line in lines[-3:]:  # 显示最后3行
                if line.strip():
                    print(f"  {line}")
        
        # 检查是否完成
        if '100%' in log_output or '修复完成' in log_output:
            print("\n  ✅ 修复完成！")
            break
        
        if i % 5 == 0 and i > 0:
            print(f"  ... 修复进行中 ({i*2}秒) ...")
    
    # 步骤4: 验证修复结果
    print("\n[步骤 4/4] 验证修复结果...")
    time.sleep(3)
    
    # 测试MySQL
    stdin, stdout, stderr = ssh.exec_command("mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test' 2>&1", timeout=10)
    mysql_output = stdout.read().decode('utf-8', errors='ignore').strip()
    
    # 测试网站
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/login/", timeout=10)
    http_code = stdout.read().decode('utf-8', errors='ignore').strip()
    
    # 显示结果
    print("\n" + "=" * 80)
    print("📊 修复结果")
    print("=" * 80)
    
    if 'test' in mysql_output.lower() or '1' in mysql_output:
        print("  ✅ MySQL: 连接正常")
    else:
        print("  ❌ MySQL: 连接失败")
        print(f"     错误信息: {mysql_output[:200]}")
    
    if http_code == '200':
        print(f"  ✅ 网站: HTTP {http_code} 正常")
    else:
        print(f"  ⚠️  网站: HTTP {http_code}")
    
    # 显示完整日志
    print("\n📋 完整修复日志:")
    print("-" * 80)
    stdin, stdout, stderr = ssh.exec_command("cat /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | tail -30", timeout=5)
    full_log = stdout.read().decode('utf-8', errors='ignore').strip()
    if full_log:
        for line in full_log.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  (日志文件为空)")
    
    print("\n" + "=" * 80)
    print("✅ 手动修复流程完成")
    print("=" * 80)
    
    print("\n💡 提示:")
    print("  • 如果MySQL仍有问题，可以再次运行此脚本")
    print("  • OpenClaw也会每2分钟自动检查并修复")
    print("  • 查看实时日志: tail -f /root/.openclaw/monitoring/logs/auto_fix.log")
    
except KeyboardInterrupt:
    print("\n\n⚠️  用户中断操作")
except Exception as e:
    print(f"\n❌ 执行出错: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
