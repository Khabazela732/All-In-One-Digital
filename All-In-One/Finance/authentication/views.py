from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
# Create your views here.

def role_redirect(request):
    profile = request.user.userprofile

    if profile.role in ["ADMIN", "HR"]:
        return redirect("hr_portal:dashboard")
  # elif profile.role == "EMPLOYEE":
    #    return redirect("employee_dashboard")

    return redirect("login")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        login(request, user)

        # SUPERUSER
        if user.is_superuser:
            return redirect("/admin/")

        profile = getattr(user, "userprofile", None)

        if profile is None:
            messages.error(request, "User profile missing. Contact admin.")
            return redirect("login")

        role = profile.role

        # ROLE ROUTING (FIXED)
        if role == "HR":
            return redirect("hr_portal:dashboard")

       # elif role == "EMPLOYEE":
        #    return redirect("employee_dashboard")

        elif role == "ADMIN":
            return redirect("hr_portal:dashboard")

        else:
            messages.error(request, "Invalid role assigned")
            return redirect("login")

    return render(request, "authentication/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")