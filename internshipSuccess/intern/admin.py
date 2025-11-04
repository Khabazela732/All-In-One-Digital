from django.contrib import admin
from administration.models import InductionEnrollment
from .models import (
    Attendance,
    WorkAttendance,
    Experience,
    Skill,
    Assignment,
    AssignmentTwo
)

# Register your models here.
admin.site.register(Attendance)
admin.site.register(AssignmentTwo)
admin.site.register(InductionEnrollment)
admin.site.register(WorkAttendance)
admin.site.register(Skill)
admin.site.register(Experience)
admin.site.register(Assignment)
