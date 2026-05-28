from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from hr_portal.models import Employee, Department
from hr_portal.forms import EmployeeForm
from authentication.decorators import hr_required

from recruitment.models import Application
from hr_portal.services import convert_applicant_to_employee


# =====================================================
# DASHBOARD
# =====================================================
@login_required
@hr_required
def dashboard(request):
    context = {
        "total_employees": Employee.objects.count(),
        "total_departments": Department.objects.count(),
        "recent_employees": Employee.objects.order_by("-hire_date")[:6],
    }

    return render(request, "hr_portal/dashboard.html", context)


# =====================================================
# EMPLOYEE LIST
# =====================================================
@login_required
@hr_required
def employee_list(request):

    query = request.GET.get("q", "")

    employees_list = Employee.objects.all().order_by("-id")

    if query:
        employees_list = employees_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(employees_list, 10)
    page_number = request.GET.get("page")
    employees = paginator.get_page(page_number)

    return render(request, "hr_portal/employee_list.html", {
        "employees": employees,
        "query": query,
    })


# =====================================================
# ADD EMPLOYEE
# =====================================================
@login_required
@hr_required
def add_employee(request):

    if request.method == "POST":
        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
            return redirect("hr_portal:employee_list")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = EmployeeForm()

    return render(request, "hr_portal/add_employee.html", {
        "form": form
    })


# =====================================================
# DEPARTMENTS
# =====================================================
@login_required
@hr_required
def departments(request):

    departments = Department.objects.prefetch_related("employees").all()

    return render(request, "hr_portal/departments.html", {
        "departments": departments
    })


# =====================================================
# HR APPLICATION MANAGEMENT (CORE FIX)
# =====================================================

@login_required
@hr_required
def applications(request):

    applications_list = Application.objects.select_related(
    "applicant",
    "job").order_by("-applied_at")

    query = request.GET.get("search", "")

    if query:
        applications_list = applications_list.filter(
            Q(applicant__first_name__icontains=query) |
            Q(applicant__last_name__icontains=query) |
            Q(job__title__icontains=query) |
            Q(status__icontains=query)
        )

    return render(request, "hr_portal/applications.html", {
        "applications": applications_list,
        "query": query
    })


@login_required
@hr_required
def update_application_status(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    if request.method == "POST":
        application.status = request.POST.get("status")
        application.hr_notes = request.POST.get("hr_notes", "")
        application.save()

        messages.success(request, "Application updated successfully.")
        return redirect("hr_portal:applications")

    return render(request, "hr_portal/update_status.html", {
        "application": application
    })


@login_required
@hr_required
def hire_applicant(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    application.status = "HIRED"
    application.save()

    convert_applicant_to_employee(application)

    messages.success(request, "Applicant successfully hired.")
    return redirect("hr_portal:applications")


# =====================================================
# STATIC HR PAGES
# =====================================================
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