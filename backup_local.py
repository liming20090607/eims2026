import datetime
import json
import os

# 设置当前时间
now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d_%H%M%S")

# 定义备份文件名
backup_file = f"backup_local_{timestamp}.json"

print(f"开始备份数据库到 {backup_file} ...")

# 使用 Django 内置函数进行备份
import django
import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    django.setup()
except Exception as e:
    print(f"Django 设置失败: {e}")
    sys.exit(1)

from django.core import serializers
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session

# 获取所有模型
all_models = apps.get_models()

# 排除不需要备份的模型
excluded_models = [ContentType, Permission, LogEntry, Session]

data = []
for model in all_models:
    if model not in excluded_models and not model._meta.proxy:
        try:
            queryset = model.objects.all()
            serialized_data = serializers.serialize('python', queryset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
            data.extend(serialized_data)
        except Exception as e:
            print(f"警告：无法序列化 {model.__name__}: {e}")

# 自定义 JSON 编码器，处理 datetime 和 Decimal 对象
from decimal import Decimal

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# 保存到文件
try:
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    print(f"成功备份到: {backup_file}")
except Exception as e:
    print(f"备份失败: {e}")
    sys.exit(1)
