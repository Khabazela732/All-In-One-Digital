from django.shortcuts import render
import json
from web.forms import NewsLetterForm
from web.models import NewsLetters
from authentication.models import HostEmployerProfile, Intern, User
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView,TemplateView
from django.urls import reverse_lazy
from .models import UserActivity, Campaign, SuccessStory, Event, Magazine
from administration.models import Application
from django.db.models import Count
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
import datetime
from django.views.decorators.csrf import csrf_exempt
from .forms import ConsentFormForm, MagazineForm,SuccessStoryForm, CampaignForm
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "mar/pages/home/index.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletters_count"] = NewsLetters.objects.count()
        context["campaigns_count"] = Campaign.objects.count()
        context["applications_received"] = Application.objects.count()
        context["events_count"] = Event.objects.count()
        context["success_stories_count"] = SuccessStory.objects.count()
        context["user_activity"] = UserActivity.objects.order_by("-timestamp")[:10]
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
    
class NewsLettersView(LoginRequiredMixin, CreateView):
    model = NewsLetters
    form_class = NewsLetterForm
    template_name = "mar/pages/posts/news/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
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

class UserActivityView(LoginRequiredMixin, ListView):
    model = UserActivity
    template_name = "mar/pages/activity.html"
    login_url = "/auth/login/"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

class CampaignListView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "mar/pages/campaign/list.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaigns"] = Campaign.objects.all().order_by("-start_date")
        return context

    def get_success_url(self):
        return reverse_lazy("campaigns")

class SuccessStoryView(LoginRequiredMixin, CreateView):
    model = SuccessStory
    form_class = SuccessStoryForm  # If using default fields, you can also use `fields = [...]`
    template_name = "mar/pages/success_stories.html"
    login_url = "/auth/login/"  # Ensure users are redirected to login if not authenticated
    success_url = reverse_lazy("success_stories")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stories'] = SuccessStory.objects.all().order_by("-created")
        return context

class SuccessStoryCreateView(LoginRequiredMixin, CreateView):
    model = SuccessStory
    fields = ["title", "content", "image"]
    template_name = "mar/pages/createsucc.html"
    success_url = reverse_lazy("success_stories")

class EventView(LoginRequiredMixin, CreateView):
    model = Event
    fields = ['name', 'description', 'date', 'location']
    template_name = "mar/pages/events.html"
    success_url = reverse_lazy("events")

class MagazineListView(LoginRequiredMixin, CreateView):
    model = Magazine
    form_class = MagazineForm
    template_name = "mar/pages/magazine/list.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["magazines"] = Magazine.objects.exclude(id__isnull=True).order_by("-issue_date")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.refresh_from_db()  # Ensure object is updated from DB
        messages.success(self.request, "Magazine uploaded successfully.")
        return response

    def get_success_url(self):
        return reverse_lazy("magazines")

# EVENT MANAGEMENT
from django.http import JsonResponse
from .models import Event

class EventsView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = NewsLetterForm
    template_name = "mar/pages/events/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MARKETING:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

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

class ConsentView(TemplateView):
    template_name = "intern/pages/induction/cosentform.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Recruitment"
        context["form"] = ConsentFormForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ConsentFormForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("success_page_name")  # Replace with your success URL name
        else:
            return render(request, self.template_name, {
                "form": form,
                "title": "Recruitment"
            })