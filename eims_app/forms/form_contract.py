# -*- coding: utf-8 -*-
from django import forms
from eims_app.models.model_contract import Contract  # 绝对导入

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_code': forms.TextInput(attrs={'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_party_a': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_party_b': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contract_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_agreement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project_scale': forms.TextInput(attrs={'class': 'form-control'}),
            'project_investment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'project_address': forms.TextInput(attrs={'class': 'form-control'}),
            'agreed_staffing': forms.TextInput(attrs={'class': 'form-control'}),
            'signing_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'service_period': forms.TextInput(attrs={'class': 'form-control'}),
            'service_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'extension_agreement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'planned_start_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_completion_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['project_code', 'contract_code', 'project_name', 'contract_party_a', 'contract_party_b']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f'"{self.fields[field].label}" 是必填项')
        return cleaned_data