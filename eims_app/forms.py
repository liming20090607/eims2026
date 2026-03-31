# eims_app/forms.py
from django import forms
from .models import Contract  # 导入你的 Contract 模型

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'  # 包含所有字段
        # 或者指定字段（推荐，更安全）：
        # fields = ['title', 'status', 'contract_type', 'amount', 'start_date', ...]