from django.contrib import admin
from .models import (
    Department,
    Staff,
    Vehicle,
    VehicleRequest,
    VehicleUsage,
    ScoringCategory,
    ScoringTask,
    StaffScoring,
    StaffTaskScore
)

# Register your models here.
admin.site.register(Department)
admin.site.register(Staff)
admin.site.register(Vehicle)
admin.site.register(VehicleUsage)
admin.site.register(StaffTaskScore)
admin.site.register(StaffScoring)
admin.site.register(ScoringTask)
admin.site.register(ScoringCategory)
admin.site.register(VehicleRequest)