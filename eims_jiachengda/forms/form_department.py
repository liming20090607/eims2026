from django import forms
from eims_app.models import Department, DepartmentRole, ApprovalChain
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    """部门信息表单"""
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 1. 过滤上级部门：只显示当前租户的部门
        dept_filter = {'is_deleted': False}
        if tenant:
            dept_filter['tenant_id'] = tenant.id
        # 排除自己（编辑时不能选自己作为上级）
        if self.instance and self.instance.pk:
            dept_filter['exclude_self'] = self.instance.pk
        
        parent_depts = Department.objects.filter(**dept_filter)
        if 'exclude_self' in dept_filter:
            parent_depts = parent_depts.exclude(id=dept_filter.pop('exclude_self'))
        self.fields['parent_department'].queryset = parent_depts.order_by('department_code')
        
        # 2. 过滤部门经理：只显示当前租户的活跃用户
        from eims_jiachengda.models import UserTenantRelation
        user_filter = {'is_active': True}
        if tenant:
            tenant_user_ids = UserTenantRelation.objects.filter(
                tenant_id=tenant.id
            ).values_list('user', flat=True).distinct()
            user_filter['id__in'] = tenant_user_ids
        self.fields['manager'].queryset = User.objects.filter(**user_filter).order_by('username')
    
    class Meta:
        model = Department
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'tenant']  # 排除 tenant，由视图自动管理
        widgets = {
            'department_code': forms.TextInput(attrs={'class': 'form-control'}),
            'department_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department_type': forms.Select(attrs={'class': 'form-select'}),
            'parent_department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'established_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DepartmentRoleForm(forms.ModelForm):
    """部门角色配置表单"""
    
    def __init__(self, *args, **kwargs):
        # 从 kwargs 中提取 tenant（如果存在）
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 1. 过滤部门：只显示当前租户的部门
        dept_filter = {'is_deleted': False}
        if tenant:
            dept_filter['tenant_id'] = tenant.id
        self.fields['department'].queryset = Department.objects.filter(**dept_filter).order_by('department_code')
        
        # 2. 获取所有已配置角色的用户 ID
        role_filter = {'is_deleted': False}
        if tenant:
            role_filter['department__tenant_id'] = tenant.id
        configured_user_ids = DepartmentRole.objects.filter(**role_filter).values_list('user', flat=True).distinct()
        
        # 如果是编辑模式（已有实例），需要排除其他用户，但保留当前用户
        if self.instance and self.instance.pk:
            # 编辑模式：排除其他已配置的用户，但保留当前记录的用户
            configured_user_ids = configured_user_ids.exclude(id=self.instance.user.id)
            # 用户字段设为隐藏字段（因为不允许修改）
            self.fields['user'].widget = forms.HiddenInput()
        
        # 3. 过滤用户：只显示当前租户的用户
        from eims_jiachengda.models import UserTenantRelation
        user_filter = {'is_active': True}
        if tenant:
            # 获取该租户下的所有用户 ID
            tenant_user_ids = UserTenantRelation.objects.filter(
                tenant_id=tenant.id
            ).values_list('user', flat=True).distinct()
            user_filter['id__in'] = tenant_user_ids
        
        self.fields['user'].queryset = User.objects.filter(**user_filter).exclude(
            id__in=configured_user_ids
        ).order_by('username')
        
        # 如果是编辑模式，需要确保当前用户在 queryset 中（否则验证会失败）
        if self.instance and self.instance.pk:
            # 将当前用户添加到 queryset（使用 | 联合查询）
            current_user = User.objects.filter(id=self.instance.user.id)
            self.fields['user'].queryset = self.fields['user'].queryset | current_user
        
        # 4. 为直属上级字段设置当前租户的活跃用户
        supervisor_filter = {'is_active': True}
        if tenant:
            tenant_user_ids = UserTenantRelation.objects.filter(
                tenant_id=tenant.id
            ).values_list('user', flat=True).distinct()
            supervisor_filter['id__in'] = tenant_user_ids
        
        self.fields['supervisor'].queryset = User.objects.filter(**supervisor_filter).order_by('username')
        self.fields['supervisor'].required = False
        
        # 5. 确保角色类型字段有正确的选项
        # 从模型中获取 ROLE_TYPE_CHOICES
        if hasattr(DepartmentRole, 'ROLE_TYPE_CHOICES'):
            self.fields['role_type'].choices = DepartmentRole.ROLE_TYPE_CHOICES
    
    class Meta:
        model = DepartmentRole
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'tenant']  # 排除 tenant，由视图自动管理
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select select2'}),
            'user': forms.Select(attrs={'class': 'form-select select2'}),
            'role_type': forms.Select(attrs={'class': 'form-select select2'}),
            'role_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permissions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supervisor': forms.Select(attrs={'class': 'form-select select2'}),
        }


class ApprovalChainForm(forms.ModelForm):
    """审批链配置表单"""
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 1. 过滤部门：只显示当前租户的部门
        dept_filter = {'is_deleted': False}
        if tenant:
            dept_filter['tenant_id'] = tenant.id
        
        self.fields['level_1_department'].queryset = Department.objects.filter(**dept_filter).order_by('department_code')
        self.fields['level_2_department'].queryset = Department.objects.filter(**dept_filter).order_by('department_code')
        self.fields['level_3_department'].queryset = Department.objects.filter(**dept_filter).order_by('department_code')
        
        # 2. 过滤角色：只显示当前租户的部门角色
        role_filter = {'is_deleted': False}
        if tenant:
            role_filter['department__tenant_id'] = tenant.id
        
        self.fields['level_1_role'].queryset = DepartmentRole.objects.filter(**role_filter).order_by('department', 'role_name')
        self.fields['level_2_role'].queryset = DepartmentRole.objects.filter(**role_filter).order_by('department', 'role_name')
        self.fields['level_3_role'].queryset = DepartmentRole.objects.filter(**role_filter).order_by('department', 'role_name')
        
        # 3. 过滤跨部门协同选项
        self.fields['cross_departments'].queryset = Department.objects.filter(**dept_filter).order_by('department_code')
    
    class Meta:
        model = ApprovalChain
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'tenant']  # 排除 tenant，由视图自动管理
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'chain_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'level_1_department': forms.Select(attrs={'class': 'form-select select2'}),
            'level_1_role': forms.Select(attrs={'class': 'form-select select2'}),
            'level_2_department': forms.Select(attrs={'class': 'form-select select2'}),
            'level_2_role': forms.Select(attrs={'class': 'form-select select2'}),
            'level_3_department': forms.Select(attrs={'class': 'form-select select2'}),
            'level_3_role': forms.Select(attrs={'class': 'form-select select2'}),
            'need_cross_department': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cross_departments': forms.SelectMultiple(attrs={'class': 'form-select select2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
