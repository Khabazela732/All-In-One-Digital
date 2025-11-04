from . import views
from django.urls import path
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from .views import LogbookView, UpdateCompletetionStatus,InternCaseLogListView,InternLogCaseView, acknowledge_induction,apply_for_leave,view_leave_requests
from . import views
from .views import (
    InternDashboardView,
    InternDetailsView,
    AccountProfileView,
    ManagePassword,
    InductionInternView,
    UpdateInternProfile,
    WriteAssignmentView,
    ViewAssignmentView,
    WriteAssignmentTwoView,
    ViewAssignmentTwoView,
    InternRotationPlanView,
    
)

urlpatterns = [
    path("dashboard/", view=InternDashboardView.as_view(), name="intern-dashboard"),
    path("myinternship/", views.my_internship, name="my_internship"),
    path("details/", view=InternDetailsView.as_view(), name="intern-details"),
    path("profile", view=AccountProfileView.as_view(), name="intern-profile"),
    path('intern/update/', UpdateInternProfile.as_view(), name='update_intern_profile'),
    path("password/", view=ManagePassword.as_view(), name="manage-password"),
    path("induction/", view=InductionInternView.as_view(), name="induction-intern"),
    
  # Assignment 1
    path('assignment/write/', WriteAssignmentView.as_view(), name='write_assignment'),
    path('assignment/view/', ViewAssignmentView.as_view(), name='view_assignment'),
    path('assignment/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),

    # Assignment 2
    path('assignment/write2/', WriteAssignmentTwoView.as_view(), name='write_assignment2'),
    path('assignment/view2/', ViewAssignmentTwoView.as_view(), name='view_assignment2'),
    path('assignment/delete2/', views.delete_assignment_two, name='delete_assignment_two'),
    path(
        "acknowledge/<int:application_id>/",
        acknowledge_induction,
        name="acknowledge_induction",
    ),
    path(
        "induction/<int:post_id>/mark-attendance/",
        views.mark_attendance,
        name="mark_attendance",
    ),
    path("mark-attendance/", views.work_attendance, name="work_attendance"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path("sign-out/", views.sign_out, name="sign_out"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path('apply-for-leave/', apply_for_leave, name='apply_for_leave'),
    path('leave-requests/', view_leave_requests, name='leave_requests'),

    # Logbooks
    path('logbook/', LogbookView.as_view(), name='intern_logbook'),
    path('logbook/completion-status', UpdateCompletetionStatus.as_view(), name='completion-status'),
    path("rotation-plan/", InternRotationPlanView.as_view(), name="intern-rotation-plan"),

    path("cases/", InternCaseLogListView.as_view(), name="intern-case-log-list"),
    path("cases/create/", InternLogCaseView.as_view(), name="intern-log-case"),
    
    
    
]
