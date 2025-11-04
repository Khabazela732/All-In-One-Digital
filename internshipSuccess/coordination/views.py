import json
from django.contrib.auth.mixins import LoginRequiredMixin
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
    Hearing
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
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
from .models import MonthlySiteVisit, CaseLog
from .forms import MonthlySiteVisitForm
from administration.forms import (
    ApplicationStatusForm,
    InductionPostForm,
    UpdatePasscodeForm,
    HostEmployerForm,
    
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
from administration.forms import DeliverableForm, QualificationForm, QuestionnaireForm, UploadFileForm, WorkItemForm
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.forms import formset_factory
from intern.models import Attendance
from authentication.models import HostEmployerProfile, Intern, User
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from administration.decorators import *
from hostCampany.models import HostEmployer, HostComapany, Report, Rotation
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.db.models import Count
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template import loader

# Create your views here.
class EventsView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = NewsLetterForm
    template_name = "coordination/pages/events/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = Event.objects.all()
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("co-events")

# Handle event data in JSON for the calendar
class RegisterHostEmployerView(LoginRequiredMixin, CreateView):
    model = HostEmployer
    form_class = HostEmployerForm
    template_name = "coordination/pages/hostEmployer/register_host_employer.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Host Employer"
        context["user"] = self.request.user
        return context

    def get_success_url(self):
        if self.request.POST.get("co_register_company"):
            return reverse_lazy("co_register_host_company", kwargs={"pk": self.object.pk})
        return reverse_lazy("register_host_company-success")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = HostEmployer.base_role  # Ensure the role is set to HOST_EMPLOYER
        user.save()
        # HostEmployerProfile.objects.create(user=user)  # Create associated profile
        return super().form_valid(form)
    
class RegisterHostCompanyView(LoginRequiredMixin, CreateView):
    model = HostComapany
    form_class = HostComapanyForm
    template_name = "coordination/pages/hostEmployer/register_host_company.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        host_employer = HostEmployer.objects.get(pk=self.kwargs["pk"])
        form.instance.mentor = host_employer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("register_host_company-success")
    
class ViewCompanieOnProfileView(LoginRequiredMixin, TemplateView):
    template_name = "coordination/pages/companies/company-view-on-emp-profile.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
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
def waiting_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.WAITING
    )
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "coordination/pages/interns/waiting_internships.html", context
    )
def placed_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.PLACED
    )
    context = {
        "internships": internships,
        "user": request.user,
    }
    return render(
        request, "coordination/pages/interns/placed_internships.html", context
    )

def terminated_internships(request):
    internships = IntershipEnrollment.objects.filter(
        status=IntershipEnrollment.InternshipStatus.TERMINATED
    )
    applications = Application.objects.all()
    internships_and_applications = zip(internships, applications)
    context = {
        "internships_and_applications": internships_and_applications,
        "user": request.user,
    }
    return render(
        request, "coordination/pages/interns/terminated_internships.html", context
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
        request, "coordination/pages/interns/terminated_internships.html", context
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
        request, "coordination/pages/interns/completed_internships.html", context
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
        request, "coordination/pages/interns/defaulted_internships.html", context
    )
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
from django.views.generic import ListView
class RotationListView(LoginRequiredMixin, ListView):
    model = Rotation
    template_name = "coordination/pages/rotation/list.html"
    context_object_name = "rotations"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            messages.error(request, "Unauthorized")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    
class ViewCompanieOnProfileView(LoginRequiredMixin, TemplateView):
    template_name = "coordination/pages/hostEmployer/company-view-on-emp-profile.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.COORDINATOR:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_employer = self.request.user
        company = get_object_or_404(HostComapany, pk=int(kwargs["company_id"]))


        context["company"] = company
        context['logbook_templates'] = company.logbook_templates.all()
        return context

class SiteVisitListView(LoginRequiredMixin, ListView):
    model = MonthlySiteVisit
    template_name = "coordination/pages/site_visit/list.html"
    context_object_name = "site_visits"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "COORDINATOR":
            messages.error(request, "Unauthorized")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
        
class CreateMonthlySiteVisitView(LoginRequiredMixin, CreateView):
    model = MonthlySiteVisit
    form_class = MonthlySiteVisitForm
    template_name = "coordination/pages/site_visit/create.html"
    success_url = reverse_lazy("site-visit-list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "COORDINATOR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

class AllCaseLogsView(LoginRequiredMixin, ListView):
    model = CaseLog
    template_name = "coordination/pages/case_log/list.html"
    context_object_name = "cases"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "COORDINATOR":
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

# Step 1: List interns who have rotation plans
class RotationReportInternListView(LoginRequiredMixin, ListView):
    template_name = "coordination/pages/rotation/rotation_report_intern_list.html"
    context_object_name = "interns"

    def get_queryset(self):
        # Only interns with at least one rotation
        return Intern.objects.filter(rotations__isnull=False).distinct()


# Step 2: Show rotation report for a selected intern
class RotationReportDetailView(LoginRequiredMixin, TemplateView):
    template_name = "coordination/pages/rotation/rotation_report_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intern_id = self.kwargs.get("intern_id")
        intern = get_object_or_404(Intern, id=intern_id)
        context['intern'] = intern

        rotations = Rotation.objects.filter(intern=intern).select_related(
            'department', 'work_item'
        ).prefetch_related('deliverables')

        rotation_data = []
        for rotation in rotations:
            for deliverable in rotation.deliverables.all():
                rotation_data.append({
                    "field": rotation.work_item.subject.name if rotation.work_item else "-",
                    "key_area": rotation.work_item.name if rotation.work_item else "-",
                    "department": rotation.department.name,
                    "poe": deliverable.deliverable.deliverable.name,
                    "start_date": rotation.start_date,
                    "end_date": rotation.end_date
                })

        context['rotation_data'] = rotation_data
        return context