import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('39.106.41.239', username='root', password='fjkl546#')

print("\n" + "=" * 80)
print("📊 当前系统状态报告")
print("=" * 80)

# 1. MySQL状态
print("\n【1】MySQL数据库状态:")
stdin, stdout, stderr = ssh.exec_command('mysql -uroot -pEIMS2026_mysql -e "SELECT 1" &>/dev/null && echo "✅ 已连接" || echo "❌ 连接失败"')
mysql_status = stdout.read().decode().strip()
print(f"   {mysql_status}")

# 2. Gunicorn状态
print("\n【2】Gunicorn应用服务器:")
stdin, stdout, stderr = ssh.exec_command('pgrep -c gunicorn 2>/dev/null')
gunicorn_count = stdout.read().decode().strip()
if gunicorn_count and int(gunicorn_count) > 0:
    print(f"   ✅ 运行中 ({gunicorn_count}个工作进程)")
else:
    print(f"   ❌ 未运行")

# 3. Nginx状态
print("\n【3】Nginx反向代理:")
stdin, stdout, stderr = ssh.exec_command('pgrep nginx >/dev/null 2>&1 && echo "✅ 运行中" || echo "❌ 未运行"')
nginx_status = stdout.read().decode().strip()
print(f"   {nginx_status}")

# 4. HTTP访问测试
print("\n【4】网站访问测试:")
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/')
http_code = stdout.read().decode().strip()
if http_code == "200":
    print(f"   ✅ HTTP状态码: {http_code} (正常)")
elif http_code == "302":
    print(f"   ✅ HTTP状态码: {http_code} (重定向，正常)")
elif http_code == "500":
    print(f"   ⚠️  HTTP状态码: {http_code} (服务器错误)")
else:
    print(f"   ❌ HTTP状态码: {http_code}")

# 5. 自动修复系统状态
print("\n【5】OpenClaw自动修复系统:")
stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep "openclaw.*health_check" | head -1')
cron_config = stdout.read().decode().strip()
if cron_config:
    print(f"   ✅ 定时任务已配置: {cron_config}")
else:
    print(f"   ❌ 定时任务未配置")

# 6. 最近的自动修复记录
print("\n【6】最近的自动修复活动:")
stdin, stdout, stderr = ssh.exec_command('tail -20 /root/.openclaw/monitoring/logs/auto_fix.log 2>/dev/null | grep -E "\\[.*%\\]|==========" | tail -15')
log_output = stdout.read().decode().strip()
if log_output:
    for line in log_output.split('\n'):
        if line.strip():
            print(f"   {line}")
else:
    print("   ℹ️  暂无自动修复记录（说明系统运行正常）")

# 7. 健康检查日志
print("\n【7】最近的健康检查:")
stdin, stdout, stderr = ssh.exec_command('tail -10 /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null | grep -E "\\[.*%\\]" | tail -5')
health_log = stdout.read().decode().strip()
if health_log:
    for line in health_log.split('\n'):
        if line.strip():
            print(f"   {line}")
else:
    print("   ℹ️  暂无健康检查记录")

print("\n" + "=" * 80)
print("💡 总结与建议")
print("=" * 80)

# 判断整体状态
all_good = (
    "已连接" in mysql_status and 
    gunicorn_count and int(gunicorn_count) > 0 and 
    "运行中" in nginx_status and
    http_code in ["200", "302"]
)

if all_good:
    print("\n✅ 所有服务运行正常！")
    print("\n您现在可以：")
    print("   • 访问网站: http://www.xietongai.com.cn/login/")
    print("   • 尝试登录系统")
    print("   • 如果MySQL再次故障，系统会在2分钟内自动修复")
else:
    print("\n⚠️  部分服务存在问题，建议执行以下操作：")
    print("   python e:\\EIMS2026\\manual_fix_now.py")

print("\n📝 查看实时进度条：")
print("   SSH登录服务器后运行：")
print("   tail -f /root/.openclaw/monitoring/logs/auto_fix.log")

print("\n" + "=" * 80)

ssh.close()
