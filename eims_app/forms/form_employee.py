from django import forms
from eims_app.models import Employee

class EmployeeForm(forms.ModelForm):
    """员工基本信息表单（入职登记）"""
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'operator']
        widgets = {
            'employee_code': forms.TextInput(attrs={'class': 'form-control'}),
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
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

