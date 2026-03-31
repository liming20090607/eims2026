from django import forms
from eims_app.models import Department, DepartmentRole, ApprovalChain
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    """部门信息表单"""
    
    class Meta:
        model = Department
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted']
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
        super().__init__(*args, **kwargs)
        
        # 获取所有已配置角色的用户 ID
        configured_user_ids = DepartmentRole.objects.filter(
            is_deleted=False
        ).values_list('user', flat=True).distinct()
        
        # 如果是编辑模式（已有实例），需要排除其他用户，但保留当前用户
        if self.instance and self.instance.pk:
            # 编辑模式：排除其他已配置的用户，但保留当前记录的用户
            configured_user_ids = configured_user_ids.exclude(id=self.instance.user.id)
            # 用户字段设为隐藏字段（因为不允许修改）
            self.fields['user'].widget = forms.HiddenInput()
        
        # 过滤出未配置角色的用户，按用户名升序排列
        # 注意：Django 的 User 模型没有 is_deleted 字段，只过滤 is_active
        self.fields['user'].queryset = User.objects.filter(
            is_active=True
        ).exclude(
            id__in=configured_user_ids
        ).order_by('username')
        
        # 如果是编辑模式，需要确保当前用户在 queryset 中（否则验证会失败）
        if self.instance and self.instance.pk:
            # 将当前用户添加到 queryset（使用 | 联合查询）
            current_user = User.objects.filter(id=self.instance.user.id)
            self.fields['user'].queryset = self.fields['user'].queryset | current_user
        
        # 为直属上级字段设置所有活跃用户（按用户名升序）
        self.fields['supervisor'].queryset = User.objects.filter(
            is_active=True
        ).order_by('username')
        self.fields['supervisor'].required = False
    
    class Meta:
        model = DepartmentRole
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted']
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
    
    class Meta:
        model = ApprovalChain
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'chain_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'level_1_department': forms.Select(attrs={'class': 'form-select'}),
            'level_1_role': forms.TextInput(attrs={'class': 'form-control'}),
            'level_2_department': forms.Select(attrs={'class': 'form-select'}),
            'level_2_role': forms.TextInput(attrs={'class': 'form-control'}),
            'level_3_department': forms.Select(attrs={'class': 'form-select'}),
            'level_3_role': forms.TextInput(attrs={'class': 'form-control'}),
            'need_cross_department': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
