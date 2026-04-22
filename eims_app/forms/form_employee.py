from django import forms
from eims_app.models import Employee

class EmployeeForm(forms.ModelForm):
    """员工基本信息表单（入职登记）"""
    
    # 明确设置必填字段
    personnel_code = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='人员编号'
    )
    name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='姓名'
    )
    gender = forms.ChoiceField(
        required=True,
        choices=Employee.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='性别'
    )
    
    # 其他字段设为非必填
    id_card = forms.CharField(
        required=False,
        max_length=18,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='身份证号'
    )
    mobile = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='手机号'
    )
    
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'operator', 'tenant']
        widgets = {
            'native_place': forms.TextInput(attrs={'class': 'form-control'}),
            'ethnic': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'home_phone': forms.TextInput(attrs={'class': 'form-control'}),
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
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

