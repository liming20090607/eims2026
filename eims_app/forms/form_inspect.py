from django import forms
from eims_app.models import Inspection

class InspectForm(forms.ModelForm):
    """巡视检查表单（验证+样式）"""
    class Meta:
        model = Inspection
        fields = '__all__'
        exclude = ['create_time', 'update_time', 'is_deleted']
        widgets = {
            'inspect_code': forms.TextInput(attrs={'class': 'form-control'}),
            'inspect_name': forms.TextInput(attrs={'class': 'form-control'}),
            'inspect_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '请选择'), ('日常检查', '日常检查'), ('专项检查', '专项检查'), ('季度检查', '季度检查'), ('年度检查', '年度检查')
            ]),
            'inspect_scope': forms.TextInput(attrs={'class': 'form-control'}),
            'inspect_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'inspect_team': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'leader': forms.TextInput(attrs={'class': 'form-control'}),
            'inspected_department': forms.TextInput(attrs={'class': 'form-control'}),
            'problem_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'major_problem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'general_problem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rectification_suggestion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rectification_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'rectification_status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '请选择'), ('未整改', '未整改'), ('整改中', '整改中'), ('已完成', '已完成')
            ]),
            'verify_person': forms.TextInput(attrs={'class': 'form-control'}),
            'verify_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        } 
