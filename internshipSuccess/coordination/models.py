from django.db import models
from hr.models import Staff

class MonthlySiteVisit(models.Model):
    company = models.ForeignKey("hostCampany.HostComapany", on_delete=models.CASCADE)
    date = models.DateField()
    is_official = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name="site_visits")
    mentor_name = models.CharField(max_length=255)
    mentor_email = models.EmailField()
    supervisor_name = models.CharField(max_length=255)
    supervisor_email = models.EmailField()

    number_of_interns = models.IntegerField(default=0)
    attendance_leave_recorded = models.TextField(blank=True, null=True)
    invoice_update = models.TextField(blank=True, null=True)
    accounting_officer = models.TextField(blank=True, null=True)
    site_visits_conducted = models.IntegerField(default=0)
    cases_reported = models.TextField(blank=True, null=True)

    comments_mentor = models.TextField(blank=True, null=True)
    comments_supervisor = models.TextField(blank=True, null=True)
    comments_intern = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Site Visit - {self.company.company_name} on {self.date}"
    
class CaseLog(models.Model):
    intern = models.ForeignKey("administration.IntershipEnrollment", on_delete=models.CASCADE, related_name="cases")
    company = models.ForeignKey("hostCampany.HostComapany", on_delete=models.CASCADE, related_name="cases")
    issue_title = models.CharField(max_length=255)
    description = models.TextField()
    date_reported = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[("Open", "Open"), ("In Progress", "In Progress"), ("Resolved", "Resolved")], default="Open")
    response = models.TextField(blank=True, null=True)  # Coordination team feedback

    def __str__(self):
        return f"Case by {self.intern.intern.get_full_name()} - {self.issue_title}"
