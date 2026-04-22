"""
批量为造价咨询子模块表单添加人员字段的租户过滤
为所有人员选择字段添加租户过滤，只显示本公司员工
"""
import re
import os

def add_personnel_tenant_filter(file_path):
    """为表单添加人员字段的租户过滤"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义每个表单需要过滤的人员字段
    form_personnel_fields = {
        'CostTaskPlanUnifiedForm': [
            'plan_compiler_personnel',
            'plan_first_reviewer_personnel',
            'plan_second_reviewer_personnel',
            'plan_third_reviewer_personnel',
        ],
        'CostTaskImplementationForm': [
            'impl_compiler_personnel',
            'impl_first_reviewer_personnel',
            'impl_second_reviewer_personnel',
            'impl_third_reviewer_personnel',
        ],
        'CostReviewResultForm': [],  # 该表单没有人员选择字段
        'CostPaymentStatusForm': [],  # 该表单没有人员选择字段
        'CostProjectArchiveForm': [],  # 该表单没有人员选择字段
        'CostRemunerationDistributionForm': [],  # 该表单没有人员选择字段
    }
    
    modified = False
    
    for form_name, personnel_fields in form_personnel_fields.items():
        if not personnel_fields:
            continue
            
        # 查找该表单的 __init__ 方法
        pattern = rf'(class {form_name}\(forms\.ModelForm\):.*?)(def __init__\(self, \*args, \*\*kwargs\):.*?tenant = kwargs\.pop\(\'tenant\', None\).*?super\(\).__init__\(\*args, \*\*kwargs\))'
        
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print(f"⚠️  未找到 {form_name} 的 __init__ 方法")
            continue
        
        init_method = match.group(2)
        
        # 检查是否已经添加了人员过滤代码
        if 'personnel_fields' in init_method and 'Personnel.objects.filter(tenant=tenant)' in init_method:
            print(f"✓ {form_name} 已包含人员过滤代码，跳过")
            continue
        
        # 构建人员过滤代码
        filter_code = f'''
        
        # 为所有人员选择字段添加租户过滤，只显示本公司员工
        from ..models import Personnel
        if tenant:
            personnel_fields = {personnel_fields}
            for field_name in personnel_fields:
                if field_name in self.fields:
                    self.fields[field_name].queryset = Personnel.objects.filter(tenant=tenant)'''
        
        # 在 __init__ 方法的最后（编辑模式代码之后）插入过滤代码
        # 查找编辑模式代码块
        edit_mode_pattern = r"(# 编辑模式隐藏项目选择器并设置初始值\s+if self\.instance\.pk:.*?self\.fields\['selected_project'\]\.required = False)"
        edit_match = re.search(edit_mode_pattern, init_method, re.DOTALL)
        
        if edit_match:
            # 在编辑模式代码后插入
            insert_pos = edit_match.end()
            new_init = init_method[:insert_pos] + filter_code + init_method[insert_pos:]
        else:
            # 如果没有找到编辑模式代码，在 super().__init__ 后插入
            super_pattern = r"(super\(\).__init__\(\*args, \*\*kwargs\))"
            super_match = re.search(super_pattern, init_method)
            if super_match:
                insert_pos = super_match.end()
                new_init = init_method[:insert_pos] + filter_code + init_method[insert_pos:]
            else:
                print(f"⚠️  无法确定在 {form_name} 中插入代码的位置")
                continue
        
        # 替换原内容
        content = content.replace(init_method, new_init)
        modified = True
        print(f"✓ 已为 {form_name} 添加人员字段租户过滤")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """主函数"""
    file_path = r'e:\EIMS2026\eims_app\forms\form_cost_sub_modules.py'
    
    print("=" * 80)
    print("批量为造价咨询子模块表单添加人员字段的租户过滤")
    print("=" * 80)
    print()
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print(f"处理文件: {file_path}")
    print()
    
    success = add_personnel_tenant_filter(file_path)
    
    print()
    if success:
        print("=" * 80)
        print("✅ 修改完成！")
        print("=" * 80)
        print()
        print("已为以下表单的人员字段添加租户过滤：")
        print("  • CostTaskPlanUnifiedForm - 编制人员、一审人员、二审人员、三审人员")
        print("  • CostTaskImplementationForm - 实施编制人员、实施审核人员等")
        print()
        print("现在这些下拉框将只显示当前公司（租户）的员工。")
    else:
        print("=" * 80)
        print("⚠️  未进行任何修改")
        print("=" * 80)


if __name__ == '__main__':
    main()
