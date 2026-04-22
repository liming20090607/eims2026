#!/usr/bin/env python3
"""
测试SSH免密码登录是否正常工作
Test SSH key-based authentication
"""
import paramiko
import os

print("=" * 80)
print("🧪 测试SSH免密码登录")
print("Test SSH Passwordless Login")
print("=" * 80)

# 服务器信息
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'

# 获取私钥路径
private_key_path = os.path.expanduser('~/.ssh/id_rsa')

print(f"\n私钥路径: {private_key_path}")
print(f"私钥存在: {os.path.exists(private_key_path)}")

try:
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("\n尝试使用密钥连接...")
    
    # 使用密钥连接（不需要密码）
    ssh.connect(
        SERVER_IP,
        username=SERVER_USER,
        key_filename=private_key_path,
        timeout=10
    )
    
    print("✅ 连接成功！无需输入密码\n")
    
    # 执行一些测试命令
    tests = [
        ("主机名", "hostname"),
        ("系统信息", "uname -a"),
        ("当前用户", "whoami"),
        ("日期时间", "date"),
    ]
    
    for name, cmd in tests:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
        result = stdout.read().decode().strip()
        print(f"{name}: {result}")
    
    print("\n" + "=" * 80)
    print("✅ SSH免密码登录工作正常！")
    print("=" * 80)
    
    print("\n💡 现在可以:")
    print("  • 运行任何Python脚本都不需要输入密码")
    print("  • 使用 'ssh eims-server' 直接登录")
    print("  • 自动化部署和运维")
    
    ssh.close()
    
except paramiko.AuthenticationException:
    print("❌ 密钥认证失败")
    print("\n可能的原因:")
    print("  1. 密钥未正确上传到服务器")
    print("  2. SSH服务需要重启")
    print("  3. 权限配置不正确")
    print("\n请重新运行: python setup_ssh_key.py")
    
except Exception as e:
    print(f"❌ 连接失败: {e}")
    import traceback
    traceback.print_exc()
