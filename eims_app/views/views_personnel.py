import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
import datetime
from io import BytesIO
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment
from eims_app.models import Personnel, Employee, Department
from eims_app.utils.tenant_utils import filter_queryset_by_tenant
from eims_app.models.model_project_detail import ProjectDetail  # 改用 ProjectDetail
from eims_app.forms.form_personnel import PersonnelForm
from django.urls import reverse 
from django.db import transaction
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_superuser

def personnel_list(request):
    """人员列表页面 - 支持筛选和搜索"""
    
    # 1. 获取筛选参数
    search_key = request.GET.get('keyword', '')
    project_code = request.GET.get('project_code', '')
    department = request.GET.get('department', '')
    position = request.GET.get('position', '')
    
    # 2. 基础查询集
    personnel_list = Personnel.objects.filter(is_deleted=False).select_related('employee').order_by('personnel_code')
    
    # 应用租户过滤
    personnel_list = filter_queryset_by_tenant(personnel_list, request)
    
    # 3. 多条件筛选
    if search_key:
        personnel_list = personnel_list.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(phone__icontains=search_key) |
            Q(department__icontains=search_key) |
            Q(position__icontains=search_key) |
            Q(email__icontains=search_key) |
            Q(remark__icontains=search_key)
        ).distinct()
    
    if project_code:
        personnel_list = personnel_list.filter(project_code=project_code)
    
    if department:
        personnel_list = personnel_list.filter(department=department)
    
    if position:
        personnel_list = personnel_list.filter(position__icontains=position)
    
    # 4. 预获取关联项目信息
    project_info = {}
    for p in ProjectDetail.objects.all():
        project_info[p.project_code] = p
    
    # 为人员对象附加项目信息
    for personnel in personnel_list:
        if personnel.project_code in project_info:
            proj = project_info[personnel.project_code]
            personnel.project_name = proj.project_name if proj.project_name else ''
        else:
            personnel.project_name = ''
    
    # 5. 分页处理
    paginator = Paginator(personnel_list, 15)  # 每页显示 15 条
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        page_obj = paginator.page(1)
    
    # 6. 统计信息
    total_personnel = Personnel.objects.filter(is_deleted=False).count()
    active_personnel = Personnel.objects.filter(is_deleted=False, project__isnull=False).count()
    
    context = {
        "page_obj": page_obj,
        "selected_keyword": search_key,
        "selected_project_code": project_code,
        "selected_department": department,
        "selected_position": position,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
        'total_personnel': total_personnel,
        'active_personnel': active_personnel,
        'all_projects': ProjectDetail.objects.order_by('project_code'),
        'all_departments': Department.objects.filter(is_deleted=False, status='active').order_by('department_code'),
    }
    return render(request, "personnel/list.html", context)


def personnel_navigation(request):
    """人员管理模块导航页面"""
    context = {
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/navigation.html", context)

@user_passes_test(is_superuser)
def personnel_add(request):
    """添加人员"""
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "人员添加成功！")
            return redirect('eims_app:personnel_list')
        else:
            messages.error(request, "人员添加失败，请检查红色标注的输入项！")
    else:
        form = PersonnelForm()
    
    return render(request, 'personnel/add.html', {'form': form})

def personnel_detail(request, pk):
    """人员详情"""
    personnel = get_object_or_404(Personnel, pk=pk, is_deleted=False)
    
    field_data = []
    for field in personnel._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            if field.name in ['id', 'create_time', 'update_time', 'is_deleted']:
                continue
            if hasattr(field, 'choices') and field.choices:
                display_value = getattr(personnel, f'get_{field.name}_display')()
            else:
                display_value = getattr(personnel, field.name, None)
            label = getattr(field, 'verbose_name', field.name).title()
            field_data.append({
                'name': field.name,
                'label': label,
                'value': display_value,
                'type': field.get_internal_type(),
                'has_choices': bool(getattr(field, 'choices', None))
            })
    
    return render(request, 'personnel/detail.html', {
        'personnel': personnel,
        'field_data': field_data
    })

@user_passes_test(is_superuser)
def personnel_edit(request, pk):
    """编辑人员"""
    personnel = get_object_or_404(Personnel, pk=pk, is_deleted=False)
    
    if request.method == "POST":
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(request, "人员信息修改成功！")
            return redirect("eims_app:personnel_list")
        else:
            messages.error(request, "人员信息修改失败，请检查红色标注的输入项！")
    else:
        form = PersonnelForm(instance=personnel)
    
    return render(request, "personnel/edit.html", {
        "form": form,
        "page_title": f"编辑人员：{personnel.name}",
        "personnel": personnel
    })

@user_passes_test(is_superuser)
def personnel_delete(request, pk):
    """删除人员（软删除）"""
    personnel = get_object_or_404(Personnel, pk=pk, is_deleted=False)
    personnel_name = personnel.name
    personnel.is_deleted = True
    personnel.save()
    messages.success(request, f"人员【{personnel_name}】删除成功！")
    return redirect("eims_app:personnel_list")

@user_passes_test(is_superuser)
def personnel_batch_delete(request):
    """批量删除人员"""
    if request.method == 'POST':
        personnel_ids = request.POST.getlist('personnel_ids')
    else:
        personnel_ids = request.GET.get('ids', '').split(',')
    
    personnel_ids = [pid for pid in personnel_ids if pid.isdigit()]
    
    if not personnel_ids:
        messages.warning(request, '未选择任何人员记录')
        return redirect('eims_app:personnel_list')
    
    try:
        with transaction.atomic():
            personnels_to_delete = Personnel.objects.filter(id__in=personnel_ids)
            count = personnels_to_delete.count()
            
            if count == 0:
                messages.warning(request, '未找到要删除的人员记录')
                return redirect('eims_app:personnel_list')
            
            # 软删除
            for p in personnels_to_delete:
                p.is_deleted = True
                p.save()
            
            messages.success(request, f'成功删除 {count} 条人员记录')
            
    except Exception as e:
        messages.error(request, f'删除失败：{str(e)}')
    
    return redirect('eims_app:personnel_list')

@user_passes_test(is_superuser)
def personnel_import(request):
    """导入人员花名册信息（导入到 Employee 模型）"""
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]
        
        if not excel_file.name.endswith(".xlsx"):
            messages.error(request, "导入失败！仅支持.xlsx 格式的 Excel 文件")
            return redirect("eims_app:personnel_list")
        
        if excel_file.size > 10 * 1024 * 1024:
            messages.error(request, "导入失败！文件过大（最大支持 10MB）")
            return redirect("eims_app:personnel_list")
        
        try:
            wb = load_workbook(excel_file)
            ws = wb.active
            
            if ws is None or ws.max_row == 0:
                messages.error(request, "导入失败！Excel 文件为空或无有效工作表")
                return redirect("eims_app:personnel_list")
            
            headers = [str(cell.value).strip() if cell.value is not None else "" for cell in ws[1]]
            required_headers = ["人员编号", "姓名"]
            missing = [h for h in required_headers if h not in headers]
            if missing:
                messages.error(request, f"导入失败！缺少必需表头：{', '.join(missing)}")
                return redirect("eims_app:personnel_list")
            
            if ws.max_row < 2:
                messages.error(request, "导入失败！Excel 文件无有效数据行")
                return redirect("eims_app:personnel_list")
            
            def safe_str(val, default=""):
                if val is None or str(val).strip() == "":
                    return default
                return str(val).strip()
            
            def parse_date(val):
                if not val:
                    return None
                try:
                    if isinstance(val, str):
                        val = val.strip()
                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                            try:
                                return datetime.datetime.strptime(val, fmt).date()
                            except ValueError:
                                continue
                    elif hasattr(val, 'date'):
                        return val.date()
                except Exception:
                    pass
                return None
            
            # 数据映射
            gender_map = {'男': 0, '女': 1, '其他': 2}
            ethnic_map = {
                '汉族': 'han', '回族': 'hui', '满族': 'man', '蒙古族': 'mongol',
                '藏族': 'tibetan', '维吾尔族': 'uyghur', '其他': 'other'
            }
            education_map = {
                '小学': 'primary', '初中': 'junior', '高中': 'senior',
                '大专': 'college', '本科': 'bachelor', '硕士': 'master', '博士': 'doctor'
            }
            
            success_count = 0
            fail_count = 0
            fail_samples = []
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                if not row or all(cell is None for cell in row):
                    continue
                
                try:
                    row_data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                    
                    employee_code = safe_str(row_data.get("人员编号"))
                    name = safe_str(row_data.get("姓名"))
                    
                    if not employee_code:
                        raise ValueError("人员编号为空（必需字段）")
                    if not name:
                        raise ValueError("姓名为空（必需字段）")
                    
                    # 准备 Employee 模型数据
                    employee_data = {
                        "employee_code": employee_code,
                        "name": name,
                        "gender": gender_map.get(safe_str(row_data.get("性别")), 0),
                        "id_card": safe_str(row_data.get("身份证号")),
                        "native_place": safe_str(row_data.get("籍贯")),
                        "ethnic": ethnic_map.get(safe_str(row_data.get("民族")), 'han'),
                        "education": education_map.get(safe_str(row_data.get("学历")), 'bachelor'),
                        "admin_position": safe_str(row_data.get("行政职务")),
                        "tech_position": safe_str(row_data.get("技术职务")),
                        "professional_qualification": safe_str(row_data.get("执业资格")),
                        "professional_title": safe_str(row_data.get("职称")),
                        "job_qualification": safe_str(row_data.get("任职资格")),
                        "mobile": safe_str(row_data.get("手机号码")),
                        "home_phone": safe_str(row_data.get("固定电话")),
                        "address": safe_str(row_data.get("住址")),
                        "emergency_contact": safe_str(row_data.get("应急联系人")),
                        "emergency_phone": safe_str(row_data.get("应急电话")),
                        "wechat": safe_str(row_data.get("微信")),
                        "email": safe_str(row_data.get("邮箱")),
                        "entry_time": parse_date(row_data.get("入职时间")),
                        "leave_time": parse_date(row_data.get("离职时间")),
                        "remark": safe_str(row_data.get("备注")),
                    }
                    
                    # 如果人员编号已存在则更新，否则创建
                    employee, created = Employee.objects.update_or_create(
                        employee_code=employee_code,
                        defaults=employee_data
                    )
                    success_count += 1
                    
                    # 创建对应的 Personnel 记录（二次分配）
                    personnel_data = {
                        "personnel_code": employee_code,
                        "name": name,
                        "gender": gender_map.get(safe_str(row_data.get("性别")), 0),
                        "department": safe_str(row_data.get("部门")) or "未分配",
                        "position": safe_str(row_data.get("岗位")),
                        "phone": safe_str(row_data.get("手机号码")),
                        "email": safe_str(row_data.get("邮箱")),
                        "entry_time": parse_date(row_data.get("入职时间")),
                        "leave_time": parse_date(row_data.get("离职时间")),
                        "employee": employee,  # 关联到 Employee
                        "operator": request.user.username,
                    }
                    
                    # 检查是否已存在 Personnel 记录
                    personnel, personnel_created = Personnel.objects.update_or_create(
                        personnel_code=employee_code,
                        defaults=personnel_data
                    )
                    
                except Exception as e:
                    fail_count += 1
                    if len(fail_samples) < 3:
                        fail_samples.append(f"第{row_idx}行：{str(e)} | 人员编号='{employee_code}'")
            
            msg = f"导入完成！成功{success_count}条，失败{fail_count}条"
            if fail_samples:
                msg += "\n\n失败示例（前 3 条）:\n" + "\n".join(fail_samples)
            messages.success(request, msg)
            return redirect("eims_app:personnel_list")
            
        except Exception as e:
            import traceback
            print("\n" + "="*70)
            print("【IMPORT CRITICAL ERROR】")
            traceback.print_exc()
            print("="*70 + "\n")
            messages.error(request, f"导入异常：{str(e)}（详见控制台日志）")
            return redirect("eims_app:personnel_list")
    
    messages.error(request, "导入失败！未检测到上传文件")
    return redirect("eims_app:personnel_list")

@user_passes_test(is_superuser)
def personnel_import_template(request):
    """下载人员花名册导入模板（Employee 模型）"""
    wb = Workbook()
    ws = wb.active
    ws.title = "人员花名册导入模板"
    
    # 完整的员工信息表头（23 个字段：Employee 21 个 + Personnel 额外 2 个）
    headers = [
        "人员编号", "姓名", "性别", "身份证号", "籍贯", "民族", "学历", 
        "行政职务", "技术职务", "执业资格", "职称", "任职资格", 
        "手机号码", "固定电话", "入职时间", "离职时间", "住址", 
        "应急联系人", "应急电话", "微信", "邮箱", "备注",
        "部门", "岗位"
    ]
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # 示例数据（23 个字段）
    sample_data = [
        "EMP001", "张三", "男", "110101199001011234", "北京", "汉族", "本科", 
        "经理", "工程师", "一级建造师", "高级工程师", "合格", 
        "13800138001", "010-12345678", "2026-01-01", "", "北京市朝阳区", 
        "李四", "13900139002", "zhangsan", "zhangsan@example.com", "示例人员",
        "技术部", "技术员"
    ]
    
    for col_idx, value in enumerate(sample_data, 1):
        ws.cell(row=2, column=col_idx, value=value)
    
    # 设置列宽
    column_widths = {
        "人员编号": 15, "姓名": 15, "身份证号": 20, "籍贯": 15, "民族": 10, "学历": 10,
        "行政职务": 15, "技术职务": 15, "执业资格": 20, "职称": 15, "任职资格": 20,
        "手机号码": 15, "固定电话": 15, "入职时间": 15, "离职时间": 15, "住址": 25,
        "应急联系人": 15, "应急电话": 15, "微信": 15, "邮箱": 25, "备注": 30,
        "部门": 15, "岗位": 15
    }
    
    for col_idx, header in enumerate(headers, 1):
        width = column_widths.get(header, 12)
        col_letter = chr(64 + col_idx) if col_idx <= 26 else f"{chr(64 + col_idx // 26)}{chr(64 + col_idx % 26)}"
        ws.column_dimensions[col_letter].width = width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = FileResponse(
        buffer,
        as_attachment=True,
        filename='人员花名册导入模板.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    return response

@user_passes_test(is_superuser)
def personnel_export(request):
    """导出人员花名册 - 导出员工基本信息 + 项目分配信息（全部字段）"""
    
    # 获取选中的 ID 列表（POST 请求）
    selected_ids = None
    if request.method == 'POST':
        selected_ids = request.POST.getlist('personnel_ids')
    
    if selected_ids:
        # 从 Personnel 表查询，并预加载关联的 Employee 数据
        personnel_list = Personnel.objects.filter(id__in=selected_ids, is_deleted=False).select_related('employee')
    else:
        # GET 请求：导出全部
        personnel_list = Personnel.objects.filter(is_deleted=False).select_related('employee').order_by('personnel_code')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "人员花名册"
    
    # 完整的员工信息字段（27 个）
    headers = [
        "序号", "人员编号", "姓名", "性别", "身份证号", "籍贯", "民族", 
        "学历", "部门", "行政职务", "技术职务", "执业资格", "职称", "任职资格", 
        "手机号码", "固定电话", "入职时间", "离职时间", "住址", "应急联系人", 
        "应急电话", "微信", "邮箱", "操作人", "创建时间", "更新时间", "备注"
    ]
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # 设置列宽
    column_widths = {
        "姓名": 15, "身份证号": 20, "籍贯": 15, "住址": 25, "备注": 30, 
        "手机号码": 15, "固定电话": 15, "应急联系人": 15, "应急电话": 15, 
        "微信": 15, "邮箱": 25, "人员编号": 15, "部门": 15, "行政职务": 15, "技术职务": 15, 
        "执业资格": 20, "职称": 15, "任职资格": 20, "学历": 10, "民族": 10,
        "操作人": 12, "创建时间": 20, "更新时间": 20
    }
    
    for col_idx, header in enumerate(headers, 1):
        width = column_widths.get(header, 12)  # 默认宽度 12
        col_letter = chr(64 + col_idx) if col_idx <= 26 else f"{chr(64 + col_idx // 26)}{chr(64 + col_idx % 26)}"
        ws.column_dimensions[col_letter].width = width
    
    # 预加载部门信息（如果需要）
    # 数据映射
    gender_map = {0: '男', 1: '女', 2: '其他'}
    ethnic_map = dict(Employee.ETHNIC_CHOICES)
    education_map = dict(Employee.EDUCATION_CHOICES)
    
    for row_idx, personnel in enumerate(personnel_list, 2):
        # 获取关联的 Employee 对象（可能为 None）
        employee = personnel.employee
        
        # 列 1: 序号
        ws.cell(row=row_idx, column=1, value=row_idx-1).alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 2: 人员编号
        ws.cell(row=row_idx, column=2, value=personnel.personnel_code or "-").alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 3: 姓名
        ws.cell(row=row_idx, column=3, value=personnel.name or "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 4: 性别
        ws.cell(row=row_idx, column=4, value=gender_map.get(personnel.gender, "-")).alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 5: 身份证号（从 Employee 获取）
        ws.cell(row=row_idx, column=5, value=employee.id_card if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 6: 籍贯（从 Employee 获取）
        ws.cell(row=row_idx, column=6, value=employee.native_place if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 7: 民族（从 Employee 获取）
        ws.cell(row=row_idx, column=7, value=ethnic_map.get(employee.ethnic, "-") if employee else "-").alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 8: 学历（从 Employee 获取）
        ws.cell(row=row_idx, column=8, value=education_map.get(employee.education, "-") if employee else "-").alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 9: 部门（从 Personnel 获取）
        ws.cell(row=row_idx, column=9, value=personnel.department or "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 10: 行政职务（从 Employee 获取）
        ws.cell(row=row_idx, column=10, value=employee.admin_position if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 11: 技术职务（从 Employee 获取）
        ws.cell(row=row_idx, column=11, value=employee.tech_position if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 12: 执业资格（从 Employee 获取）
        ws.cell(row=row_idx, column=12, value=employee.professional_qualification if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 13: 职称（从 Employee 获取）
        ws.cell(row=row_idx, column=13, value=employee.professional_title if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 14: 任职资格（从 Employee 获取）
        ws.cell(row=row_idx, column=14, value=employee.job_qualification if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 15: 手机号码（从 Employee 获取）
        ws.cell(row=row_idx, column=15, value=employee.mobile if employee else "-").alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 16: 固定电话（从 Employee 获取）
        ws.cell(row=row_idx, column=16, value=employee.home_phone if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 17: 入职时间（从 Employee 获取）
        entry_time_str = employee.entry_time.strftime("%Y-%m-%d") if employee and employee.entry_time else "-"
        ws.cell(row=row_idx, column=17, value=entry_time_str).alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 18: 离职时间（从 Employee 获取）
        leave_time_str = employee.leave_time.strftime("%Y-%m-%d") if employee and employee.leave_time else "-"
        ws.cell(row=row_idx, column=18, value=leave_time_str).alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 19: 住址（从 Employee 获取）
        ws.cell(row=row_idx, column=19, value=employee.address if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 20: 应急联系人（从 Employee 获取）
        ws.cell(row=row_idx, column=20, value=employee.emergency_contact if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 21: 应急电话（从 Employee 获取）
        ws.cell(row=row_idx, column=21, value=employee.emergency_phone if employee else "-").alignment = Alignment(horizontal="center", vertical="center")
        
        # 列 22: 微信（从 Employee 获取）
        ws.cell(row=row_idx, column=22, value=employee.wechat if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 23: 邮箱（从 Employee 获取）
        ws.cell(row=row_idx, column=23, value=employee.email if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 24: 操作人（从 Personnel 获取）
        ws.cell(row=row_idx, column=24, value=personnel.operator or "-").alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 25: 创建时间（从 Personnel 获取）
        create_time_str = personnel.create_time.strftime("%Y-%m-%d %H:%M:%S") if personnel.create_time else "-"
        ws.cell(row=row_idx, column=25, value=create_time_str).alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 26: 更新时间（从 Personnel 获取）
        update_time_str = personnel.update_time.strftime("%Y-%m-%d %H:%M:%S") if personnel.update_time else "-"
        ws.cell(row=row_idx, column=26, value=update_time_str).alignment = Alignment(horizontal="left", vertical="center")
        
        # 列 27: 备注（从 Employee 获取）
        ws.cell(row=row_idx, column=27, value=employee.remark if employee else "-").alignment = Alignment(horizontal="left", vertical="center")
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = FileResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=人员信息表_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response


@user_passes_test(is_superuser)
def personnel_destination(request):
    """人员去向页面 - 展示所有人员的部门和项目分配情况"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    department_filter = request.GET.get('department', '')
    
    # 查询所有人员
    personnel_list = Personnel.objects.filter(is_deleted=False).order_by('department', 'personnel_code')
    
    # 筛选处理
    if search_key:
        personnel_list = personnel_list.filter(
            Q(name__icontains=search_key) |
            Q(personnel_code__icontains=search_key) |
            Q(department__icontains=search_key)
        )
    
    if department_filter:
        personnel_list = personnel_list.filter(department=department_filter)
    
    # 预加载所有项目信息
    project_info = {p.project_code: p for p in ProjectDetail.objects.all()}
    
    # 为每个人员加载项目分配信息
    for personnel in personnel_list:
        # 主要项目
        if personnel.project_code and personnel.project_code in project_info:
            personnel.project1_info = project_info[personnel.project_code]
        else:
            personnel.project1_info = None
        
        # 项目 2
        if personnel.project_code2 and personnel.project_code2 in project_info:
            personnel.project2_info = project_info[personnel.project_code2]
        else:
            personnel.project2_info = None
            
        # 项目 3
        if personnel.project_code3 and personnel.project_code3 in project_info:
            personnel.project3_info = project_info[personnel.project_code3]
        else:
            personnel.project3_info = None
            
        # 项目 4
        if personnel.project_code4 and personnel.project_code4 in project_info:
            personnel.project4_info = project_info[personnel.project_code4]
        else:
            personnel.project4_info = None
            
        # 项目 5
        if personnel.project_code5 and personnel.project_code5 in project_info:
            personnel.project5_info = project_info[personnel.project_code5]
        else:
            personnel.project5_info = None
    
    # 获取所有部门
    all_departments = Department.objects.filter(
        is_deleted=False,
        status='active'
    ).order_by('department_code')
    
    # 分页处理
    paginator = Paginator(personnel_list, 20)  # 每页显示 20 条
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        page_obj = paginator.page(1)
    
    context = {
        'page_obj': page_obj,
        'all_personnel': personnel_list,
        'all_departments': all_departments,
        'selected_department': department_filter,
        'search_keyword': search_key,
        'home_url': reverse('eims_app:eims_index'),
        'eims_index_url': reverse('eims_app:eims_index'),
    }
    return render(request, "personnel/destination.html", context)
