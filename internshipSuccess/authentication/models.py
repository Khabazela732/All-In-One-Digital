from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER

# Create your models here.


# By default the user is admin
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        INTERN = "INTERN", "Intern" 
        COORDINATOR = "COORDINATOR", "Coordinator"
        HOST_EMPLOYER = "HOST_EMPLOYER", "Host Employer"
        MARKETING = "MARKETING", "Marketing"
        HR = "HR", "Human Resources"

    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# START OF INTERN
class InternManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.INTERN)

class Intern(User):
    base_role = User.Role.INTERN
    intern = InternManager()
    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Interns"

class InternProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    intern_id = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=Intern)
def create_intern_profile_and_enrollment(sender, instance, created, **kwargs):
    user = instance
    if created and instance.role == "INTERN":
        InternProfile.objects.create(user=user)

# END OF INTERN

# START OF HOST_EMPLOYER
class HostEmployerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.HOST_EMPLOYER)

class HostEmployer(User):
    base_role = User.Role.HOST_EMPLOYER
    host_employer = HostEmployerManager()
    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Host Employers"

class HostEmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    host_emp_id = models.IntegerField(null=True, blank=True)
@receiver(post_save, sender=HostEmployer)
def create_host_emp_profile_and_enrollment(sender, instance, created, **kwargs):
    user = instance
    if created and instance.role == User.Role.HOST_EMPLOYER:
        HostEmployerProfile.objects.create(user=user)
# END OF HOST_EMPLOYER
# START OF COORDINATOR
class CoordinatorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.COORDINATOR)

class Coordinator(User):
    base_role = User.Role.COORDINATOR
    coordinator = CoordinatorManager()
    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Host Employers"

class CoordinatorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coordinator_id = models.IntegerField(null=True, blank=True)
@receiver(post_save, sender=Coordinator)
def create_coordinator_profile_and_enrollment(sender, instance, created, **kwargs):
    user = instance
    if created and instance.role == User.Role.COORDINATOR:
        HostEmployerProfile.objects.create(user=user)
# END OF HOST_EMPLOYER

# ================= MARKETING ==================
class MarketingManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.MARKETING)

class Marketing(User):
    base_role = User.Role.MARKETING
    marketing = MarketingManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Marketing Team"

class MarketingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    marketing_id = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=Marketing)
def create_marketing_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.MARKETING:
        MarketingProfile.objects.create(user=instance)


# ================= HUMAN RESOURCES (HR) ==================
class HRManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.HR)

class HR(User):
    base_role = User.Role.HR
    hr = HRManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for HR Team"

class HRProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hr_id = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=HR)
def create_hr_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.HR:
        HRProfile.objects.create(user=instance)