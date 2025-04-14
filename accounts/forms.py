from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already in use.')
        return email

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Only validate email if changed
        if email != self.instance.email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('Email already in use.')
        return email
