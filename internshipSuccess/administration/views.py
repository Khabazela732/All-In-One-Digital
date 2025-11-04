import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from reportlab.lib.pagesizes import A4
import pandas as pd
from django.utils.dateparse import parse_date
from django.db.models import Exists, OuterRef
from django.views.generic.base import TemplateView
from core.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from administration.models import (
    Event,
    InductionPost,
    IntershipEnrollment,
    InductionEnrollment,
    RecordAction,
    LeaveRequest,
    Hearing, Subject
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.shortcuts import redirect
from administration.models import InductionPost, Application, Questionnaire
from administration.forms import (
    ApplicationStatusForm,
    InductionPostForm,
    UpdatePasscodeForm,
    HostEmployerForm,
    SubjectForm
    
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import redirect
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import date
from django.views.generic.edit import BaseCreateView
from hostCampany.forms import HostComapanyForm
from intern.models import WorkAttendance, Assignment
from web.forms import NewsLetterForm
from web.models import NewsLetters
from .forms import DeliverableForm, QualificationForm, QuestionnaireForm, UploadFileForm, WorkItemForm
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.forms import formset_factory
from intern.models import Attendance
from authentication.models import HostEmployerProfile, Intern, User
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from .decorators import *
from hostCampany.models import HostEmployer, HostComapany, Report, InternInvoice, MonthlyCompanyInvoice, Payment
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.db.models import Count, Q
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template import loader
from marketing.models import Magazine, SuccessStory, Campaign
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from .models import Payment

class HomeView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/home/index.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/home/index.html"]
        return super().get_template_names()
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


        current_year = datetime.datetime.now().year

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

class InductionApplicationsView(LoginRequiredMixin, TemplateView):
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MARKETING]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/induction/index.html"]
        elif self.request.user.role == User.Role.MARKETING:
            return ["mar/pages/induction/index.html"]
        return super().get_template_names()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Induction Applications"
        context["user"] = self.request.user
        inductions = InductionPost.objects.all()
        context["inductions"] = inductions
        return context

@csrf_exempt
def toggle_induction_status(request, induction_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON from request
            induction = InductionPost.objects.get(id=induction_id)
            induction.closed = data.get("closed", False)  # Update status
            induction.save()

            return JsonResponse({"success": True, "new_status": induction.closed})
        except InductionPost.DoesNotExist:
            return JsonResponse({"success": False, "error": "Induction post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    
def import_applications(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            try:
                induction_post = InductionPost.objects.get(id=6)
            except InductionPost.DoesNotExist:
                messages.error(request, 'Induction post with ID 6 does not exist.')
                return redirect('import_applications')

            for index, row in df.iterrows():
                Application.objects.create(
                    induction_post=induction_post,
                    name=row['Name'],
                    surname=row['Surname'],
                    national_id=row['National ID'],
                    email=row['Email'],
                    phone_number=row['Phone Number'],
                    age=row['Age'],
                    gender=row['Gender'],
                    qualification=row.get('Qualification', ''),
                    qualification_description=row.get('Qualification Description', ''),
                    college_name=row.get('College Name', 'None'),
                    residental_address=row.get('Residential Address', ''),
                    post_address=row.get('Post Address', ''),
                    status=row['Status'],
                    #created_at=row['Created At'],
                )
            messages.success(request, 'Applications imported successfully!')
            return redirect('import_applications')
    else:
        form = UploadFileForm()
    return render(request, 'administration/pages/import_applications.html', {'form': form})
def export_applications_view(request):
    applications = Application.objects.all()
    data = []
    for application in applications:
        data.append({
            'Name': application.name,
            'Surname': application.surname,
            'National ID': application.national_id,
            'Email': application.email,
            'Phone Number': application.phone_number,
            'Age': application.age,
            'Gender': application.get_gender_display(),
            'Qualification': application.qualification,
            'Qualification Description': application.qualification_description,
            'College Name': application.college_name,
            'Residential Address': application.residental_address,
            'Post Address': application.post_address,
            'Status': application.get_status_display(),
            #'Created At': application.created_at,
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=applications.xlsx'
    df.to_excel(response, index=False)
    return response

class AssesmentListAllView(View):
    template_name = "administration/pages/induction/assements/assignments.html"
    def get(self, request, *args, **kwargs):
        assignments_one = Assignment.objects.all()
        assignments_two = AssignmentTwo.objects.all()
        return render(request, self.template_name, {"assignments_one": assignments_one, "assignments_two": assignments_two})
    
class InductionAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/attendence.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Induction Attendance"
        context["user"] = self.request.user
        inductions = InductionPost.objects.all()
        context["inductions"] = inductions
        return context
class InductionAssigmentsView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/induction_ass.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user
        inductions = InductionPost.objects.all()
        context["inductions"] = inductions
        return context
    
class InductionAssigmentsTwoView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/induction_ass_two.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user
        inductions = InductionPost.objects.all()
        context["inductions"] = inductions
        return context
    
class CreateInductionPostView(LoginRequiredMixin, CreateView):
    model = InductionPost
    form_class = InductionPostForm
    template_name = "administration/pages/induction/create_induct_post.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MARKETING]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Induction"
        context["user"] = self.request.user
        return context

    def get_success_url(self):
        return reverse_lazy("induction-create-success")

    def form_valid(self, form):
        admin = self.request.user
        form.instance.admin = admin
        return super().form_valid(form)
    
def admit_all_applications(request):
    # Update the status of all applications to "ADMITTED"
    Application.objects.all().update(status=Application.Status.ADMITTED)
    messages.success(request, 'All applications have been admitted.')
    return redirect('some-view-name')  # Replace with the name of the view you want to redirect to

class InductionPostSuccessCreateView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/create_induct_post_success.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MARKETING]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Successfully created Indution Application"
        context["user"] = self.request.user
        return context

class ViewInductionPostApplications(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/induction_post_applications.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        induction_post_id = self.kwargs["id"]
        induction_post = InductionPost.objects.get(id=induction_post_id)
        induction_post_applications = induction_post.induction_post_applications.all()
        context["induction_post_applications"] = induction_post_applications
        context["induction_post"] = induction_post
        context["title"] = "Induction Post Applications"
        context["user"] = self.request.user
        return context
    
class ViewAllApplications(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/all_applications.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        induction_post_applications = Application.objects.all()
        context["induction_post_applications"] = induction_post_applications
        return context
    
class ViewAssignment(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/view_answer.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment_id = self.kwargs["id"]
        assignment = Assignment.objects.get(id=assignment_id)
        induction_assignment = assignment.intern
        context["induction_assignment"] = induction_assignment
        context["assignment"] = assignment
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user
        return context
    
class AssesmentListView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/assesment_list.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user

        assignment = Assignment.objects.filter(induction_post_id=post_id)
        context["assignment"] = assignment
        context["induction_post"] = InductionPost.objects.filter(id=post_id).first()
        return context
    
from intern.models import AssignmentTwo
class ViewAssignmentTwo(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/view_answer2.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment_id = self.kwargs["id"]
        assignment = AssignmentTwo.objects.get(id=assignment_id)
        induction_assignment = assignment.intern
        context["induction_assignment"] = induction_assignment
        context["assignment"] = assignment
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user
        return context
    
class AssesmentTwoListView(LoginRequiredMixin, TemplateView):
    template_name = "administration/pages/induction/assements/assesment_list2.html"
    login_url = (
        "/auth/login/"  # Specify the URL to redirect to if the user is not logged in
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        context["title"] = "Induction Assignment"
        context["user"] = self.request.user

        assignment = AssignmentTwo.objects.filter(induction_post_id=post_id)
        context["assignment"] = assignment
        context["induction_post"] = InductionPost.objects.filter(id=post_id).first()
        return context  
     
def manage_leave_requests(request):
    leave_requests = LeaveRequest.objects.all()

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)

        if action == 'approve':
            leave_request.status = 'approved'
        elif action == 'reject':
            leave_request.status = 'rejected'
        
        leave_request.save()
        return redirect('manage_leave_requests')

    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'administration/pages/work/manage_leave_requests.html', context)
        
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
    return render(request, "administration/pages/work/attendance_list.html", context)

from django.http import HttpResponseBadRequest
def meeting_attendance_list(request):
    # Get the date from the request GET parameters if available
    date_str = request.GET.get("date")
    
    try:
        if date_str:
            # Convert the date string from the request to a date object
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            # Filter attendance by the specified date and type
            attendances = WorkAttendance.objects.filter(date=date, type='MEETING')
        else:
            # Show all records if no date is provided
            attendances = WorkAttendance.objects.filter(type='MEETING')
    except ValueError:
        # Handle invalid date format
        return HttpResponseBadRequest("Invalid date format. Please use YYYY-MM-DD.")
    
    interns = IntershipEnrollment.objects.all()
    context = {
        "attendances": attendances,
        "interns": interns,
    }
    return render(request, "administration/pages/work/meeting_list.html", context)

from django.templatetags.static import static
from django.contrib.staticfiles import finders
from django.conf import settings
import os

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
class ViewInductionApplicantView(LoginRequiredMixin, UpdateView):
    template_name = "administration/pages/induction/view_induction_applicant.html"
    form_class = ApplicationStatusForm
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated and has the role "ADMIN"
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the existing context data and add custom context for application and questionnaire
        context = super().get_context_data(**kwargs)
        application_id = int(self.kwargs["id"])
        
        # Fetch the application based on the passed ID
        application = Application.objects.get(id=application_id)
        
        # Fetch the questionnaire linked to the application (if it exists)
        try:
            questionnaire = Questionnaire.objects.get(application=application)
            context["questionnaire"] = questionnaire
            context["questionnaire_id"] = questionnaire.application
        except Questionnaire.DoesNotExist:
            context["questionnaire_id"] = None
        
        # Add progress bar data and form to the context
        context["application"] = application
        context["progress_bar_data"] = get_progress_bar_data(status=application.status)
        context["title"] = (
            f"Application for {application.name.capitalize()} {application.surname.capitalize()} - {application.national_id}"
        )
        context["user"] = self.request.user
        context["form"] = self.get_form()
        
        return context

    def get_object(self, queryset=None):
        # Fetch the application based on the ID in the URL
        return get_object_or_404(Application, id=self.kwargs["id"])

    def get_success_url(self):
        # Redirect to the same view after form submission
        application_id = self.kwargs["id"]
        return reverse_lazy("induction-application-view", kwargs={"id": application_id})


def get_progress_bar_data(status):
    print("Progress bar data", status)
    if status == "ADMITTED":
        return {"width": "100%", "color": "success", "icon": "bi-check-circle"}

    elif status == "PENDING":
        return {"width": "25%", "color": "warning", "icon": "bi-clock"}

    elif status == "REJECTED":
        return {"width": "10%", "color": "danger", "icon": "bi-x-circle-fill"}

    elif status == "ACKNOWLEDGED":
        return {"width": "75%", "color": "primary", "icon": "bi-eye-fill"}
    else:
        return {"width": "0%", "color": "secondary", "icon": "fa-question-circle"}

class ViewQuestionnaireView(UpdateView):
    template_name = "administration/pages/induction/view_questionnaire.html"
    form_class = QuestionnaireForm

    def get_context_data(self, **kwargs):
        # Get the existing context data and add custom context for questionnaire and application
        context = super().get_context_data(**kwargs)
        questionnaire_id = self.kwargs["id"]
        
        # Fetch the questionnaire using its ID
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        
        # Fetch the related application through the questionnaire's foreign key
        application = questionnaire.application
        
        # Add both the questionnaire and application to the context
        context["questionnaire"] = questionnaire
        context["application"] = application
        
        return context

    def get_object(self, queryset=None):
        # Fetch and return the questionnaire based on the ID in the URL
        return get_object_or_404(Questionnaire, id=self.kwargs["id"])

    def get_success_url(self):
        # After the form is successfully updated, redirect to the same questionnaire view
        questionnaire_id = self.kwargs["id"]
        return reverse_lazy("view_questionnaire", kwargs={"id": questionnaire_id})

def view_attended_interns(request, post_id):
    try:
        induction_post = get_object_or_404(InductionPost, pk=post_id)
        attended_interns = Attendance.objects.filter(induction_post_id=post_id)
    except InductionPost.DoesNotExist:
        return HttpResponseServerError("InductionPost does not exist.")
    return render(
        request,
        "administration/pages/induction/view_attended_interns.html",
        {"attended_interns": attended_interns, "post": induction_post},
    )

@admin_required
def update_passcode(request, post_id):
    post = get_object_or_404(InductionPost, pk=post_id)
    if request.method == "POST":
        form = UpdatePasscodeForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(
                "view_attended_interns", post_id=post_id
            )  # Redirect to the induction detail page
    else:
        form = UpdatePasscodeForm(instance=post)
    return render(
        request,
        "administration/pages/induction/assements/update_passcode.html",
        {"form": form, "post": post},
    )

class HostEmployerView(LoginRequiredMixin, UpdateView):
    login_url = "/auth/login/"
    model = HostComapany
    fields = ["mentor", "company_name", "description", "joined_date", "location"]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/hostEmployer/company.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/hostEmployer/company.html"]
        return super().get_template_names()
    
    def get_object(self, queryset=None):
        # Get the HostEmployer instance based on the pk from URL
        post_id = self.kwargs.get("pk")
        return get_object_or_404(HostComapany, pk=post_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_employer = self.object  # Get the HostEmployer instance
        application = Application.objects.all()
        intern = IntershipEnrollment.objects.filter(company=host_employer)
        interns = zip(intern, application)
        context["host_employer"] = host_employer
        context["interns"] = interns  # Pass filtered interns to context
        return context

def waiting_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.WAITING
    )
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "administration/pages/interns/waiting_internships.html", context
    )

from django.db.models import Case, When, Value, BooleanField
from django.utils.timezone import now

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
    )

    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "administration/pages/interns/placed_internships.html", context
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
        request, "administration/pages/interns/terminated_internships.html", context
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
        request, "administration/pages/interns/completed_internships.html", context
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
        request, "administration/pages/interns/defaulted_internships.html", context
    )
class HostEmployersListView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/hostEmployer/companies.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/hostEmployer/companies.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/hostEmployer/companies.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        host_employers = HostEmployer.host_employer.all()
        host_company = HostComapany.objects.annotate(intern_count=Count("internCompany")).order_by("company_name")
        host_company = HostComapany.objects.annotate(intern_count=Count("internCompany"))
        context["host_companies"] = host_company
        context["host_employers"] = host_employers
        return context
    
class HearingCreateView(CreateView):
    model = Hearing
    fields = ["title", "date", "description"]
    template_name = "administration/hearings/hearing_form.html"

    def form_valid(self, form):
        # Retrieve intern_id from POST data
        intern_id = self.request.POST.get("intern_id")
        if not intern_id:
            messages.error(self.request, "Invalid request. Intern ID is missing.")
            return self.form_invalid(form)

        # Fetch the intern object
        intern = get_object_or_404(Intern, id=intern_id)
        form.instance.intern = intern
        form.instance.created_by = self.request.user

        # Save the form and send notification
        response = super().form_valid(form)
        self.send_email_notification(intern, form.instance)

        messages.success(self.request, "Hearing successfully scheduled and notification sent.")
        return response

    def send_email_notification(self, intern, hearing):
        subject = "You are Invited to a Hearing"
        context = {
            "fullname": intern.user.get_full_name(),
            "title": hearing.title,
            "date": hearing.date.strftime("%Y-%m-%d %H:%M"),
            "description": hearing.description,
        }
        html_content = render_to_string("administration/email/hearing_invite.html", context)
        from_email = EMAIL_HOST_USER
        to_email = intern.user.email

        try:
            msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Log the error and notify the admin
            print(f"Error sending email: {e}")
            messages.warning(
                self.request,
                f"The hearing was scheduled, but we couldn't send the email notification to {to_email}.",
            )

    def get_success_url(self):
        return reverse("intern_profile", kwargs={"intern_id": self.object.intern.id})
    
class InternProfileView(TemplateView):
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to authenticated admin users
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/interns/internprofile.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/interns/internprofile.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/interns/internprofile.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intern_id = self.kwargs.get("intern_id")
        
        try:
            intern = Intern.objects.get(id=intern_id)
        except Intern.DoesNotExist:
            # Handle case where intern does not exist
            context['error'] = "Intern not found"
            return context
        
        # Fetch reports
        reports = intern.reports.all()  # Assuming related_name="reports" in InternReport model
        context["reports"] = reports
        
        # Retrieve the first user enrollment (if exists)
        induction_enrollment = intern.user_enrollments.all().first()
        context["induction_enrollment"] = induction_enrollment
        
        try:
            # Retrieve the application and host employer data
            application = intern.user_applications.all().first()
            host_employer = HostComapany.objects.all()  # Assuming you're retrieving all HostCompanies, modify if necessary
            context["host_employer"] = host_employer
            context["application"] = application
            context["intern"] = intern

            # Get internship enrollment data
            internship_enrollment = IntershipEnrollment.objects.get(intern_id=intern_id)
            context["internship_enrollment"] = internship_enrollment

            # Retrieve any existing hearings for the intern
            hearings = Hearing.objects.filter(intern=intern).order_by("date")
            leaves = LeaveRequest.objects.filter(intern=intern)
            context["hearings"] = hearings
            context["leaves"] = leaves

        except IntershipEnrollment.DoesNotExist:
            context["internship_enrollment"] = None
        except HostComapany.DoesNotExist:
            context["host_employer"] = None

        return context
    def get(self, request, *args, **kwargs):
        # Check if "generate_cv" is present in the URL and trigger PDF generation
        if "generate_cv" in request.GET:
            return self.generate_cv(request)

        return super().get(request, *args, **kwargs)

    def generate_cv(self, request):
        intern_id = self.kwargs.get("intern_id")
        intern = Intern.intern.get(id=intern_id)
        application = intern.user_applications.all().first()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CV_{intern.first_name}_{intern.last_name}.pdf"'

        # Create PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles for a more modern look
        title_style = ParagraphStyle(
            'TitleStyle', fontSize=20, fontName='Helvetica-Bold', textColor=colors.HexColor("#007BFF"),
            spaceAfter=14, alignment=1)
        subtitle_style = ParagraphStyle(
            'SubtitleStyle', fontSize=14, fontName='Helvetica', textColor=colors.HexColor("#444444"),
            spaceAfter=10)
        section_title_style = ParagraphStyle(
            'SectionTitleStyle', fontSize=16, fontName='Helvetica-Bold', textColor=colors.HexColor("#007BFF"),
            spaceAfter=8)
        normal_style = ParagraphStyle(
            'NormalStyle', fontSize=12, fontName='Helvetica', textColor=colors.HexColor("#333333"),
            spaceAfter=10)

        elements = []

        # Title (Name and Role)
        elements.append(Paragraph(f"{intern.first_name} {intern.last_name}", title_style))
        elements.append(Spacer(1, 20))

        # Section: About Me
        elements.append(Paragraph("About Me", section_title_style))

        # Fetch the 'about_me' field from the intern model, with fallback to the default if empty
        about_me = application.about_me if application.about_me else "No bio available"
        elements.append(Paragraph(about_me, normal_style))
        elements.append(Spacer(1, 20))

        # Section: Contact Information
        elements.append(Paragraph("Contact Information", section_title_style))
        contact_info = (f"Phone: {application.phone_number}<br/>"
                        f"Email: {intern.email}<br/>"
                        f"National ID: {application.national_id}<br/>"
                        f"Address: {application.residental_address}")
        elements.append(Paragraph(contact_info, normal_style))
        elements.append(Spacer(1, 20))

        # Section: Education
        elements.append(Paragraph("Education", section_title_style))
        education = f"{application.qualification}<br/>{application.college_name}"
        elements.append(Paragraph(education, normal_style))
        elements.append(Spacer(1, 20))

        # Section: Experience
        elements.append(Paragraph("Experience", section_title_style))

        # Fetch all experience entries for the intern
        experiences = intern.experiences.all()

        if experiences.exists():
            # Display each experience with job title, company name, and date range
            experience_paragraphs = []
            for experience in experiences:
                end_date = experience.end_date.strftime("%Y") if experience.end_date else "Present"
                experience_paragraphs.append(f"{experience.start_date.strftime('%Y')} - {end_date}: {experience.job_title} at {experience.company_name}")
            experience_text = "<br/>".join(experience_paragraphs)  # Joining each experience with a line break
        else:
            experience_text = "No experience provided"

        elements.append(Paragraph(experience_text, normal_style))
        elements.append(Spacer(1, 20))

        # Section: Skills
        elements.append(Paragraph("Skills", section_title_style))

        # Fetch all skills for the intern
        skills_list = intern.skills.all()

        if skills_list.exists():
            # Display each skill as a bullet point
            skill_paragraphs = [f"- {skill.name}" for skill in skills_list]
            skills = "<br/>".join(skill_paragraphs)  # Joining each skill with a line break
        else:
            skills = "No skills provided"

        elements.append(Paragraph(skills, normal_style))
        elements.append(Spacer(1, 20))


        # Build the document
        doc.build(elements)

        return response
    
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UploadProfilePictureView(View):
    def post(self, request, enrollment_id):
        enrollment = IntershipEnrollment.objects.get(id=enrollment_id)
        if 'profile_picture' in request.FILES:
            enrollment.profile_picture = request.FILES['profile_picture']
            enrollment.save()
            return JsonResponse({'message': 'Profile picture uploaded successfully'})
        return JsonResponse({'error': 'No file provided'}, status=400)
    
class UploadCvView(View):
    def post(self, request, application_id):
        application = Application.objects.get(id=application_id)
        if 'resume_cv' in request.FILES:
            application.resume_cv = request.FILES['resume_cv']
            application.save()
            return JsonResponse({'message': ' CV uploaded successfully'})
        return JsonResponse({'error': 'No file provided'}, status=400)
    
class UploadQualificationView(View):
    def post(self, request, application_id):
        application = Application.objects.get(id=application_id)
        if 'qualification_document' in request.FILES:
            application.qualification_document = request.FILES['qualification_document']
            application.save()
            return JsonResponse({'message': ' Qualification uploaded successfully'})
        return JsonResponse({'error': 'No file provided'}, status=400)   
@csrf_protect
def upload_contract(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(IntershipEnrollment, id=enrollment_id)

        if 'contrac_doc' in request.FILES:
            enrollment.contrac_doc = request.FILES['contrac_doc']
            enrollment.save(update_fields=['contrac_doc'])
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

class AllInternsView(TemplateView):
    template_name = "administration/pages/interns/all-interns.html"
    login_url = "/auth/login/"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/interns/all-interns.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/interns/all-interns.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/interns/all-interns.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # intern_id = self.kwargs.get("intern_id")

        # Get all the Interns 
        interns = Intern.intern.all()
        context["interns"] = interns
        return context
    
class ExitReport(TemplateView):
    login_url = "/auth/login/"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/exitreport.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/exitreport.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Update statuses dynamically
        self.update_internship_statuses()

        # Fetch and filter interns by status
        interns_placed = IntershipEnrollment.objects.filter(status=IntershipEnrollment.InternshipStatus.PLACED)
        interns_completed = IntershipEnrollment.objects.filter(status=IntershipEnrollment.InternshipStatus.COMPLETED)
        interns_terminated = IntershipEnrollment.objects.filter(status=IntershipEnrollment.InternshipStatus.TERMINATED)

        all_interns = list(interns_placed) + list(interns_completed) + list(interns_terminated)

        for intern in all_interns:
            # Default values
            intern.completed_percent = 0
            intern.months_left = None
            intern.certificate_application_date = None  # New field

            # Completed percentage calculation
            try:
                logbook = InternLogbook.objects.get(intern=intern.intern)
                deliverables_count = logbook.deliverables.count()
                completed_deliverables_count = InternDeliverable.objects.filter(
                    intern_logbook=logbook, completed=True
                ).count()

                if deliverables_count > 0:
                    intern.completed_percent = round((completed_deliverables_count / deliverables_count) * 100, 2)

                # Calculate certificate application date if end_date exists
                if intern.end_date:
                    application_date = intern.end_date - timedelta(days=90)  # 3 months = ~90 days
                    intern.certificate_application_date = application_date
            except InternLogbook.DoesNotExist:
                pass  # No logbook, leave as None

            # Months left calculation for PLACED interns
            if intern.status == IntershipEnrollment.InternshipStatus.PLACED:
                intern.months_left = intern.calculate_time_left_in_months()

        context["interns"] = all_interns
        context["today"] = timezone.now().date()

        return context

    def update_internship_statuses(self):
        """
        Update statuses of all internships dynamically based on their dates.
        """
        internships = IntershipEnrollment.objects.filter(
            status=IntershipEnrollment.InternshipStatus.PLACED
        )
        for internship in internships:
            internship.save()  # Save triggers the logic in the model to update status if needed

    def generate_pdf(self, request):
        """
        Generate PDF from the context data for the Exit Report page.
        """
        context = self.get_context_data()
        template = loader.get_template(self.template_name)
        html_content = template.render(context)

        # Create a HttpResponse object with content type 'application/pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="intern_exit_report.pdf"'

        # We use html2pdf to convert HTML content to PDF
        from io import BytesIO
        import weasyprint

        weasyprint.HTML(string=html_content).write_pdf(response, stylesheets=['/static/assets/compiled/css/app.css'])

        return response
    
# def register_host_employer(request):
#     if request.method == "POST":
#         form = HostEmployerForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # Redirect to a success page or do something else
#     else:
#         form = HostEmployerForm()
#     return render(
#         request,
#         "administration/pages/hostEmployer/register_host_employer.html",
#         {"form": form},
#     )
class Host(TemplateView):
    template_name = "administration/pages/Host/host.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Recruitment" 
        return context
    
class RegisterHostEmployerView(LoginRequiredMixin, CreateView):
    model = HostEmployer
    form_class = HostEmployerForm
    template_name = "administration/pages/hostEmployer/register_host_employer.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Host Employer"
        context["user"] = self.request.user
        return context

    def get_success_url(self):
        if self.request.POST.get("register_company"):
            return reverse_lazy("register_host_company", kwargs={"pk": self.object.pk})
        return reverse_lazy("register_host_company-success")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = HostEmployer.base_role  # Ensure the role is set to HOST_EMPLOYER
        user.save()
        # HostEmployerProfile.objects.create(user=user)  # Create associated profile
        return super().form_valid(form)
    
def internship_stats_view(request):
    # Count interns placed per company type
    interns_placed = IntershipEnrollment.objects.filter(
        status='PLACED'
    ).values('company__company_type').annotate(
        total=Count('id')
    )

    # Count interns with completed logbooks per company type
    # An intern is considered completed if all their deliverables are completed
    logbooks_completed = InternDeliverable.objects.filter(
        completed=True
    ).values('intern_logbook__logbook_template__company__company_type').annotate(
        total=Count('intern_logbook__intern', distinct=True)
    )

    context = {
        'interns_placed': interns_placed,
        'logbooks_completed': logbooks_completed
    }
    return render(request, 'administration/pages/internship_stats.html', context)

class RegisterHostCompanyView(LoginRequiredMixin, CreateView):
    model = HostComapany
    form_class = HostComapanyForm
    template_name = "administration/pages/hostEmployer/register_host_company.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        host_employer = HostEmployer.objects.get(pk=self.kwargs["pk"])
        form.instance.mentor = host_employer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("register_host_company-success")

class RegisterHostCompanySuccessView(LoginRequiredMixin, CreateView):
    model = HostComapany
    form_class = HostComapanyForm
    template_name = (
        "administration/pages/hostEmployer/register-host-company-success.html"
    )
    login_url = "/auth/login/"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

from django.core.mail import send_mail
from django.utils.html import strip_tags
def place_intern(request, enrollment_id, intern_id):
    if request.method == "POST":
        selected_employer_id = request.POST.get("employer_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        stipend = request.POST.get("stipend")  # Get stipend from POST data
        intern_enrollment = get_object_or_404(
            IntershipEnrollment, id=int(enrollment_id)
        )
        intern = get_object_or_404(Intern, id=int(intern_id))
        induction_enrollment = intern.user_enrollments.first()
        if selected_employer_id and stipend:
            company = get_object_or_404(HostComapany, id=selected_employer_id)
            intern_enrollment.company = company
            intern_enrollment.status = IntershipEnrollment.InternshipStatus.PLACED
            intern_enrollment.contract = start_date
            intern_enrollment.end_date = end_date
            intern_enrollment.stipend = stipend  # Save stipend
            induction_enrollment.placed = True
            induction_enrollment.save()
            intern_enrollment.save()
            return HttpResponse("Intern placed successfully", status=200)
        else:
            return HttpResponse("Company ID and stipend are required", status=400)

def admin_required(user):
    # Check if user is authenticated and has ADMIN role
    return user.is_authenticated and hasattr(user, 'role') and user.role == "ADMIN"

from django.db.models.functions import TruncMonth
class FinancialDashboardView(TemplateView):  # Add AdminRequiredMixin if needed
    template_name = 'administration/pages/invoices/financial_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Financial Metrics
        context['total_approved_paid'] = MonthlyCompanyInvoice.objects.filter(
            approval='APPROVED', status='PAID'
        ).aggregate(total=Sum('total_amount'))['total'] or 0.00
        context['total_expenses'] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0.00
        context['pending_invoices'] = MonthlyCompanyInvoice.objects.filter(
            approval='PENDING'
        ).count()
        context['suspended_invoices'] = MonthlyCompanyInvoice.objects.filter(
            status='SUSPENDED'
        ).count()

        # Chart Data (last 12 months)
        months_ago = 12
        end_date = timezone.now().replace(day=1)  # Start of current month
        start_date = end_date - timedelta(days=30 * months_ago)

        # Approved and Paid Invoices
        approved_paid_invoices = (
            MonthlyCompanyInvoice.objects.filter(
                approval='APPROVED',
                status='PAID',
                month__gte=start_date,
                month__lte=end_date
            )
            .annotate(month_trunc=TruncMonth('month'))
            .values('month_trunc')
            .annotate(total=Sum('total_amount'))
            .order_by('month_trunc')
        )

        # Expenses
        expenses = (
            Payment.objects.filter(
                created__gte=start_date,
                created__lte=end_date
            )
            .annotate(month_trunc=TruncMonth('created'))
            .values('month_trunc')
            .annotate(total=Sum('amount'))
            .order_by('month_trunc')
        )

        # Prepare chart data
        labels = []
        invoice_data = []
        expense_data = []
        current_date = start_date
        while current_date <= end_date:
            month_str = current_date.strftime('%b %Y')
            labels.append(month_str)
            invoice_total = next(
                (item['total'] for item in approved_paid_invoices if item['month_trunc'].strftime('%b %Y') == month_str),
                0
            )
            expense_total = next(
                (item['total'] for item in expenses if item['month_trunc'].strftime('%b %Y') == month_str),
                0
            )
            invoice_data.append(float(invoice_total))  # Convert Decimal to float
            expense_data.append(float(expense_total))
            current_date += timedelta(days=30)

        context['chart_labels'] = labels
        context['approved_paid_invoices'] = invoice_data
        context['expenses'] = expense_data

        return context

class InductionDashboardView(TemplateView):
    template_name = 'administration/pages/induction/induction_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        start_date = datetime.datetime(current_year, 1, 1)  # Naive datetime for current year
        end_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Metrics
        context['total_induction_posts'] = InductionPost.objects.filter(
            start_date__year=current_year
        ).count()
        context['total_applications'] = Application.objects.filter(
            induction_post__start_date__year=current_year
        ).count()
        context['total_admitted'] = InductionEnrollment.objects.filter(
            admitted=True,
            induction_post__start_date__year=current_year
        ).count()
        context['total_day_1_attended'] = Attendance.objects.filter(
            approve=True,
            induction_post__start_date__year=current_year,
            induction_post__induction_post_enrollments__day_1=True
        ).count()
        context['total_day_2_attended'] = Attendance.objects.filter(
            approve=True,
            induction_post__start_date__year=current_year,
            induction_post__induction_post_enrollments__day_2=True
        ).count()
        context['pending_placements'] = InductionEnrollment.objects.filter(
            pending_placement=True,
            induction_post__start_date__year=current_year
        ).count()
        context['placed_interns'] = InductionEnrollment.objects.filter(
            placed=True,
            induction_post__start_date__year=current_year
        ).count()
        context['bypassed_enrollments'] = InductionEnrollment.objects.filter(
            bypassed=True,
            induction_post__start_date__year=current_year
        ).count()

        # Chart 1: Bar Graph - Applications and Admitted per Induction Post
        induction_posts = InductionPost.objects.filter(start_date__year=current_year)
        bar_labels = [post.title for post in induction_posts]
        applications_data = [
            Application.objects.filter(induction_post=post).count()
            for post in induction_posts
        ]
        admitted_data = [
            InductionEnrollment.objects.filter(induction_post=post, admitted=True).count()
            for post in induction_posts
        ]
        context['bar_labels'] = bar_labels
        context['applications_data'] = applications_data
        context['admitted_data'] = admitted_data

        # Chart 2: Pie Chart - Gender Distribution
        gender_data = Application.objects.filter(
            induction_post__start_date__year=current_year
        ).values('gender').annotate(count=Count('id'))
        gender_labels = [item['gender'] or 'Unknown' for item in gender_data]
        gender_counts = [item['count'] for item in gender_data]
        context['gender_labels'] = gender_labels
        context['gender_counts'] = gender_counts

        # Chart 3: Radial Bar Progress - Day 1 and Day 2 Attendance Completion
        day_1_completion = [
            (Attendance.objects.filter(
                approve=True,
                induction_post=post,
                induction_post__induction_post_enrollments__day_1=True
            ).count() / max(1, InductionEnrollment.objects.filter(induction_post=post, admitted=True).count())) * 100
            for post in induction_posts
        ]
        day_2_completion = [
            (Attendance.objects.filter(
                approve=True,
                induction_post=post,
                induction_post__induction_post_enrollments__day_2=True
            ).count() / max(1, InductionEnrollment.objects.filter(induction_post=post, admitted=True).count())) * 100
            for post in induction_posts
        ]
        context['radial_labels'] = bar_labels
        context['day_1_completion'] = day_1_completion
        context['day_2_completion'] = day_2_completion

        # Chart 4: Line Chart - Applications Over Time
        applications = (
            Application.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                induction_post__start_date__year=current_year
            )
            .annotate(month_trunc=TruncMonth('created_at'))
            .values('month_trunc')
            .annotate(count=Count('id'))
            .order_by('month_trunc')
        )
        line_labels = []
        line_data = []
        current_date = start_date
        while current_date <= end_date:
            month_str = current_date.strftime('%b %Y')
            line_labels.append(month_str.split()[0])  # Show only month (e.g., "Jan")
            count = next(
                (item['count'] for item in applications if item['month_trunc'].strftime('%b %Y') == month_str),
                0
            )
            line_data.append(count)
            current_date += datetime.timedelta(days=30)

        context['line_labels'] = line_labels
        context['line_data'] = line_data
        context['current_year'] = current_year

        return context

class QuestionnaireDashboardView(TemplateView):
    template_name = 'administration/pages/induction/questionnaire_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        start_date = datetime.datetime(current_year, 1, 1)  # Naive datetime for current year
        end_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Filter questionnaires for applications in 2025
        questionnaires = Questionnaire.objects.filter(
            application__created_at__gte=start_date,
            application__created_at__lte=end_date
        )

        # Metrics
        context['total_questionnaires'] = questionnaires.count()
        context['internship_success_before'] = questionnaires.filter(internship_success_before=True).count()
        context['internship_before'] = questionnaires.filter(internship_before=True).count()
        context['pregnant'] = questionnaires.filter(pregnant=True).count()
        context['criminal_record'] = questionnaires.filter(criminal_record=True).count()
        context['qualification_completed'] = questionnaires.filter(qualification_completed=True).count()
        context['stipend_eligibility'] = questionnaires.filter(stipend_eligibility=True).count()
        context['willing_to_relocate_nelspruit'] = questionnaires.filter(willing_to_relocate_nelspruit=True).count()
        context['willing_to_relocate_barberton'] = questionnaires.filter(willing_to_relocate_barberton=True).count()
        context['willing_to_work_shifts'] = questionnaires.filter(willing_to_work_shifts=True).count()
        context['acceptance_statement'] = questionnaires.filter(acceptance_statement=True).count()

        # Chart 1: Bar Graph - True Responses for Boolean Fields
        bar_labels = [
            'Internship Success Before', 'Internship Before', 'Pregnant', 'Criminal Record',
            'Qualification Completed', 'Stipend Eligibility', 'Relocate Nelspruit',
            'Relocate Barberton', 'Work Shifts', 'Acceptance Statement'
        ]
        bar_data = [
            context['internship_success_before'], context['internship_before'], context['pregnant'],
            context['criminal_record'], context['qualification_completed'], context['stipend_eligibility'],
            context['willing_to_relocate_nelspruit'], context['willing_to_relocate_barberton'],
            context['willing_to_work_shifts'], context['acceptance_statement']
        ]
        context['bar_labels'] = bar_labels
        context['bar_data'] = bar_data

        # Chart 2: Pie Chart - Stipend Eligibility
        stipend_true = context['stipend_eligibility']
        stipend_false = context['total_questionnaires'] - stipend_true
        context['pie_labels'] = ['Eligible', 'Not Eligible']
        context['pie_data'] = [stipend_true, stipend_false]

        # Chart 3: Radial Bar Chart - Relocation and Shifts
        total = max(1, context['total_questionnaires'])
        radial_labels = ['Relocate Nelspruit', 'Relocate Barberton', 'Work Shifts']
        radial_data = [
            (context['willing_to_relocate_nelspruit'] / total) * 100,
            (context['willing_to_relocate_barberton'] / total) * 100,
            (context['willing_to_work_shifts'] / total) * 100
        ]
        context['radial_labels'] = radial_labels
        context['radial_data'] = radial_data

        context['current_year'] = current_year
        return context
           
class CompanyInvoiceListView(LoginRequiredMixin, ListView):
    model = HostComapany
    template_name = "administration/pages/invoices/company_list.html"
    context_object_name = "companies"

    def dispatch(self, request, *args, **kwargs):
        # Enforce admin-only access
        if not admin_required(self.request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Get the first day of the current month
        current_month = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Query companies with invoices for the current month, annotating total invoiced amount
        return HostComapany.objects.filter(
            monthly_invoices__month=current_month
        ).select_related("mentor").annotate(
            total_invoiced=Sum("monthly_invoices__total_amount")
        ).order_by("company_name")

    def get_context_data(self, **kwargs):
        # Add additional context for the template
        context = super().get_context_data(**kwargs)
        context["current_month"] = datetime.datetime.now().strftime("%B %Y")
        context["title"] = "Company Invoices"
        return context
    
class MonthlyInvoiceListView(LoginRequiredMixin, ListView):
    model = MonthlyCompanyInvoice
    template_name = "administration/pages/invoices/monthly_invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        company = get_object_or_404(HostComapany, id=self.kwargs["company_id"])
        return MonthlyCompanyInvoice.objects.filter(company=company).order_by("-month")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(HostComapany, id=self.kwargs["company_id"])
        return context

from decimal import Decimal
class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = MonthlyCompanyInvoice
    template_name = "administration/pages/invoices/invoice_detail.html"
    context_object_name = "invoice"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        # Get placed interns for the invoice month
        context["intern_invoices"] = InternInvoice.objects.filter(
            host_company=invoice.company,
            enrollment__status="PLACED",
            billing_month=invoice.month  # Updated to use billing_month
        )
        # Calculate total + VAT (15% as per South Africa)
        context["vat_rate"] = Decimal('0.15')  # Convert to Decimal
        context["vat_amount"] = invoice.total_amount * context["vat_rate"]
        context["total_with_vat"] = invoice.total_amount + context["vat_amount"]
        return context


def generate_invoices(request):
    current_month = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Step 1: Generate InternInvoice for all PLACED interns with a valid company
    placed_enrollments = IntershipEnrollment.objects.filter(status="PLACED").select_related("company")
    for enrollment in placed_enrollments:
        # Check if company exists and InternInvoice does not already exist for this enrollment
        if enrollment.company and not InternInvoice.objects.filter(enrollment=enrollment).exists():
            InternInvoice.objects.create(
                enrollment=enrollment,
                host_company=enrollment.company,
                amount=3000.00,  # Fixed amount
                expected_day_of_month=1,  # Default to 1st of the month
                status="PENDING",
                billing_month=current_month  # Set billing month to current month
            )

    # Step 2: Generate MonthlyCompanyInvoice for each company
    for company in HostComapany.objects.all():
        # Check for existing invoice for the current month
        if MonthlyCompanyInvoice.objects.filter(company=company, month=current_month).exists():
            continue
        
        # Get InternInvoices for PLACED interns for the company for the current billing month
        intern_invoices = InternInvoice.objects.filter(
            host_company=company,
            enrollment__status="PLACED",
            billing_month=current_month
        )
        total_amount = intern_invoices.aggregate(Sum("amount"))["amount__sum"] or 0
        
        if total_amount > 0:
            # Create MonthlyCompanyInvoice
            invoice = MonthlyCompanyInvoice.objects.create(
                company=company,
                month=current_month,
                total_amount=total_amount,
                status="PENDING",
                approval="PENDING"
            )
            # Send email notification (uncomment when email setup is confirmed)
            # send_invoice_email(invoice)
    
    return HttpResponse("Invoices generated successfully")

# def send_invoice_email(invoice):
#     subject = f"Invoice for {invoice.month.strftime('%B %Y')} - {invoice.company.company_name}"
#     mentor_email = invoice.company.mentor.email  # Assumes mentor is a User with email
#     intern_invoices = InternInvoice.objects.filter(
#         host_company=invoice.company,
#         enrollment__status="PLACED",
#         created__year=invoice.month.year,
#         created__month=invoice.month.month
#     )
#     vat_rate = 0.15
#     vat_amount = invoice.total_amount * vat_rate
#     total_with_vat = invoice.total_amount + vat_amount
#     context = {
#         "invoice": invoice,
#         "intern_invoices": intern_invoices,
#         "vat_rate": vat_rate,
#         "vat_amount": vat_amount,
#         "total_with_vat": total_with_vat,
#         "privacy_notice": "Your data is processed in accordance with POPIA. Contact POPIA@[domain].com for details."
#     }
#     html_message = render_to_string("email/invoice_summary.html", context)
#     send_mail(
#         subject,
#         "Please see your invoice summary attached.",
#         "no-reply@[domain].com",
#         [mentor_email],
#         html_message=html_message,
#         fail_silently=False
#     )

def terminate_intern(request, intern_id):
    if request.method == "POST":
        intern = get_object_or_404(IntershipEnrollment, id=intern_id)
        reason = request.POST.get("reason")

        # Update the status of the internship enrollment to TERMINATED and reset the stipend
        intern.status = IntershipEnrollment.InternshipStatus.TERMINATED
        intern.stipend = 0.00
        intern.save()

        # Create a new RecordAction instance for the termination
        RecordAction.objects.create(
            placing=False,
            company=intern.company,
            reason=reason,
            action=f"Contract terminated for intern {intern}",
            user=request.user if request.user.is_authenticated else None,
        )
        return JsonResponse({"message": "Internship terminated successfully"})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
def complet_intern(request, intern_id):
    if request.method == "POST":
        intern = get_object_or_404(IntershipEnrollment, id=intern_id)
        reason = request.POST.get("reason")

        # Update the status of the internship enrollment to TERMINATED and reset the stipend
        intern.status = IntershipEnrollment.InternshipStatus.COMPLETED
        intern.stipend = 0.00
        intern.save()

        # Create a new RecordAction instance for the termination
        RecordAction.objects.create(
            placing=False,
            company=intern.company,
            reason=reason,
            action=f"{intern} is completed",
            user=request.user if request.user.is_authenticated else None,
        )
        return JsonResponse({"message": "Internship Completed"})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
def default_intern(request, intern_id):
    if request.method == "POST":
        intern = get_object_or_404(IntershipEnrollment, id=intern_id)
        reason = request.POST.get("reason")

        # Update the status of the internship enrollment to TERMINATED and reset the stipend
        intern.status = IntershipEnrollment.InternshipStatus.DEFAULTED
        intern.stipend = 0.00
        intern.save()

        # Create a new RecordAction instance for the termination
        RecordAction.objects.create(
            placing=False,
            company=intern.company,
            reason=reason,
            action=f"{intern} is dafaulted",
            user=request.user if request.user.is_authenticated else None,
        )
        return JsonResponse({"message": "Internship Defaulted"})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({"message": "Invalid request method"}, status=400)

def intern_bypass_induction(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=application_id)
        intern = application.applicant
        induction_enrollment = intern.user_enrollments.all().first()
        reason = request.POST.get("reason")
        now = timezone.now()
        
        if application:
            induction_post = application.induction_post
            # InductionEnrollment.objects.create(
            #     intern_user = intern,
            #     induction_post = induction_post,
            #     admitted = True,
            #     acknowledged = True,
            #     day_1 = True,
            #     day_2 = True,
            #     pending_placement = True,
            #     bypassed = True,
            #     bypass_reason = reason
            # )
            if induction_enrollment:
                induction_enrollment.acknowledged = True
                induction_enrollment.day_1 = True
                induction_enrollment.day_2 = True
                induction_enrollment.pending_placement = True
                induction_enrollment.bypassed = True
                induction_enrollment.bypass_reason = reason
                induction_enrollment.save()

            # Adding attendance
            # First Attendance
            Attendance.objects.create(
                intern=intern, 
                induction_post=induction_post,
                time=now.time(),
                date=induction_post.start_date,
                approve=True,
                )
            # Second Attendance
            Attendance.objects.create(
                intern=intern, 
                induction_post=induction_post,
                time=now.time(),
                date=induction_post.end_date,
                approve=True,
                )

            IntershipEnrollment.objects.create(
                intern = intern,
                status = IntershipEnrollment.InternshipStatus.WAITING,
            )

        return JsonResponse({"message": "Induction Bypassed successfully"})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({"message": "Invalid request method"}, status=400)

class AttendedInternsView(DetailView):
    model = InductionPost
    template_name = "administration/pages/induction/view_attended_interns.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        induction_post = self.object
        attended_interns = Attendance.objects.filter(
            induction_post_id=induction_post.pk
        )
        context["attended_interns"] = attended_interns
        return context

    def post(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]
        # induction_post = get_object_or_404(InductionPost, id=post_id)
        approved_attendance_ids = [
            key.split("_")[-1]
            for key in request.POST.keys()
            if key.startswith("attendance_to_approve_")
        ]
        for approved_attendance_id in approved_attendance_ids:
            attendance = get_object_or_404(Attendance, id=approved_attendance_id)
            attendance.approve = True
            attendance.save()
        return redirect("view_attended_interns", post_id=post_id)

def intern_form(request, intern_id):
    internship_enrollment = get_object_or_404(IntershipEnrollment, intern__id=intern_id)
    intern = internship_enrollment.intern
    context = {
        'application': {
            'name': intern.first_name,
            'surname': intern.last_name
        }
    }
    return render(request, 'path/to/your/form_template.html', context)

# Web Posts 
class NewsLettersView(LoginRequiredMixin, CreateView):
    model = NewsLetters
    form_class = NewsLetterForm
    template_name = "administration/pages/posts/news/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        newsletters = NewsLetters.objects.all()
        print(newsletters)
        
        context['newsletters'] = newsletters
        return context

    def form_valid(self, form):
        # host_employer = HostEmployer.objects.get(pk=self.kwargs["pk"])
        # form.instance.mentor = host_employer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("news_letters")
    
# EVENT MANAGEMENT
from django.http import JsonResponse
from .models import Deliverable, Event, InternDeliverable, InternLogbook, LogbookTemplate, Qualification, WorkItem

class EventsView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = NewsLetterForm
    template_name = "administration/pages/events/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MARKETING, User.Role.HR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/events/index.html"]
        elif self.request.user.role == User.Role.MARKETING:
            return ["mar/pages/events/index.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/events/index.html"]
        return super().get_template_names()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = Event.objects.all()
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("events")

# Handle event data in JSON for the calendar
@csrf_exempt
def get_events(request):
    events = Event.objects.all()
    events_list = []
    for event in events:
        events_list.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_time.strftime("%Y-%m-%d")
        })
    return JsonResponse(events_list, safe=False)

@csrf_exempt
def get_event_by_date(request):
    date = request.GET.get('date')
    event = Event.objects.filter(start_time__date=date).first()
    try:

        if event:
            return JsonResponse({
                    "id": event.id,
                    "title": event.title,
                    "start": event.start_time.strftime("%Y-%m-%d")
                } ,safe=False)
        else:
            return JsonResponse({}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.views.decorators.http import require_GET
@require_GET
def events_by_date(request):
    # Get the selected date from the request parameters
    selected_date = request.GET.get('date', None)

    if selected_date:
        # Convert selected_date to a datetime object
        try:
            selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        # Filter events that have start_time on the selected date
        events = Event.objects.filter(
            start_time__date=selected_date_obj.date()
        )

        # Serialize the events into JSON format
        events_data = [
            {
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat(),
                'created_by': event.created_by.username
            } for event in events
        ]

        return JsonResponse(events_data, safe=False)
    else:
        return JsonResponse({'error': 'No date provided'}, status=400)

@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print(data)

            # Parse the start date from ISO 8601 format 'YYYY-MM-DDTHH:MM'
            start_date = data.get('start')
            if not start_date:
                return JsonResponse({'error': 'No start date provided'}, status=400)
            
            # Parse the string to a datetime object
            start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M')

            # Create the event
            event = Event.objects.create(
                title=data['title'],
                start_time=start_date_obj,
                end_time=start_date_obj,  # Assuming one-day events
                created_by=request.user
            )

            print*('Created event DATE', event.start_time)

            # Return a JSON response
            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.strftime("%Y-%m-%dT%H:%M")
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_event(request, event_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.get(id=event_id)
        event.title = data['title']
        event.start_time = data['start']
        event.end_time = data['start']
        event.save()
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.strftime("%Y-%m-%d")
        })
# ./EVENT MANAGEMENT

# LOGBOOK IMPPLEMENTATION
class QualificationsView(LoginRequiredMixin, CreateView):
    model = Qualification
    form_class = QualificationForm
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/qualifications/index.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/qualifications/index.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qualifictaions"] = Qualification.objects.all()
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user  # Get the current user
        if user.role == User.Role.ADMIN:
            return reverse_lazy("qualifications")  # Redirect to Admin qualifications page
        elif user.role == User.Role.COORDINATOR:
            return reverse_lazy("coordanation-qualifications")  # Redirect to Coordinator qualifications page
        else:
            return reverse_lazy("dashboard")  # Default fallback

class QualificationView(LoginRequiredMixin, CreateView):
    model = WorkItem
    form_class = WorkItemForm
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/qualifications/workitems/index.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/qualifications/workitems/index.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualification_id = self.kwargs.get("qualification_id")
        qualification = get_object_or_404(Qualification, id=qualification_id)
        context["qualification"] = qualification
        context["workItems"] = qualification.workitems.all()
        return context

    def form_valid(self, form):
                # Get the workitem_id from the URL kwargs
        qualification_id = self.kwargs.get("qualification_id")
        
        # Attach the work item to the deliverable before saving
        form.instance.qualification_id = qualification_id
        return super().form_valid(form)

    def get_success_url(self):
        qualification_id = self.kwargs.get("qualification_id")
        return reverse_lazy("qualification", kwargs={"qualification_id": qualification_id})
        
class AddSubjectView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "administration/pages/qualifications/add_subject_popup.html"
    success_url = reverse_lazy("close_popup")  # We'll define this view to close the window

    def form_valid(self, form):
        return super().form_valid(form)
    

class WorkItemView(LoginRequiredMixin, CreateView):
    model = Deliverable
    form_class = DeliverableForm
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/qualifications/workitems/deliverables/index.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/qualifications/workitems/deliverables/index.html"]
        return super().get_template_names()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workitem_id = self.kwargs.get("workitem_id")
        workitem = get_object_or_404(WorkItem, id=workitem_id)
        context["workitem"] = workitem
        context["deliverables"] = workitem.deliverables.all()
        return context

    def form_valid(self, form):
        # Get the workitem_id from the URL kwargs
        workitem_id = self.kwargs.get("workitem_id")        
        # Attach the work item to the deliverable before saving
        print(form.instance)
        form.instance.work_item_id = workitem_id
        return super().form_valid(form)

    def get_success_url(self):
        workitem_id = self.kwargs.get("workitem_id")
        return reverse_lazy("workitem", kwargs={"workitem_id": workitem_id})
      
from .forms import BulkAssignWorkItemsForm
from django.views.generic import FormView

class BulkAssignWorkItemsView(FormView):
    template_name = 'administration/pages/bulk_assign.html'
    form_class = BulkAssignWorkItemsForm
    success_url = reverse_lazy('bulk-assign')  # redirect to the same page

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        work_items = form.cleaned_data['work_items']
        work_items.update(subject=subject)
        messages.success(self.request, f"{work_items.count()} work items assigned to subject: {subject.name}")
        return super().form_valid(form)
from collections import OrderedDict
class CreateCompanyLogbookPreview(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"

    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/logbooks/steps/company-logbook-preview.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/logbooks/steps/company-logbook-preview.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logbook_template_id = self.kwargs.get("logbook_template_id")
        logbook_template = get_object_or_404(LogbookTemplate, pk=logbook_template_id)

        context["logbook_template"] = logbook_template
        context['total_credits'] = self.total_credits
        context['minimum_credits_required'] = self.minimum_credits_required
        context['percentage_pass'] = self.percentage_pass * 100

        all_template_deliverables = logbook_template.deliverables.all()
        context['deliverable_pts'] = self.total_credits / logbook_template.deliverables.count()

        # Group WorkItems by Subject for this Qualification
        grouped_subjects = OrderedDict()
        for work_item in logbook_template.qualification.workitems.select_related('subject').prefetch_related('deliverables'):
            if work_item.subject:
                subject_id = work_item.subject.id
                if subject_id not in grouped_subjects:
                    grouped_subjects[subject_id] = {
                        "subject": work_item.subject,
                        "work_items": []
                    }
                grouped_subjects[subject_id]["work_items"].append(work_item)

        context['grouped_subjects'] = grouped_subjects.values()
        return context

from django.db.models import Q as query

class DistributeLogbookToInterns(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/logbooks/assign-logbook-to-interns.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/logbooks/assign-logbook-to-interns.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get("company_id") 

        # Get the HostCompany object
        host_company = get_object_or_404(HostComapany, pk=company_id)

        # Get all enrollments associated with the company
        host_company_enrollments = host_company.internCompany.all()

        # Filter enrollments where the intern does not have an InternLogbook
        enrollments_without_logbooks = host_company_enrollments.filter(
            ~query(intern__logbooks__isnull=False)
        )

        # Add the filtered enrollments to the context
        context['host_company_enrollments'] = enrollments_without_logbooks

        return context


    def post(self, request, *args,  **kwargs):
        logbook_template_id = self.kwargs.get("logbook_template_id")
        print('logbook template id:', logbook_template_id)
        interns_to_assign_ids = request.POST.getlist('interns_to_assign')
        logbook_template = get_object_or_404(LogbookTemplate, pk=logbook_template_id)
        print('logbook template:', logbook_template)
        print('interns to assign:', interns_to_assign_ids)
        for intern_id in interns_to_assign_ids:
            intern_logbook = InternLogbook.objects.create(intern_id=intern_id, logbook_template=logbook_template)
            intern_logbook.save()
            print('Intern logbook created:', intern_logbook)
            deliverables = logbook_template.deliverables.all()
            for deliverable in deliverables:
                print('Deliverable:', deliverable)
                intern_deliverable = InternDeliverable.objects.create(intern_logbook=intern_logbook, deliverable=deliverable)
                intern_deliverable.save()
                print('Intern deliverable created:', intern_deliverable)

        return redirect(reverse_lazy('company-preview-logbook', kwargs={'logbook_template_id':logbook_template_id }))
        # return redirect(reverse_lazy('company-new-logbook-2', kwargs={'logbook_template_id':logbook_template_id}))

class InternLogbookView(LoginRequiredMixin, TemplateView):
    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["administration/pages/logbooks/intern/index.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["coordination/pages/logbooks/intern/index.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Intern Logbook"

        intern_id = self.kwargs.get("intern_id")
        intern = get_object_or_404(Intern, id=intern_id)
        print("Intern:", intern)
        intern_logbook = InternLogbook.objects.get(intern=intern)
        print("Intern logbook:", intern_logbook)
        context["intern"] = intern
        context["intern_logbook"] = intern_logbook
        context['total_credits'] = self.total_credits
        context['minimum_credits_required'] = self.minimum_credits_required
        context['percentage_pass'] = round(self.percentage_pass * 100, 2) 
        try:
            context['deliverable_pts'] = self.total_credits / intern_logbook.deliverables.count()
        except ZeroDivisionError:
            context['deliverable_pts'] = 0
        completed_deliverables_count = InternDeliverable.objects.filter(intern_logbook=intern_logbook, completed=True).count()
        context['completed_deliverables_count'] = completed_deliverables_count
        context['completed_percent'] = round((completed_deliverables_count / intern_logbook.deliverables.count()) * 100, 2)
        return context
    
class UpdateApprovalStatus(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse JSON body
            data = json.loads(request.body)
            logbook_deliverable_id = data.get("logbook_deliverable_id")
            action = data.get("action")

            # Perform your logic here
            print(f"Logbook deliverable ID: {logbook_deliverable_id}")
            print(f"Action: {action}")
            logbook_deliverable = get_object_or_404(InternDeliverable, pk=logbook_deliverable_id)
            if action == "approve":
                logbook_deliverable.approved = True
            elif action == "disapprove":
                logbook_deliverable.approved = False
                logbook_deliverable.completed = False

            logbook_deliverable.save()
            print(logbook_deliverable)
            # Respond with success
            return JsonResponse({"message": "Status updated successfully"})
        except Exception as e:
            # Handle errors
            return JsonResponse({"error": str(e)}, status=400)
# ./LOGBOOK IMPLEMENTATION

class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class PaymentListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = sum(p.amount for p in context['payments'])
        return context

class PaymentCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Payment
    fields = ['expense_type', 'amount', 'description']
    template_name = 'administration/pages/payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

class PaymentUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Payment
    fields = ['expense_type', 'amount', 'description']
    template_name = 'administration/pages/payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

class PaymentDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Payment
    template_name = 'admistration/payment_confirm_delete.html'
    success_url = reverse_lazy('administration/pages/payments/payment_list')

def reset_all_interns_to_waiting(request):
    enrollments = IntershipEnrollment.objects.all()
    for enrollment in enrollments:
        enrollment.status = IntershipEnrollment.InternshipStatus.WAITING
        enrollment.company = None
        enrollment.shift = None
        enrollment.contract = None
        enrollment.end_date = None
        enrollment.department = None
        enrollment.stipend = None
        # Keep intern, profile_picture, contrac_doc unchanged
        enrollment.save()

    messages.success(request, "All interns have been reset to 'WAITING' for placement.")
    return redirect('placed_internships')  # Change to the URL where you want to redirect

from hr.models import ScoringTask, StaffScoring, VehicleRequest, Vehicle,Staff, Department
from django.db.models import Count, Avg
from .models import HRGoal
from .forms import HRGoalForm

class HRDashboardView(TemplateView):
    template_name = 'administration/pages/hr_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        start_date = datetime.datetime(current_year, 1, 1)  # Naive datetime for DateField
        end_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Internship Enrollment Metrics
        context['total_interns'] = IntershipEnrollment.objects.count()
        context['placed_interns'] = IntershipEnrollment.objects.filter(status='PLACED').count()
        context['pending_logbook'] = IntershipEnrollment.objects.filter(status='PENDING_LOGBOOK').count()
        context['terminated_interns'] = IntershipEnrollment.objects.filter(status='TERMINATED').count()
        context['completed_interns'] = IntershipEnrollment.objects.filter(status='COMPLETED').count()

        # HR Goal and Progress
        hr_goal, created = HRGoal.objects.get_or_create(year=current_year, defaults={'target_interns_placed': 0})
        context['hr_goal'] = hr_goal
        context['target_interns_placed'] = hr_goal.target_interns_placed
        context['placement_progress'] = (
            (context['placed_interns'] / max(1, hr_goal.target_interns_placed)) * 100
            if hr_goal.target_interns_placed > 0 else 0
        )

        # Work Attendance Metrics (2025)
        attendance = WorkAttendance.objects.filter(date__year=current_year)
        context['total_attendance_records'] = attendance.count()
        context['present_days'] = attendance.filter(status='PRESENT', approved=True).count()
        context['absent_days'] = attendance.filter(status='ABSENT', approved=True).count()
        context['total_duty_hours'] = sum(
            att.duty_hours for att in attendance.filter(approved=True) if att.duty_hours
        ) or 0

        # Staff Metrics
        context['total_staff'] = Staff.objects.filter(status='Active').count()
        context['superior_performers'] = StaffScoring.objects.filter(
            performance_category='A', appraisal_date__year=current_year
        ).count()
        context['avg_performance_score'] = StaffScoring.objects.filter(
            appraisal_date__year=current_year
        ).aggregate(avg_score=Avg('percentage_score'))['avg_score'] or 0.00

        # Vehicle Metrics
        context['total_vehicles'] = Vehicle.objects.count()
        context['vehicles_in_use'] = Vehicle.objects.filter(status='BUSY').count()
        context['vehicles_in_maintenance'] = Vehicle.objects.filter(status='MAINTENANCE').count()

        # Vehicle Request Metrics (2025)
        vehicle_requests = VehicleRequest.objects.filter(date_requested__year=current_year)
        context['total_vehicle_requests'] = vehicle_requests.count()
        context['approved_vehicle_requests'] = vehicle_requests.filter(is_approved=True).count()

        # Chart 1: Bar Graph - Intern Status and Staff by Department
        intern_statuses = IntershipEnrollment.objects.values('status').annotate(count=Count('id'))
        bar_labels = [item['status'] for item in intern_statuses]
        intern_status_data = [item['count'] for item in intern_statuses]
        departments = Department.objects.values('name').annotate(count=Count('staff_members'))
        bar_labels.extend([item['name'] for item in departments])
        staff_department_data = [item['count'] for item in departments]
        context['bar_labels'] = bar_labels
        context['intern_status_data'] = intern_status_data + [0] * len(departments)
        context['staff_department_data'] = [0] * len(intern_statuses) + staff_department_data

        # Chart 2: Pie Chart - Vehicle Status Distribution
        vehicle_statuses = Vehicle.objects.values('status').annotate(count=Count('id'))
        context['pie_labels'] = [item['status'] for item in vehicle_statuses]
        context['pie_data'] = [item['count'] for item in vehicle_statuses]

        # Chart 3: Radial Bar Chart - Attendance Percentages
        total_attendance = max(1, context['total_attendance_records'])
        context['radial_attendance_labels'] = ['Present', 'Absent']
        context['radial_attendance_data'] = [
            (context['present_days'] / total_attendance) * 100,
            (context['absent_days'] / total_attendance) * 100
        ]

        # Chart 4: Radial Bar Chart - Intern Placement Progress
        context['radial_progress_labels'] = ['Placement Progress']
        context['radial_progress_data'] = [context['placement_progress']]

        # Chart 5: Line Chart - Vehicle Requests Over Time
        requests = (
            VehicleRequest.objects.filter(
                date_requested__gte=start_date,
                date_requested__lte=end_date
            )
            .annotate(month_trunc=TruncMonth('date_requested'))
            .values('month_trunc')
            .annotate(count=Count('id'))
            .order_by('month_trunc')
        )
        line_labels = []
        line_data = []
        current_date = start_date
        while current_date <= end_date:
            month_str = current_date.strftime('%b %Y')
            line_labels.append(month_str.split()[0])
            count = next(
                (item['count'] for item in requests if item['month_trunc'].strftime('%b %Y') == month_str),
                0
            )
            line_data.append(count)
            current_date += datetime.timedelta(days=30)

        context['line_labels'] = line_labels
        context['line_data'] = line_data
        context['current_year'] = current_year
        context['form'] = HRGoalForm(instance=hr_goal)

        return context

    def post(self, request, *args, **kwargs):
        current_year = timezone.now().year
        hr_goal, created = HRGoal.objects.get_or_create(year=current_year)
        form = HRGoalForm(request.POST, instance=hr_goal)
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)