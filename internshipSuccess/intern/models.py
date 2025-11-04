from django.db import models
from authentication.models import User
from administration.models import InductionPost, IntershipEnrollment, Shift
from django.utils import timezone
from authentication.models import Intern
import os


# Create your models here.

class Attendance(models.Model):
    intern = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attendance_records"
    )
    induction_post = models.ForeignKey(
        InductionPost, on_delete=models.CASCADE, related_name="attendance_records"
    )
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
    approve = models.BooleanField(default=False)

class Skill(models.Model):
    intern = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="skills"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Experience(models.Model):
    intern = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="experiences"
    )
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Allow for ongoing jobs

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

from decimal import Decimal

def assignment_directory_path(instance, filename):
    # Upload path: documents/assignment/<username>/<filename>
    return f"documents/assignment/{instance.intern.username}/{filename}"

def assignment_two_directory_path(instance, filename):
    return f"documents/assignment/{instance.intern.username}/{filename}"

class Assignment(models.Model):
    intern = models.ForeignKey(User, on_delete=models.CASCADE)
    # Use string reference for InductionPost to avoid import issues
    induction_post = models.ForeignKey(
        'administration.InductionPost',  # replace 'administration' with actual app name if different
        on_delete=models.CASCADE,
        related_name="assignment_answers",
        null=True,
        blank=True,
        default=None
    )
    answer = models.FileField(blank=True, null=True, upload_to=assignment_directory_path)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.intern.username} - Assignment"

    # Optional: delete file when model instance is deleted
    def delete(self, *args, **kwargs):
        if self.answer:
            self.answer.delete(save=False)  # delete file via storage backend
        super().delete(*args, **kwargs)



class AssignmentTwo(models.Model):
    intern = models.ForeignKey(User, on_delete=models.CASCADE)
    induction_post = models.ForeignKey(
        'administration.InductionPost',  # replace 'administration' with actual app name if different
        on_delete=models.CASCADE,
        related_name="assignment_two_answers",
        null=True,
        blank=True,
        default=None
    )
    answer = models.FileField(blank=True, null=True, upload_to=assignment_two_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.intern.username} - Assignment Two"

    def delete(self, *args, **kwargs):
        if self.answer:
            self.answer.delete(save=False)
        super().delete(*args, **kwargs)

    
class WorkAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        LATE = "LATE", "Late"
        EARLY = "EARLY", "Early"
        ABSENT = "ABSENT", "Absent"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"
    
    class AttendanceType(models.TextChoices):
        WORK = "WORK", "Work"
        MEETING = "MEETING", "Meeting"

    intern = models.ForeignKey(IntershipEnrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.UNAVAILABLE
    )
    type = models.CharField(
        max_length=50, choices=AttendanceType.choices, default=Status.UNAVAILABLE
    )
    approved = models.BooleanField(default=False)
    sign_in_time = models.DateTimeField(null=True, blank=True)
    sign_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.intern.intern.username} - {self.date} - {self.status}"

    @property
    def duty_hours(self):
        if self.sign_in_time and self.sign_out_time:
            duration = self.sign_out_time - self.sign_in_time
            return duration.total_seconds() / 3600  # return hours
        return 0

    @property
    def stipend_earned(self):
        weekly_hours = Decimal("45")
        stipend_per_hour = self.intern.stipend / (Decimal("4") * weekly_hours)
        return Decimal(self.duty_hours) * stipend_per_hour

    class Meta:
        unique_together = ("intern", "date")


