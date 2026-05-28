from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class ApplicantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    cv = models.FileField(upload_to="cvs/")
    cover_letter = models.TextField(blank=True)

    address = models.TextField()
    experience = models.TextField(blank=True)

    is_complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

from django.contrib.auth.models import User

class Job(models.Model):

    title = models.CharField(max_length=255)

    description = models.TextField()

    requirements = models.TextField()

    department = models.CharField(max_length=100)

    location = models.CharField(max_length=100)

    salary = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

class Application(models.Model):

    STATUS_CHOICES = [
        ("SUBMITTED", "Submitted"),
        ("REVIEW", "Under Review"),
        ("SHORTLISTED", "Shortlisted"),
        ("INTERVIEW", "Interview"),
        ("OFFERED", "Offered"),
        ("HIRED", "Hired"),
        ("REJECTED", "Rejected"),
    ]

    applicant = models.ForeignKey(ApplicantProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SUBMITTED")

    hr_notes = models.TextField(blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)