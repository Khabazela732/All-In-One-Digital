from django import forms
from .models import WorkAttendance,Assignment, AssignmentTwo
from administration.models import Application, LeaveRequest
from coordination.models import CaseLog

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'sick_note']

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        sick_note = cleaned_data.get("sick_note")

        if leave_type == "sick" and not sick_note:
            raise forms.ValidationError("A sick note is required for Sick Leave.")

        return cleaned_data

    
class AttendanceForm(forms.Form):
    passcode = forms.CharField(max_length=50, widget=forms.PasswordInput)
    action = forms.ChoiceField(
        choices=[("sign_in", "Sign In"), ("sign_out", "Sign Out")]
    )

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )

class ApplicationInternForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['qualification', 'qualification_description', 'resume_cv', 'qualification_document']
        # widgets = {
        #     'start_date': forms.DateInput(attrs={'type': 'date'}),
        #     'end_date': forms.DateInput(attrs={'type': 'date'}),
        # }
    def __init__(self, *args, **kwargs):
        super(ApplicationInternForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )
# ----------------- Assignment Forms -----------------
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['answer']

    def save(self, commit=True):
        assignment = super().save(commit=False)
        
        # If updating existing assignment, delete old file
        if assignment.pk:  # existing record
            old_assignment = Assignment.objects.get(pk=assignment.pk)
            if old_assignment.answer and self.cleaned_data.get('answer') != old_assignment.answer:
                old_assignment.answer.delete(save=False)

        if commit:
            assignment.save()
        return assignment


class AssignmentTwoForm(forms.ModelForm):
    class Meta:
        model = AssignmentTwo
        fields = ['answer']

    def save(self, commit=True):
        assignment = super().save(commit=False)
        
        # If updating existing assignment, delete old file
        if assignment.pk:  # existing record
            old_assignment = AssignmentTwo.objects.get(pk=assignment.pk)
            if old_assignment.answer and self.cleaned_data.get('answer') != old_assignment.answer:
                old_assignment.answer.delete(save=False)

        if commit:
            assignment.save()
        return assignment

class CaseLogForm(forms.ModelForm):
    class Meta:
        model = CaseLog
        fields = ['issue_title', 'description']
