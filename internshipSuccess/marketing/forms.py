from django import forms
from .models import ConsentForm, Magazine, SuccessStory, Campaign

class ConsentFormForm(forms.ModelForm):
    class Meta:
        model = ConsentForm
        fields = '__all__'
        widgets = {
            # Contact Info
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'form_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            # Consent Purposes
            'purpose_training': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'purpose_marketing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'purpose_awareness': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'purpose_commercial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'content_photos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'content_videos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'content_audio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'content_testimonials': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'content_story': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Individual
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),

            'role_intern': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role_employer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role_employee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role_ambassador': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role_influencer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Consent
            'consent': forms.RadioSelect(choices=[('yes', 'I consent'), ('no', 'I do NOT consent')]),
            'signature_data': forms.HiddenInput(),  # Signature in base64
            'sign_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            # Guardian Section
            'is_minor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'minor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'minor_age': forms.NumberInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_consent': forms.RadioSelect(choices=[('yes', 'I consent'), ('no', 'I do NOT consent')]),
            'guardian_signature_data': forms.HiddenInput(),
            'guardian_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_signature_data(self):
        signature = self.cleaned_data.get('signature_data')
        if not signature:
            raise forms.ValidationError("Please provide your signature.")
        return signature

    def clean(self):
        cleaned_data = super().clean()
        is_minor = cleaned_data.get("is_minor")

        if is_minor:
            required_fields = ['minor_name', 'minor_age', 'guardian_name', 'relationship', 'guardian_phone', 'guardian_consent', 'guardian_signature_data', 'guardian_date']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for minors.")

class MagazineForm(forms.ModelForm):
    class Meta:
        model = Magazine
        fields = ['title', 'description', 'issue_date','cover_image', 'pdf']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }
class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'start_date', 'end_date', 'image']

class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ['title', 'content', 'image']