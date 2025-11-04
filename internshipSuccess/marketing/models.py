from django.db import models
from authentication.models import HostEmployerProfile, Intern, User

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

def campaign_directory_path(instance, filename):
    return "document/campaign/{0}/{1}".format(instance.name, filename)
class Campaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=campaign_directory_path, blank=True, null=True)

def successstory_directory_path(instance, filename):
    return "document/magazine/{0}/{1}".format(instance.title, filename)
class SuccessStory(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to=successstory_directory_path, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

def magazine_pdf_directory_path(instance, filename):
    return "document/magazine/{0}/{1}".format(instance.title, filename)

def magazine_cover_image_path(instance, filename):
    return f"magazines/covers/{filename}"

class Magazine(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    issue_date = models.DateField()
    pdf = models.FileField(blank=True, null=True, upload_to=magazine_pdf_directory_path)
    cover_image = models.ImageField(upload_to=magazine_cover_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    
class ConsentForm(models.Model):
    # Section: Contact Information
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    form_date = models.DateField()

    # Section: Consent Details
    purpose_training = models.BooleanField(default=False)
    purpose_marketing = models.BooleanField(default=False)
    purpose_awareness = models.BooleanField(default=False)
    purpose_commercial = models.BooleanField(default=False)

    content_photos = models.BooleanField(default=False)
    content_videos = models.BooleanField(default=False)
    content_audio = models.BooleanField(default=False)
    content_testimonials = models.BooleanField(default=False)
    content_story = models.BooleanField(default=False)

    # Section: Individual Details
    full_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=20)
    dob = models.DateField()
    age = models.PositiveIntegerField()
    company = models.CharField(max_length=255, blank=True, null=True)

    # Roles
    role_intern = models.BooleanField(default=False)
    role_employer = models.BooleanField(default=False)
    role_employee = models.BooleanField(default=False)
    role_public = models.BooleanField(default=False)
    role_ambassador = models.BooleanField(default=False)
    role_influencer = models.BooleanField(default=False)

    # Consent option
    consent = models.CharField(
        max_length=10,
        choices=[('yes', 'I consent'), ('no', 'I do NOT consent')]
    )

    # Signature data URL
    signature_data = models.TextField(help_text="Base64-encoded image of the signature")
    sign_date = models.DateField()

    # Guardian Section (if under 18)
    is_minor = models.BooleanField(default=False)
    minor_name = models.CharField(max_length=255, blank=True, null=True)
    minor_age = models.PositiveIntegerField(blank=True, null=True)
    guardian_name = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_consent = models.CharField(
        max_length=10,
        choices=[('yes', 'I consent'), ('no', 'I do NOT consent')],
        blank=True,
        null=True
    )
    guardian_signature_data = models.TextField(blank=True, null=True, help_text="Base64-encoded image of the guardian's signature")
    guardian_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Consent Form - {self.full_name}"
    
