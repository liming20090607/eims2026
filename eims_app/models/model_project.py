# E:\EIMS\eims_app\models\model_project.py
# 严格保留您上传的model_project.py内容 + 必要增强

from django.db import models
from django.utils import timezone  # 新增：用于 created_at/updated_at
from .model_contract import Contract  # 确保导入路径正确

# 导入新增的模型
from .model_output_payment import OutputPayment
from .model_personnel import Personnel
from .model_project_dynamic import ProjectDynamic

class Project(models.Model):
    """项目管理核心模型 - 与合同表通过project_code精准关联"""
    
    # ===== 项目基础信息 =====
    project_code = models.CharField("项目编号", max_length=50, unique=True, db_index=True, 
                                   help_text="唯一标识，用于关联合同表的project_code字段")
    project_name = models.CharField("项目名称", max_length=200, db_index=True)
    
    PROJECT_CATEGORY_CHOICES = [
        ('infrastructure', '基础设施'),
        ('construction', '房屋建筑'),
        ('municipal', '市政工程'),
        ('transportation', '交通工程'),
        ('water', '水利工程'),
        ('other', '其他')
    ]
    project_category = models.CharField("项目类别", max_length=20, choices=PROJECT_CATEGORY_CHOICES)
    project_address = models.CharField("项目地址", max_length=255, blank=True)
    project_scale = models.CharField("项目规模", max_length=100, blank=True, 
                                   help_text="如：建筑面积5万㎡/道路长度10km")
    project_investment = models.DecimalField("项目投资(万元)", max_digits=15, decimal_places=2, 
                                           null=True, blank=True, help_text="计划总投资额")
    
    # ===== 关键时间节点 =====
    notice_date = models.DateField("进场通知书日期", null=True, blank=True)
    entry_time = models.DateField("进场时间", null=True, blank=True)
    actual_start_time = models.DateField("实际开工时间", null=True, blank=True)
    planned_completion_time = models.DateField("预计竣工时间", null=True, blank=True)
    
    # ===== 项目状态与延期 =====
    PROJECT_STATUS_CHOICES = [
        ('not_started', '未开工'),
        ('normal_construction', '正常施工'),
        ('stopped', '在停工'),
        ('completed', '已完工')
    ]
    project_status = models.CharField("项目状态", max_length=20, choices=PROJECT_STATUS_CHOICES, 
                                    default='not_started')
    is_delayed = models.BooleanField("是否延期", default=False)
    delay_status = models.CharField("延期情况", max_length=100, blank=True, 
                                  help_text="如：延期45天（自动计算）")
    delay_description = models.TextField("延期说明", blank=True)
    
    # ===== 人员职责 =====
    project_manager = models.CharField("现场负责人", max_length=50, blank=True)
    project_director = models.CharField("项目总监", max_length=50, blank=True, db_index=True)
    actual_manager = models.CharField("实际负责人", max_length=50, blank=True, db_index=True)
    
    # ===== 辅助信息 =====
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)  # 新增：自动记录创建时间
    updated_at = models.DateTimeField("更新时间", auto_now=True)    # 新增：自动更新时间
    
    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目管理"
        ordering = ['-created_at']  # 优化：按创建时间倒序
        indexes = [
            models.Index(fields=['project_code', 'project_name']),
            models.Index(fields=['project_category', 'project_status']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    # ========== 合同关联方法（精准修复）==========
    @property
    def related_contracts(self):
        """获取所有关联的合同（通过project_code精准匹配）"""
        # ✅ 修复：使用project_code而非外键（兼容您原有的设计）
        return Contract.objects.filter(project_code=self.project_code)
    
    @property
    def contract_count(self):
        """关联合同数量（用于列表显示）"""
        return self.related_contracts.count()
    
    @property
    def main_contract(self):
        """获取主合同（按金额最大的合同）"""
        return self.related_contracts.order_by('-contract_amount').first()
    
    # ========== 产值回款关联 ==========
    @property
    def related_output_payments(self):
        """获取所有关联的产值回款（通过项目编号）"""
        return OutputPayment.objects.filter(project_code=self.project_code).order_by('-month')
    
    # ========== 项目人员关联 ==========
    @property
    def related_personnel(self):
        """获取所有关联的项目人员（通过项目编号）"""
        return Personnel.objects.filter(project_code=self.project_code).order_by('-entry_time')
    
    # ========== 项目动态关联 ==========
    @property
    def related_dynamics(self):
        """获取所有关联的项目动态（通过项目编号）"""
        return ProjectDynamic.objects.filter(project_code=self.project_code).order_by('-update_time')