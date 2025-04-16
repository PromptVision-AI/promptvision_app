from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from rest_app.models import Account


class CustomUserCreationForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    # class Meta:
    #     model = Account
    #     fields = ('email', 'password1', 'password2')

class CustomAuthenticationForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class FileUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    # folder = forms.CharField(
    #     max_length=255, 
    #     required=False,
    #     widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Folder name (optional)'})
    # )