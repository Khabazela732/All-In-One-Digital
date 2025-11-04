# models.py

from django.db import models
from authentication.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

def id_doc_directory_path(instance, filename):
    return "documents/staff/id/{0}/{1}".format(instance.user.id, filename)

def drivers_license_directory_path(instance, filename):
    return "documents/staff/license/{0}/{1}".format(instance.user.id, filename)

def contract_doc_directory_path(instance, filename):
    return "documents/staff/contract/{0}/{1}".format(instance.user.id, filename)
  
from django.core.validators import RegexValidator

rsa_id_validator = RegexValidator(
    regex=r'^\d{13}$',
    message="Enter a valid 13-digit RSA ID number."
)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="staff_members")
    #role = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    # RSA ID and documents
    rsa_id_number = models.CharField(max_length=13, validators=[rsa_id_validator], unique=True)
    id_document = models.FileField(upload_to=id_doc_directory_path, null=True, blank=True)
    drivers_license = models.FileField(upload_to=drivers_license_directory_path, null=True, blank=True)
    contract_agreement = models.FileField(upload_to=contract_doc_directory_path, null=True, blank=True)

    def __str__(self):
        return self.full_name
    
def vehicle_proof_upload_path(instance, filename):
    return f"vehicles/{instance.request}/proofs/{filename}"

class Vehicle(models.Model):
    STATUS_CHOICES = [
        ("FREE", "Free for Use"),
        ("BUSY", "In Use"),
        ("DAMAGED", "Damaged"),
        ("MAINTENANCE", "In Maintenance"),
    ]

    FUEL_TYPES = [
        ("PETROL", "Petrol"),
        ("DIESEL", "Diesel"),
        ("ELECTRIC", "Electric"),
    ]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="FREE")
    image = models.ImageField(upload_to=vehicle_proof_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"

class VehicleRequest(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    destination = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approver")
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.staff} requested {self.vehicle} - {'Approved' if self.is_approved else 'Pending'}"

class VehicleUsage(models.Model):
    request = models.OneToOneField(VehicleRequest, on_delete=models.CASCADE)
    open_odometer = models.PositiveIntegerField()
    open_odometer_proof = models.ImageField(upload_to=vehicle_proof_upload_path)

    close_odometer = models.PositiveIntegerField(null=True, blank=True)
    close_odometer_proof = models.ImageField(upload_to=vehicle_proof_upload_path, null=True, blank=True)

    def distance_driven(self):
        if self.close_odometer and self.open_odometer:
            return self.close_odometer - self.open_odometer
        return None

    def __str__(self):
        return f"{self.request.vehicle.registration_number} - {self.request.staff.user.get_full_name()}"

class ScoringCategory(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ScoringTask(models.Model):
    category = models.ForeignKey(ScoringCategory, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.name} - {self.description}"

class StaffScoring(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='scoring_sessions')
    assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    appraisal_date = models.DateField(auto_now_add=True)
    total_points = models.PositiveIntegerField(default=0)
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    performance_category = models.CharField(max_length=50, choices=[
        ('A', 'Superior'),
        ('B', 'Excellent'),
        ('C', 'Average'),
        ('D', 'Below Average'),
        ('F', 'Poor'),
    ], blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

class StaffTaskScore(models.Model):
    scoring_session = models.ForeignKey(StaffScoring, on_delete=models.CASCADE, related_name='task_scores')
    task = models.ForeignKey(ScoringTask, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=[
        (4, 'Fully Achieved'),
        (3, 'To a Greater Degree'),
        (2, 'To an Accepted Degree'),
        (1, 'To a Lesser Degree'),
        (0, 'Not at All'),
    ])

    def __str__(self):
        return f"{self.scoring_session.staff.user.get_full_name()} - {self.task.description}"
