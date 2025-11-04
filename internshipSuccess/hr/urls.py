from django.urls import path
from . import views
from .views import HomeView, hr_waiting_internships, placed_internships,hr_attendance_list, defaulted_internships, terminated_internships,generate_attendance_pdf, completed_internships,  hr_manage_leave_requests
from administration.views import EventsView, InternProfileView, HostEmployerView,  HostEmployersListView, AllInternsView,HearingCreateView
from hostCampany.views import HostEmployerProfile
from .views import (
     RegisterUserView, 
     RegisterStaffView,
     RegisterStaffCompanySuccessView,
     StaffListView,
     StaffProfileView,
     StaffUpdateView, 
     StaffDeleteView,
     VehicleListView,
     VehicleCreateView,
     VehicleDetailView,
     approve_vehicle_request,
     CreateVehicleRequestView,
     UpdateVehicleUsageView,
     AvailableVehicleListView,
     VehicleRequestSuccessView,
     CreateStaffScoringView,
     DepartmentListView,
     CategoryListByDepartmentView,
     TaskListByCategoryView,
     ScoringCategoryCreateView,
     ScoringTaskCreateView,
     ScoringCategoryUpdateView,
     ScoringCategoryDeleteView,
     ScoringTaskUpdateView,
     ScoringTaskDeleteView,
     CreateMonthlySiteVisitView,
        SiteVisitListView,
    )
urlpatterns = [
    path("event-management", EventsView.as_view(), name="hr-event-management"),
    path("hr-dashboard/", view=HomeView.as_view(), name="hr-dashboard"),
    path("waiting/", hr_waiting_internships, name="hr_waiting_internships"),
    path(
        "intern_profil/<int:intern_id>/",
        InternProfileView.as_view(),
        name="hrintern_profile",
    ),
    path(
        "hostemployer/<int:pk>/", HostEmployerView.as_view(), name="hr_hostemployer"
    ),
    path("host-employers/", HostEmployersListView.as_view(), name="hrhost_employer_list"),
    path("hearings/create/", HearingCreateView.as_view(), name="hr_hearing_create"),
    path(
        "host-employer/<int:hostemp_id>",
        HostEmployerProfile.as_view(),
        name="hr-host-employer-profile",
    ),
    path("placed/", placed_internships, name="hrplaced_internships"),
    path("terminated/", terminated_internships, name="hrterminated_internships"),
    path("defaulted/", defaulted_internships, name="hrdefaulted_internships"),
    path("completed/", completed_internships, name="hrcompleted_internships"),
    path("all_interns", AllInternsView.as_view(), name="hr-all-interns"),
    path('manage-leave-requests/', hr_manage_leave_requests, name='hr_manage_leave_requests'),
    path("work-attendance-list/", hr_attendance_list, name="hr_work_attendance_list"),
    path('admin/generate-attendance-pdf/', generate_attendance_pdf, name='hr_generate_attendance_pdf'),

    path("staff/", StaffListView.as_view(), name="staff_list"),
    path("register-user/", RegisterUserView.as_view(), name="register_user"),
    path("register-staff/<int:pk>/", RegisterStaffView.as_view(), name="register_staff_profile"),
    path("register-staff/success/", RegisterStaffCompanySuccessView.as_view(), name="staff_registration_success"),
    path("staff/profile/<int:pk>/", StaffProfileView.as_view(), name="staff-profile-view"),
    path("staff/edit/<int:pk>/", StaffUpdateView.as_view(), name="staff-edit"),
    path("staff/delete/<int:pk>/", StaffDeleteView.as_view(), name="staff-delete"),

    path("site-visit/create/", CreateMonthlySiteVisitView.as_view(), name="hr-site-visit-create"),
    path("site-visit/list/", SiteVisitListView.as_view(), name="hr-site-visit-list"),

    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/create/", VehicleCreateView.as_view(), name="vehicle-create"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
    path("vehicle-request/<int:pk>/approve/", approve_vehicle_request, name="approve-vehicle-request"),
    path("request/", AvailableVehicleListView.as_view(), name="vehicle-request-list"),
    path("request/<int:pk>/create/", CreateVehicleRequestView.as_view(), name="vehicle-request-create"),
    path("usage/<int:pk>/update/", UpdateVehicleUsageView.as_view(), name="vehicle-usage-update"),
    path("request/success/", VehicleRequestSuccessView.as_view(), name="vehicle-request-success"),

    path('scoring/departments/', DepartmentListView.as_view(), name='scoring-department-list'),
    path('scoring/departments/<int:department_id>/categories/', CategoryListByDepartmentView.as_view(), name='scoring-category-list-by-department'),
    path('scoring/departments/<int:department_id>/categories/create/', ScoringCategoryCreateView.as_view(), name='scoring-category-create'),
    path('scoring/categories/<int:category_id>/tasks/', TaskListByCategoryView.as_view(), name='scoring-task-list-by-category'),
    path('scoring/tasks/create/', ScoringTaskCreateView.as_view(), name='scoring-task-create'),
    path('scoring/<int:staff_id>/create/', CreateStaffScoringView.as_view(), name='create-staff-scoring'),
    # Categories
    path('scoring/categories/<int:pk>/edit/', ScoringCategoryUpdateView.as_view(), name='scoring-category-edit'),
    path('scoring/categories/<int:pk>/delete/', ScoringCategoryDeleteView.as_view(), name='scoring-category-delete'),

    # Tasks
    path('scoring/tasks/<int:pk>/edit/', ScoringTaskUpdateView.as_view(), name='scoring-task-edit'),
    path('scoring/tasks/<int:pk>/delete/', ScoringTaskDeleteView.as_view(), name='scoring-task-delete'),
    

    ]