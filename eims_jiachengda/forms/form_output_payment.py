# E:\EIMS2026\eims_app\forms\form_output_payment.py
# 产值回款表单

from django import forms
from ..models.model_output_payment import OutputPayment


class OutputForm(forms.ModelForm):
    """产值回款表单"""
    
    class Meta:
        model = OutputPayment
        fields = '__all__'
        exclude = ['operator', 'project_code', 'output_amount', 'payment_amount']
        widgets = {
            'month': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '格式：2026-01'
            }),
            'monthly_output': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'cumulative_output': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'contract_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'cumulative_received': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'contract_receivable': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'near_term_receivable': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'actual_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'next_month_plan': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'payment_basis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'last_payment_situation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recent_payment_request': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_month_request': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_measures': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'need_assistance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
