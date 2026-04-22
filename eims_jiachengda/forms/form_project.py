from django import forms
from eims_app.models.model_project import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_code', 'project_name', 'project_category', 'project_address',
            'project_scale', 'project_investment', 'project_status', 'is_delayed',
            'notice_date', 'entry_time', 'actual_start_time', 'planned_completion_time',
            'project_manager', 'project_director', 'actual_manager', 'remark'
        ]
        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目编号'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目名称'}),
            'project_category': forms.Select(attrs={'class': 'form-select'}),
            'project_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目地址'}),
            'project_scale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目规模'}),
            'project_investment': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '项目投资(万元)', 'step': '0.01'}),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'is_delayed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'entry_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_start_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_completion_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'project_manager': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '现场负责人'}),
            'project_director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目总监'}),
            'actual_manager': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '实际负责人'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '备注'}),
        }