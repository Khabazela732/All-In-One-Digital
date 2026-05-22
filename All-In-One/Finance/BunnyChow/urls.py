from django.urls import path
from .views import home, AboutView, DashboardView, SignupView, employee_list, add_employee

urlpatterns = [
 path('', home, name='home'),
 path("signup/", SignupView.as_view(), name="signup"),
 path('about/', AboutView.as_view(), name='about'),
 path('dashboard/', DashboardView.as_view(), name='dashboard'),
 path("employees/", employee_list, name="employee_list"),
path("employees/add/", add_employee, name="add_employee"),
]