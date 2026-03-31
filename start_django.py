import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# 设置 Django 配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# 启动服务器
print("=" * 50)
print("Starting Django development server...")
print("=" * 50)
print()

# 执行 runserver 命令
sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
execute_from_command_line(sys.argv)
