from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from administration.forms import ApplicationForm, QuestionnaireAffidavitForm, QuestionnaireForm
from administration.models import InductionPost, Application, Questionnaire
from django.shortcuts import get_object_or_404
from web.models import NewsLetters
from marketing.models import Magazine

class HomeView(TemplateView):
    template_name = "web/pages/home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        context["newsletters"] = NewsLetters.objects.all().order_by("-created")[:5]  # limit to latest 5
        context["magazines"] = Magazine.objects.all().order_by("-issue_date")[:5]
        return context
    
class AboutView(TemplateView):
    template_name = "web/pages/about/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "About Us" 
        return context
    
class ServicesView(TemplateView):
    template_name = "web/pages/services/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Our Services" 
        return context
    
class NewsView(TemplateView):
    template_name = "web/pages/news/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "News and Updates" 
        newsletters =  NewsLetters.objects.all()
        context['newsletters'] = newsletters
        return context

class ContactView(TemplateView):
    template_name = "web/pages/contact/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Contact Us" 
        return context
    
class MarketingView(TemplateView):
    template_name = "web/pages/marketing/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Marketing" 
        return context    

from django.views.generic import TemplateView
from hr.models import Staff, Department

class TeamView(TemplateView):
    template_name = "web/pages/team/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Team"

        # Only active staff
        active_staff = Staff.objects.filter(status="Active").select_related("department")

        # Role priority
        role_priority = {
            "CEO": 1,
            "Operation Manager": 2,
            "Office Manager": 3,
            "Human Resource": 4
        }

        # Group staff by department
        staff_by_department = {}
        for staff in active_staff:
            dept_name = staff.department.name if staff.department else "Other"
            staff_by_department.setdefault(dept_name, []).append(staff)

        # Sort staff in each department by role priority
        for dept, staff_list in staff_by_department.items():
            staff_list.sort(
                key=lambda x: role_priority.get(x.role, 1000)
            )

        context["staff_by_department"] = staff_by_department
        return context
       

class ManagementView(TemplateView):
    template_name = "web/pages/management/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Management" 
        return context  
    
class PlacementView(TemplateView):
    template_name = "web/pages/placement/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Placement" 
        return context   
class RecruitmentView(TemplateView):
    template_name = "web/pages/recruitment/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Recruitment" 
        return context    
class Host(TemplateView):
    template_name = "web/pages/recruitment/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Recruitment" 
        return context  
        return context  

class RecruitmentInterns(TemplateView):
    template_name = "web/pages/services/recruitmentIntern.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternRecruitment" 
        return context  

class InternWorkplace(TemplateView):
    template_name = "web/pages/services/intern_workplace.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternWorkplace" 
        return context   

class hostSourcing(TemplateView):
    template_name = "web/pages/services/hostSourcing.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "hostSourcing" 
        return context   

class mentorship_and_site(TemplateView):
    template_name = "web/pages/services/mentorship_and_site.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "mentorship_and_site" 
        return context    

class InductionPostsView(TemplateView):
    template_name = "web/pages/induction/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        induction_post = InductionPost.objects.filter(closed=False)
        induction_posts = InductionPost.objects.filter(closed=False)
        context["induction_post"] = induction_post
        context['induction_posts'] = induction_posts
        return context

# views.py
class InductionApplicationCreateView(CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "web/pages/application-form/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Submit Application"
        induction_post = get_object_or_404(InductionPost, id=self.kwargs["id"])
        context["induction_post"] = induction_post
        return context

    def form_valid(self, form):
        induction_post = get_object_or_404(InductionPost, id=self.kwargs["id"])
        national_id = form.cleaned_data.get('national_id')
        email = form.cleaned_data.get('email').lower()

        # Check for duplicate application by national_id for the same induction_post
        if Application.objects.filter(induction_post=induction_post, national_id=national_id).exists():
            form.add_error('national_id', 'You have already applied for this induction post.')
            return self.form_invalid(form)

        # Check if email is already verified
        existing_verified_app = Application.objects.filter(
            induction_post=induction_post, email=email, email_verified=True
        ).exists()

        if not existing_verified_app:
            # Save temporarily and send OTP
            form.instance.induction_post = induction_post
            form.instance.email = email
            form.instance.save()
            form.instance.send_otp_email()

            return redirect(reverse_lazy("verify_email", kwargs={"application_id": form.instance.pk}))

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("create_questionnaire", kwargs={"application_id": self.object.pk})
    
from django.core.cache import cache
from django.contrib import messages  
def verify_email(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if application.verify_otp(entered_otp):
            return redirect("create_questionnaire", application_id=application.pk)
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "web/pages/verify_email.html", {"application": application})

class SuccefullApplicationView(TemplateView):
    template_name = "web/pages/application_induction_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Application for Induction Success"
        return context
class CheckApplicationStatus(TemplateView):
    template_name = "web/pages/induction/application-status/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Access GET parameters
        email = self.request.GET.get('email')
        contact = self.request.GET.get('contact')
        national_id = self.request.GET.get('national_id')

        # Check if application exists with given email, contact, and national_id
        applications = Application.objects.filter(
            email=email, phone_number=contact, national_id=national_id
        )
 
        context['applications'] = applications
        # Add them to the context
        context['email'] = email
        context['contact'] = contact
        context['national_id'] = national_id
        
        return context


def create_questionnaire(request, application_id):
    application = Application.objects.get(id=application_id)
    if request.method == "POST":
        form = QuestionnaireForm(request.POST)
       
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.application = application
            questionnaire.save()
            return redirect("induction-application-success")  # Redirect to success page
    else:
        form = QuestionnaireForm()
    return render(
        request,
        "web/pages/questionnaire_form.html",
        {"form": form, "application": application},
    )


from django.http import HttpResponse
def upload_questionnaire_affidavit(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    application = questionnaire.application  # Get associated application

    if request.method == "POST":
        form = QuestionnaireAffidavitForm(request.POST, request.FILES, instance=questionnaire)  # Include files
        
        national_id = request.POST.get("national_id")
        email = request.POST.get("email")

        if form.is_valid():
            if application.national_id == national_id and application.email == email:
                form.save()
                return redirect("induction-application-success")  # Redirect to a success page
            else:
                return render(
                    request, 
                    "web/pages/validate_user_for_affidavit.html", 
                    {"form": form, "error": "Your ID number or email do not match our records."}
                )

    else:
        form = QuestionnaireAffidavitForm(instance=questionnaire)

    return render(
        request,
        "web/pages/validate_user_for_affidavit.html",
        {"form": form, "questionnaire": questionnaire},
    )