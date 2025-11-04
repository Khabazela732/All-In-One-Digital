from django.urls import path
from . import views
from .views import (
    CompaniesListView,
    CompanyLogbookPreview,
    CreateCompanyLogbookStepTwo,
    DeliverableSelectionForLogbookTemplate,
    HomeView,
    ActiveInternListView,
    DepartmentsListView,
    InternLogbookOnHostEmployerView,
    ShiftsListView,
    InternProfileViewHost,
    CreateHostCompanyView,
    CreateHostCompanySuccessView,
    ViewCompanieListView,
    ViewCompanieOnProfileView,
    HostEmployerProfile,
    TerminatedInternListView,
    ReportSuccessView,
    CreateCompanyLogbookStepOne,
    CreateCompanyLogbookPreview,
    RotationListView,
    CreateRotationView

  

)

urlpatterns = [
    path("", view=HomeView.as_view(), name="host-employer-home"),
    path("active-interns", view=ActiveInternListView.as_view(), name="active-interns"),
    path("terminated-interns", view=TerminatedInternListView.as_view(), name="terminated-interns"),
    path("departments/", view=DepartmentsListView.as_view(), name="department_list"),
    path("Shifts/", view=ShiftsListView.as_view(), name="shift_list"),
    path(
        "host-employer/<int:hostemp_id>",
        view=HostEmployerProfile.as_view(),
        name="host-employer-profile",
    ),
    path("report-success/", ReportSuccessView.as_view(), name="report_success"),
    path(
        "intern_profile/<int:intern_id>/",
        InternProfileViewHost.as_view(),
        name="intern_profile",
    ),
    path("departments/add/", views.add_department, name="add_department"),
    path('change-department/<int:enrollment_id>/', views.change_department, name='change_department'),
    path("rotations/", RotationListView.as_view(), name="rotation-list"),
    path("rotations/create/", CreateRotationView.as_view(), name="rotation-create"),
    path(
        "departments/delete/<int:department_id>/",
        views.delete_department,
        name="delete_department",
    ),
    path(
        "departments/edit/<int:department_id>/",
        views.edit_department,
        name="edit_department",
    ),
    path("shifts/add/", views.add_shift, name="add_shifts"),
    path("shifts/edit/<int:shift_id>/", views.edit_shift, name="edit_shift"),
    path("shifts/delete/<int:shift_id>/", views.delete_shift, name="delete_shift"),
    path('change-shift/<int:enrollment_id>/', views.change_shift, name='change_shift'),
    path("attendance-list/", views.attendance_list, name="attendance_list"),
    path(
        "approve-attendance/<int:attendance_id>/",
        views.approve_attendance,
        name="approve_attendance",
    ),
    # Host Companies
    path("companies", CompaniesListView.as_view(), name="companies"),
    path("companies/create", CreateHostCompanyView.as_view(), name="companies-create"),
    path(
        "companies/success",
        CreateHostCompanySuccessView.as_view(),
        name="companies-create-success",
    ),
    path(
        "companies/view/<int:company_id>",
        ViewCompanieListView.as_view(),
        name="company-view",
    ),
    path(
        "companies/view/<int:company_id>/employer-profile",
        ViewCompanieOnProfileView.as_view(),
        name="company-view-employer-profile",
    ),
    # Log Books
    path(
        "companies/view/<int:company_id>/logbook",
        CreateCompanyLogbookStepOne.as_view(),
        name="company-new-logbook",
    ),
    path(
        "companies/view/logbook/<int:logbook_template_id>",
        CreateCompanyLogbookStepTwo.as_view(),
        name="company-new-logbook-2",
    ),
    path(
        "companies/view/logbook/<int:logbook_template_id>/deliverable-selection",
        DeliverableSelectionForLogbookTemplate.as_view(),
        name="deliverable-selection",
    ),
    path(
        "companies/logbook/<int:logbbok_id>/",
        CreateCompanyLogbookPreview.as_view(),
        name="company-preview-logbook",
    ),
    
    path('logbook/<int:logbook_template_id>/preview', CompanyLogbookPreview.as_view(), name='host_emp_intern_logbook_preview'),
    path('logbook/<int:intern_logbook_id>', InternLogbookOnHostEmployerView.as_view(), name='host_emp_intern_logbook'),
    
]