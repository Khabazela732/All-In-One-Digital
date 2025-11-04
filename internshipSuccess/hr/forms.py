from django import forms
from authentication.models import User
from .models import Staff, Vehicle, VehicleRequest, VehicleUsage, ScoringCategory, ScoringTask

class SystemUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password','role']

    def __init__(self, *args, **kwargs):
        super(SystemUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'phone', 'department', 'status','role', 'rsa_id_number', 'id_document', 'drivers_license', 'contract_agreement', 'photo']

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['brand', 'model', 'registration_number', 'fuel_type', 'status', 'image']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Corolla'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ABC 123 MP'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class VehicleRequestForm(forms.ModelForm):
    class Meta:
        model = VehicleRequest
        fields = ['destination', 'company_name', 'reason']

class VehicleUsageForm(forms.ModelForm):
    class Meta:
        model = VehicleUsage
        fields = ['open_odometer', 'open_odometer_proof', 'close_odometer', 'close_odometer_proof']

class ScoringCategoryForm(forms.ModelForm):
    class Meta:
        model = ScoringCategory
        fields = ['name']

class ScoringTaskForm(forms.ModelForm):
    class Meta:
        model = ScoringTask
        fields = ['description']