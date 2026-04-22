import subprocess
import time

print("="*60)
print("手动重置 MySQL 密码 - 详细步骤")
print("="*60)

# 检查 MySQL 服务状态
print("\n[1] 检查 MySQL 服务状态...")
result = subprocess.run(['sc', 'query', 'MySQL80'], capture_output=True, text=True)
print(result.stdout)

# 停止服务
print("\n[2] 停止 MySQL80 服务...")
subprocess.run(['net', 'stop', 'MySQL80'], capture_output=True)
time.sleep(3)

# 确认服务已停止
result = subprocess.run(['sc', 'query', 'MySQL80'], capture_output=True, text=True)
if 'STOPPED' in result.stdout or '1  STOPPED' in result.stdout:
    print("✅ MySQL 服务已停止")
else:
    print("⚠️ 服务可能仍在运行，尝试强制停止...")
    subprocess.run(['taskkill', '/F', '/IM', 'mysqld.exe'], 
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

print("\n✅ 准备就绪，请手动执行以下步骤:")
print("\n方法 A - 使用 MySQL 安装目录的命令:")
print('1. 以管理员身份打开命令提示符')
print('2. 执行: cd "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin"')
print('3. 执行: mysqld --skip-grant-tables --console')
print('4. 保持这个窗口打开，再打开一个新的命令提示符')
print('5. 在新窗口执行: mysql -u root')
print("6. 在 MySQL 提示符下依次执行:")
print("   FLUSH PRIVILEGES;")
print("   ALTER USER 'root'@'localhost' IDENTIFIED BY 'mysql2026!';")
print("   FLUSH PRIVILEGES;")
print("   exit;")
print('7. 回到第一个窗口，按 Ctrl+C 停止 mysqld')
print('8. 执行: net start MySQL80')

print("\n方法 B - 我帮您自动执行（需要管理员权限）:")
print("请在新的终端以管理员身份运行:")
print("  powershell -Command \"Start-Process powershell -Verb RunAs\"")
print("然后在新窗口执行重置脚本")
