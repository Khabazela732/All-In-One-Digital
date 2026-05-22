from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from authentication.utils import is_hr, is_admin
from hr_portal.models import Employee, Department
from .forms import EmployeeForm
from authentication.decorators import hr_required

def dashboard(request):

    context = {
        "total_employees": Employee.objects.count(),
        "total_departments": Department.objects.count(),
        "recent_employees": Employee.objects.order_by("-hire_date")[:6],
    }

    return render(request, "hr_portal/dashboard.html", context)

# employee list view
@login_required
@hr_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "hr_portal/employees.html", {"employees": employees})

# add employee view
@login_required
@hr_required
def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("hr_employees")
    else:
        form = EmployeeForm()

    return render(request, "hr_portal/add_employee.html", {
        "form": form
    })

# department list view
@login_required
@hr_required
def departments(request):
    departments = Department.objects.prefetch_related("employees").all()

    return render(request, "hr_portal/departments.html", {
        "departments": departments
    })

# Placeholder views for other sections
@login_required
@hr_required
def recruitment(request):
    return render(request, "hr_portal/recruitment.html")

@login_required
@hr_required
def applications(request):
    return render(request, "hr_portal/applications.html")

@login_required
@hr_required
def attendance(request):
    return render(request, "hr_portal/attendance.html")

@login_required
@hr_required
def payroll(request):
    return render(request, "hr_portal/payroll.html")

@login_required
@hr_required
def reports(request):
    return render(request, "hr_portal/reports.html")

@login_required
@hr_required
def settings_view(request):
    return render(request, "hr_portal/settings.html")