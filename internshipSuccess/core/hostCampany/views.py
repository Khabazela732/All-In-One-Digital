from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.base import TemplateView
from intern.models import WorkAttendance
from .forms import LogbookTemplateForm, ReportForm
from administration.forms import HostEmployerFormForProfile
from hostCampany.forms import HostComapanyForm
from .models import (
    HostComapany,
    HostEmployer,
    Department,
    Rotation
)
from administration.models import Deliverable, InternDeliverable, InternLogbook, IntershipEnrollment, Intern, Application, LogbookTemplate, LogbookTemplateDeliverable, Shift, User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Count
from marketing.models import Campaign, SuccessStory, Magazine
from web.models import NewsLetters


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_employer = HostComapany.objects.filter(mentor=user).first()
            if host_employer:
                interns = IntershipEnrollment.objects.filter(company=host_employer)
                context["interns"] = interns
                context["host_employer"] = host_employer
                context["magazines"] = Magazine.objects.order_by("-issue_date")[:5]
                context["success_stories"] = SuccessStory.objects.order_by("-created")[:5]
                context["newsletters"] = NewsLetters.objects.order_by("-created")[:5]
                context["campaigns"] = Campaign.objects.order_by("-created")[:5]
        return context


class ActiveInternListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/active_interns.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_employer = HostComapany.objects.filter(mentor=user).first()
            if host_employer:
                interns = IntershipEnrollment.objects.filter(company=host_employer, status="PLACED")
                context["interns"] = interns
                context["host_employer"] = host_employer
        return context
    
class TerminatedInternListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/teminated_interns.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_employer = HostComapany.objects.filter(mentor=user).first()
            if host_employer:
                interns = IntershipEnrollment.objects.filter(company=host_employer, status="TERMINATED")
                context["interns"] = interns
                context["host_employer"] = host_employer
        return context


class InternProfileViewHost(TemplateView):
    template_name = "pages/internprofile_host.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to authenticated host employer users
        if not request.user.is_authenticated or request.user.role != User.Role.HOST_EMPLOYER:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intern_id = self.kwargs.get("intern_id")
        
        # Retrieve the intern based on the ID
        intern = Intern.objects.get(id=intern_id)
        context["intern"] = intern

        # Retrieve the first user enrollment for induction
        induction_enrollment = intern.user_enrollments.all().first()
        context["induction_enrollment"] = induction_enrollment

        # Retrieve the application and host employer data
        application = intern.user_applications.all().first()
        context["application"] = application
        
        # Get the host employer associated with the logged-in user
        host_employer = HostComapany.objects.filter(mentor=self.request.user).first()
        context["host_employer"] = host_employer
        
        # Retrieve departments related to the host employer, if available
        departments = Department.objects.filter(Company=host_employer) if host_employer else []
        context["departments"] = departments

        shifts = Shift.objects.filter(company=host_employer) if host_employer else []
        context["shifts"] = shifts

        reports = intern.reports.all()  # Assuming `related_name="reports"` in the `InternReport` model
        context["reports"] = reports
        # Get internship enrollment data if it exists
        context["report_form"] = ReportForm()
        try:
            internship_enrollment = IntershipEnrollment.objects.get(intern=intern)
            context["internship_enrollment"] = internship_enrollment
        except IntershipEnrollment.DoesNotExist:
            context["internship_enrollment"] = None

        return context
    def post(self, request, *args, **kwargs):
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.host_employer = request.user
            report.intern_id = self.kwargs.get("intern_id")
            report.save()
            return redirect("success_page")  # Replace with actual success URL
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.host_employer = request.user
            report.intern_id = self.kwargs.get("intern_id")
            report.save()
            return redirect("report_success")  # Replace with actual success URL
        return self.render_to_response(self.get_context_data(form=form))
class ReportSuccessView(TemplateView):
    template_name = "pages/report_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get intern_id from query parameters or other logic
        intern_id = self.request.GET.get("intern_id")
        context["intern_id"] = intern_id  # Pass intern_id to the template
        return context
class DepartmentsListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/department_list.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_employer = HostComapany.objects.filter(mentor=user).first()
            if host_employer:
                departments = Department.objects.filter(Company=host_employer)
                context["departments"] = departments
                context["host_employer"] = host_employer
        return context


from django.http import JsonResponse


def add_department(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            user = request.user
            if user.is_authenticated and user.role == "HOST_EMPLOYER":
                host_employer = HostEmployer.objects.filter(mentor=user).first()
                if host_employer:
                    department = Department.objects.create(
                        name=name, Company=host_employer
                    )
                    # Return a JSON response indicating success
                    return JsonResponse({"success": True})
    # Return a JSON response indicating failure
    return JsonResponse({"success": False})


def delete_department(request, department_id):
    if request.method == "DELETE":
        department = get_object_or_404(Department, pk=department_id)
        department.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def edit_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == "POST":
        new_name = request.POST.get("new_name")
        if new_name:
            department.name = new_name
            department.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})


class ShiftsListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/shifts_list.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_employer = HostComapany.objects.filter(mentor=user).first()
            if host_employer:
                shifts = Shift.objects.filter(company=host_employer)
                context["shifts"] = shifts
                context["host_employer"] = host_employer
        return context


def add_shift(request):
    if request.method == "POST":
        name = request.POST.get("name")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        if name:
            user = request.user
            if user.is_authenticated and user.role == "HOST_EMPLOYER":
                host_company = HostComapany.objects.filter(mentor=user).first()
                if host_company:
                    # Parse the time strings to datetime objects and extract the time part
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()
                    shift = Shift.objects.create(
                        name=name,
                        start_time=start_time,
                        end_time=end_time,
                        company=host_company,
                    )
                    return JsonResponse({"success": True})
                else:
                    return JsonResponse({"success": False, "error": "Host company not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})



def edit_shift(request, shift_id):
    if request.method == "POST":
        name = request.POST.get("name")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        # Retrieve the Shift instance
        shift = get_object_or_404(Shift, pk=shift_id)

        if name:
            # Update the shift attributes
            shift.name = name

            # Parse the time strings to time objects and update start_time and end_time
            shift.start_time = datetime.strptime(start_time_str, "%H:%M").time()
            shift.end_time = datetime.strptime(end_time_str, "%H:%M").time()

            # Save the changes
            shift.save()

            # Return a JSON response indicating success
            return JsonResponse({"success": True})
    # Return a JSON response indicating failure
    return JsonResponse({"success": False})


def delete_shift(request, shift_id):
    if request.method == "DELETE":
        shift = get_object_or_404(Shift, pk=shift_id)
        shift.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def change_shift(request, enrollment_id):
    # Ensure the user is a host employer
    user = request.user
    if not user.is_authenticated or user.role != "HOST_EMPLOYER":
        messages.error(request, "You are not authorized to make this change.")
        return redirect("home")

    internship_enrollment = get_object_or_404(IntershipEnrollment, id=enrollment_id)
    intern_id = internship_enrollment.intern.id  # Get the intern's ID for redirection

    if request.method == "POST":
        # Get the selected shift from the form
        shift_id = request.POST.get("shift")
        if shift_id:
            shift = get_object_or_404(Shift, id=shift_id)
            internship_enrollment.shift = shift  # Assuming there's a `shift` field
            internship_enrollment.save()
            messages.success(request, "Shift updated successfully.")
        else:
            messages.error(request, "Please select a valid Shift.")

    # Redirect to the intern's profile view
    return redirect("active-interns")


# Companies
class CompaniesListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/companies/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Log Books"
        host_employer = self.request.user
        companies = host_employer.mentor_comapanies.all()
        context["companies"] = companies
        return context


class ViewCompanieListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/companies/company-view.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_employer = self.request.user
        company = get_object_or_404(HostComapany, pk=int(kwargs["company_id"]))

        # Annotate logbooks with the number of interns assigned to each
        logbooks = company.logbook_templates.annotate(
            num_interns=Count("logbooks")
        )

        for log in logbooks:
            print(log.num_interns)

        context["company"] = company
        context["logbooks"] = logbooks
        return context

class ViewCompanieOnProfileView(LoginRequiredMixin, TemplateView):
    template_name = "pages/companies/company-view-on-emp-profile.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_employer = self.request.user
        company = get_object_or_404(HostComapany, pk=int(kwargs["company_id"]))
        placed_interns = IntershipEnrollment.objects.filter(company=company).select_related('intern')

        context["placed_interns"]=placed_interns
        context["company"] = company
        context['logbook_templates'] = company.logbook_templates.all()
        return context
    
class CreateCompanyLogbookStepOne(LoginRequiredMixin, CreateView):
    model = LogbookTemplate
    form_class = LogbookTemplateForm    
    template_name = "pages/logbooks/steps/company-logbook-creation.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get("company_id") 
        print(company_id) 
        company = get_object_or_404(HostComapany, pk=company_id)
        
        context["company"] = company
        return context
    
    def form_valid(self, form):
        # Attach the company to the logbook before saving
        company_id = self.kwargs.get("company_id")
        company = get_object_or_404(HostComapany, pk=company_id)
        form.instance.company = company

        # Save the logbook and store the logbook_template_id
        response = super().form_valid(form)
        self.logbook_template_id = form.instance.id  # Store the ID for use in get_success_url
        return response

    def get_success_url(self):
        return reverse_lazy("company-new-logbook-2", kwargs={"logbook_template_id": self.object.id})  
    
class CreateCompanyLogbookStepTwo(LoginRequiredMixin, TemplateView):   
    template_name = "pages/logbooks/steps/company-logbook-creation-step2.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logbook_template_id = self.kwargs.get("logbook_template_id") 
        print(logbook_template_id)
        logbook_template = get_object_or_404(LogbookTemplate, pk=logbook_template_id)
        context["logbook_template"] = logbook_template
        print(logbook_template.qualification)
        context['workitems'] = logbook_template.qualification.workitems
        return context
    
class DeliverableSelectionForLogbookTemplate(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/steps/company-logbook-creation-step2.html"
    login_url = "/auth/login/"
    def post(self, request, *args,  **kwargs):
        logbook_template_id = self.kwargs.get("logbook_template_id")
        selected_deliverable_ids = request.POST.getlist('deliverables')
        
        for deliverable_id in selected_deliverable_ids:
            logbook_template=get_object_or_404(LogbookTemplate, pk=logbook_template_id)
            deliverable=get_object_or_404(Deliverable, pk=deliverable_id)
            LogbookTemplateDeliverable.objects.create(
                logbook_template=logbook_template,
                deliverable=deliverable
            )
            # LogbookTemplateDeliverable.objects.create(logbook_template=get_object_or_404()

        return redirect(reverse_lazy('company-preview-logbook', kwargs={'logbook_template_id':logbook_template_id}))
        # return redirect(reverse_lazy('company-new-logbook-2', kwargs={'logbook_template_id':logbook_template_id}))
     
class CreateCompanyLogbookPreview(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/steps/company-logbook-preview.html"
    login_url = "/auth/login/"

    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logbook_template_id = self.kwargs.get("logbook_template_id")  # Get logbook_id from URL parameter
        logbook_template = get_object_or_404(LogbookTemplate, pk=logbook_template_id)
        context["logbook_template"] = logbook_template

        context['total_credits'] = self.total_credits
        context['minimum_credits_required'] = self.minimum_credits_required
        context['percentage_pass'] = self.percentage_pass * 100

        all_template_deliverables =  logbook_template.deliverables.all()
        context['deliverable_pts'] = self.total_credits / logbook_template.deliverables.count()
        return context


class CreateHostCompanyView(LoginRequiredMixin, CreateView):
    model = HostComapany
    form_class = HostComapanyForm
    template_name = "pages/companies/create_company.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Host employer"
        context["user"] = self.request.user
        return context

    def get_success_url(self):
        return reverse_lazy("companies-create-success")

    def form_valid(self, form):
        hostemployer = self.request.user
        form.instance.mentor = hostemployer
        return super().form_valid(form)


class CreateHostCompanySuccessView(LoginRequiredMixin, TemplateView):
    template_name = "pages/companies/create_company_success.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Log Books"
        # logBooks = HostComapany.company_logbooks.objects.all()
        # print(logBooks)
        return context


# END COMAPANIES


class LogBooksListView(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in (
            User.Role.HOST_EMPLOYER,
            User.Role.ADMIN,
        ):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Log Books"
        # logBooks = HostComapany.company_logbooks.objects.all()
        # print(logBooks)
        return context

class HostEmployerProfile(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.HR, User.Role.HOST_EMPLOYER,User.Role.COORDINATOR]:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """Return different templates based on user role."""
        if self.request.user.role == User.Role.ADMIN:
            return ["pages/hostemployer.html"]
        elif self.request.user.role == User.Role.HR:
            return ["hr/pages/host/hostemployer.html"]
        elif self.request.user.role == User.Role.COORDINATOR:
            return ["pages/hostemployerco.html"]
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_employer_id = self.kwargs.get("hostemp_id")
        host_employer = get_object_or_404(HostEmployer, id=int(host_employer_id))
        context["host_employer"] = host_employer
        context["host_companies"] = host_employer.mentor_comapanies.all()
        context["title"] = (
            f"Host Employer Profile - {host_employer.first_name} {host_employer.last_name}"
        )
        # Initialize the form
        context["form"] = HostEmployerFormForProfile(instance=host_employer)
        return context

    def post(self, request, *args, **kwargs):
        form = HostEmployerFormForProfile(
            request.POST, instance=self.get_host_employer()
        )
        if form.is_valid():
            form.save()
            # Redirect or show success message
        else:
            # Handle invalid form
            pass
        return render(request, self.template_name, {"form": form})

    def get_host_employer(self):
        host_employer_id = self.kwargs.get("hostemp_id")
        return get_object_or_404(HostEmployer, id=int(host_employer_id))


def attendance_list(request):
    user = request.user
    if user.is_authenticated and user.role == "HOST_EMPLOYER":
        host_employer = HostComapany.objects.filter(mentor=user).first()
        if host_employer:
            # Get departments related to this host employer's company
            departments = Department.objects.filter(Company=host_employer)

            # Get the date from the request's query parameters
            date_str = request.GET.get("date")
            department_id = request.GET.get("department")
            
            # Filter attendances by company
            attendances = WorkAttendance.objects.filter(intern__company=host_employer)
            
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
                "host_employer": host_employer,
                "departments": departments,
                "selected_date": date_str,
                "selected_department": department_id,
            }
            return render(request, "pages/attendance/attendance_list.html", context)
    
    messages.error(request, "You are not authorized to view this page.")
    return redirect("home")

def change_department(request, enrollment_id):
    # Ensure the user is a host employer
    user = request.user
    if not user.is_authenticated or user.role != "HOST_EMPLOYER":
        messages.error(request, "You are not authorized to make this change.")
        return redirect("home")

    internship_enrollment = get_object_or_404(IntershipEnrollment, id=enrollment_id)
    intern_id = internship_enrollment.intern.id  # Get the intern's ID for redirection

    if request.method == "POST":
        # Get the selected department from the form
        department_id = request.POST.get("department")
        if department_id:
            department = get_object_or_404(Department, id=department_id)
            internship_enrollment.department = department
            internship_enrollment.save()
            messages.success(request, "Department updated successfully.")
        else:
            messages.error(request, "Please select a valid department.")

    # Redirect to the intern's profile view
    return redirect("active-interns")

from django.views.generic import ListView
class RotationListView(LoginRequiredMixin, ListView):
    model = Rotation
    template_name = "pages/rotation/list.html"
    context_object_name = "rotations"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HOST_EMPLOYER":
            messages.error(request, "Unauthorized")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        host_company = get_object_or_404(HostComapany, mentor=user)

        # Filter rotations where the intern is placed in this host company
        return Rotation.objects.filter(
            intern__company=host_company,
            intern__status=IntershipEnrollment.InternshipStatus.PLACED
        )
    
class CreateRotationView(LoginRequiredMixin, CreateView):
    model = Rotation
    fields = ['intern', 'qualification', 'department', 'start_date', 'end_date']
    template_name = "pages/rotation/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_authenticated and user.role == "HOST_EMPLOYER":
            host_company = HostComapany.objects.filter(mentor=user).first()
            if host_company:
                enrollments = IntershipEnrollment.objects.filter(company=host_company, status="PLACED")
                context['enrollments'] = enrollments
                context['departments'] = Department.objects.filter(Company=host_company)
        return context

    def form_valid(self, form):
        user = self.request.user
        host_company = HostComapany.objects.filter(mentor=user).first()
        if not host_company:
            messages.error(self.request, "You are not authorized to create this rotation.")
            return redirect("home")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("rotation-list")


def approve_attendance(request, attendance_id):
    attendance = get_object_or_404(WorkAttendance, id=attendance_id)
    if request.user == attendance.intern.company.mentor:
        attendance.approved = True
        attendance.save()
        messages.success(request, "Attendance approved.")
    else:
        messages.error(request, "You are not authorized to approve this attendance.")
    return redirect("attendance_list")

class DistributeLogbookToInterns(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/steps/company-logbook-creation-step2.html"
    login_url = "/auth/login/"
    def post(self, request, *args,  **kwargs):
        logbook_template_id = self.kwargs.get("logbook_template_id")
        selected_deliverable_ids = request.POST.getlist('deliverables')
        
        for deliverable_id in selected_deliverable_ids:
            logbook_template=get_object_or_404(LogbookTemplate, pk=logbook_template_id)
            deliverable=get_object_or_404(Deliverable, pk=deliverable_id)
            LogbookTemplateDeliverable.objects.create(
                logbook_template=logbook_template,
                deliverable=deliverable
            )
            # LogbookTemplateDeliverable.objects.create(logbook_template=get_object_or_404()

        return redirect(reverse_lazy('company-preview-logbook', kwargs={'logbook_template_id':logbook_template_id}))
        # return redirect(reverse_lazy('company-new-logbook-2', kwargs={'logbook_template_id':logbook_template_id}))

class InternLogbookOnHostEmployerView(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/intern/index.html"
    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role is User.Role.HOST_EMPLOYER:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Intern Logbook"

        intern_logbook_id = self.kwargs.get("intern_logbook_id")
        intern_logbook = InternLogbook.objects.get(pk=intern_logbook_id)
        print("Intern logbook:", intern_logbook)
        
        context["intern_logbook"] = intern_logbook
        context['total_credits'] = self.total_credits
        context['minimum_credits_required'] = self.minimum_credits_required
        context['percentage_pass'] = self.percentage_pass * 100
        try:
            context['deliverable_pts'] = self.total_credits / intern_logbook.deliverables.count()
        except ZeroDivisionError:
            context['deliverable_pts'] = 0
        completed_deliverables_count = InternDeliverable.objects.filter(intern_logbook=intern_logbook, completed=True).count()
        context['completed_deliverables_count'] = completed_deliverables_count
        context['completed_percent'] = (completed_deliverables_count / intern_logbook.deliverables.count()) * 100
        return context
    
class CompanyLogbookPreview(LoginRequiredMixin, TemplateView):
    template_name = "pages/logbooks/company-logbook-preview.html"
    login_url = "/auth/login/"

    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.HOST_EMPLOYER:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logbook_template_id = self.kwargs.get("logbook_template_id")  # Get logbook_id from URL parameter
        logbook_template = get_object_or_404(LogbookTemplate, pk=logbook_template_id)
        
        context['intern_logbook_count'] = logbook_template.logbooks.all().count()
        context["logbook_template"] = logbook_template
        context["intern_logbooks"] = logbook_template.logbooks
        context['total_credits'] = self.total_credits
        context['minimum_credits_required'] = self.minimum_credits_required
        context['percentage_pass'] = self.percentage_pass * 100
        
        all_template_deliverables =  logbook_template.deliverables.all()
        context['deliverable_pts'] = self.total_credits / logbook_template.deliverables.count()
        return context