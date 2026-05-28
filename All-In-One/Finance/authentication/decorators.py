from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def hr_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # 1. Authentication check
        if not request.user.is_authenticated:
            return redirect("login")

        # 2. Profile check (safe)
        profile = getattr(request.user, "userprofile", None)

        if profile is None:
            return HttpResponseForbidden("User profile missing")

        # 3. Role check
        if profile.role not in ["HR", "ADMIN"]:
            return HttpResponseForbidden("Access denied")

        return view_func(request, *args, **kwargs)

    return wrapper