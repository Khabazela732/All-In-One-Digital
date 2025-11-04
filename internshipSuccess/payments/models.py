
# Create your models here.
from django.db import models

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
