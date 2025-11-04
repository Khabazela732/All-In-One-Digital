import json
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from administration.models import (
    Application,
    InductionEnrollment,
    InductionPost,
    InternDeliverable,
    InternLogbook,
    IntershipEnrollment,
    LeaveRequest,
    Questionnaire,
)
from authentication.models import Intern
from .models import Attendance, WorkAttendance, Assignment, AssignmentTwo
from authentication.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from datetime import date
from django.http import HttpResponseServerError, JsonResponse
from django.db.models import Count
from administration.decorators import intern_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from .forms import ApplicationInternForm, AttendanceForm,LeaveRequestForm,AssignmentForm, AssignmentTwoForm, CaseLogForm
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from coordination.models import CaseLog
from marketing.models import Campaign, SuccessStory, Magazine
from web.models import NewsLetters
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model  # <- Add this line

from .models import IntershipEnrollment

def my_internship(request):
    internship = get_object_or_404(IntershipEnrollment, intern=request.user)
    context = {"internship": internship}
    return render(request, "intern/pages/home/dashboard.html", context)
# Create your views here.

class InternDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "intern/pages/home/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to interns only
        if not request.user.is_authenticated or request.user.role != User.Role.INTERN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternDashboard"
        user = self.request.user

        # ✅ Safer application loading
        try:
            application = Application.objects.get(applicant=user)
            context["application"] = application

            if application.induction_post:
                context["post_id"] = application.induction_post.pk
            else:
                context["post_id"] = None

            try:
                induction_enrollment = InductionEnrollment.objects.get(
                    induction_post=application.induction_post, intern_user=user
                )
                context["induction_enrollment"] = induction_enrollment
            except InductionEnrollment.DoesNotExist:
                context["induction_enrollment"] = None
                messages.warning(
                    self.request,
                    "You are not yet enrolled in any induction program."
                )

        except Application.DoesNotExist:
            context["application"] = None
            messages.info(
                self.request,
                "You haven’t submitted an application yet. Please complete your internship application to proceed."
            )

        # Add latest content regardless of application status
        context["magazines"] = Magazine.objects.order_by("-issue_date")[:5]
        context["success_stories"] = SuccessStory.objects.order_by("-created")[:5]
        context["newsletters"] = NewsLetters.objects.order_by("-created")[:5]
        context["campaigns"] = Campaign.objects.order_by("-created")[:5]

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)



class InductionAttendanceView(TemplateView):
    template_name = "intern/pages/induction/induction_post_applications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternInduction"
        return context


class InternDetailsView(TemplateView):
    template_name = "intern/pages/profile/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternDetails"
        return context

# Logbooks
class LogbookView(TemplateView):
    template_name = "intern/pages/logbook/index.html"
    total_credits = 180
    minimum_credits_required = 144
    percentage_pass = 0.80
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.INTERN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "InternLogbook"
        user = self.request.user
        intern_logbook = InternLogbook.objects.get(intern=user)
        print("This is my logbook", intern_logbook.logbook_template)
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
    
class InternRotationPlanView(LoginRequiredMixin, TemplateView):
    template_name = "intern/pages/rotation_plan.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.role == "INTERN":
            enrollment = getattr(user, "intern_profile", None)
            if enrollment:
                context["rotations"] = enrollment.rotations.all()
        return context
        
class UpdateCompletetionStatus(View):
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
            if action == "complete-deliverable":
                logbook_deliverable.completed = True
            elif action == "cancel-completion":
                logbook_deliverable.completed = False

            logbook_deliverable.save()
            print(logbook_deliverable)
            # Respond with success
            return JsonResponse({"message": "Status updated successfully"})
        except Exception as e:
            # Handle errors
            return JsonResponse({"error": str(e)}, status=400)
    

# END Logbook


class AccountProfileView(LoginRequiredMixin,UpdateView):
    template_name = "intern/pages/profile/profile.html"
    form_class = ApplicationInternForm
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.INTERN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Intern Profile"
        user = self.request.user
        application = Application.objects.get(applicant=user)
        context["application"] = application
        return context
    
    def get_object(self, queryset=None):
        user = self.request.user
        application = get_object_or_404(Application, applicant=user)
        return application
    def get_success_url(self):
        return reverse_lazy("intern-profile")

class ManagePassword(TemplateView):
    template_name = "intern/pages/profile/password-manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Manage Password"
        user = self.request.user
        application = Application.objects.get(applicant=user)
        context["application"] = application
        return context

    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is correct")
        elif new_password != confirm_password:
            messages.error(request, "New Password and confirm password do not match")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfuly")
        return render(request, self.template_name)


def acknowledge_induction(request, application_id):
    application = Application.objects.get(id=application_id)
    user = request.user
    induction_enrollment = InductionEnrollment.objects.get(
        induction_post=application.induction_post, intern_user=user
    )
    
    if request.method == "POST":
        # Check if the affidavit file is in the request
        if request.FILES.get('affidavit'):
            affidavit_file = request.FILES['affidavit']
            # Save the affidavit file to the application object
            application.affidavit.save(affidavit_file.name, affidavit_file)
            application.save()
        
        if "acknowledge_induction" in request.POST:
            # Once the applicant acknowledges the induction attendance, application status must change
            application.status = Application.Status.ACKNOWLEDGED
            application.save()
            induction_enrollment.acknowledged = True
            induction_enrollment.save()
            
            # Redirect to a success page or wherever appropriate
            return redirect("intern-dashboard")
        
        elif "reject" in request.POST:
            # User account is deleted from the database if the applicant does not confirm their availability
            User.objects.get(id=user.id).delete()
            # Delete the application and induction enrollment
            application.delete()
            induction_enrollment.delete()
            
            # Redirect to a page acknowledging rejection or wherever appropriate
            return redirect("login")

    return render(request, "intern-dashboard.html", {"application": application})

@intern_required
def mark_attendance(request, post_id):
    try:
        post = InductionPost.objects.get(pk=post_id)
        induction_enrollments = InductionEnrollment.objects.filter(induction_post=post)
    except InductionPost.DoesNotExist:
        return HttpResponseServerError("InductionPost does not exist.")
    except InductionEnrollment.DoesNotExist:
        return HttpResponseServerError(
            "InductionEnrollment does not exist for this post."
        )

    if request.method == "POST":
        entered_passcode = request.POST.get("passcode")
        scanned_date = date.today()
        # Check if the entered passcode matches the post's passcode
        if entered_passcode != post.passcode:
            return HttpResponseServerError("Incorrect passcode")
        # Get the authenticated user (intern)
        intern = request.user

        # Check if the intern has already attended twice
        if Attendance.objects.filter(intern=intern, induction_post=post).count() >= 2:
            return HttpResponseServerError("You have already attended twice")

        # Check if the scanned date matches either the start_date or end_date
        if scanned_date not in [post.start_date, post.end_date]:
            return HttpResponseServerError(
                "Attendance date must match either the start date or end date"
            )
        
        # Check if the intern has already attended on the same date
        if Attendance.objects.filter(
            intern=intern, induction_post=post, date=scanned_date
        ).exists():
            return HttpResponseServerError("You have already attended on this date")

        # Determine which day to mark attendance
        if scanned_date == post.start_date:
            for enrollment in induction_enrollments:
                enrollment.day_1 = True
                enrollment.save()
        elif scanned_date == post.end_date:
            with transaction.atomic():
                for enrollment in induction_enrollments:
                    enrollment.day_2 = True
                    enrollment.pending_placement = True
                    print("User ID:", request.user.id)
                    enrollment.save()
                # After attending day 2, register the intern in IntershipEnrollment
                IntershipEnrollment.objects.create(
                    intern=intern,
                    status=IntershipEnrollment.InternshipStatus.WAITING,
                    # Set other fields to default values
                )
        try:
            Attendance.objects.create(
                intern=intern, induction_post=post, date=scanned_date
            )
            return redirect("intern-dashboard")
        except Exception as e:
            return HttpResponseServerError("Error marking attendance: " + str(e))

    return render(
        request, "intern/pages/induction/mark_attendance.html", {"post": post}
    )


User = get_user_model()


@method_decorator(login_required, name='dispatch')
class InductionInternView(TemplateView):
    template_name = "intern/pages/induction/index.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.INTERN:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        application = get_object_or_404(Application, applicant=user)

        if application.induction_post:
            context["post_id"] = application.induction_post.pk
        else:
            context["post_id"] = None  

        induction_enrollment = get_object_or_404(
            InductionEnrollment, 
            induction_post=application.induction_post, 
            intern_user=user
        )

        # Check if the intern already submitted an assignment
        assignment = Assignment.objects.filter(intern=user).first()
        context['assignment'] = assignment
        context['assignment_submitted'] = bool(assignment)
        if not assignment:
            context['assignment_form'] = AssignmentForm()

        context["induction_enrollment"] = induction_enrollment
        context["application"] = application
        return context


@method_decorator(login_required, name='dispatch')
class WriteAssignmentView(TemplateView):
    template_name = 'intern/pages/assessments/index.html'

    def get(self, request, *args, **kwargs):
        assignment = Assignment.objects.filter(intern=request.user).first()
        form = AssignmentForm(instance=assignment)
        return render(request, self.template_name, {'form': form, 'assignment': assignment})

    def post(self, request, *args, **kwargs):
        assignment = Assignment.objects.filter(intern=request.user).first()
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.intern = request.user
            assignment.save()

            if assignment.pk and request.FILES:
                messages.success(request, "Assignment updated successfully!")
            else:
                messages.success(request, "Assignment submitted successfully!")

            return redirect('view_assignment')

        return render(request, self.template_name, {'form': form, 'assignment': assignment})

@method_decorator(login_required, name='dispatch')
class ViewAssignmentView(TemplateView):
    template_name = 'intern/pages/assessments/view_assignment.html'

    def get(self, request, *args, **kwargs):
        assignment = get_object_or_404(Assignment, intern=request.user)
        return render(request, self.template_name, {'assignment': assignment})

@login_required
def delete_assignment(request, pk=None):
    """
    Deletes Assignment.
    If pk is None, delete current user's assignment.
    """
    if pk:
        assignment = get_object_or_404(Assignment, pk=pk, intern=request.user)
    else:
        assignment = get_object_or_404(Assignment, intern=request.user)

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('write_assignment')

    return render(request, 'intern/pages/assignment/confirm_delete.html', {'assignment': assignment})

@method_decorator(login_required, name='dispatch')
class WriteAssignmentTwoView(TemplateView):
    template_name = 'intern/pages/assessments/index_two.html'
    
    def get(self, request, *args, **kwargs):
        assignment = AssignmentTwo.objects.filter(intern=request.user).first()
        form = AssignmentTwoForm(instance=assignment)
        return render(request, self.template_name, {'form': form, 'assignment': assignment})

    def post(self, request, *args, **kwargs):
        assignment = AssignmentTwo.objects.filter(intern=request.user).first()
        form = AssignmentTwoForm(request.POST, request.FILES, instance=assignment)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.intern = request.user
            assignment.save()
            messages.success(request, "Assignment Two submitted/updated successfully!")
            return redirect('view_assignment2')

        return render(request, self.template_name, {'form': form, 'assignment': assignment})

@method_decorator(login_required, name='dispatch')
class ViewAssignmentTwoView(TemplateView):
    template_name = 'intern/pages/assignment/view_assignment_two.html'

    def get(self, request, *args, **kwargs):
        assignment = get_object_or_404(AssignmentTwo, intern=request.user)
        return render(request, self.template_name, {'assignment': assignment})

@login_required
def delete_assignment_two(request):
    assignment = get_object_or_404(AssignmentTwo, intern=request.user)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment Two deleted successfully!")
        return redirect('write_assignment2')
    return render(request, 'intern/pages/assignment/confirm_delete.html', {'assignment': assignment})

def apply_for_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)  # Accept file uploads
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.intern = request.user
            leave_request.save()
            return redirect('leave_requests')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'intern/pages/work/apply_for_leave.html', {'form': form})

def view_leave_requests(request):
    leave_requests = LeaveRequest.objects.filter(intern=request.user)
    return render(request, 'intern/pages/work/view_leave_requests.html', {'leave_requests': leave_requests})

class UpdateInternProfile(TemplateView):
    template_name = "intern/pages/profile/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get the application associated with the user
        try:
            application = Application.objects.get(applicant=user)
            context["application"] = application
        except Application.DoesNotExist:
            context["application"] = None  # If the application does not exist
        
        context["title"] = "Update Profile"
        return context


class UpdateInternProfile(TemplateView):
    template_name = "intern/pages/profile/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get the application associated with the user
        try:
            application = Application.objects.get(applicant=user)
            context["application"] = application
        except Application.DoesNotExist:
            context["application"] = None  # If the application does not exist
        
        context["title"] = "Update Profile"
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        
        # Get the application for the user
        application = get_object_or_404(Application, applicant=user)

        # Update the application fields with the submitted data
        application.name = request.POST.get('name', application.name)
        application.surname = request.POST.get('surname', application.surname)
        application.email = request.POST.get('email', application.email)
        application.phone_number = request.POST.get('phone', application.phone_number)
        application.gender = request.POST.get('gender', application.gender)
        application.national_id = request.POST.get('national_id', application.national_id)
        application.post_address = request.POST.get('post_address', application.post_address)

        # Save the updated data
        application.save()

        # Display success message
        messages.success(request, 'Profile updated successfully!')

        # Redirect to the profile update page
        return redirect('update_intern_profile')

from datetime import datetime
from datetime import timedelta
from django.utils.timezone import make_aware, is_naive
@intern_required
def work_attendance(request):
    intern_profile = get_object_or_404(IntershipEnrollment, intern=request.user)
    date_today = timezone.now().date()  # This is timezone-aware
    attendance, created = WorkAttendance.objects.get_or_create(
        intern=intern_profile, date=date_today
    )

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            passcode = form.cleaned_data["passcode"]
            action = form.cleaned_data["action"]
            if passcode == intern_profile.company.passcode:
                if action == "sign_in":
                    current_time = timezone.now()  # Timezone-aware
                    shift_start_time = intern_profile.shift.start_time

                    # Ensure `shift_start_time` is timezone-aware
                    if is_naive(shift_start_time):
                        shift_start_time = make_aware(
                            datetime.combine(date_today, shift_start_time)
                        )

                    # Calculate lateness
                    lateness_threshold = shift_start_time + timedelta(minutes=40)

                    if attendance.sign_in_time is None:
                        attendance.sign_in_time = current_time
                        if current_time <= lateness_threshold:
                            attendance.status = WorkAttendance.Status.PRESENT
                        elif current_time <= shift_start_time + timedelta(hours=3):
                            attendance.status = WorkAttendance.Status.LATE
                        else:
                            attendance.status = WorkAttendance.Status.ABSENT
                        attendance.save()
                        messages.success(request, "Successfully signed in.")
                    else:
                        messages.error(request, "Already signed in.")
                elif action == "sign_out":
                    if attendance.sign_out_time is None:
                        attendance.sign_out_time = timezone.now()
                        attendance.save()
                        messages.success(request, "Successfully signed out.")
                    else:
                        messages.error(request, "Already signed out.")
                return redirect("work_attendance")
            else:
                messages.error(request, "Invalid company passcode.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = AttendanceForm()

    return render(
        request,
        "intern/pages/mark_attendance.html",
        {"form": form, "attendance": attendance},
    )

@intern_required
def sign_in(request):
    intern_profile = get_object_or_404(IntershipEnrollment, intern=request.user)
    date_today = timezone.now().date()
    attendance, created = WorkAttendance.objects.get_or_create(
        intern=intern_profile, date=date_today
    )

    if attendance.sign_in_time is None:
        attendance.sign_in_time = timezone.now()
        attendance.status = WorkAttendance.Status.PRESENT
        attendance.save()
        messages.success(request, "Successfully signed in.")
    else:
        messages.error(request, "Already signed in.")

    return redirect("work_attendance")


@intern_required
def sign_out(request):
    intern_profile = get_object_or_404(IntershipEnrollment, intern=request.user)
    date_today = timezone.now().date()
    attendance = get_object_or_404(
        WorkAttendance, intern=intern_profile, date=date_today
    )

    if attendance.sign_out_time is None:
        attendance.sign_out_time = timezone.now()
        attendance.save()
        messages.success(request, "Successfully signed out of duty. See you tomorrow!")
    else:
        messages.error(request, "Already signed out.")

    return redirect("work_attendance")

class InternLogCaseView(LoginRequiredMixin, CreateView):
    model = CaseLog
    form_class = CaseLogForm
    template_name = "intern/pages/case_log/create.html"

    def form_valid(self, form):
        user = self.request.user
        enrollment = user.intern_profile
        form.instance.intern = enrollment
        form.instance.company = enrollment.company
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("intern-case-log-list")

from django.views.generic import ListView    
class InternCaseLogListView(LoginRequiredMixin, ListView):
    model = CaseLog
    template_name = "intern/pages/case_log/list.html"
    context_object_name = "cases"

    def get_queryset(self):
        return CaseLog.objects.filter(intern=self.request.user.intern_profile)
