from functools import wraps
from django.http import HttpResponseForbidden

def hr_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseForbidden("Not authenticated")

        try:
            role = request.user.userprofile.role
        except:
            return HttpResponseForbidden("No profile")

        if role in ["HR", "ADMIN"]:
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden("Access denied")

    return wrapper