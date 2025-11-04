from django.contrib import admin
from administration.models import LogbookTemplate, LogbookTemplateDeliverable
from hostCampany.models import HostComapany, Department, Report, Rotation, InternInvoice, MonthlyCompanyInvoice

# Register your models here.
admin.site.register(HostComapany)
admin.site.register(Department)
admin.site.register(Report)
admin.site.register(LogbookTemplate)
admin.site.register(LogbookTemplateDeliverable)
admin.site.register(Rotation)
admin.site.register(InternInvoice)
admin.site.register(MonthlyCompanyInvoice)

