import os
import hashlib
import datetime
from django.conf import settings

def format_date(date_obj, format_str="%Y-%m-%d"):
    """格式化日期对象为字符串（处理None值）"""
    return date_obj.strftime(format_str) if date_obj else "无"

def format_decimal(decimal_obj, decimal_places=2):
    """格式化Decimal金额（处理None值）"""
    return round(decimal_obj, decimal_places) if decimal_obj else 0.00

def calculate_file_md5(file_path):
    """计算文件MD5值（防重复上传）"""
    if not os.path.exists(file_path):
        return ""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in f.chunks():
            md5.update(chunk)
    return md5.hexdigest()

def get_file_size(file_path):
    """获取文件大小（单位：KB，保留2位小数）"""
    if not os.path.exists(file_path):
        return 0.00
    return round(os.path.getsize(file_path) / 1024, 2)

def check_permission(user, permission_code):
    """校验用户权限（后续扩展角色权限用）"""
    # 超级用户默认拥有所有权限
    if user.is_superuser:
        return True
    # 普通用户权限逻辑（可根据实际需求扩展）
    return False

def get_module_verbose_name(module_name):
    """根据模块名获取中文名称（用于页面显示）"""
    module_map = {
        "contract": "合同信息",
        "personnel": "人员信息",
        "project": "项目信息",
        "output": "产值回款",
        "inspect": "巡视检查",
        "collect": "信息收集",
        "file": "文件管理",
        "notice": "通知公告",
    }
    return module_map.get(module_name, module_name) 
