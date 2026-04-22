#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查HTTPS配置并诊断问题
Check HTTPS configuration and diagnose issues
"""
import paramiko
import time

def main():
    print("=" * 70)
    print("HTTPS配置检查")
    print("HTTPS Configuration Check")
    print("=" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("\n[1] 连接服务器...")
        ssh.connect('39.106.41.239', port=22, username='root', password='fjkl546#')
        print("✓ SSH 连接成功")
        
        # 检查Nginx监听的端口
        print("\n[2] 检查Nginx监听端口...")
        stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep nginx')
        ports = stdout.read().decode()
        print(ports)
        
        # 检查防火墙状态
        print("\n[3] 检查防火墙状态...")
        stdin, stdout, stderr = ssh.exec_command('firewall-cmd --list-all')
        firewall = stdout.read().decode()
        print(firewall)
        
        # 测试HTTP访问
        print("\n[4] 测试HTTP访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "HTTP状态码: %{http_code}\\n" http://localhost/')
        http_status = stdout.read().decode()
        print(http_status)
        
        # 测试HTTPS访问
        print("\n[5] 测试HTTPS访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -k -s -o /dev/null -w "HTTPS状态码: %{http_code}\\n" https://localhost/')
        https_status = stdout.read().decode()
        print(https_status)
        
        # 检查SSL证书
        print("\n[6] 检查SSL证书配置...")
        stdin, stdout, stderr = ssh.exec_command('ls -la /etc/nginx/ssl/ 2>/dev/null || echo "SSL目录不存在"')
        ssl_check = stdout.read().decode()
        print(ssl_check)
        
        # 检查Nginx配置
        print("\n[7] 当前Nginx配置中的server块...")
        stdin, stdout, stderr = ssh.exec_command('grep -A 5 "listen" /usr/local/nginx/conf/nginx.conf | head -20')
        nginx_config = stdout.read().decode()
        print(nginx_config)
        
        print("\n" + "=" * 70)
        print("诊断结果")
        print("=" * 70)
        
        if '443' not in ports:
            print("❌ Nginx未监听HTTPS端口443")
            print("   → 需要配置SSL证书并启用HTTPS")
        else:
            print("✓ Nginx已监听HTTPS端口443")
        
        if '443' in firewall:
            print("✓ 防火墙已开放443端口")
        else:
            print("❌ 防火墙未开放443端口")
            print("   → 需要执行: firewall-cmd --permanent --add-port=443/tcp")
        
        if 'ssl' in nginx_config.lower():
            print("✓ Nginx已配置SSL")
        else:
            print("❌ Nginx未配置SSL")
            print("   → 需要添加SSL证书配置")
        
        print("\n" + "=" * 70)
        print("建议解决方案")
        print("=" * 70)
        print("\n方案1: 使用HTTP访问（立即可用）")
        print("   http://www.xietongai.com.cn/")
        print("   http://39.106.41.239/")
        
        print("\n方案2: 配置HTTPS（需要SSL证书）")
        print("   1. 获取SSL证书（Let's Encrypt免费证书或购买）")
        print("   2. 配置Nginx启用HTTPS")
        print("   3. 开放防火墙443端口")
        print("   4. 重启Nginx服务")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
