from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User

class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("password1", "password2", "email", "nickname")

    def clean_username(self):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    
class ChangePassword(PasswordChangeForm):
    def clean_new_password1(self):
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        
        if old_password == new_password1:
            raise forms.ValidationError("새 비밀번호는 기존 비밀번호와 같을 수 없습니다.")
        
        return new_password1
    pass