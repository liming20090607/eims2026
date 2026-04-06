# -*- coding: utf-8 -*-
"""
服务器问题排查脚本
检查 Gunicorn、Supervisor、防火墙等状态
"""

import os
import sys
import socket

def check_port(port, host='0.0.0.0'):
    """检测端口是否被占用"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False

def main():
    print("=" * 60)
    print("EIMS 服务器问题排查")
    print("=" * 60)
    print()
    
    # 检查端口 8000
    print("📡 检查 Django/Gunicorn 端口 (8000)...")
    if check_port(8000):
        print("✅ 端口 8000 已开放 - Gunicorn 正在运行")
    else:
        print("❌ 端口 8000 未开放 - Gunicorn 可能未运行")
        print("   解决方案：启动 Supervisor 或 Gunicorn 服务")
    print()
    
    # 检查端口 22
    print(" 检查 SSH 端口 (22)...")
    if check_port(22):
        print("✅ 端口 22 已开放 - SSH 服务正常")
    else:
        print("❌ 端口 22 未开放 - SSH 服务异常")
    print()
    
    # 检查进程
    print("🔍 检查 Gunicorn 进程...")
    os.system('ps aux | grep gunicorn | grep -v grep')
    gunicorn_count = os.popen('ps aux | grep gunicorn | grep -v grep | wc -l').read().strip()
    if int(gunicorn_count) > 0:
        print(f"✅ 发现 {gunicorn_count} 个 Gunicorn 进程")
    else:
        print("❌ 未发现 Gunicorn 进程")
    print()
    
    # 检查 Supervisor 状态
    print("🔍 检查 Supervisor 状态...")
    os.system('systemctl status supervisord | head -n 10')
    print()
    
    # 检查防火墙
    print(" 检查防火墙状态...")
    os.system('firewall-cmd --state 2>/dev/null || echo "防火墙命令不可用"')
    print()
    
    # 检查安全组（提示）
    print("🛡️  阿里云安全组检查:")
    print("   请登录阿里云控制台检查:")
    print("   1.  ECS 实例 -> 安全组")
    print("   2.  确认已添加入方向规则:")
    print("      - 端口 8000，协议 TCP，授权对象 0.0.0.0/0")
    print()
    
    # 检查 Django 配置
    print("⚙️  检查 Django 配置...")
    os.chdir('/var/www/eims')
    if os.path.exists('settings.py'):
        print("✅ settings.py 存在")
        # 检查 ALLOWED_HOSTS
        try:
            with open('settings.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ALLOWED_HOSTS' in content:
                    print("✅ ALLOWED_HOSTS 配置存在")
                else:
                    print("⚠️  未找到 ALLOWED_HOSTS 配置")
        except Exception as e:
            print(f"❌ 读取 settings.py 失败：{e}")
    else:
        print("❌ settings.py 不存在")
    print()
    
    # 检查 Nginx（如果使用）
    print(" 检查 Nginx 状态...")
    os.system('systemctl status nginx | head -n 5 2>/dev/null || echo "Nginx 未安装或未运行"')
    print()
    
    print("=" * 60)
    print("排查完成！")
    print("=" * 60)
    print()
    print(" 建议的操作步骤:")
    print("1. 如果 Gunicorn 未运行：sudo supervisorctl start eims")
    print("2. 如果 Supervisor 未运行：sudo systemctl start supervisord")
    print("3. 检查阿里云安全组是否开放 8000 端口")
    print("4. 查看 Gunicorn 日志：sudo tail -f /var/log/eims/error.log")
    print()

if __name__ == "__main__":
    main()
