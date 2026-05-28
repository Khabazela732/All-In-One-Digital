from django import forms
from .models import ApplicantProfile, Application, Job


class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = [
            "first_name",
            "last_name",
            "cv",
            "cover_letter",
            "address",
            "experience",
        ]


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["job"]