from django import forms
from .models import Application, Deliverable, InductionPost, Qualification, Questionnaire, WorkItem, Subject
from django.contrib.auth.forms import UserCreationForm
from authentication.models import HostEmployer, Intern
from django.forms import inlineformset_factory
from hostCampany.models import HostComapany
from django import forms
from .models import InductionPost, HRGoal
from django.core.exceptions import ValidationError

class BulkAssignWorkItemsForm(forms.Form):
    work_items = forms.ModelMultipleChoiceField(
        queryset=WorkItem.objects.filter(subject__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label="Select Work Items"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label="Select Subject"
    )
class UploadFileForm(forms.Form):
    file = forms.FileField()
class HostEmployerForm(UserCreationForm):
    register_company = forms.BooleanField(
        required=False, label="Register company after creating host employer"
    )

    class Meta:
        model = HostEmployer
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super(HostEmployerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )
        self.fields["register_company"].widget.attrs.update(
            {
                "class": "form-check-input",  # Checkbox class
            }
        )


class HostEmployerFormForProfile(forms.ModelForm):
    class Meta:
        model = HostEmployer
        fields = ["username", "first_name", "last_name", "email"]
        # Customize the fields according to your needs

    def __init__(self, *args, **kwargs):
        super(HostEmployerFormForProfile, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )



class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            "answer",
            "internship_success_before",
            "internship_before",
            "pregnant",
            "pregnancy_weeks",
            "pregnancy_months",
            "criminal_record",
            "qualification_completed",
            "qualification_completion_date",
            "willing_to_relocate_nelspruit",
            "willing_to_relocate_barberton",  # Corrected field name
            "willing_to_work_shifts",
            "acceptance_statement",
            "signature_date",
            "signature_place",
            "witness_name",
            "witness_signature",
            "signature",
        ]

    def __init__(self, *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )


class QuestionnaireAffidavitForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            "affidavit",
            "first_assignment",
        ]

    def __init__(self, *args, **kwargs):
        super(QuestionnaireAffidavitForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "name",
            "surname",
            "national_id",
            "email",
            "phone_number",
            "age",
            "gender",
            "qualification",
            "qualification_description",
            "residental_address",
            "willing_to_work_paid_hours",
            "willing_to_work_unpaid_hours",
            "willing_to_work_hospitality_hours",
            "is_your_location_far",
            "post_address",
            "resume_cv",
            "qualification_document",
        ]

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            new_data = {"class": "form-control"}
            self.fields[str(field)].widget.attrs.update(new_data)

class InductionPostForm(forms.ModelForm):
    class Meta:
        model = InductionPost
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "requirements",
            "closing_date"
        ]

    def __init__(self, *args, **kwargs):
        super(InductionPostForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,  # Use the field's label as the placeholder
                }
            )

        # Set the widget for date fields to DateInput with type="date"
        self.fields["start_date"].widget = forms.DateInput(attrs={"type": "date"})
        self.fields["end_date"].widget = forms.DateInput(attrs={"type": "date"})
        self.fields["closing_date"].widget = forms.DateInput(attrs={"type": "date"})

class UpdatePasscodeForm(forms.ModelForm):
    class Meta:
        model = InductionPost
        fields = ["passcode"]

    def __init__(self, *args, **kwargs):
        super(UpdatePasscodeForm, self).__init__(*args, **kwargs)
        # Update the widget attributes for the passcode field
        self.fields["passcode"].widget.attrs.update(
            {
                "class": "form-control",  # Bootstrap class for form control
                "placeholder": self.fields[
                    "passcode"
                ].label,  # Use the field's label as the placeholder
                "type": "password",  # Set the input type to password
                "pattern": r"^\d{6}$",  # Only allow digits and exactly 6 characters
                "title": "Passcode must be exactly 6 digits",  # Tooltip for the pattern
            }
        )

    def clean_passcode(self):
        # Get the value of the passcode field
        passcode = self.cleaned_data.get("passcode")
        # Check if the passcode is exactly 6 digits
        if not passcode.isdigit() or len(passcode) != 6:
            raise ValidationError("Passcode must be exactly 6 digits")
        # Always return the cleaned data
        return passcode

class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = [
            "code",
            "name",
            "duration_in_yrs",
            "description"
        ]

    def __init__(self, *args, **kwargs):
        super(QualificationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        
class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            "name",
            "subject",
            "description"
        ]
    def __init__(self, *args, **kwargs):
        super(WorkItemForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )
class DeliverableForm(forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = [
            "name",
            "description"
        ]
    def __init__(self, *args, **kwargs):
        super(DeliverableForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                }
            )

class HRGoalForm(forms.ModelForm):
    class Meta:
        model = HRGoal
        fields = ['target_interns_placed']
        widgets = {
            'target_interns_placed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
        }   
