from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.core.validators import ValidationError
from eims_app.models.model_user import UserProfile
from datetime import date

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['real_name', 'gender', 'birthday', 'phone', 'wechat']
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'}),
            'wechat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入微信号'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        real_name = cleaned_data.get('real_name')
        gender = cleaned_data.get('gender')
        birthday = cleaned_data.get('birthday')
        phone = cleaned_data.get('phone')
        
        errors = []
        if not real_name:
            errors.append('姓名不能为空')
        if not gender:
            errors.append('性别不能为空')
        if not birthday:
            errors.append('生日不能为空')
        if not phone:
            errors.append('手机号不能为空')
        
        if errors:
            raise ValidationError(errors)
        
        return cleaned_data

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料保存成功！')
            return redirect('eims_app:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile.html', {
        'form': form,
        'profile': profile
    })
