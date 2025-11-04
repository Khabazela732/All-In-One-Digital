from django.contrib import admin
from .models import (
    Application,
    Deliverable,
    InductionPost,
    InternDeliverable,
    InternLogbook,
    Qualification,
    Questionnaire,
    IntershipEnrollment,
    RecordAction,
    Shift,
    Event,
    Hearing,
    WorkItem,
    Subject

    
)

admin.site.site_url = "/admin/"
# Register your models here.
admin.site.register(Application)
admin.site.register(Hearing)
admin.site.register(InductionPost)
admin.site.register(Questionnaire)
admin.site.register(IntershipEnrollment)
admin.site.register(RecordAction)
admin.site.register(Shift)
admin.site.register(Event)
admin.site.register(Qualification)
admin.site.register(WorkItem)
admin.site.register(Deliverable)
admin.site.register(InternLogbook)
admin.site.register(InternDeliverable)
admin.site.register(Subject)

