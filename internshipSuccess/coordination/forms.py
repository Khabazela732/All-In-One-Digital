from django import forms
from .models import MonthlySiteVisit

class MonthlySiteVisitForm(forms.ModelForm):
    class Meta:
        model = MonthlySiteVisit
        fields = '__all__'
