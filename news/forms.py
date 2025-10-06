from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, label="パスワード")
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=8, label="パスワード確認")
    
    class Meta:
        model = User
        fields = ['username', 'email']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に使用されています")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "パスワードが一致しません")
            
class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(label="ユーザー名またはメールアドレス", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")