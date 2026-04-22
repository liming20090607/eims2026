# -*- coding: utf-8 -*-
"""
EIMS Django服务器启动器
自动检测端口8000是否已运行，如未运行则自动启动
"""
import socket
import subprocess
import sys
import os
import ctypes

def check_port(port=8000):
    """检测端口是否被占用"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex(('127.0.0.1', port))
    s.close()
    return result == 0

def notify(title, message):
    """弹出Windows通知"""
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x40)
    except:
        print(f"{title}: {message}")

def main():
    port = 8000
    
    print(f"正在检测Django服务器 (端口 {port})...")
    
    if check_port(port):
        notify("EIMS服务器", f"✅ 服务器已在运行中！\n\n请访问: http://localhost:{port}/")
    else:
        print("服务器未运行，正在启动...")
        notify("EIMS服务器", f"⚠️ 服务器未运行，正在启动...\n\n请稍候刷新页面: http://localhost:{port}/")
        
        # 启动服务器
        os.chdir(r"E:\EIMS2026")
        subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        notify("EIMS服务器", f"✅ 服务器已启动！\n\n请访问: http://localhost:{port}/")

if __name__ == "__main__":
    main()
