from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

# Create your views here.
from django.contrib.auth.views import LoginView
from authentication.forms import LoginForm


from django.urls import reverse_lazy
from django.contrib.auth import get_user_model


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):

        # Get the user model
        User = get_user_model()
        # Get the current user
        user = self.request.user
        # Check the user's role and redirect accordingly
        if user.role == User.Role.ADMIN:
            return reverse_lazy("admini-home")
        elif user.role == User.Role.INTERN:
            return reverse_lazy("intern-dashboard")
        elif user.role == User.Role.COORDINATOR:
            return reverse_lazy("coordinator-home")
        elif user.role == User.Role.HOST_EMPLOYER:
            return reverse_lazy("host-employer-home")
        elif user.role == User.Role.MARKETING:
            return reverse_lazy("marketing-dashboard")
        elif user.role == User.Role.HR:
            return reverse_lazy("hr-dashboard")
        else:
            # Default URL if role is not recognized
            return reverse_lazy("login")


class SignOutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("home"))
