from django.db import models
from administration.models import  User
from authentication.models import HostEmployer, Intern

# Create your models here.
class HostComapany(models.Model):
    class CompanyType(models.TextChoices):
        PRIVATE = "PRIVATE", "Private"
        PRIVATE_WITH_IS = "PRIVATE_WITH_IS", "Private With Internship Success"
        GOVERNMENT = "GOVERNMENT", "Government"

    mentor = models.ForeignKey(
        HostEmployer, on_delete=models.CASCADE, related_name="mentor_comapanies"
    )
    company_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(help_text="Explain what the company do.")
    joined_date = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=10000, null=True, blank=True)
    passcode = models.CharField(max_length=50, default="internship#@", blank=True, null=True)
    contant_number = models.CharField(max_length=15, null=True, blank=True)
    
    company_type = models.CharField(
        max_length=50,
        choices=CompanyType.choices,
        default=CompanyType.PRIVATE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.company_name}"


    # def get_interns(self):
    #     return Intern.objects.filter(intern_profile__company=self.mentor)

class Department(models.Model):
    name = models.CharField(max_length=100)
    Company = models.ForeignKey(
        HostComapany, on_delete=models.CASCADE, related_name="company_departments"
    )

    def __str__(self):
        return f"{self.name} - {self.name}"

class InternInvoice(models.Model):
    enrollment = models.OneToOneField(
        "administration.IntershipEnrollment", on_delete=models.CASCADE
    )
    host_company = models.ForeignKey(
        HostComapany, on_delete=models.CASCADE, related_name="invoices"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The total amount to be charged monthly for the intern",
        default=3000.00  # Set default to 3000.00
    )
    expected_day_of_month = models.PositiveSmallIntegerField(
        choices=[(i, f"{i}th") for i in range(1, 32)],
        help_text="Select the day of the month when payment is expected (e.g., 1 = 1st of every month)",
        default=1  # Set default to 1st
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("SUSPENDED", "Suspended")
        ],
        default="PENDING"
    )
    created = models.DateField(auto_now_add=True)
    billing_month = models.DateField(
        help_text="First day of the month this invoice applies to",
        null=True,  # Allow null for existing records
        blank=True
    )

    def __str__(self):
        return f"{self.enrollment.intern} | {self.host_company.company_name} | R{self.amount} on {self.expected_day_of_month} | {self.status}"


class MonthlyCompanyInvoice(models.Model):
    company = models.ForeignKey(
        HostComapany, on_delete=models.CASCADE, related_name="monthly_invoices"
    )
    month = models.DateField(help_text="First day of the invoice month")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("PAID", "Paid"), ("SUSPENDED", "Suspended")],
        default="PENDING"
    )
    approval = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("APPROVED", "Approved")],
        default="PENDING"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "month")  # Prevent duplicate invoices

    def __str__(self):
        return f"{self.company.company_name} | {self.month.strftime('%B %Y')} | R{self.total_amount} | {self.status}" 
    
class Rotation(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name="rotations")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="rotations")
    work_item = models.ForeignKey(
        "administration.WorkItem",
        on_delete=models.CASCADE,
        related_name="rotations",
        null=True,
        blank=True
    )
    deliverables = models.ManyToManyField("administration.InternDeliverable", blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically assign all deliverables under the selected work item
        if self.work_item:
            logbook = self.intern.logbooks  # OneToOneField
            related_deliverables = logbook.deliverables.filter(
                deliverable__deliverable__work_item=self.work_item
            )
            self.deliverables.set(related_deliverables)

class Report(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    intern = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    host_employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="filed_reports")
    reason = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Report by {self.host_employer} on {self.intern} - {self.get_status_display()}"

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
