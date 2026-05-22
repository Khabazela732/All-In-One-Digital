# forms.py
from django import forms
from .models import Employee, Department


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
            "hire_date": forms.DateInput(attrs={"type": "date"}),
        }