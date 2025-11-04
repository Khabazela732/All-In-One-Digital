from django.urls import path
from .views import RotationListView, AllCaseLogsView, CreateMonthlySiteVisitView, SiteVisitListView, EventsView,ViewCompanieOnProfileView,RegisterHostEmployerView, RegisterHostCompanyView, get_events, create_event, get_event_by_date, update_event, events_by_date, RotationReportInternListView, RotationReportDetailView
from administration.views import HomeView,InternProfileView, AllInternsView, ExitReport, HostEmployersListView, QualificationsView, QualificationView, WorkItemView,CreateCompanyLogbookPreview,DistributeLogbookToInterns, InternLogbookView, UpdateApprovalStatus
from hostCampany.views import (
    CompaniesListView,
    CompanyLogbookPreview,
    CreateCompanyLogbookStepTwo,
    DeliverableSelectionForLogbookTemplate,
    ActiveInternListView,
    DepartmentsListView,
    InternLogbookOnHostEmployerView,
    ShiftsListView,
    InternProfileViewHost,
    CreateHostCompanyView,
    CreateHostCompanySuccessView,
    ViewCompanieListView,
    TerminatedInternListView,
    ReportSuccessView,
    CreateCompanyLogbookStepOne,
    
  

)
from . import views
urlpatterns = [
    
    path("", view=HomeView.as_view(), name="coordinator-home"),
    path("rotations/", RotationListView.as_view(), name="co-rotation-list"),
    #Host company
    path("host-employers/", HostEmployersListView.as_view(), name="co-host_employer_list"),
    path(
        "register-host-employer/",
        RegisterHostEmployerView.as_view(),
        name="co_register_host_employer",
    ),
    path("register-host-company/<int:pk>/", RegisterHostCompanyView.as_view(), name="co_register_host_company"),
    path(
        "companies/view/<int:company_id>/employer-profile",
        ViewCompanieOnProfileView.as_view(),
        name="co-company-view-employer-profile",
    ),
    path(
        "intern_profil/<int:intern_id>/",
        InternProfileView.as_view(),
        name="co_intern_profil",
    ),
    path("interns/all", ExitReport.as_view(), name="co_exitreport"),
    #logbook for Coordinators
     path('qualifications/', QualificationsView.as_view(), name='coordanation-qualifications'),
    path('qualification/<int:qualification_id>', QualificationView.as_view(), name='coordanation-qualification'), # Shows qualification details and Work Items
    path('qualification/workitem/<int:workitem_id>', WorkItemView.as_view(), name='coordanation-workitem'), # Shows work item details and deliverables
    path(
        "companies/logbook/<int:logbook_template_id>/",
        CreateCompanyLogbookPreview.as_view(),
        name="coordanation-company-preview-logbook",
    ),
    path(
        "companies/logbook/<int:logbook_template_id>/assignment/<int:company_id>/",
        DistributeLogbookToInterns.as_view(),
        name="coordanation-distribute-logbook",
    ),
    path('logbook/intern/<int:intern_id>', InternLogbookView.as_view(), name='coordanation-admin_intern_logbook'),
    path('logbook/approval-status', UpdateApprovalStatus.as_view(), name='coordanation-approval-status'),

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

    #  Evenet Management
    path("event-management", EventsView.as_view(), name="co-event-management"),

    path('events/', EventsView.as_view(), name='co-events'),
    path('events/data/', get_events, name='co-events-data'),
    path('events/create/', create_event, name='co-create-event'),
    path('events/data/view', get_event_by_date, name='co-create-event'),
    path('events/<int:event_id>/update/', update_event, name='co-update-event'),
    path('events-by-date/', events_by_date, name='co-events_by_date'),
    path("exitreport", AllInternsView.as_view(), name="co-all-interns"),

    path("waiting/", views.waiting_internships, name="co_waiting_internships"),
    path("placed/", views.placed_internships, name="co_placed_internships"),
    path("terminated/", views.terminated_internships, name="co_terminated_internships"),
    path("defaulted/", views.defaulted_internships, name="co_defaulted_internships"),
    path("completed/", views.completed_internships, name="co_completed_internships"),

    path("site-visit/create/", CreateMonthlySiteVisitView.as_view(), name="site-visit-create"),
    path("site-visit/list/", SiteVisitListView.as_view(), name="site-visit-list"),
    path("cases/", AllCaseLogsView.as_view(), name="case-log-list"),

    path('report/', RotationReportInternListView.as_view(), name='rotation-report-intern-list'),
    path('report/<int:intern_id>/', RotationReportDetailView.as_view(), name='rotation-report-detail'),

    

    ]