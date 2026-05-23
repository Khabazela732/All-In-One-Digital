from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
import json
from datetime import datetime, timedelta
from .models import Employee, Department
from .forms import EmployeeForm

def home(request):
 return render(request, 'home.html')

class HomeView(View):
    def get(self, request):
        context = {
            'page_title': 'All In One - BunnyChow Home',
        }
        return render(request, 'home.html', context)


class AboutView(View):
    def get(self, request):
        context = {
            'page_title': 'About Kwantatshana Public Secondary School',
            'school': {
                'name': 'Kwantatshana Public Secondary School',
                'location': 'Bergville, Acton Homes, Kwazulu-Natal, South Africa',
                'established': '1985',
                'principal': {
                    'name': 'Mr. Thabo Nkosi',
                    'qualification': 'B.Ed (Hons), NPDE',
                    'experience': '18 years'
                },
                'hods': [
                    {'name': 'Mrs. Nomsa Dlamini', 'department': 'Mathematics & Science'},
                    {'name': 'Mr. Sipho Zulu', 'department': 'Languages'},
                    {'name': 'Ms. Lerato Mthembu', 'department': 'Social Sciences'},
                    {'name': 'Mr. Jabu Khumalo', 'department': 'Business Studies'},
                ]
            },
            'subjects': {
                'grade8_9': ['Mathematics', 'English', 'IsiZulu', 'Natural Sciences', 'Social Sciences', 'Technology', 'Life Orientation', 'Economic Management Sciences'],
                'grade10_12': ['Mathematics / Mathematical Literacy', 'English Home / First Additional', 'IsiZulu Home', 'Physical Sciences', 'Life Sciences', 'Geography / History', 'Accounting / Business Studies', 'Life Orientation']
            }
        }
        return render(request, 'about.html', context)


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        context = {
            'page_title': 'Ordering Dashboard',
            'total_orders': 127,
            'revenue_today': 12450,
            'new_customers': 89,
            'avg_prep_time': '4.2',
            'recent_orders': [
                {'id': '001', 'items': 'BunnyChow x2', 'amount': 89, 'status': 'preparing'},
                {'id': '002', 'items': 'ShisaNyama Pack', 'amount': 250, 'status': 'out-for-delivery'},
                {'id': '003', 'items': 'Gaming Room 2hr', 'amount': 180, 'status': 'completed'},
                {'id': '004', 'items': 'Car Wash Premium', 'amount': 120, 'status': 'preparing'},
            ],
            'chart_data': {
                'labels': ['10AM', '11AM', '12PM', '1PM', '2PM', '3PM'],
                'data': [1200, 1900, 3000, 2500, 4200, 5800]
            }
        }
        return render(request, 'dashboard.html', context)

# 1. Employee list (table)
@login_required
def employee_list(request):
    employees = Employee.objects.all().order_by("last_name", "first_name")
    return render(
        request,
        "employee_list.html",
        {"employees": employees},
    )


# 2. Add new employee (form page)
@login_required
def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Employee added successfully.",
                extra_tags="success",
            )
            return redirect("employee_list")
    else:
        form = EmployeeForm()

    return render(
        request,
        "employee_add.html",
        {"form": form},
    )