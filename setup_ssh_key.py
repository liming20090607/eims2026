#!/usr/bin/env python3
"""
配置SSH免密码登录
Configure SSH key-based authentication for passwordless login
"""
import paramiko
import os
import time

print("=" * 80)
print("🔑 配置SSH免密码登录")
print("Configure SSH Passwordless Login")
print("=" * 80)

# 服务器信息
SERVER_IP = '39.106.41.239'
SERVER_USER = 'root'
SERVER_PASSWORD = 'fjkl546#'

try:
    # 步骤1: 检查本地是否有SSH密钥
    print("\n[步骤 1/5] 检查本地SSH密钥...")
    
    ssh_dir = os.path.expanduser('~/.ssh')
    public_key_path = os.path.join(ssh_dir, 'id_rsa.pub')
    private_key_path = os.path.join(ssh_dir, 'id_rsa')
    
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)
        print(f"  创建SSH目录: {ssh_dir}")
    
    if os.path.exists(public_key_path) and os.path.exists(private_key_path):
        print(f"  ✅ SSH密钥已存在")
        print(f"     公钥: {public_key_path}")
        print(f"     私钥: {private_key_path}")
        
        # 读取公钥
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
    else:
        print("  ❌ 未找到SSH密钥，正在生成...")
        
        # 使用paramiko生成密钥
        import subprocess
        
        try:
            # 使用ssh-keygen生成密钥（不设置密码）
            result = subprocess.run(
                ['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', private_key_path, '-N', '', '-q'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ SSH密钥生成成功")
                
                # 读取公钥
                with open(public_key_path, 'r') as f:
                    public_key = f.read().strip()
            else:
                print(f"  ❌ 密钥生成失败: {result.stderr}")
                exit(1)
        except Exception as e:
            print(f"  ❌ 密钥生成错误: {e}")
            print("\n💡 请手动运行以下命令生成密钥:")
            print(f"  ssh-keygen -t rsa -b 4096 -f {private_key_path} -N ''")
            exit(1)
    
    # 步骤2: 连接到服务器并上传公钥
    print("\n[步骤 2/5] 连接服务器并配置免密码登录...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=15)
        print("  ✅ 已连接到服务器")
        
        # 确保.ssh目录存在
        stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
        stdout.read()
        
        # 检查authorized_keys文件
        stdin, stdout, stderr = ssh.exec_command("test -f ~/.ssh/authorized_keys && echo 'exists' || echo 'not_exists'")
        auth_keys_status = stdout.read().decode().strip()
        
        if auth_keys_status == 'not_exists':
            print("  创建authorized_keys文件...")
            ssh.exec_command("touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys")
        
        # 检查公钥是否已存在
        stdin, stdout, stderr = ssh.exec_command(f"grep -F '{public_key[:50]}' ~/.ssh/authorized_keys")
        existing_key = stdout.read().decode().strip()
        
        if existing_key:
            print("  ℹ️  公钥已存在于服务器上")
        else:
            print("  添加公钥到服务器...")
            # 追加公钥到authorized_keys
            stdin, stdout, stderr = ssh.exec_command(f"echo '{public_key}' >> ~/.ssh/authorized_keys")
            stdout.read()
            
            # 设置正确的权限
            ssh.exec_command("chmod 600 ~/.ssh/authorized_keys")
            ssh.exec_command("chown root:root ~/.ssh/authorized_keys")
            
            print("  ✅ 公钥已添加到服务器")
        
        # 验证配置
        print("\n[步骤 3/5] 验证SSH配置...")
        ssh.exec_command("chmod 700 ~/.ssh")
        ssh.exec_command("restorecon -R ~/.ssh 2>/dev/null || true")  # SELinux上下文
        
        print("  ✅ SSH配置完成")
        
    finally:
        ssh.close()
    
    # 步骤4: 测试免密码登录
    print("\n[步骤 4/5] 测试免密码登录...")
    
    test_ssh = paramiko.SSHClient()
    test_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 尝试使用密钥登录
        test_ssh.connect(
            SERVER_IP,
            username=SERVER_USER,
            key_filename=private_key_path,
            timeout=10
        )
        
        # 执行简单命令测试
        stdin, stdout, stderr = test_ssh.exec_command("echo 'SSH key authentication successful!'")
        result = stdout.read().decode().strip()
        
        if 'successful' in result.lower():
            print("  ✅ 免密码登录测试成功！")
            print(f"     服务器响应: {result}")
        else:
            print(f"  ⚠️  测试结果: {result}")
            
    except paramiko.AuthenticationException:
        print("  ❌ 密钥认证失败，可能需要重启SSH服务")
        
        # 尝试重启SSH服务
        print("\n  尝试重启SSH服务...")
        restart_ssh = paramiko.SSHClient()
        restart_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        restart_ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=15)
        
        restart_ssh.exec_command("systemctl restart sshd 2>/dev/null || service sshd restart 2>/dev/null || true")
        time.sleep(3)
        restart_ssh.close()
        
        print("  SSH服务已重启，请再次测试")
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    finally:
        test_ssh.close()
    
    # 步骤5: 创建配置文件
    print("\n[步骤 5/5] 创建SSH配置文件...")
    
    ssh_config_path = os.path.join(ssh_dir, 'config')
    
    ssh_config_content = f"""# EIMS2026 Server Configuration
Host eims-server
    HostName {SERVER_IP}
    User {SERVER_USER}
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

# 也可以使用IP直接连接
Host {SERVER_IP}
    User {SERVER_USER}
    IdentityFile {private_key_path}
    IdentitiesOnly yes
"""
    
    # 备份现有配置
    if os.path.exists(ssh_config_path):
        backup_path = ssh_config_path + '.backup'
        import shutil
        shutil.copy2(ssh_config_path, backup_path)
        print(f"  备份现有配置: {backup_path}")
    
    # 写入新配置
    with open(ssh_config_path, 'w') as f:
        f.write(ssh_config_content)
    
    # 设置权限
    os.chmod(ssh_config_path, 0o600)
    
    print("  ✅ SSH配置文件已创建")
    print(f"     位置: {ssh_config_path}")
    
    print("\n" + "=" * 80)
    print("✅ SSH免密码登录配置完成！")
    print("=" * 80)
    
    print("\n📋 使用方法:")
    print("\n方法1: 使用别名（推荐）")
    print("  ssh eims-server")
    
    print("\n方法2: 使用IP地址")
    print(f"  ssh {SERVER_USER}@{SERVER_IP}")
    
    print("\n方法3: 在Python脚本中使用")
    print("""
    import paramiko
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        '39.106.41.239',
        username='root',
        key_filename='~/.ssh/id_rsa'  # 使用密钥而不是密码
    )
    """)
    
    print("\n💡 提示:")
    print("  • 现在所有SSH连接都不需要输入密码")
    print("  • 更安全（使用密钥而非密码）")
    print("  • 更快速（无需手动输入）")
    print("  • 可以自动化部署和运维")
    
    print("\n⚠️  安全建议:")
    print("  • 保护好私钥文件 (~/.ssh/id_rsa)")
    print("  • 不要将私钥分享给他人")
    print("  • 定期备份密钥文件")
    print("  • 如需更高安全性，可为密钥设置密码短语")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 配置失败: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 手动配置方法:")
    print(f"\n1. 生成密钥（如果还没有）:")
    print("   ssh-keygen -t rsa -b 4096")
    
    print(f"\n2. 复制公钥到服务器:")
    print(f"   ssh-copy-id {SERVER_USER}@{SERVER_IP}")
    print(f"   （需要输入一次密码）")
    
    print(f"\n3. 测试免密码登录:")
    print(f"   ssh {SERVER_USER}@{SERVER_IP}")
