#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
在嘉诚达项目台账中添加3条测试项目记录
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_project_detail import ProjectDetail
from eims_app.models.model_tenant import Tenant

print("=" * 80)
print("  在嘉诚达项目台账中添加测试项目记录")
print("=" * 80)
print()

# 获取嘉诚达租户
try:
    jiachengda_tenant = Tenant.objects.get(code='jiachengda')
    print(f"✓ 找到嘉诚达租户: ID={jiachengda_tenant.id}, name={jiachengda_tenant.name}")
except Tenant.DoesNotExist:
    print("✗ 找不到嘉诚达租户")
    sys.exit(1)

print()

# 测试项目数据
test_projects = [
    {
        'project_code': 'JCD2026001',
        'contract_code': 'JCD-HT-2026-001',
        'project_name': '南宁市青秀区某住宅小区工程监理项目',
        'contract_category': 'engineering_supervision',
        'project_status': 'under_construction',
        'contract_status': 'executing',
        'settlement_status': 'unsettled',
        'monthly_report_required': True,
        'contract_party_a': '南宁市房地产开发有限公司',
        'contract_party_b': '广西嘉诚达工程造价咨询有限公司',
        'signing_date': date(2026, 1, 15),
        'contract_amount': Decimal('1200000.00'),
        'cumulative_payment': Decimal('360000.00'),
        'contract_balance': Decimal('840000.00'),
        'project_address': '南宁市青秀区民族大道168号',
        'project_scale': '建筑面积约8万㎡',
        'project_investment': Decimal('15000.00'),
        'agreed_staffing': '总监1人，监理工程师3人，监理员2人',
        'service_start_date': date(2026, 2, 1),
        'service_period_months': 18,
        'project_director': '秦林',
        'project_manager': '林漓',
        'contact_phone': '0771-5678901',
        'entry_notice': 'yes',
        'entry_time': date(2026, 2, 10),
        'actual_start_date': date(2026, 2, 15),
        'estimated_completion_date': date(2027, 8, 15),
        'construction_permit_status': 'completed',
        'remark': '重点监理项目，质量要求严格',
    },
    {
        'project_code': 'JCD2026002',
        'contract_code': 'JCD-HT-2026-002',
        'project_name': '南宁市西乡塘区道路改造工程监理',
        'contract_category': 'engineering_supervision',
        'project_status': 'not_started',
        'contract_status': 'pending_review',
        'settlement_status': 'unsettled',
        'monthly_report_required': True,
        'contract_party_a': '南宁市城市管理局',
        'contract_party_b': '广西嘉诚达工程造价咨询有限公司',
        'signing_date': date(2026, 3, 5),
        'contract_amount': Decimal('850000.00'),
        'cumulative_payment': Decimal('0.00'),
        'contract_balance': Decimal('850000.00'),
        'project_address': '南宁市西乡塘区大学东路',
        'project_scale': '道路长度5.2km',
        'project_investment': Decimal('8500.00'),
        'agreed_staffing': '总监1人，监理工程师2人',
        'service_start_date': date(2026, 4, 1),
        'service_period_months': 12,
        'project_director': '王敏志',
        'project_manager': '方永明',
        'contact_phone': '0771-5678902',
        'entry_notice': 'no',
        'construction_permit_status': 'in_progress',
        'remark': '市政道路工程，预计4月份开工',
    },
    {
        'project_code': 'JCD2026003',
        'contract_code': 'JCD-HT-2026-003',
        'project_name': '南宁市江南区商业中心造价咨询项目',
        'contract_category': 'cost_consulting',
        'project_status': 'under_construction',
        'contract_status': 'executing',
        'settlement_status': 'unsettled',
        'monthly_report_required': True,
        'contract_party_a': '南宁市江南区商业投资有限公司',
        'contract_party_b': '广西嘉诚达工程造价咨询有限公司',
        'signing_date': date(2025, 11, 20),
        'contract_amount': Decimal('680000.00'),
        'cumulative_payment': Decimal('408000.00'),
        'contract_balance': Decimal('272000.00'),
        'project_address': '南宁市江南区星光大道',
        'project_scale': '建筑面积约12万㎡',
        'project_investment': Decimal('25000.00'),
        'agreed_staffing': '造价师2人，造价员3人',
        'service_start_date': date(2025, 12, 1),
        'service_period_months': 24,
        'project_director': '唐薇薇',
        'project_manager': '宋弦弦',
        'contact_phone': '0771-5678903',
        'entry_notice': 'yes',
        'entry_time': date(2025, 12, 5),
        'actual_start_date': date(2025, 12, 10),
        'estimated_completion_date': date(2027, 12, 10),
        'construction_permit_status': 'completed',
        'remark': '全过程造价咨询服务',
    },
]

print(f"准备插入 {len(test_projects)} 条项目记录...")
print()

success_count = 0
skip_count = 0
error_count = 0

for idx, project_data in enumerate(test_projects, 1):
    print(f"项目 {idx}: {project_data['project_name']}")
    print("-" * 80)
    
    # 检查是否已存在
    try:
        existing = ProjectDetail.objects.using('jiachengda').get(
            project_code=project_data['project_code']
        )
        print(f"  ⚠ 跳过: 项目已存在 (ID={existing.id})")
        skip_count += 1
        print()
        continue
    except ProjectDetail.DoesNotExist:
        pass
    
    # 创建新项目
    try:
        # 添加租户信息
        project_data['tenant'] = jiachengda_tenant
        
        project = ProjectDetail(**project_data)
        project.save(using='jiachengda')
        
        print(f"  ✓ 创建成功")
        print(f"    项目编号: {project.project_code}")
        print(f"    合同编号: {project.contract_code}")
        print(f"    项目状态: {project.get_project_status_display()}")
        print(f"    合同金额: ¥{project.contract_amount:,.2f}")
        print(f"    项目总监: {project.project_director}")
        print(f"    服务周期: {project.service_period_months} 个月")
        if project.service_deadline:
            print(f"    服务到期: {project.service_deadline}")
        print()
        
        success_count += 1
        
    except Exception as e:
        print(f"  ✗ 创建失败: {e}")
        print()
        error_count += 1

print()
print("=" * 80)
print("  插入结果汇总")
print("=" * 80)
print(f"✓ 成功: {success_count} 条")
print(f"⚠ 跳过: {skip_count} 条")
print(f"✗ 失败: {error_count} 条")
print()

# 验证插入结果
if success_count > 0:
    print("验证: 嘉诚达项目台账中的项目列表")
    print("-" * 80)
    projects = ProjectDetail.objects.using('jiachengda').all().order_by('project_code')
    
    print(f"总计: {projects.count()} 条项目记录")
    print()
    for p in projects:
        print(f"  {p.project_code} | {p.project_name[:30]} | {p.get_project_status_display()} | ¥{p.contract_amount:,.2f}")

print()
print("=" * 80)
print("  ✅ 所有操作完成！")
print("=" * 80)
print()
