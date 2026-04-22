#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证OpenClaw监控配置
Verify OpenClaw monitoring configuration
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("验证OpenClaw监控配置")
    print("Verify OpenClaw Monitoring Configuration")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 检查目录和文件
        print("\n[2] 检查监控文件...")
        check_files = '''
echo "=== 监控目录 ==="
ls -la /root/.openclaw/monitoring/

echo -e "\\n=== 监控脚本 ==="
ls -la /root/.openclaw/monitoring/scripts/

echo -e "\\n=== 监控配置 ==="
ls -la /root/.openclaw/monitoring/configs/

echo -e "\\n=== 监控日志 ==="
ls -la /root/.openclaw/monitoring/logs/

echo -e "\\n=== 备份目录 ==="
ls -la /var/www/eims/backups/ 2>/dev/null || echo "备份目录不存在"
'''
        stdin, stdout, stderr = ssh.exec_command(check_files)
        files_output = stdout.read().decode()
        print(files_output)
        
        # 检查定时任务
        print("\n[3] 检查定时任务...")
        stdin, stdout, stderr = ssh.exec_command('crontab -l')
        crontab = stdout.read().decode()
        print(crontab)
        
        # 检查健康检查日志
        print("\n[4] 查看健康检查日志...")
        stdin, stdout, stderr = ssh.exec_command('cat /root/.openclaw/monitoring/logs/health_check.log 2>/dev/null || echo "日志文件不存在"')
        health_log = stdout.read().decode()
        if health_log.strip() and '不存在' not in health_log:
            print(health_log[-1000:])
        else:
            print("日志文件尚未生成")
            print("执行手动健康检查...")
            stdin, stdout, stderr = ssh.exec_command('/root/.openclaw/monitoring/scripts/health_check.sh')
            time.sleep(3)
            result = stdout.read().decode()
            print(result)
        
        # 测试健康检查脚本
        print("\n[5] 测试健康检查脚本...")
        stdin, stdout, stderr = ssh.exec_command('bash /root/.openclaw/monitoring/scripts/health_check.sh')
        time.sleep(2)
        test_result = stdout.read().decode()
        print(test_result)
        
        # 检查服务状态
        print("\n[6] 当前服务状态...")
        status_check = '''
echo "Gunicorn进程:"
ps aux | grep gunicorn | grep -v grep | wc -l

echo -e "\\nNginx进程:"
ps aux | grep nginx | grep -v grep | wc -l

echo -e "\\nMySQL进程:"
ps aux | grep mysqld | grep -v grep | wc -l

echo -e "\\n监听端口:"
netstat -tlnp | grep -E ":(80|8000|3306)" || ss -tlnp | grep -E ":(80|8000|3306)"

echo -e "\\n磁盘使用:"
df -h /

echo -e "\\n内存使用:"
free -h
'''
        stdin, stdout, stderr = ssh.exec_command(status_check)
        status_output = stdout.read().decode()
        print(status_output)
        
        print("\n" + "=" * 70)
        print("✅ OpenClaw监控配置验证完成！")
        print("=" * 70)
        
        if 'health_check.sh' in files_output:
            print("\n✓ 监控脚本已创建")
        else:
            print("\n⚠️ 监控脚本可能未正确创建")
        
        if 'monitoring.json' in files_output:
            print("✓ 监控配置已创建")
        else:
            print("⚠️ 监控配置可能未正确创建")
        
        if 'EIMS2026' in crontab or 'health_check' in crontab:
            print("✓ 定时任务已配置")
        else:
            print("⚠️ 定时任务可能未正确配置")
        
        print("\n📋 配置摘要:")
        print("   监控目录: /root/.openclaw/monitoring/")
        print("   健康检查脚本: /root/.openclaw/monitoring/scripts/health_check.sh")
        print("   自动修复脚本: /root/.openclaw/monitoring/scripts/auto_fix.sh")
        print("   监控配置: /root/.openclaw/monitoring/configs/monitoring.json")
        print("   健康检查日志: /root/.openclaw/monitoring/logs/health_check.log")
        print("   自动修复日志: /root/.openclaw/monitoring/logs/auto_fix.log")
        
        print("\n🎯 下一步:")
        print("   1. 监控将自动运行（每5分钟健康检查）")
        print("   2. 可以手动执行: /root/.openclaw/monitoring/scripts/health_check.sh")
        print("   3. 查看日志: tail -f /root/.openclaw/monitoring/logs/health_check.log")
        print("   4. 如需调整配置，编辑: /root/.openclaw/monitoring/configs/monitoring.json")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
