from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from administration.models import Department , Application,InductionEnrollment, IntershipEnrollment, InductionPost, Shift, Intern, InternLogbook, LeaveRequest, Hearing, Event
from hostCampany.models import HostComapany, Report
from datetime import datetime, timedelta
from django.db.models.functions import ExtractMonth
from .models import Staff, Vehicle, VehicleRequest, VehicleUsage, StaffScoring, ScoringCategory, StaffTaskScore, ScoringTask
from django.db.models import Count
import json
from django.views import View
from django.db.models import Case, When, Value, BooleanField
from django.utils.timezone import now
from django.db.models import Exists, OuterRef
from intern.models import WorkAttendance
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from authentication.models import User
from .forms import SystemUserRegistrationForm, StaffForm, VehicleForm, VehicleRequestForm, VehicleUsageForm, ScoringTaskForm, ScoringCategoryForm
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from marketing.models import Campaign, SuccessStory, Magazine
from web.models import NewsLetters
from coordination.models import MonthlySiteVisit
from coordination.forms import MonthlySiteVisitForm

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "hr/pages/home/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        context["user"] = self.request.user
        context["applications_received"] = Application.objects.count()
        context["interns_count"] = IntershipEnrollment.objects.count()
        context["active_interns_count"] = IntershipEnrollment.objects.filter(
            status=IntershipEnrollment.InternshipStatus.PLACED
        ).count()
        context["completed_interns_count"] = IntershipEnrollment.objects.filter(
            status=IntershipEnrollment.InternshipStatus.COMPLETED
        ).count()
        context["inductions_count"] = InductionPost.objects.count()
        context["host_employers_count"] = HostComapany.objects.count()
        context["magazines"] = Magazine.objects.order_by("-issue_date")[:5]
        context["success_stories"] = SuccessStory.objects.order_by("-created")[:5]
        context["newsletters"] = NewsLetters.objects.order_by("-created")[:5]
        context["campaigns"] = Campaign.objects.order_by("-created")[:5]
        current_year = datetime.now().year

        # Calculate applications received per month for the current year
        applications_per_month = (
            Application.objects.filter(created_at__year=current_year)
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Generate a list for chart data
        months_data = [0] * 12
        for item in applications_per_month:
            months_data[item['month'] - 1] = item['count']

        # Calculate gender distribution
        gender_counts = {
            'Male': Application.objects.filter(gender=Application.Gender.MALE).count(),
            'Female': Application.objects.filter(gender=Application.Gender.FEMALE).count(),
            'Unspecified': Application.objects.filter(gender__isnull=True).count()
        }

        # Convert data to JSON for JavaScript
        context["applications_per_month"] = json.dumps(months_data)
        context["gender_data"] = json.dumps(list(gender_counts.values()))
        context["current_year"] = current_year
        return context
    
def hr_waiting_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.WAITING
    )
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "hr/pages/interns/waiting_internships.html", context
    )
def placed_internships(request):
    # Query for pending reports
    pending_reports = Report.objects.filter(
        intern=OuterRef("intern"), status="pending"
    )

    # Get today's date
    today = now().date()

    # Fetch internships and annotate with:
    # - `has_pending_reports`: Flag for pending reports
    # - `is_absent_today`: Flag for absentees
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.PLACED
    ).annotate(
        has_pending_reports=Exists(pending_reports),
        is_absent_today=Case(
            When(
                workattendance__date=today, workattendance__status=WorkAttendance.Status.ABSENT, 
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField(),
        ),
    )

    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "hr/pages/interns/placed_internships.html", context
    )
def terminated_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.TERMINATED
    )
    # applications = Application.objects.all()
    # internships_and_applications = zip(internships, applications)
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "hr/pages/interns/terminated_internships.html", context
    )

def completed_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.COMPLETED
    )
    # applications = Application.objects.all()
    # internships_and_applications = zip(internships, applications)
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "hr/pages/interns/completed_internships.html", context
    )
def defaulted_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.DEFAULTED
    )
    # applications = Application.objects.all()
    # internships_and_applications = zip(internships, applications)
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "hr/pages/interns/defaulted_internships.html", context
    )

def attendance_list(request):
            # Get departments related to this host employer's company
            departments = Department.objects()

            # Get the date from the request's query parameters
            date_str = request.GET.get("date")
            department_id = request.GET.get("department")
            
            # Filter attendances by company
            attendances = WorkAttendance.objects()
            
            # If a date is provided, filter attendance by that date
            if date_str:
                try:
                    filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    attendances = attendances.filter(date=filter_date)
                except ValueError:
                    messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            
            # If a department is selected, filter attendances by department
            if department_id and department_id != "all":
                attendances = attendances.filter(intern__department_id=department_id)
            
            context = {
                "attendances": attendances,
                "departments": departments,
                "selected_date": date_str,
                "selected_department": department_id,
            }
            return render(request, "hr/pages/attendance/attendance_list.html", context)

def hr_attendance_list(request):
    user = request.user
    if user.is_authenticated and user.role == "HR":
        companies = HostComapany.objects.all()
        departments = Department.objects.all()

        date_str = request.GET.get("date")
        company_id = request.GET.get("company")
        department_id = request.GET.get("department")

        attendances = WorkAttendance.objects.all()

        # Filter by company
        if company_id and company_id != "all":
            host_employer = HostComapany.objects.get(id=company_id)
            attendances = attendances.filter(intern__company=host_employer)

        # Filter by date
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                attendances = attendances.filter(date=filter_date)
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

        # Filter by department
        if department_id and department_id != "all":
            attendances = attendances.filter(intern__department_id=department_id)

        context = {
            "attendances": attendances,
            "companies": companies,
            "departments": departments,
            "selected_date": date_str,
            "selected_company": company_id,
            "selected_department": department_id,
        }
        return render(request, "hr/pages/attendance/attendance_list.html", context)

    messages.error(request, "You are not authorized to view this page.")
    return redirect("hr-dashboard")
  
def hr_manage_leave_requests(request):
    leave_requests = LeaveRequest.objects.all()

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)

        if action == 'approve':
            leave_request.status = 'approved'
            messages.success(request, "Leave request approved successfully.")
        elif action == 'reject':
            leave_request.status = 'rejected'
            messages.error(request, "Leave request rejected.")

        leave_request.save()
        return redirect('hr_manage_leave_requests')

    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'hr/pages/work/manage_leave_requests.html', context)   

def work_attendance_list(request):
    # Get the date from the request GET parameters if available
    date_str = request.GET.get("date")
    if date_str:
        # Convert the date string from the request to a date object
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        # Filter attendance by the specified date
        attendances = WorkAttendance.objects.filter(date=date)
    else:
        # Show all records if no date is provided
        attendances = WorkAttendance.objects.filter()
    
    intern = IntershipEnrollment.objects.all()
    context = {
        "attendances": attendances,
        "intern": intern,
    }
    return render(request, "hr/pages/work/attendance_list.html", context)

from django.templatetags.static import static
from django.contrib.staticfiles import finders
from django.conf import settings
import os
from reportlab.lib.pagesizes import A4

def generate_attendance_pdf(request):
    # Get the date from the GET parameter
    date_str = request.GET.get("date")
    if not date_str:
        return HttpResponse("Date parameter is required", status=400)
    
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Filter attendance records by the selected date
    attendances = WorkAttendance.objects.filter(date=date)
    
    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{date}.pdf"'

    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y_position = height - 60  # Start position for the content

    # Find the logo path using Django's finders
    logo_path = finders.find('media/logo.png')
    
    # Draw company logo on the far right
    if logo_path:
        p.drawImage(logo_path, width - 3.5 * inch, height - 1.5 * inch, width=3 * inch, height=2 * inch, preserveAspectRatio=True)
    else:
        print("Logo file not found at the specified path.")

    # Title and Date
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y_position, f"Attendance Report for {date_str}")
    y_position -= 40  # Move down for the next line

    # Table Headers
    p.setFont("Helvetica-Bold", 12)
    headers = ["Intern ID No.", "Status", "Sign-In", "Sign-Out", "Approval"]
    x_positions = [40, 160, 240, 320, 400]

    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y_position, header)
    y_position -= 20  # Move down for the content

    # Table Content with Background Color and Status-based Coloring
    p.setFont("Helvetica", 10)
    for attendance in attendances:
        # Set background color based on status
        if attendance.status == "PRESENT":
            p.setFillColor(colors.green)
        elif attendance.status in ["ABSENT", "UNAVAILABLE"]:
            p.setFillColor(colors.red)
        else:
            p.setFillColor(colors.lightgrey)
        
        # Draw background rectangle for the entire row
        p.rect(35, y_position - 10, width - 70, 20, fill=True, stroke=False)
        
        # Reset fill color for text
        p.setFillColor(colors.black)

        # Draw content in each cell without borders
        p.drawString(40, y_position, attendance.intern.intern.username)
        p.drawString(160, y_position, attendance.status)
        p.drawString(240, y_position, attendance.sign_in_time.strftime("%H:%M") if attendance.sign_in_time else "N/A")
        p.drawString(320, y_position, attendance.sign_out_time.strftime("%H:%M") if attendance.sign_out_time else "N/A")
        p.drawString(400, y_position, "Approved" if attendance.approved else "Pending")
        
        y_position -= 20  # Move down for the next record
    
    # Close the PDF object
    p.showPage()
    p.save()

    return response
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

class RegisterUserView(LoginRequiredMixin, CreateView):
    model = User
    form_class = SystemUserRegistrationForm
    template_name = "hr/pages/staff/register_user.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # 🔐 Generate password reset link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = self.request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )

        # 📩 Render the HTML email
        html_message = render_to_string("hr/email/staff_onboarding_email.html", {
            "full_name": f"{user.first_name} {user.last_name}",
            "role": user.get_role_display(),
            "reset_link": reset_link,
        })

        subject = "Welcome to Internship Success"
        email = EmailMessage(subject, html_message, to=[user.email])
        email.content_subtype = "html"  # Send as HTML
        email.send()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("register_staff_profile", kwargs={"pk": self.object.pk})

class RegisterStaffView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm  # You’ll create this form
    template_name = "hr/pages/staff/register_staff.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.HR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs["pk"])
        context["user_first_name"] = user.first_name
        context["user_last_name"] = user.last_name
        return context
    
    def form_valid(self, form):
        user = User.objects.get(pk=self.kwargs["pk"])
        form.instance.user = user
        print("Form is valid and about to save staff")  # DEBUG
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("staff_registration_success")
    
class RegisterStaffCompanySuccessView(LoginRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = (
        "hr/pages/hostEmployer/register-host-company-success.html"
    )
    login_url = "/auth/login/"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.HR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
from django.views.generic import DetailView
class StaffProfileView(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = "hr/pages/staff/staff_profile.html"
    context_object_name = "staff"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

from django.views.generic import ListView   
class StaffListView(LoginRequiredMixin, ListView):
    model = Staff
    template_name = "hr/pages/staff/staff_list.html"
    context_object_name = "staff_members"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Staff.objects.select_related("user", "department").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Staff List"
        context["user"] = self.request.user
        return context
    
class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = "hr/pages/staff/staff_edit.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("staff-profile-view", kwargs={"pk": self.object.pk})  
    
from django.views.generic import DeleteView
from django.shortcuts import redirect, get_object_or_404

class SiteVisitListView(LoginRequiredMixin, ListView):
    model = MonthlySiteVisit
    template_name = "hr/pages/site_visit/list.html"
    context_object_name = "site_visits"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            messages.error(request, "Unauthorized")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
        
class CreateMonthlySiteVisitView(LoginRequiredMixin, CreateView):
    model = MonthlySiteVisit
    form_class = MonthlySiteVisitForm
    template_name = "hr/pages/site_visit/create.html"
    success_url = reverse_lazy("site-visit-list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    template_name = "hr/pages/staff/staff_confirm_delete.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        staff = self.get_object()
        user = staff.user  # Linked user

        # Delete user first before staff to avoid FK issues
        try:
            user.delete()  # Delete user account
            staff.delete()  # Delete staff profile (safe even if user already gone)
        except Exception as e:
            print(f"[ERROR] User or Staff deletion failed: {e}")

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("staff_list")

class VehicleListView(LoginRequiredMixin, TemplateView):
    template_name = "hr/pages/vehicle/vehicle_list.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.HR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicles"] = Vehicle.objects.all()
        return context
    
class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "hr/pages/vehicle/vehicle_form.html"
    success_url = reverse_lazy("vehicle-list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.HR:
            return redirect("/auth/login/")
        return super().dispatch(request, *args, **kwargs)

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = "hr/pages/vehicle/vehicle_detail.html"
    context_object_name = "vehicle"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        requests = VehicleRequest.objects.filter(vehicle=vehicle)
        usages = VehicleUsage.objects.filter(request__vehicle=vehicle)

        context["requests"] = requests
        context["usages"] = usages
        return context
   
@login_required
def approve_vehicle_request(request, pk):
    if request.user.role != User.Role.HR:
        return redirect("vehicle-list")  # or a 403 page

    vehicle_request = get_object_or_404(VehicleRequest, pk=pk)
    vehicle_request.is_approved = True
    vehicle_request.approved_by = request.user
    vehicle_request.approved_at = now()
    vehicle_request.save()

    # Update vehicle status
    vehicle = vehicle_request.vehicle
    vehicle.status = "BUSY"
    vehicle.save()

    return redirect("vehicle-detail", pk=vehicle.id)

class CreateVehicleRequestView(LoginRequiredMixin, CreateView):
    model = VehicleRequest
    form_class = VehicleRequestForm
    template_name = "hr/pages/vehicle/vehicle_request_form.html"
    success_url = reverse_lazy("vehicle-request-success")

    def form_valid(self, form):
        staff = self.request.user.staff

        if not staff.drivers_license:
            messages.error(self.request, "You must upload your driver's license before requesting a vehicle.")
            return redirect("vehicle-request-list")

        form.instance.staff = staff
        form.instance.vehicle = get_object_or_404(Vehicle, pk=self.kwargs["pk"])  # ✅ assign vehicle

        return super().form_valid(form)
    
class UpdateVehicleUsageView(LoginRequiredMixin, UpdateView):
    model = VehicleUsage
    form_class = VehicleUsageForm
    template_name = "hr/pages/vehicle/vehicle_usage_form.html"

    def dispatch(self, request, *args, **kwargs):
        usage = self.get_object()
        if usage.request.staff.user != request.user:
            return redirect("vehicle-list")  # Or 403
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.object.request.vehicle.id})
    
class AvailableVehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "hr/pages/vehicle/available_vehicles.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.all()
    
class VehicleRequestSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "hr/pages/vehicle/vehicle-request-success.html"
    login_url = "/auth/login/"

class CreateStaffScoringView(LoginRequiredMixin, View):
    def get(self, request, staff_id):
        staff = get_object_or_404(Staff, pk=staff_id)
        categories = ScoringCategory.objects.filter(department=staff.department).prefetch_related('tasks')
        scores = [4, 3, 2, 1, 0]
        return render(request, 'hr/pages/scoring/create.html', {
            'categories': categories,
            'staff_id': staff_id,
            'staff': staff,
            'scores': scores,
        })

    def post(self, request, staff_id):
        staff = get_object_or_404(Staff, pk=staff_id)
        scoring = StaffScoring.objects.create(
            staff=staff,
            assessor=request.user
        )

        total = 0
        max_possible = 0
        for task_id, score in request.POST.items():
            if task_id.startswith('task_'):
                task_pk = task_id.split('_')[1]
                task = get_object_or_404(ScoringTask, pk=task_pk)
                StaffTaskScore.objects.create(scoring_session=scoring, task=task, score=int(score))
                total += int(score)
                max_possible += 4

        percentage = (total / max_possible) * 100 if max_possible else 0

        if percentage >= 90:
            category = 'A'
        elif percentage >= 75:
            category = 'B'
        elif percentage >= 60:
            category = 'C'
        elif percentage >= 50:
            category = 'D'
        else:
            category = 'F'

        scoring.total_points = total
        scoring.percentage_score = percentage
        scoring.performance_category = category
        scoring.save()

        messages.success(request, "Scoring submitted successfully.")
        return redirect('staff-profile-view', staff_id=staff.id)
from hr.models import Department 
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = "hr/pages/scoring/department_list.html"
    context_object_name = "departments"

class CategoryListByDepartmentView(LoginRequiredMixin, ListView):
    model = ScoringCategory
    template_name = "hr/pages/scoring/category_list.html"
    context_object_name = "categories"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ScoringCategory.objects.filter(department_id=self.kwargs['department_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the department explicitly
        context['department'] = get_object_or_404(Department, pk=self.kwargs['department_id'])
        return context

class ScoringCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ScoringCategory
    form_class = ScoringCategoryForm
    template_name = "hr/pages/scoring/category_create.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect("login")
        # department_id comes from URL now
        self.department_id = self.kwargs.get('department_id')
        if not self.department_id:
            messages.error(request, "No department selected.")
            return redirect("scoring-department-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # assign department directly
        form.instance.department_id = self.department_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'scoring-category-list-by-department', 
            kwargs={'department_id': self.department_id}
        )
class TaskListByCategoryView(LoginRequiredMixin, ListView):
    model = ScoringTask
    template_name = "hr/pages/scoring/task_list.html"
    context_object_name = "tasks"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        self.category = get_object_or_404(ScoringCategory, pk=self.kwargs['category_id'])
        return ScoringTask.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest

class ScoringTaskCreateView(LoginRequiredMixin, CreateView):
    model = ScoringTask
    form_class = ScoringTaskForm
    template_name = "hr/pages/scoring/task_create.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return redirect("login")
        self.category_id = self.request.GET.get("category")
        if not self.category_id:
            return HttpResponseBadRequest("Missing category ID. Please access via proper link.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.category = get_object_or_404(ScoringCategory, id=self.category_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("scoring-task-list-by-category", kwargs={'category_id': self.category_id})
    

# Category Views
class ScoringCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ScoringCategory
    form_class = ScoringCategoryForm
    template_name = "hr/pages/scoring/category_update.html"

    def get_success_url(self):
        return reverse_lazy("scoring-category-list-by-department", kwargs={'department_id': self.object.department.id})

class ScoringCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ScoringCategory
    template_name = "hr/pages/scoring/category_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("scoring-category-list-by-department", kwargs={'department_id': self.object.department.id})

# Task Views
class ScoringTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = ScoringTask
    form_class = ScoringTaskForm
    template_name = "hr/pages/scoring/task_update.html"

    def get_success_url(self):
        return reverse_lazy("scoring-task-list-by-category", kwargs={'category_id': self.object.category.id})

class ScoringTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = ScoringTask
    template_name = "hr/pages/scoring/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("scoring-task-list-by-category", kwargs={'category_id': self.object.category.id})

