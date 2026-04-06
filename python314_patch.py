"""
Python 3.14 兼容性补丁
修复 Django 4.2.x 在 Python 3.14 上的 Context.__copy__ 问题
"""
import sys
from django.template.context import Context

# 检查 Python 版本
if sys.version_info >= (3, 14):
    # 保存原始 __copy__ 方法
    _original_copy = Context.__copy__
    
    def _patched_copy(self):
        """修复 Python 3.14 的 Context 复制问题"""
        # 直接创建新的 Context 实例并复制属性
        duplicate = Context(
            dict_=self.dicts[0].copy() if self.dicts else {},
            use_l10n=self.use_l10n,
            use_tz=self.use_tz,
            autoescape=self.autoescape,
        )
        # 复制剩余的 dicts
        if len(self.dicts) > 1:
            duplicate.dicts = [self.dicts[0]] + self.dicts[1:]
        return duplicate
    
    # 应用补丁
    Context.__copy__ = _patched_copy
    import sys
    if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower():
        print("✓ Applied Python 3.14 compatibility patch for Django Context")
    else:
        print("[OK] Applied Python 3.14 compatibility patch for Django Context")
