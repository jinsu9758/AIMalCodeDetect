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
    pass