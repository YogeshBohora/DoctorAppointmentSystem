from django import forms
from django.contrib.auth.models import User

from .models import Doctor, Patient

class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
