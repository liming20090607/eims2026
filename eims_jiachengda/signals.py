from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# 导入需要触发信号的模型
from .models.model_contract import Contract
from .models.model_project import Project

# -------------------------- 示例1：合同新增/修改后触发信号 --------------------------
@receiver(post_save, sender=Contract)
def contract_save_handler(sender, instance, created, **kwargs):
    """
    合同新增（created=True）或修改（created=False）后触发
    instance：当前操作的合同对象
    """
    if created:
        # 新增合同逻辑（如记录日志、发送通知）
        print(f"新增合同：{instance.contract_name}（合同号：{instance.contract_code}）")
    else:
        # 修改合同逻辑（如记录修改记录）
        print(f"修改合同：{instance.contract_name}（合同号：{instance.contract_code}）")

# -------------------------- 示例2：项目删除后触发信号 --------------------------
@receiver(post_delete, sender=Project)
def project_delete_handler(sender, instance, **kwargs):
    """项目删除后触发，可用于清理关联数据、记录日志"""
    print(f"删除项目：{instance.project_name}（项目号：{instance.project_no}）")

# -------------------------- 其他模块信号（按需添加） --------------------------
# 可参考上述示例，为Personnel、OutputPayment等模型添加信号触发逻辑
