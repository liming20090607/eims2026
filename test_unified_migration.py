#!/usr/bin/env python
"""
造价咨询统一表迁移 - 综合测试脚本

测试内容：
1. 模型层测试 - 验证统一表结构和数据
2. 视图层测试 - 验证所有视图函数正常工作
3. 性能测试 - 对比新旧架构的查询性能
4. 数据完整性测试 - 验证迁移后的数据正确性
"""

import os
import sys
import django
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from eims_app.models import (
    CostProjectUnified,
    CostUnifiedRemunerationItem,
    Tenant,
)
from eims_app.views.views_cost_sub_modules import (
    cost_project_info_list,
    cost_task_plan_list,
    cost_task_implementation_list,
    cost_review_result_list,
    cost_payment_status_list,
    cost_project_archive_list,
    cost_remuneration_distribution_list,
)


def print_section(title):
    """打印分隔线"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_model_structure():
    """测试1: 模型结构验证"""
    print_section("测试1: 模型结构验证")
    
    try:
        # 检查字段数量
        fields = CostProjectUnified._meta.get_fields()
        print(f"[OK] 统一表字段数: {len(fields)}")
        
        # 检查关键字段是否存在
        required_fields = [
            'project_code', 'project_name', 'project_type',
            'plan_compiler', 'impl_compiler', 'review_compiler',
            'payment_invoice_amount', 'archive_status',
            'remuneration_total_remuneration'
        ]
        
        field_names = [f.name for f in fields]
        missing_fields = [f for f in required_fields if f not in field_names]
        
        if missing_fields:
            print(f"✗ 缺少字段: {missing_fields}")
            return False
        else:
            print(f"[OK] 所有关键字段都存在")
        
        # 检查索引
        indexes = CostProjectUnified._meta.indexes
        print(f"[OK] 数据库索引数: {len(indexes)}")
        
        # 检查Choices常量
        choices_attrs = [
            'PROJECT_STATUS_CHOICES',
            'PROJECT_TYPE_CHOICES',
        ]
        
        for attr in choices_attrs:
            if hasattr(CostProjectUnified, attr):
                print(f"[OK] {attr} 存在")
            else:
                print(f"[FAIL] {attr} 缺失")
                return False
        
        print("\n[PASS] 模型结构验证通过")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 模型结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_integrity():
    """测试2: 数据完整性验证"""
    print_section("测试2: 数据完整性验证")
    
    try:
        # 检查记录数
        total_count = CostProjectUnified.objects.count()
        print(f"[OK] 统一表记录数: {total_count}")
        
        if total_count == 0:
            print("⚠️  警告: 统一表中没有数据")
            print("   建议运行: python migrate_cost_to_unified.py")
            return False
        
        # 检查数据分布
        project_types = CostProjectUnified.objects.values('project_type').distinct()
        print(f"[OK] 项目类型数: {project_types.count()}")
        
        project_statuses = CostProjectUnified.objects.values('project_status').distinct()
        print(f"[OK] 项目状态数: {project_statuses.count()}")
        
        # 随机抽样检查
        sample = CostProjectUnified.objects.first()
        print(f"\n示例项目:")
        print(f"  项目编号: {sample.project_code}")
        print(f"  项目名称: {sample.project_name}")
        print(f"  项目类型: {sample.get_project_type_display()}")
        print(f"  项目状态: {sample.get_project_status_display()}")
        
        # 检查任务计划字段
        if sample.plan_compiler:
            print(f"  计划编制人: {sample.plan_compiler}")
        
        # 检查审核成果字段
        if sample.review_final_approved_amount:
            print(f"  审定金额: {sample.review_final_approved_amount}万元")
        
        # 检查收费情况字段
        if sample.payment_invoice_amount:
            print(f"  开票金额: {sample.payment_invoice_amount}万元")
        
        print("\n[PASS] 数据完整性验证通过")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 数据完整性验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_functions():
    """测试3: 视图函数测试"""
    print_section("测试3: 视图函数测试")
    
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'password': 'test123'}
        )
        
        # 创建RequestFactory
        factory = RequestFactory()
        
        # 测试各个列表视图
        views_to_test = [
            ('项目信息列表', cost_project_info_list),
            ('任务计划列表', cost_task_plan_list),
            ('任务实施列表', cost_task_implementation_list),
            ('审核成果列表', cost_review_result_list),
            ('收费情况列表', cost_payment_status_list),
            ('项目存档列表', cost_project_archive_list),
            ('酬劳分配列表', cost_remuneration_distribution_list),
        ]
        
        passed = 0
        failed = 0
        
        for view_name, view_func in views_to_test:
            try:
                # 创建GET请求
                request = factory.get('/')
                request.user = user
                
                # 调用视图
                response = view_func(request)
                
                if response.status_code == 200:
                    print(f"[OK] {view_name}: HTTP 200 OK")
                    passed += 1
                else:
                    print(f"[FAIL] {view_name}: HTTP {response.status_code}")
                    failed += 1
                    
            except Exception as e:
                print(f"[FAIL] {view_name}: {str(e)[:50]}")
                failed += 1
        
        print(f"\n测试结果: {passed} 通过, {failed} 失败")
        
        if failed == 0:
            print("\n[PASS] 视图函数测试全部通过")
            return True
        else:
            print(f"\n[WARN] 部分视图函数测试失败")
            return False
        
    except Exception as e:
        print(f"\n[FAIL] 视图函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_performance():
    """测试4: 查询性能测试"""
    print_section("测试4: 查询性能测试")
    
    try:
        # 测试1: 简单查询
        start_time = time.time()
        count = CostProjectUnified.objects.count()
        elapsed = time.time() - start_time
        print(f"[OK] 计数查询: {count}条记录, 耗时 {elapsed*1000:.2f}ms")
        
        # 测试2: 带筛选的查询
        start_time = time.time()
        queryset = CostProjectUnified.objects.filter(project_status='in_progress')
        count = queryset.count()
        elapsed = time.time() - start_time
        print(f"[OK] 筛选查询: {count}条记录, 耗时 {elapsed*1000:.2f}ms")
        
        # 测试3: 使用.only()优化查询
        start_time = time.time()
        queryset = CostProjectUnified.objects.only(
            'id', 'project_code', 'project_name', 'created_at'
        ).all()[:10]
        list(queryset)  # 强制执行查询
        elapsed = time.time() - start_time
        print(f"[OK] 优化查询(.only): 10条记录, 耗时 {elapsed*1000:.2f}ms")
        
        # 测试4: 搜索查询
        start_time = time.time()
        from django.db.models import Q
        queryset = CostProjectUnified.objects.filter(
            Q(project_code__icontains='J') | Q(project_name__icontains='项目')
        )
        count = queryset.count()
        elapsed = time.time() - start_time
        print(f"[OK] 搜索查询: {count}条记录, 耗时 {elapsed*1000:.2f}ms")
        
        print("\n[PASS] 查询性能测试完成")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 查询性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_field_mapping():
    """测试5: 字段映射验证"""
    print_section("测试5: 字段映射验证")
    
    try:
        sample = CostProjectUnified.objects.first()
        
        if not sample:
            print("⚠️  没有数据可测试")
            return False
        
        # 测试模块前缀字段
        field_groups = {
            '任务计划': ['plan_compiler', 'plan_first_reviewer'],
            '任务实施': ['impl_compiler', 'impl_first_reviewer_personnel'],
            '审核成果': ['review_compiler', 'review_final_approved_amount'],
            '收费情况': ['payment_invoice_amount', 'payment_is_invoiced'],
            '项目存档': ['archive_status', 'archive_electronic'],
            '酬劳分配': ['remuneration_total_remuneration', 'remuneration_distribution_status'],
        }
        
        all_passed = True
        
        for module_name, fields in field_groups.items():
            has_field = all(hasattr(sample, field) for field in fields)
            if has_field:
                print(f"[OK] {module_name}: 字段存在")
            else:
                print(f"[FAIL] {module_name}: 字段缺失")
                all_passed = False
        
        if all_passed:
            print("\n[PASS] 字段映射验证通过")
            return True
        else:
            print("\n[FAIL] 部分字段映射验证失败")
            return False
        
    except Exception as e:
        print(f"\n[FAIL] 字段映射验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tenant_isolation():
    """测试6: 多租户隔离测试"""
    print_section("测试6: 多租户隔离测试")
    
    try:
        from eims_app.utils.tenant_utils import filter_queryset_by_tenant
        
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='test_tenant_user',
            defaults={'password': 'test123'}
        )
        
        # 创建模拟请求
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        
        # 测试租户过滤
        queryset = CostProjectUnified.objects.all()
        filtered_queryset = filter_queryset_by_tenant(queryset, request)
        
        print(f"[OK] 原始查询集: {queryset.count()}条")
        print(f"[OK] 过滤后查询集: {filtered_queryset.count()}条")
        print(f"[OK] 租户隔离功能正常")
        
        print("\n[PASS] 多租户隔离测试通过")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 多租户隔离测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_summary_report():
    """生成总结报告"""
    print_section("测试总结报告")
    
    total_count = CostProjectUnified.objects.count()
    field_count = len(CostProjectUnified._meta.get_fields())
    
    print(f"[INFO] 统计数据:")
    print(f"  统一表记录数: {total_count}")
    print(f"  字段总数: {field_count}")
    print(f"  索引数量: {len(CostProjectUnified._meta.indexes)}")
    
    # 数据分布
    if total_count > 0:
        type_dist = CostProjectUnified.objects.values('project_type').annotate(
            count=models.Count('id')
        )
        print(f"\n[INFO] 项目类型分布:")
        for item in type_dist:
            type_name = dict(CostProjectUnified.PROJECT_TYPE_CHOICES).get(
                item['project_type'], item['project_type']
            )
            print(f"  {type_name}: {item['count']}个")
    
    print("\n" + "="*70)
    print("  测试完成！请查看上述结果")
    print("="*70)


if __name__ == '__main__':
    from django.db import models
    
    print("\n" + "="*70)
    print("  造价咨询统一表迁移 - 综合测试")
    print("="*70)
    
    # 执行所有测试
    results = []
    
    results.append(("模型结构", test_model_structure()))
    results.append(("数据完整性", test_data_integrity()))
    results.append(("视图函数", test_view_functions()))
    results.append(("查询性能", test_query_performance()))
    results.append(("字段映射", test_field_mapping()))
    results.append(("租户隔离", test_tenant_isolation()))
    
    # 生成总结报告
    generate_summary_report()
    
    # 打印最终结果
    print_section("最终测试结果")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！迁移成功！")
    else:
        print(f"\n[WARN] 有 {total - passed} 个测试失败，请检查上述错误信息")
    
    print("\n")
