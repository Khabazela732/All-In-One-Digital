from django.shortcuts import redirect
from django.urls import reverse
from hr.models import Staff
from authentication.models import User  # Make sure this path matches your project

class BlockInactiveStaffMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Skip all URLs under 'web' app (i.e. root level)
        # If your system URLs are namespaced (e.g. /intern/, /hr/), this is safe
        system_prefixes = ["/admin/", "/support/", "/hr/", "/coordination/", "/marketing/"]

        # If the request is NOT for system URLs, skip checks (it's likely a web page)
        if not any(path.startswith(prefix) for prefix in system_prefixes):
            return self.get_response(request)

        # ✅ Only run for authenticated users
        if hasattr(request, "user") and request.user.is_authenticated:
            role = request.user.role

            # Allow interns and host employers
            if role in [User.Role.INTERN, User.Role.ADMIN,User.Role.HR, User.Role.HOST_EMPLOYER]:
                return self.get_response(request)

            try:
                staff = request.user.staff
                if staff.status == "Inactive":
                    return redirect("account-suspended")
            except Staff.DoesNotExist:
                return redirect("not-a-staff")

        return self.get_response(request)
