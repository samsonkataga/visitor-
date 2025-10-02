from django import forms
from .models import Visitor, Employee
from .models import Visitor, Employee, Staff, StaffCheckInOut

class VisitorCheckInForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'email', 'phone', 'company', 'host', 'purpose']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your company name'}),
            'host': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Purpose of visit', 'rows': 3}),
        }

class CheckOutForm(forms.Form):
    badge_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your badge ID'
        })
    )

class StaffRegistrationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'staff_id', 'email', 'department', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'staff_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter staff ID'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }

class StaffCheckInForm(forms.Form):
    staff_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your staff ID'
        })
    )

class StaffCheckOutForm(forms.Form):
    staff_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your staff ID'
        })
    )