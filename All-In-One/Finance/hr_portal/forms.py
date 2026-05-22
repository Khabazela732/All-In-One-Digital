from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "department",
            "position",
            "hire_date",
        ]

        widgets = {
            "employee_id": forms.TextInput(attrs={
                "placeholder": "EMP-001",
                "class": "form-control"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First Name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last Name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "email@company.com"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            }),
            "gender": forms.Select(attrs={
                "class": "form-control"
            }),
            "department": forms.Select(attrs={
                "class": "form-control"
            }),
            "position": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Job Title"
            }),
            "hire_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
        }