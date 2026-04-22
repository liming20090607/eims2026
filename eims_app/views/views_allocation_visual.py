import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from eims_app.models import Personnel, PersonnelAllocation, Department
from eims_app.models.model_project_detail import ProjectDetail  # 改用 ProjectDetail
from eims_app.forms.form_personnel_detail import PersonnelAllocationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
import json

def is_superuser(user):
    return user.is_superuser

def has_personnel_permission(user):
    """检查用户是否具有人员管理权限"""
    if user.is_superuser:
        return True
    return user.has_perm('eims_app.view_personnel') or user.has_perm('eims_app.change_personnel')

# ==================== 可视化人员分配 ====================

@login_required
@user_passes_test(has_personnel_permission)
def allocation_visual(request):
    """可视化人员分配页面 - 支持复选、双击等交互方式"""
    
    # 如果是 /root/ 路径且没有选择公司，重定向到公司选择页面
    if hasattr(request, 'current_system') and request.current_system == 'root':
        if not hasattr(request, 'tenant') or not request.tenant:
            from django.contrib import messages
            messages.warning(request, '请先选择要查看的公司')
            return redirect('eims_app:tenant_select')
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    department_filter = request.GET.get('department', '')
    
    # 查询所有人员（按租户过滤）
    personnel_filter = {'is_deleted': False}
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    all_personnel = Personnel.objects.filter(**personnel_filter).order_by('personnel_code')
    
    # 分类逻辑：
    # 1. 待分配人员：所有5个项目都为空，且部门为空或"未分配"
    # 2. 部门人员：有部门的人员（无论是否有项目）
    # 3. 项目人员：有任一项目的人员（用于单独显示）
    
    # 待分配人员：所有项目字段都为空，且部门为空/未分配
    unassigned_personnel = all_personnel.filter(
        Q(project__isnull=True) &
        Q(project2__isnull=True) &
        Q(project3__isnull=True) &
        Q(project4__isnull=True) &
        Q(project5__isnull=True) &
        (Q(department__isnull=True) | Q(department='') | Q(department='未分配'))
    ).order_by('personnel_code')
    
    # 部门人员：有部门的人员（包括已分配项目和未分配项目的）
    department_personnel = all_personnel.filter(
        department__isnull=False
    ).exclude(
        department__in=[None, '', '未分配']
    ).order_by('personnel_code')
    
    # 项目人员：有任一项目的人员
    project_personnel = all_personnel.filter(
        Q(project__isnull=False) |
        Q(project2__isnull=False) |
        Q(project3__isnull=False) |
        Q(project4__isnull=False) |
        Q(project5__isnull=False)
    ).order_by('personnel_code')
    
    # 筛选处理
    if search_key:
        unassigned_personnel = unassigned_personnel.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(department__icontains=search_key)
        )
        department_personnel = department_personnel.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(department__icontains=search_key)
        )
        project_personnel = project_personnel.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key)
        )
    
    if department_filter:
        unassigned_personnel = unassigned_personnel.filter(department=department_filter)
        department_personnel = department_personnel.filter(department=department_filter)
    
    # 获取所有部门（从组织管理模块）
    dept_filter = {
        'is_deleted': False,
        'status': 'active'
    }
    if hasattr(request, 'tenant') and request.tenant:
        dept_filter['tenant_id'] = request.tenant.id
    
    all_departments = Department.objects.filter(**dept_filter).order_by('order', 'department_code')
    
    # 获取项目列表，按租户过滤
    proj_filter = {}
    if hasattr(request, 'tenant') and request.tenant:
        proj_filter['tenant_id'] = request.tenant.id
    
    projects = ProjectDetail.objects.filter(**proj_filter).order_by('project_code')
    
    context = {
        'unassigned_personnel': unassigned_personnel[:50],  # 限制显示数量
        'assigned_personnel': department_personnel[:50],  # 部门人员（原已分配人员）
        'project_personnel': project_personnel[:50],  # 项目人员
        'all_departments': all_departments,
        'all_projects': projects,
        'selected_department': department_filter,
        'search_keyword': search_key,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/allocation_visual.html", context)


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def allocate_personnel_ajax(request):
    """AJAX 接口：批量分配人员到多个项目（支持一人多项目，每个项目有独立的岗位、分配时间和到岗时间）"""
    try:
        from django.utils import timezone
        data = json.loads(request.body)
        personnel_ids = data.get('personnel_ids', [])
        projects = data.get('projects', [])  # 项目数组，每个项目包含：project_code, position, allocation_date, arrival_date
        
        if not personnel_ids or not projects:
            return JsonResponse({
                'success': False,
                'message': '请选择人员和项目'
            })
        
        allocated_count = 0
        skipped_count = 0
        
        for pid in personnel_ids:
            try:
                personnel = Personnel.objects.get(pk=pid)
                
                # 处理多个项目
                for idx, proj_data in enumerate(projects):
                    project_code = proj_data.get('project_code', '')
                    position = proj_data.get('position', '')
                    allocation_date = proj_data.get('allocation_date', None)
                    arrival_date = proj_data.get('arrival_date', None)
                    
                    if not project_code:
                        continue
                    
                    project = get_object_or_404(ProjectDetail, project_code=project_code)
                    
                    # 检查该人员是否已经分配到这个项目
                    existing_allocation = PersonnelAllocation.objects.filter(
                        personnel=personnel,
                        to_project_code=project_code,
                        allocation_status='allocated'
                    ).first()
                    
                    if existing_allocation:
                        # 已经分配到该项目，更新分配信息而不是跳过
                        if position:
                            existing_allocation.allocation_position = position
                        if allocation_date:
                            existing_allocation.allocation_date = allocation_date
                        if arrival_date:
                            existing_allocation.remark = f"岗位：{position}, 分配时间：{allocation_date or '未指定'}, 到岗时间：{arrival_date}"
                        existing_allocation.save()
                        
                        # 更新人员的项目字段
                        if idx == 0:
                            personnel.project = project
                            personnel.project_code = project_code
                            if position:
                                personnel.position = position
                            personnel.save(update_fields=['project', 'project_code', 'position'])
                        else:
                            if idx == 1:
                                personnel.project2 = project
                                personnel.project_code2 = project_code
                            elif idx == 2:
                                personnel.project3 = project
                                personnel.project_code3 = project_code
                            elif idx == 3:
                                personnel.project4 = project
                                personnel.project_code4 = project_code
                            elif idx == 4:
                                personnel.project5 = project
                                personnel.project_code5 = project_code
                            personnel.save()
                        
                        allocated_count += 1
                        continue
                    
                    # 获取旧项目信息
                    old_project = personnel.project
                    
                    # 如果是第一个项目，更新主要项目和人员信息
                    if idx == 0:
                        personnel.project = project
                        personnel.project_code = project_code
                        if position:
                            personnel.position = position
                        personnel.save(update_fields=['project', 'project_code', 'position'])
                    else:
                        # 为第 2-5 个项目更新对应字段
                        if idx == 1:
                            personnel.project2 = project
                            personnel.project_code2 = project_code
                        elif idx == 2:
                            personnel.project3 = project
                            personnel.project_code3 = project_code
                        elif idx == 3:
                            personnel.project4 = project
                            personnel.project_code4 = project_code
                        elif idx == 4:
                            personnel.project5 = project
                            personnel.project_code5 = project_code
                        personnel.save()
                    
                    # 创建分配记录（支持一人多项目）
                    # 优先使用分配时间，如果没有则使用当前日期
                    alloc_date = None
                    if allocation_date:
                        alloc_date = allocation_date
                    elif arrival_date:
                        alloc_date = arrival_date
                    else:
                        alloc_date = timezone.now().date()
                    
                    allocation = PersonnelAllocation.objects.create(
                        allocation_code=f"ALLOC{timezone.now().strftime('%Y%m%d%H%M%S')}{pid}_{idx}",
                        personnel=personnel,
                        personnel_code=personnel.personnel_code,
                        from_project=old_project,
                        from_project_code=old_project.project_code if old_project else '',
                        to_project=project,
                        to_project_code=project_code,
                        allocation_position=position or personnel.position,
                        allocation_date=alloc_date,
                        allocation_status='allocated',
                        operator=request.user.username if request.user.is_authenticated else '',
                        remark=f"岗位：{position}, 分配时间：{allocation_date or '未指定'}, 到岗时间：{arrival_date or '未指定'}" if position or arrival_date else '',
                    )
                    allocated_count += 1
                    
            except Personnel.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功分配 {allocated_count} 人次到项目' + (f'，跳过 {skipped_count} 名已分配人员' if skipped_count > 0 else ''),
            'allocated_count': allocated_count,
            'skipped_count': skipped_count
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"分配人员失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'分配失败：{str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def assign_to_department_ajax(request):
    """AJAX 接口：分配人员到部门"""
    try:
        data = json.loads(request.body)
        personnel_ids = data.get('personnel_ids', [])
        department = data.get('department', '')
        
        if not personnel_ids or not department:
            return JsonResponse({
                'success': False,
                'message': '请选择人员和部门'
            })
        
        updated_count = 0
        for pid in personnel_ids:
            try:
                personnel = Personnel.objects.get(pk=pid)
                personnel.department = department
                personnel.save(update_fields=['department'])
                updated_count += 1
            except Personnel.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功将 {updated_count} 名人员分配到部门 {department}',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"分配部门失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'分配失败：{str(e)}'
        }, status=500)


@login_required
@user_passes_test(has_personnel_permission)
def recall_personnel_ajax(request, pk):
    """AJAX 接口：召回人员（从部门召回公司，待分配状态）"""
    try:
        personnel = get_object_or_404(Personnel, pk=pk)
        old_project = personnel.project
        old_department = personnel.department
        
        # 更新人员状态 - 清空所有部门和项目信息（所有5个项目字段）
        personnel.department = ''
        personnel.position = ''
        personnel.project = None
        personnel.project_code = ''
        personnel.project2 = None
        personnel.project_code2 = ''
        personnel.project3 = None
        personnel.project_code3 = ''
        personnel.project4 = None
        personnel.project_code4 = ''
        personnel.project5 = None
        personnel.project_code5 = ''
        personnel.save(update_fields=['department', 'position', 'project', 'project_code', 
                                      'project2', 'project_code2', 'project3', 'project_code3', 
                                      'project4', 'project_code4', 'project5', 'project_code5'])
        
        # 创建分配记录（召回）
        PersonnelAllocation.objects.create(
            allocation_code=f"RECALL{timezone.now().strftime('%Y%m%d%H%M%S')}{pk}",
            personnel=personnel,
            personnel_code=personnel.personnel_code,
            from_project=old_project,
            from_project_code=old_project.project_code if old_project else '',
            to_project=None,
            to_project_code='',
            allocation_position='待分配',
            allocation_department=old_department,  # 记录原部门
            allocation_date=timezone.now(),
            allocation_status='recalled',
            allocation_reason='从部门召回公司',
            operator=request.user.username if request.user.is_authenticated else '',
        )
        
        return JsonResponse({
            'success': True,
            'message': f'已成功召回人员 {personnel.name}，回到待分配状态'
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"召回人员失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'召回失败：{str(e)}'
        }, status=500)


@login_required
@user_passes_test(has_personnel_permission)
def get_personnel_projects(request, pk):
    """AJAX 接口：获取人员的当前项目分配信息（用于编辑模式）"""
    try:
        personnel = get_object_or_404(Personnel, pk=pk)
        
        # 收集该人员的所有项目分配信息
        projects = []
        
        # 项目 1
        if personnel.project:
            projects.append({
                'project_code': personnel.project_code,
                'position': personnel.position or '',
                'allocation_date': '',  # 需要从 PersonnelAllocation 中获取
                'arrival_date': ''
            })
        
        # 项目 2
        if personnel.project2:
            projects.append({
                'project_code': personnel.project_code2,
                'position': personnel.position or '',
                'allocation_date': '',
                'arrival_date': ''
            })
        
        # 项目 3
        if personnel.project3:
            projects.append({
                'project_code': personnel.project_code3,
                'position': personnel.position or '',
                'allocation_date': '',
                'arrival_date': ''
            })
        
        # 项目 4
        if personnel.project4:
            projects.append({
                'project_code': personnel.project_code4,
                'position': personnel.position or '',
                'allocation_date': '',
                'arrival_date': ''
            })
        
        # 项目 5
        if personnel.project5:
            projects.append({
                'project_code': personnel.project_code5,
                'position': personnel.position or '',
                'allocation_date': '',
                'arrival_date': ''
            })
        
        # 尝试从 PersonnelAllocation 获取更详细的分配信息
        allocations = PersonnelAllocation.objects.filter(
            personnel=personnel,
            allocation_status='allocated'
        ).order_by('-allocation_date')[:5]  # 获取最近 5 条分配记录
        
        # 用分配记录补充信息
        for i, alloc in enumerate(allocations):
            if i < len(projects):
                projects[i]['allocation_date'] = alloc.allocation_date.strftime('%Y-%m-%d') if alloc.allocation_date else ''
                projects[i]['arrival_date'] = alloc.arrival_date.strftime('%Y-%m-%d') if hasattr(alloc, 'arrival_date') and alloc.arrival_date else ''
                if alloc.allocation_position:
                    projects[i]['position'] = alloc.allocation_position
        
        return JsonResponse({
            'success': True,
            'personnel_id': personnel.id,
            'personnel_name': personnel.name,
            'projects': projects
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"获取人员项目信息失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }, status=500)


# 导入 Django 的 timezone
from django.utils import timezone


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def update_personnel_allocation(request, pk):
    """AJAX 接口：更新人员的项目分配（支持一人多项目）"""
    try:
        personnel = get_object_or_404(Personnel, pk=pk)
        data = json.loads(request.body)
        projects = data.get('projects', [])
        
        if not projects:
            return JsonResponse({
                'success': False,
                'message': '请至少选择一个项目'
            })
        
        # 删除该人员的所有现有分配记录
        PersonnelAllocation.objects.filter(
            personnel=personnel,
            allocation_status='allocated'
        ).delete()
        
        # 清除人员的所有项目字段（只到项目 4）
        personnel.project = None
        personnel.project_code = ''
        personnel.project2 = None
        personnel.project_code2 = ''
        personnel.project3 = None
        personnel.project_code3 = ''
        personnel.project4 = None
        personnel.project_code4 = ''
        
        # 重新分配项目（最多 4 个）
        for idx, proj_data in enumerate(projects):
            project_code = proj_data.get('project_code', '')
            position = proj_data.get('position', '')
            allocation_date = proj_data.get('allocation_date', None)
            arrival_date = proj_data.get('arrival_date', None)
            
            if not project_code:
                continue
            
            project = get_object_or_404(ProjectDetail, project_code=project_code)
            
            # 优先使用分配时间，如果没有则使用当前日期
            alloc_date = None
            if allocation_date:
                alloc_date = allocation_date
            elif arrival_date:
                alloc_date = arrival_date
            else:
                alloc_date = timezone.now().date()
            
            # 第一个项目更新主要项目字段
            if idx == 0:
                personnel.project = project
                personnel.project_code = project_code
                if position:
                    personnel.position = position
            else:
                # 为第 2-4 个项目更新对应字段
                if idx == 1:
                    personnel.project2 = project
                    personnel.project_code2 = project_code
                elif idx == 2:
                    personnel.project3 = project
                    personnel.project_code3 = project_code
                elif idx == 3:
                    personnel.project4 = project
                    personnel.project_code4 = project_code
            
            # 创建分配记录
            allocation = PersonnelAllocation.objects.create(
                allocation_code=f"ALLOC{timezone.now().strftime('%Y%m%d%H%M%S')}{pk}_{idx}",
                personnel=personnel,
                personnel_code=personnel.personnel_code,
                from_project=None,
                from_project_code='',
                to_project=project,
                to_project_code=project_code,
                allocation_position=position or personnel.position,
                allocation_date=alloc_date,
                allocation_status='allocated',
                operator=request.user.username if request.user.is_authenticated else '',
                remark=f"岗位：{position}, 分配时间：{allocation_date or '未指定'}, 到岗时间：{arrival_date or '未指定'}" if position or arrival_date else '',
            )
        
        # 保存人员信息
        personnel.save()
        
        return JsonResponse({
            'success': True,
            'message': f'成功更新 {personnel.name} 的项目分配'
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"更新人员分配失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'更新失败：{str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def delete_all_personnel_allocation(request, pk):
    """AJAX 接口：删除人员的所有项目分配"""
    try:
        personnel = get_object_or_404(Personnel, pk=pk)
        
        # 删除该人员的所有分配记录
        deleted_count, _ = PersonnelAllocation.objects.filter(
            personnel=personnel,
            allocation_status='allocated'
        ).delete()
        
        # 清除人员的所有项目字段（只到项目 4）
        personnel.project = None
        personnel.project_code = ''
        personnel.project2 = None
        personnel.project_code2 = ''
        personnel.project3 = None
        personnel.project_code3 = ''
        personnel.project4 = None
        personnel.project_code4 = ''
        personnel.save()
        
        return JsonResponse({
            'success': True,
            'message': f'已成功删除 {personnel.name} 的所有项目分配'
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"删除人员分配失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'删除失败：{str(e)}'
        }, status=500)


# ==================== 部门人员管理 ====================

@login_required
@user_passes_test(has_personnel_permission)
def department_personnel(request):
    """部门人员管理页面 - 显示已分配部门但未分配项目的人员"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    department_filter = request.GET.get('department', '')
    
    # 查询部门人员：department 不为空且 project 为空
    personnel_filter = {
        'is_deleted': False,
        'department__isnull': False
    }
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    department_personnel_qs = Personnel.objects.filter(**personnel_filter).exclude(
        department__in=[None, '', '未分配']
    ).filter(
        project__isnull=True
    ).order_by('department', 'personnel_code')
    
    # 筛选处理
    if search_key:
        department_personnel_qs = department_personnel_qs.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(department__icontains=search_key)
        )
    
    if department_filter:
        department_personnel_qs = department_personnel_qs.filter(department=department_filter)
    
    # 获取所有部门和项目
    dept_filter = {
        'is_deleted': False,
        'status': 'active'
    }
    if hasattr(request, 'tenant') and request.tenant:
        dept_filter['tenant_id'] = request.tenant.id
    
    all_departments = Department.objects.filter(**dept_filter).order_by('order', 'department_code')
    
    proj_filter = {}
    if hasattr(request, 'tenant') and request.tenant:
        proj_filter['tenant_id'] = request.tenant.id
    
    projects = ProjectDetail.objects.filter(**proj_filter).order_by('project_code')
    
    context = {
        'department_personnel': department_personnel_qs[:100],  # 限制显示数量
        'all_departments': all_departments,
        'all_projects': projects,
        'selected_department': department_filter,
        'search_keyword': search_key,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/department_personnel.html", context)


# ==================== 项目人员管理 ====================

@login_required
@user_passes_test(has_personnel_permission)
def project_personnel(request):
    """项目人员管理页面 - 显示已分配项目的人员"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    project_filter = request.GET.get('project', '')
    
    # 查询项目人员：project 不为空
    personnel_filter = {
        'is_deleted': False,
        'project__isnull': False
    }
    if hasattr(request, 'tenant') and request.tenant:
        personnel_filter['tenant_id'] = request.tenant.id
    
    project_personnel_qs = Personnel.objects.filter(**personnel_filter).order_by('project', 'department')
    
    # 筛选处理
    if search_key:
        project_personnel_qs = project_personnel_qs.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(project__project_name__icontains=search_key)
        )
    
    if project_filter:
        project_personnel_qs = project_personnel_qs.filter(project_code=project_filter)
    
    # 获取所有项目
    proj_filter = {}
    if hasattr(request, 'tenant') and request.tenant:
        proj_filter['tenant_id'] = request.tenant.id
    
    projects = ProjectDetail.objects.filter(**proj_filter).order_by('project_code')
    
    context = {
        'project_personnel': project_personnel_qs[:100],  # 限制显示数量
        'all_projects': projects,
        'selected_project': project_filter,
        'search_keyword': search_key,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/project_personnel.html", context)


# ==================== AJAX 接口 ====================

@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def allocate_to_project_ajax(request):
    """AJAX 接口：从部门人员分配到项目"""
    try:
        from django.utils import timezone
        data = json.loads(request.body)
        personnel_ids = data.get('personnel_ids', [])
        projects = data.get('projects', [])
        
        if not personnel_ids or not projects:
            return JsonResponse({
                'success': False,
                'message': '请选择人员和项目'
            })
        
        allocated_count = 0
        
        for pid in personnel_ids:
            try:
                personnel = Personnel.objects.get(pk=pid)
                
                # 处理多个项目
                for idx, proj_data in enumerate(projects):
                    project_code = proj_data.get('project_code', '')
                    position = proj_data.get('position', '')
                    allocation_date = proj_data.get('allocation_date', None)
                    arrival_date = proj_data.get('arrival_date', None)
                    
                    if not project_code:
                        continue
                    
                    project = get_object_or_404(ProjectDetail, project_code=project_code)
                    
                    # 检查该人员是否已经分配到这个项目
                    existing_allocation = PersonnelAllocation.objects.filter(
                        personnel=personnel,
                        to_project_code=project_code,
                        allocation_status='allocated'
                    ).first()
                    
                    if existing_allocation:
                        continue
                    
                    # 获取旧项目信息
                    old_project = personnel.project
                    
                    # 如果是第一个项目，更新主要项目和人员信息
                    if idx == 0:
                        personnel.project = project
                        personnel.project_code = project_code
                        if position:
                            personnel.position = position
                        personnel.save(update_fields=['project', 'project_code', 'position'])
                    else:
                        # 为第 2-5 个项目更新对应字段
                        if idx == 1:
                            personnel.project2 = project
                            personnel.project_code2 = project_code
                        elif idx == 2:
                            personnel.project3 = project
                            personnel.project_code3 = project_code
                        elif idx == 3:
                            personnel.project4 = project
                            personnel.project_code4 = project_code
                        elif idx == 4:
                            personnel.project5 = project
                            personnel.project_code5 = project_code
                        personnel.save()
                    
                    # 创建分配记录
                    alloc_date = None
                    if allocation_date:
                        alloc_date = allocation_date
                    elif arrival_date:
                        alloc_date = arrival_date
                    else:
                        alloc_date = timezone.now().date()
                    
                    allocation = PersonnelAllocation.objects.create(
                        allocation_code=f"ALLOC{timezone.now().strftime('%Y%m%d%H%M%S')}{pid}_{idx}",
                        personnel=personnel,
                        personnel_code=personnel.personnel_code,
                        from_project=old_project,
                        from_project_code=old_project.project_code if old_project else '',
                        to_project=project,
                        to_project_code=project_code,
                        allocation_position=position or personnel.position,
                        allocation_date=alloc_date,
                        allocation_status='allocated',
                        operator=request.user.username if request.user.is_authenticated else '',
                        remark=f"岗位：{position}, 分配时间：{allocation_date or '未指定'}, 到岗时间：{arrival_date or '未指定'}" if position or arrival_date else '',
                    )
                    allocated_count += 1
                    
            except Personnel.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功分配 {allocated_count} 人次到项目',
            'allocated_count': allocated_count
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"分配人员失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'分配失败：{str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def recall_to_company_ajax(request):
    """AJAX 接口：从部门召回公司（待分配状态）"""
    try:
        data = json.loads(request.body)
        personnel_ids = data.get('personnel_ids', [])
        
        if not personnel_ids:
            return JsonResponse({
                'success': False,
                'message': '请选择人员'
            })
        
        updated_count = 0
        for pid in personnel_ids:
            try:
                personnel = Personnel.objects.get(pk=pid)
                # 清空部门和项目信息（包括所有5个项目字段）
                personnel.department = ''
                personnel.position = ''
                personnel.project = None
                personnel.project_code = ''
                personnel.project2 = None
                personnel.project_code2 = ''
                personnel.project3 = None
                personnel.project_code3 = ''
                personnel.project4 = None
                personnel.project_code4 = ''
                personnel.project5 = None
                personnel.project_code5 = ''
                personnel.save(update_fields=['department', 'position', 'project', 'project_code',
                                              'project2', 'project_code2', 'project3', 'project_code3',
                                              'project4', 'project_code4', 'project5', 'project_code5'])
                updated_count += 1
            except Personnel.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功将 {updated_count} 名人员召回公司',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"召回公司失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'召回失败：{str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@user_passes_test(has_personnel_permission)
def recall_to_department_ajax(request):
    """AJAX 接口：从项目召回部门（保留部门信息，清空项目信息）"""
    try:
        from django.utils import timezone
        data = json.loads(request.body)
        personnel_ids = data.get('personnel_ids', [])
        
        if not personnel_ids:
            return JsonResponse({
                'success': False,
                'message': '请选择人员'
            })
        
        updated_count = 0
        for pid in personnel_ids:
            try:
                personnel = Personnel.objects.get(pk=pid)
                old_project = personnel.project
                
                # 清空项目信息，保留部门信息
                personnel.project = None
                personnel.project_code = ''
                personnel.project2 = None
                personnel.project_code2 = ''
                personnel.project3 = None
                personnel.project_code3 = ''
                personnel.project4 = None
                personnel.project_code4 = ''
                personnel.project5 = None
                personnel.project_code5 = ''
                personnel.save()
                
                # 创建分配记录（召回部门）
                PersonnelAllocation.objects.create(
                    allocation_code=f"RECALL{timezone.now().strftime('%Y%m%d%H%M%S')}{pid}",
                    personnel=personnel,
                    personnel_code=personnel.personnel_code,
                    from_project=old_project,
                    from_project_code=old_project.project_code if old_project else '',
                    to_project=None,
                    to_project_code='',
                    allocation_position='待分配',
                    allocation_date=timezone.now(),
                    allocation_status='recalled',
                    allocation_reason='从项目召回部门',
                    operator=request.user.username if request.user.is_authenticated else '',
                )
                updated_count += 1
            except Personnel.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功将 {updated_count} 名人员召回部门',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"召回部门失败：{str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'召回失败：{str(e)}'
        }, status=500)
