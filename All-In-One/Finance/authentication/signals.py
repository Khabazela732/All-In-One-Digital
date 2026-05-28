from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from recruitment.models import ApplicantProfile


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):

    if created:

        # MAIN USER PROFILE
        UserProfile.objects.create(
            user=instance,
            role="APPLICANT"
        )

        # APPLICANT PROFILE
        ApplicantProfile.objects.create(
            user=instance,
            first_name="",
            last_name="",
            address=""
        )