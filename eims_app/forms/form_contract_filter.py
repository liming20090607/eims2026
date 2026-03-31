# eims_app/forms/form_contract_filter.py
from django import forms
from .model_contract import Contract

class ContractFilterForm(forms.Form):
    STATUS_CHOICES = [('', '全部')] + Contract.STATUS_CHOICES
    CONTRACT_TYPE_CHOICES = [('', '全部')] + Contract.CONTRACT_TYPE_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contract_type = forms.ChoiceField(
        choices=CONTRACT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '合同编号/项目名称/甲方'
        })
    )