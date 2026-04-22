from django import forms
from eims_app.models import Personnel, Department

class PersonnelForm(forms.ModelForm):
    """人员花名册表单（验证 + 样式）"""
    # 部门字段使用 ChoiceField，在 __init__ 中动态加载
    department = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # 手机号码字段设为非必填
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        # 从 kwargs 中提取 tenant（如果存在）
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        # 动态加载部门选项，按租户过滤
        dept_filter = {'is_deleted': False, 'status': 'active'}
        if tenant:
            dept_filter['tenant_id'] = tenant.id
        
        departments = Department.objects.filter(**dept_filter).order_by('department_code')
        dept_choices = [('', '请选择部门')]
        for dept in departments:
            dept_choices.append((dept.department_name, f'{dept.department_code} - {dept.department_name}'))
        self.fields['department'].choices = dept_choices
    
    class Meta:
        model = Personnel
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'operator', 'tenant']
        widgets = {
            'personnel_code': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'id_card': forms.TextInput(attrs={'class': 'form-control'}),
            'native_place': forms.TextInput(attrs={'class': 'form-control'}),
            'ethnic': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'home_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'wechat': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_position': forms.TextInput(attrs={'class': 'form-control'}),
            'tech_position': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_title': forms.TextInput(attrs={'class': 'form-control'}),
            'job_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'entry_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
