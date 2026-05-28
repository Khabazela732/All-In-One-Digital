from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("HR", "HR Manager"),
        ("EMPLOYEE", "Employee"),
        ("APPLICANT", "Applicant"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="APPLICANT")

    def __str__(self):
        return self.user.username