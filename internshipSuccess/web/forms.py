from django import forms
from .models import NewsLetters
from django.core.exceptions import ValidationError

class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetters
        fields = [
            "title",
            "description",
            "image",
        ]

    class ApplicationForm(forms.Form):
        national_id = forms.CharField(
        max_length=13,
        min_length=13,
        required=True,
        widget=forms.TextInput(attrs={
            'maxlength': '13',
            'minlength': '13',
            'pattern': '[0-9]{13}',
            'title': 'National ID must be 13 digits long and contain only numbers',
            'placeholder': 'Enter 13-digit ID',
        })
    )

    def __init__(self, *args, **kwargs):
        super(NewsLetterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,  # Use the field's label as the placeholder
                }
            )
        
         
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id.isdigit():
            raise ValidationError("National ID must contain only numbers.")
        if len(national_id) != 13:
            raise ValidationError("National ID must be exactly 13 digits long.")
        return national_id