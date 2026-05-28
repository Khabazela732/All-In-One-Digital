from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from authentication.decorators import hr_required

from .models import Job, ApplicantProfile, Application
from .forms import ApplicantProfileForm

from hr_portal.services import convert_applicant_to_employee


# =====================================================
# APPLICANT SIDE
# =====================================================

@login_required
def complete_profile(request):

    profile, _ = ApplicantProfile.objects.get_or_create(user=request.user)

    form = ApplicantProfileForm(instance=profile)

    if request.method == "POST":
        form = ApplicantProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_complete = True
            profile.save()
            return redirect("recruitment:job_list")

    return render(request, "recruitment/applicant/profile_form.html", {
        "form": form
    })


@login_required
def job_list(request):

    jobs = Job.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "recruitment/applicant/job_list.html", {
        "jobs": jobs
    })


@login_required
def apply_job(request, job_id):

    profile = get_object_or_404(
        ApplicantProfile,
        user=request.user
    )

    # PROFILE CHECK
    if not profile.is_complete:
        return redirect(
            "recruitment:complete_profile"
        )

    job = get_object_or_404(
        Job,
        id=job_id
    )

    # DUPLICATE CHECK
    already_applied = Application.objects.filter(
        applicant=profile,
        job=job
    ).exists()

    if already_applied:
        return redirect(
            "recruitment:my_applications"
        )

    Application.objects.create(
        applicant=profile,
        job=job,
        status="SUBMITTED"
    )

    return redirect(
        "recruitment:my_applications"
    )

@login_required
def my_applications(request):

    profile = get_object_or_404(
        ApplicantProfile,
        user=request.user
    )

    applications = Application.objects.filter(
        applicant=profile
    ).order_by("-applied_at")

    return render(
        request,
        "recruitment/applicant/my_applications.html",
        {
            "applications": applications
        }
    )
# =====================================================
# HR RECRUITMENT SIDE
# =====================================================

@login_required
@hr_required
def create_job(request):

    if request.method == "POST":

        Job.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            requirements=request.POST.get("requirements"),
            department=request.POST.get("department"),
            location=request.POST.get("location"),
            salary=request.POST.get("salary"),
            created_by=request.user
        )

        return redirect("recruitment:applications")

    return render(
        request,
        "recruitment/hr/create_job.html"
    )

@login_required
def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True
    )

    return render(
        request,
        "recruitment/applicant/job_detail.html",
        {
            "job": job
        }
    )


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

    status_filter = request.GET.get("status")

    if status_filter:
        applications_list = applications_list.filter(status=status_filter)

    return render(request, "recruitment/hr/applications.html", {
        "applications": applications_list,
        "query": query,
        "status_filter": status_filter,
    })


@login_required
@hr_required
def update_application_status(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    if request.method == "POST":
        application.status = request.POST.get("status")
        application.hr_notes = request.POST.get("hr_notes", "")
        application.save()

        return redirect("recruitment:applications")

    return render(request, "recruitment/hr/update_status.html", {
        "application": application
    })


@login_required
@hr_required
def hire_applicant(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    application.status = "HIRED"
    application.save()

    convert_applicant_to_employee(application)

    return redirect("recruitment:applications")