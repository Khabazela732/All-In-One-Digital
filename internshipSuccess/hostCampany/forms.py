from django import forms

from administration.models import LogbookTemplate, InternDeliverable, WorkItem
from .models import HostComapany,  Report, Rotation, Department
from authentication.models import Intern

class HostComapanyForm(forms.ModelForm):
    class Meta:
        model = HostComapany
        fields = [
            "company_name",
            "description",
            "contant_number",
            "location",
        ]

    def __init__(self, *args, **kwargs):
        super(HostComapanyForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,  # Use the field's label as the placeholder
                }
            )

        # Set the widget for date fields to DateInput with type="date"

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
        labels = {
            "reason": "Reason for Reporting",
        }

class HostComapanyForm(forms.ModelForm):
    class Meta:
        model = HostComapany
        fields = [
            "company_name",
            "description",
            "location",
        ]

    def __init__(self, *args, **kwargs):
        super(HostComapanyForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,  # Use the field's label as the placeholder
                }
            )

class RotationForm(forms.ModelForm):
    class Meta:
        model = Rotation
        fields = ['intern', 'department', 'work_item', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['intern'].queryset = Intern.objects.all()
        self.fields['department'].queryset = Department.objects.all()
        self.fields['work_item'].queryset = WorkItem.objects.all()

class LogbookTemplateForm(forms.ModelForm):
    class Meta:
        model = LogbookTemplate
        fields = [
            "name",
            "description",
            "qualification"
        ]

    def __init__(self, *args, **kwargs):
        super(LogbookTemplateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,  # Use the field's label as the placeholder
                }
            )