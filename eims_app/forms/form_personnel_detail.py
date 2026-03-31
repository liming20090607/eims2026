from django import forms
from eims_app.models import PersonnelCertificate, PersonnelAllocation

class PersonnelCertificateForm(forms.ModelForm):
    """人员证书表单（验证 + 样式）"""
    class Meta:
        model = PersonnelCertificate
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'operator']
        widgets = {
            'certificate_code': forms.TextInput(attrs={'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'personnel_code': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_name': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_type': forms.Select(attrs={'class': 'form-select'}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valid_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PersonnelAllocationForm(forms.ModelForm):
    """ 人员分配表单（验证 + 样式）"""
    class Meta:
        model = PersonnelAllocation
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted', 'operator']
        widgets = {
            'allocation_code': forms.TextInput(attrs={'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'personnel_code': forms.TextInput(attrs={'class': 'form-control'}),
            'from_project': forms.Select(attrs={'class': 'form-select'}),
            'from_project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'to_project': forms.Select(attrs={'class': 'form-select'}),
            'to_project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'allocation_position': forms.TextInput(attrs={'class': 'form-control'}),
            'allocation_department': forms.TextInput(attrs={'class': 'form-control'}),
            'allocation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expected_duration': forms.TextInput(attrs={'class': 'form-control'}),
            'allocation_status': forms.Select(attrs={'class': 'form-select'}),
            'allocation_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
