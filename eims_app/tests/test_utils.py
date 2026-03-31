from django.test import TestCase
from eims_app.utils import format_date, format_decimal, get_module_verbose_name
import datetime
from decimal import Decimal

class TestUtils(TestCase):
    def test_format_date(self):
        """测试日期格式化"""
        date_obj = datetime.date(2026, 1, 1)
        self.assertEqual(format_date(date_obj), "2026-01-01")
        self.assertEqual(format_date(None), "无")

    def test_format_decimal(self):
        """测试金额格式化"""
        self.assertEqual(format_decimal(Decimal("10000.567")), 10000.57)
        self.assertEqual(format_decimal(None), 0.00)

    def test_get_module_verbose_name(self):
        """测试模块名称映射"""
        self.assertEqual(get_module_verbose_name("contract"), "合同信息")
        self.assertEqual(get_module_verbose_name("unknown"), "unknown") 
