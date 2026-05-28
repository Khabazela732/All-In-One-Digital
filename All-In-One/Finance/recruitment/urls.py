from django.urls import path
from . import views

app_name = "recruitment"

urlpatterns = [
    # =========================
    # APPLICANT SIDE
    # =========================
    path("profile/", views.complete_profile, name="complete_profile"),
    path("jobs/", views.job_list, name="job_list"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("my-applications/", views.my_applications, name="my_applications"),

    # =========================
    # HR RECRUITMENT SIDE
    # =========================

    # CREATE JOB
    path("jobs/create/", views.create_job, name="create_job"),

    # VIEW APPLICATIONS (HR)
    path("applications/", views.applications, name="applications"),

    # UPDATE APPLICATION STATUS
    path("applications/<int:app_id>/update/", views.update_application_status, name="update_application_status"),

    # HIRE APPLICANT
    path("applications/<int:app_id>/hire/", views.hire_applicant, name="hire_applicant"),
    path("jobs/<int:job_id>/",views.job_detail,name="job_detail"),
]