from django.db import models
from django.contrib.auth.models import AbstractUser, Group, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import Intern, User
from datetime import datetime
from django.core.exceptions import ValidationError
from hostCampany.models import Department
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.conf import settings
from hostCampany.models import HostComapany
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from math import ceil
from django.utils.timezone import now
import random
import string

class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()  # Changed from DateTimeField to TimeField
    end_time = models.TimeField()  # Changed from DateTimeField to TimeField
    company = models.ForeignKey(
        HostComapany,
        on_delete=models.CASCADE,
        related_name="company",
        null=True,
        blank=True,
    )

class InductionPost(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_applications",
        null=True,
        blank=True,
    )  # Buy default a user model is treated as admin
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(
        help_text="Explain what the application post is about."
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    passcode = models.CharField(
        max_length=50, default="123456", blank=True, null=True
    )
    closed = models.BooleanField(default=False, null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.closing_date and self.closing_date < now().date():
            self.closed = True  # Automatically close the post if the closing date has passed
        super().save(*args, **kwargs)  
                    

class InductionEnrollment(models.Model):
    intern_user = models.ForeignKey(
        Intern,
        on_delete=models.CASCADE,
        related_name="user_enrollments",
        blank=True,
        null=True,
    )
    induction_post = models.ForeignKey(
        InductionPost,
        on_delete=models.CASCADE,
        related_name="induction_post_enrollments",
        null=True,
        blank=True,
    )
    admitted = models.BooleanField(default=False)  # Accepted to attend induction
    acknowledged = models.BooleanField(
        default=False
    ) 
    day_1 = models.BooleanField(default=False)  # Day 1
    day_2 = models.BooleanField(default=False)  # Day 2
    pending_placement = models.BooleanField(
        default=False
    )  
    placed = models.BooleanField(default=False)  
    bypassed = models.BooleanField(default=False) 
    bypass_reason = models.TextField(
        help_text="Explain Explain why this induction was bypassed",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.intern_user} - {self.induction_post.title}"

def cv_directory_path(instance, filename):
    return "documents/cv/{0}/{1}".format(instance.national_id, filename)

def questionnaire_directory_path(instance, filename):
    return "documents/questionnaire/{0}/{1}".format(instance.national_id, filename)

def qualification_directory_path(instance, filename):
    return "documents/qualification/{0}/{1}".format(instance.national_id, filename)
from django.core.cache import cache

class HRGoal(models.Model):
    year = models.PositiveIntegerField()
    target_interns_placed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('year',)  # One goal per year

    def __str__(self):
        return f"HR Goal {self.year}: {self.target_interns_placed} interns"
    
class Application(models.Model):
    induction_post = models.ForeignKey(
        "InductionPost",
        on_delete=models.CASCADE,
        related_name="induction_post_applications",
        null=True,
        blank=True,
        default=None
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="user_applications",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    national_id = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255)
    age = models.IntegerField()
    resume_cv = models.FileField(blank=True, null=True, upload_to="cv/")
    qualification_document = models.FileField(blank=True, null=True, upload_to="qualification/")
    affidavit = models.FileField(blank=True, null=True, upload_to="questionnaire/")
    college_name = models.CharField(max_length=255, default="None")

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"

    gender = models.CharField(max_length=50, choices=Gender.choices, null=True, blank=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    qualification_description = models.TextField(null=True, blank=True)
    about_me = models.TextField(null=True, blank=True, default="No bio")
    residental_address = models.CharField(max_length=255, blank=True, null=True)
    post_address = models.CharField(max_length=255, blank=True, null=True)
    willing_to_work_paid_hours = models.BooleanField(default=False)
    willing_to_work_unpaid_hours = models.BooleanField(default=False)
    willing_to_work_hospitality_hours = models.BooleanField(default=False)
    is_your_location_far = models.BooleanField(default=False)

    class Status(models.TextChoices):
        ADMITTED = "ADMITTED", "Admitted"
        PENDING = "PENDING", "Pending"
        NOQUESTIONNAIRE = "NOQUESTIONNAIRE", "NoQuestionnaire"
        REJECTED = "REJECTED", "Rejected"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"

    status = models.CharField(
        default=Status.PENDING,
        max_length=50,
        choices=Status.choices,
        null=True,
        blank=True,
    )
    email_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ("induction_post", "national_id")

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Normalize email
        super().save(*args, **kwargs)

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))

    def send_otp_email(self):
        """Send OTP via email"""
        if not self.email_verified:
            otp = self.generate_otp()
            cache.set(f"otp_{self.email}", otp, timeout=600)  # Store OTP in cache for 10 min

            subject = "OTP for Email Verification"
            context = {"otp": otp, "fullname": f"{self.name} {self.surname}"}
            html_content = render_to_string("administration/email/email_verification.html", context)

            try:
                msg = EmailMultiAlternatives(subject, "", "no-reply@example.com", [self.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print(f"Error sending OTP Email: {e}")

    def verify_otp(self, entered_otp):
        """Check OTP validity"""
        cached_otp = cache.get(f"otp_{self.email}")
        if str(cached_otp) == str(entered_otp):
            self.email_verified = True
            cache.delete(f"otp_{self.email}")  # Remove OTP from cache
            self.save(update_fields=['email_verified'])
            return True
        return False

    def __str__(self):
        return f"{self.name} {self.surname}"



@receiver(post_save, sender=Application)
def create_intern_account_upon_admission(sender, instance, created, **kwargs):
    if instance.status == Application.Status.PENDING:
        # Send the welcome email to the user
        subject = "Application Received Successfully"
        context = {
            "fullname": f"{instance.name} {instance.surname}",
            "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
        }
        html_content = render_to_string(
            "administration/email/application_received.html", context
        )
        from_email = EMAIL_HOST_USER
        to_email = instance.email

        try:

            msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            pass

    if instance.status == Application.Status.NOQUESTIONNAIRE:
        # Send quetionnaire link to an applicant
        subject = "Aswer Questionnaire"
        context = {
            "fullname": f"{instance.name} {instance.surname}",
            "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
            "applicationID": instance.id,
        }
        html_content = render_to_string(
            "administration/email/complete_questionnaire.html", context
        )
        from_email = EMAIL_HOST_USER
        to_email = instance.email

        try:

            msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            pass

    if instance.status == Application.Status.ADMITTED:
        try:

            questionnaire = instance.questionnaire

            initials = instance.name[0].capitalize() + instance.surname[0].capitalize()
            username = instance.national_id
            password = instance.national_id + initials  # Constructed password format
            first_name = instance.name
            surname_name = instance.surname
            email = instance.email
            if not Intern.objects.filter(username=instance.national_id):
                new_intern_account = Intern.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=surname_name,
                    email=email,
                    role=Intern.Role.INTERN,
                )
                application_post = Application.objects.get(national_id=instance.national_id)
                application_post.applicant = new_intern_account
                application_post.save()
                InductionEnrollment.objects.create(
                    intern_user=new_intern_account,
                    admitted=True,
                    induction_post=application_post.induction_post,
                )
                # Send the welcome email to the user
                subject = "You Have been invited to Attend induction"
                context = {
                    "fullname": f"{instance.name} {instance.surname}",
                    "username": new_intern_account.username,
                    "password": password,
                    "questionnaireID": questionnaire.id,
                    "start_date": application_post.induction_post.start_date,
                    "end_date": application_post.induction_post.end_date,
                    "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
                }
                html_content = render_to_string(
                    "administration/email/welcome_email.html", context
                )
                from_email = EMAIL_HOST_USER
                to_email = email
                try:
                    msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as e:
                    print("Error sending Email: " + str(e))
        except Application.questionnaire.RelatedObjectDoesNotExist:  # Specific error for missing questionnaire
            application_post = Application.objects.get(national_id=instance.national_id)
            application_post.status = Application.Status.NOQUESTIONNAIRE  # Update status to NOQUESTIONNAIRE
            application_post.save()  # Save the change
            # Send email notification for questionnaire filling
            subject = "Aswer Questionnaire"
            context = {
                "fullname": f"{instance.name} {instance.surname}",
                "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
                "applicationID": instance.id,
            }
            html_content = render_to_string(
                "administration/email/complete_questionnaire.html", context
            )
            from_email = EMAIL_HOST_USER
            to_email = instance.email

            try:
                msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                pass
            print("No questionnaire found, status set to NOQUESTIONNAIRE.")
        except Exception as e:
            application_post = Application.objects.get(national_id=instance.national_id)
            application_post.status = Application.Status.PENDING
            print("Error sending Email: " + str(e))
            
def sick_note_directory_path(instance, filename):
    return "documents/sick_note/{0}/{1}".format(instance.intern.username, filename)
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('Study', 'Study'),
        ('Family', 'Family Responsibility'),
        
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    intern = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sick_note = models.FileField(upload_to=sick_note_directory_path, null=True, blank=True)

    def __str__(self):
        return f"{self.intern.username} - {self.leave_type} - {self.start_date} to {self.end_date}"

def affidavit_directory_path(instance, filename):
    return "documents/affidavit/{0}/{1}".format(instance.application.id, filename)

def first_assigment_directory_path(instance, filename):
    return "documents/assigment/{0}/{1}".format(instance.application.id, filename)

class Hearing(models.Model): 
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name="hearings")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=[("Scheduled", "Scheduled"), ("Completed", "Completed"), ("Cancelled", "Cancelled")],
        default="Scheduled"
    )

    def __str__(self):
        return f"{self.title} - {self.intern.username}"

    def send_email_notification(self):
        """Send email notification to the intern when a hearing is created."""
        subject = "You are Invited to a Hearing"
        context = {
            "fullname": self.intern.get_full_name(),
            "title": self.title,
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "description": self.description,
        }
        html_content = render_to_string("administration/email/hearing_invite.html", context)
        from_email = settings.EMAIL_HOST_USER
        to_email = self.intern.email

        try:
            # Ensure you're creating the EmailMultiAlternatives object correctly
            msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()  # Make sure .send() is being called on the EmailMultiAlternatives object
        except Exception as e:
            print(f"Error sending email: {e}")

    def save(self, *args, **kwargs):
        """Override save method to send email when a new hearing is created."""
        is_new = self._state.adding  # Check if the instance is being created (not updated)
        
        # Save the Hearing instance first
        super().save(*args, **kwargs)

        if is_new:
            # Send email notification only for new instances
            self.send_email_notification()
    
class Questionnaire(models.Model):
    application = models.OneToOneField(
        "Application",
        on_delete=models.CASCADE,
        related_name="questionnaire",
        null=True,
        blank=True,
    )
    answer = models.TextField(blank=True)
    internship_success_before = models.BooleanField(default=False)
    internship_before = models.BooleanField(default=False)
    pregnant = models.BooleanField(default=False)
    pregnancy_weeks = models.IntegerField(blank=True, null=True)
    pregnancy_months = models.IntegerField(blank=True, null=True)
    criminal_record = models.BooleanField(default=False)
    qualification_completed = models.BooleanField(default=False)
    qualification_completion_date = models.DateField(blank=True, null=True)
    stipend_eligibility = models.BooleanField(default=False)
    willing_to_relocate_nelspruit = models.BooleanField(default=False)
    willing_to_relocate_barberton = models.BooleanField(default=False)
    willing_to_work_shifts = models.BooleanField(default=False)
    acceptance_statement = models.BooleanField(default=False)
    signature = models.CharField(max_length=255, blank=True)
    signature_date = models.DateField(blank=True, null=True)
    signature_place = models.CharField(max_length=255, blank=True)
    witness_name = models.CharField(max_length=255, blank=True)
    witness_signature = models.CharField(max_length=255, blank=True)
    affidavit = models.FileField(blank=True, null=True, upload_to=affidavit_directory_path)
    first_assignment = models.FileField(blank=True, null=True, upload_to=first_assigment_directory_path)

@receiver(post_save, sender=Questionnaire)
def give_option_to_submit_affidavit(sender, instance, created, **kwargs):

    if instance.affidavit == None:
                # Send the welcome email to the user
        subject = "Affidavit Request"
        context = {
            "fullname": f"{instance.application.name} {instance.application.surname}",
            "questionnaire_id" : instance.id,
            "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
        }
        html_content = render_to_string(
            "administration/email/questionnaire_affidavit_req.html", context
        )
        from_email = EMAIL_HOST_USER
        to_email = instance.application.email

        try:
            msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            pass

def contract_doc_directory_path(instance, filename):
    return "documents/contract/{0}/{1}".format(instance.intern.id, filename)
def profile_pic_directory_path(instance, filename):
    return "pictures/profile/{0}/{1}".format(instance.intern.id, filename)
class IntershipEnrollment(models.Model):
    class InternshipStatus(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        PLACED = "PLACED", "Placed"
        TERMINATED = "TERMINATED", "Terminated"
        COMPLETED = "COMPLETED", "Completed"
        DEFAULTED = "DEFAULTED", "Defaulted"
        PENDING_LOGBOOK = "PENDING_LOGBOOK", "pending logbook"

    intern = models.OneToOneField(
        Intern,
        on_delete=models.CASCADE,
        related_name="intern_profile",
        null=True,
        blank=True,
    )
    status = models.CharField(
        default=InternshipStatus.WAITING,
        max_length=50,
        choices=InternshipStatus.choices,
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        HostComapany,  
        related_name="internCompany",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    shift = models.ForeignKey(
        Shift,  
        related_name="shift",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    contract = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    department = models.ForeignKey(
        Department,  
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    profile_picture = models.ImageField(
        upload_to=profile_pic_directory_path, null=True, blank=True
    )
    stipend = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, null=True, blank=True
    )
    contrac_doc = models.FileField(upload_to=contract_doc_directory_path, null=True, blank=True)

    def calculate_time_left_in_months(self):
        """
        Calculate the remaining time for the internship in months.
        Approximation: 1 month = 30 days.
        """
        today = now().date()

        # Ensure end_date is a datetime.date object
        if isinstance(self.end_date, str):
            try:
                self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            except ValueError:
                raise TypeError("end_date must be a valid date in YYYY-MM-DD format.")
        
        if self.end_date:
            days_left = (self.end_date - today).days
            if days_left > 0:
                return ceil(days_left / 30)  # Round up to the nearest whole month
        return 0  # If the internship has ended
    def save(self, *args, **kwargs):
        """
        Automatically update status to COMPLETED if time left is 0.
        """
        if self.pk:  # Ensure object exists in the database
            if self.calculate_time_left_in_months() == 0 and self.status == self.InternshipStatus.PLACED:
                self.status = self.InternshipStatus.COMPLETED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.intern} to {self.company}"

class Payment(models.Model):
    EXPENSE_TYPES = [
        ('FUEL', 'Fuel'),
        ('ELECTRICITY', 'Electricity'),
        ('WATER', 'Water'),
        ('RENT', 'Rent'),
        ('OTHER', 'Other'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES, default='OTHER')
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.expense_type} - R{self.amount} on {self.created.strftime('%Y-%m-%d')}"
       
class RecordAction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    placing = models.BooleanField(default=False)
    company = models.ForeignKey(
        HostComapany,
        related_name="hcompany",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reason = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    user = models.ForeignKey(
        User, related_name="RAuser", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self) -> str:
        return self.action
    
# EVENT MANAGEMENT
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

#  ./EVENT MANAGEMENT

# No Questionnaire is available
def no_questionnaire_status_msg(instance):
    subject = "Aswer Questionnaire"
    context = {
        "fullname": f"{instance.name} {instance.surname}",
        "company_logo_url": "https://internshipsuccess.co.za/static/administration/compiled/svg/logo.png",  # Replace with the URL of your company logo
        "applicationID": instance.id,
    }
    html_content = render_to_string(
        "administration/email/complete_questionnaire.html", context
    )
    from_email = EMAIL_HOST_USER
    to_email = instance.email

    try:

        msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        pass

class Qualification(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    duration_in_yrs = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    def __str__(self):
            return self.name

class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name
    
class WorkItem(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject',default=None,null=True,blank=True)
    name = models.CharField(max_length=255)
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, related_name='workitems', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name
    
class Deliverable(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='deliverables')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class LogbookTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey(HostComapany, on_delete=models.CASCADE, related_name='logbook_templates')
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, related_name='logbook_templates')

    def __str__(self):
        return self.name
    
class LogbookTemplateDeliverable(models.Model):
    logbook_template = models.ForeignKey(LogbookTemplate, on_delete=models.CASCADE, related_name='deliverables')
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='logbook_template_deliverables')

    def __str__(self):
        return f"{self.logbook_template} - {self.deliverable}"
    
class InternLogbook(models.Model):
    intern = models.OneToOneField(Intern, on_delete=models.CASCADE, related_name='logbooks')
    logbook_template = models.ForeignKey(LogbookTemplate, on_delete=models.CASCADE, related_name='logbooks')

    def __str__(self):   
        return f"{self.intern} - {self.logbook_template}"
    
class InternDeliverable(models.Model):
    intern_logbook = models.ForeignKey(InternLogbook, on_delete=models.CASCADE, related_name='deliverables')
    deliverable = models.ForeignKey(LogbookTemplateDeliverable, on_delete=models.CASCADE, related_name='intern_deliverables')
    completed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.intern_logbook} - {self.deliverable}"