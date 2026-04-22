"""
批量迁移视图层 - 将所有子模块视图从旧模型切换到统一表
"""

import re

# 读取文件
with open('eims_app/views/views_cost_sub_modules.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义替换规则
replacements = [
    # 任务计划模块
    (r'queryset = CostTaskPlan\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'plan_compiler\', \'plan_first_reviewer\', \'plan_second_reviewer\', \'plan_third_reviewer\', \'created_at\').all()'),
    (r'queryset = CostTaskPlan\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostTaskPlan,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostTaskPlan\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
    (r'CostTaskPlan\.PROJECT_STATUS_CHOICES', 
     r'CostProjectUnified.PROJECT_STATUS_CHOICES'),
    
    # 任务实施模块
    (r'queryset = CostTaskImplementation\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'impl_compiler\', \'impl_first_reviewer_personnel\', \'implementation_status\', \'created_at\').all()'),
    (r'queryset = CostTaskImplementation\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostTaskImplementation,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostTaskImplementation\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
    
    # 审核成果模块
    (r'queryset = CostReviewResult\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'review_compiler\', \'review_final_approved_amount\', \'created_at\').all()'),
    (r'queryset = CostReviewResult\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostReviewResult,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostReviewResult\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
    
    # 收费情况模块
    (r'queryset = CostPaymentStatus\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'payment_invoice_amount\', \'payment_is_invoiced\', \'payment_is_settled\', \'created_at\').all()'),
    (r'queryset = CostPaymentStatus\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostPaymentStatus,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostPaymentStatus\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
    
    # 项目存档模块
    (r'queryset = CostProjectArchive\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'archive_status\', \'archive_electronic\', \'archive_paper\', \'created_at\').all()'),
    (r'queryset = CostProjectArchive\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostProjectArchive,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostProjectArchive\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
    
    # 酬劳分配模块
    (r'queryset = CostRemunerationDistribution\.objects\.select_related\(\'project\'\)\.all\(\)', 
     r'queryset = CostProjectUnified.objects.only(\'id\', \'project_code\', \'project_name\', \'remuneration_total_remuneration\', \'remuneration_distribution_status\', \'created_at\').all()'),
    (r'queryset = CostRemunerationDistribution\.objects\.all\(\)', 
     r'queryset = CostProjectUnified.objects.all()'),
    (r'get_object_or_404\(CostRemunerationDistribution,', 
     r'get_object_or_404(CostProjectUnified,'),
    (r'CostRemunerationDistribution\.objects\.filter\(id__in=ids\)\.delete\(\)', 
     r'CostProjectUnified.objects.filter(id__in=ids).delete()'),
]

# 执行替换
for old_pattern, new_pattern in replacements:
    content = re.sub(old_pattern, new_pattern, content)

# 写回文件
with open('eims_app/views/views_cost_sub_modules.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("批量替换完成！")
print(f"共执行了 {len(replacements)} 个替换规则")
