"""
信号模块 - 自动注册所有信号处理程序
"""

# 导入所有信号处理程序以完成注册
from . import signal_monthly_report_sync

# 确保 Django 加载此模块时自动注册所有信号
__all__ = ['signal_monthly_report_sync']
