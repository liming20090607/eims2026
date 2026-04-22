#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查OpenClaw安装状态和能力
Check OpenClaw installation status and capabilities
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("检查OpenClaw安装状态")
    print("Check OpenClaw Installation Status")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 检查OpenClaw是否安装
        print("\n[2] 检查OpenClaw安装...")
        check_commands = [
            ('which openclaw', 'OpenClaw路径'),
            ('openclaw --version', 'OpenClaw版本'),
            ('openclaw --help', 'OpenClaw帮助信息'),
        ]
        
        openclaw_installed = False
        
        for cmd, desc in check_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            print(f"\n   {desc}:")
            if output:
                print(f"   {output[:300]}")
                if 'version' in cmd.lower() or '--version' in cmd:
                    openclaw_installed = True
            if error and 'not found' not in error.lower():
                print(f"   错误: {error[:200]}")
        
        # 检查OpenClaw配置文件
        print("\n[3] 检查OpenClaw配置...")
        config_locations = [
            '~/.openclaw/config.yaml',
            '~/.openclaw/config.yml',
            '/etc/openclaw/config.yaml',
            '/root/.openclaw/config.yaml',
        ]
        
        for config_path in config_locations:
            stdin, stdout, stderr = ssh.exec_command(f'ls -la {config_path} 2>/dev/null && cat {config_path} 2>/dev/null || echo "Not found"')
            config_output = stdout.read().decode()
            
            if 'Not found' not in config_output:
                print(f"\n✓ 找到配置文件: {config_path}")
                print(config_output[:500])
        
        # 检查OpenClaw进程
        print("\n[4] 检查OpenClaw进程...")
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep openclaw | grep -v grep')
        processes = stdout.read().decode()
        
        if processes.strip():
            print("✓ OpenClaw进程正在运行:")
            print(processes[:500])
        else:
            print("  OpenClaw进程未运行")
        
        # 检查OpenClaw服务
        print("\n[5] 检查OpenClaw服务...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status openclaw 2>/dev/null || service openclaw status 2>/dev/null || echo "No systemd service"')
        service_status = stdout.read().decode()
        print(service_status[:500])
        
        # 检查相关工具
        print("\n[6] 检查相关工具...")
        tools = ['docker', 'docker-compose', 'kubectl', 'helm', 'ansible']
        
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f'which {tool} 2>/dev/null && {tool} --version 2>/dev/null | head -1 || echo "Not installed"')
            tool_output = stdout.read().decode().strip()
            if 'Not installed' not in tool_output:
                print(f"   ✓ {tool}: {tool_output[:100]}")
        
        print("\n" + "=" * 70)
        print("总结")
        print("=" * 70)
        
        if openclaw_installed:
            print("✅ OpenClaw已安装")
            print("\n可以协助的工作:")
            print("1. 自动化服务器管理")
            print("2. 部署和配置管理")
            print("3. 监控和日志分析")
            print("4. 安全检查和加固")
            print("5. 性能优化")
            print("6. 备份和恢复")
            print("7. CI/CD流程自动化")
            print("8. 多环境管理")
        else:
            print("⚠️ OpenClaw可能未正确安装或配置")
            print("\n建议:")
            print("1. 检查安装路径")
            print("2. 查看安装日志")
            print("3. 重新安装或配置")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
