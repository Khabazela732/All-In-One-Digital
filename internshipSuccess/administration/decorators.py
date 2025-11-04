from authentication.models import User
from django.shortcuts import redirect
from django.contrib import messages
# DECORATORS

def admin_required(function):
    def wrap(request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('login') # Assuming 'login' is the name of a URL pattern

        # Check if the user has the ADMIN role
        if not request.user.role == User.Role.ADMIN:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home') # Assuming 'home' is the name of a URL pattern

        # If the user passes the checks, proceed with the original view function
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def intern_required(function):
    def wrap(request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('login') # Assuming 'login' is the name of a URL pattern

        # Check if the user has the ADMIN role
        if not request.user.role == User.Role.INTERN:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home') # Assuming 'home' is the name of a URL pattern

        # If the user passes the checks, proceed with the original view function
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap