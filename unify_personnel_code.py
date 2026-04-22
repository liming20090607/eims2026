"""
统一人员编号字段名：employee_code → personnel_code
同时将显示文本从"员工编号"改为"人员编号"
"""
import os
import re

def replace_in_file(file_path, replacements):
    """在文件中执行替换"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  ❌ 处理文件失败 {file_path}: {e}")
        return False

def main():
    print("=" * 80)
    print("统一人员编号字段和显示文本")
    print("=" * 80)
    
    # 定义所有需要替换的模式
    replacements = [
        # 模型定义
        ("employee_code = models.CharField(max_length=50, unique=True, verbose_name='员工编号'", 
         "personnel_code = models.CharField(max_length=50, unique=True, verbose_name='人员编号'"),
        ("employee_code = models.CharField(max_length=50, unique=True, verbose_name='员工编号', help_text='请输入唯一的员工编号')",
         "personnel_code = models.CharField(max_length=50, unique=True, verbose_name='人员编号', help_text='请输入唯一的人员编号')"),
        ("('employee_code', models.CharField(help_text='请输入唯一的员工编号', max_length=50, unique=True, verbose_name='员工编号'))",
         "('personnel_code', models.CharField(help_text='请输入唯一的人员编号', max_length=50, unique=True, verbose_name='人员编号'))"),
        
        # 表单定义
        ("employee_code = forms.CharField(", 
         "personnel_code = forms.CharField("),
        ("label='员工编号'", 
         "label='人员编号'"),
        
        # __str__ 方法
        ('return f"{self.employee_code} - {self.name}"',
         'return f"{self.personnel_code} - {self.name}"'),
        
        # 视图中的查询和排序
        (".order_by('employee_code')",
         ".order_by('personnel_code')"),
        (".order_by('employee_code'",
         ".order_by('personnel_code'"),
        ("Q(employee_code__icontains=search_key)",
         "Q(personnel_code__icontains=search_key)"),
        ("sort_field = request.GET.get('sort_field', 'employee_code')",
         "sort_field = request.GET.get('sort_field', 'personnel_code')"),
        ("all_employees = Employee.objects.filter(is_deleted=False, tenant_id=tenant_id).order_by('employee_code')",
         "all_employees = Employee.objects.filter(is_deleted=False, tenant_id=tenant_id).order_by('personnel_code')"),
        ("all_employees = Employee.objects.filter(is_deleted=False).order_by('employee_code')",
         "all_employees = Employee.objects.filter(is_deleted=False).order_by('personnel_code')"),
        ("employee_list = Employee.objects.filter(is_deleted=False, tenant_id=request.tenant.id).order_by('employee_code')",
         "employee_list = Employee.objects.filter(is_deleted=False, tenant_id=request.tenant.id).order_by('personnel_code')"),
        ("employee_list = Employee.objects.filter(is_deleted=False).order_by('employee_code')",
         "employee_list = Employee.objects.filter(is_deleted=False).order_by('personnel_code')"),
        ("queryset = Employee.objects.filter(is_deleted=False, tenant_id=request.tenant.id).order_by('employee_code')",
         "queryset = Employee.objects.filter(is_deleted=False, tenant_id=request.tenant.id).order_by('personnel_code')"),
        ("queryset = Employee.objects.filter(is_deleted=False).order_by('employee_code')",
         "queryset = Employee.objects.filter(is_deleted=False).order_by('personnel_code')"),
        
        # 属性访问
        ("self.employee_code = source.employee_code",
         "self.personnel_code = source.personnel_code"),
        ("self.personnel_code = source.employee_code  # 别名",
         "# personnel_code 字段已经统一"),
        ("self.employee_code = source.personnel_code  # 使用personnel_code",
         "# personnel_code 字段已经统一"),
        
        # 字典键
        ("'employee_code': '员工编号',",
         "'personnel_code': '人员编号',"),
        ("employee.employee_code",
         "employee.personnel_code"),
        
        # 模板中的显示
        ("员工编号",
         "人员编号"),
        ("输入员工编号",
         "输入人员编号"),
    ]
    
    # 需要处理的文件列表
    files_to_process = [
        # eims_app 模型和表单
        'eims_app/models/model_employee.py',
        'eims_app/forms/form_employee.py',
        'eims_app/views/views_employee.py',
        'eims_app/views/views_personnel.py',
        
        # eims_jiachengda 模型
        'eims_jiachengda/models/model_employee.py',
    ]
    
    modified_count = 0
    
    for file_path in files_to_process:
        full_path = os.path.join('e:\\EIMS2026', file_path)
        if os.path.exists(full_path):
            print(f"\n处理: {file_path}")
            if replace_in_file(full_path, replacements):
                print(f"  ✅ 已修改")
                modified_count += 1
            else:
                print(f"  ⏭️  无需修改")
        else:
            print(f"\n⚠️  文件不存在: {file_path}")
    
    # 处理模板文件
    template_files = [
        'eims_app/templates/employee/list.html',
        'eims_app/templates/employee/add.html',
        'eims_app/templates/employee/edit.html',
        'eims_app/templates/eims_app/user_management.html',
        'eims_jiachengda/templates/employee/list.html',
        'eims_jiachengda/templates/employee/add.html',
        'eims_jiachengda/templates/employee/edit.html',
        'eims_jiachengda/templates/eims_jiachengda/user_management.html',
    ]
    
    print("\n" + "=" * 80)
    print("处理模板文件...")
    print("=" * 80)
    
    template_replacements = [
        ('员工编号', '人员编号'),
        ('employee_code', 'personnel_code'),
        ('输入员工编号', '输入人员编号'),
        ('id_employee_code', 'id_personnel_code'),
        ('id="id_employee_code"', 'id="id_personnel_code"'),
        ('name="employee_code"', 'name="personnel_code"'),
        ('value="{{ form.employee_code.value }}"', 'value="{{ form.personnel_code.value }}"'),
        ('{{ form.employee_code }}', '{{ form.personnel_code }}'),
        ('form.employee_code.errors', 'form.personnel_code.errors'),
        ('form.employee_code', 'form.personnel_code'),
        ('data-field="employee_code"', 'data-field="personnel_code"'),
        ('data-column="0" data-type="text" data-field="employee_code"', 
         'data-column="0" data-type="text" data-field="personnel_code"'),
    ]
    
    for file_path in template_files:
        full_path = os.path.join('e:\\EIMS2026', file_path)
        if os.path.exists(full_path):
            print(f"\n处理: {file_path}")
            if replace_in_file(full_path, template_replacements):
                print(f"  ✅ 已修改")
                modified_count += 1
            else:
                print(f"  ⏭️  无需修改")
        else:
            print(f"\n⚠️  文件不存在: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"✅ 完成！共修改 {modified_count} 个文件")
    print("=" * 80)
    print("\n⚠️  下一步：")
    print("1. 创建数据库迁移文件: python manage.py makemigrations")
    print("2. 执行迁移: python manage.py migrate")
    print("3. 验证数据完整性")

if __name__ == '__main__':
    main()
