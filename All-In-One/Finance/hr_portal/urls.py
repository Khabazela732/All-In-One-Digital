from django.urls import path
from . import views

app_name = "hr_portal"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.add_employee, name="add_employee"),
    path("departments/", views.departments, name="departments"),

    path("recruitment/", views.recruitment, name="recruitment"),
    path("applications/", views.applications, name="applications"),
    path("attendance/", views.attendance, name="attendance"),
    path("payroll/", views.payroll, name="payroll"),
    path("reports/", views.reports, name="reports"),
    path("settings/", views.settings_view, name="settings"),
]