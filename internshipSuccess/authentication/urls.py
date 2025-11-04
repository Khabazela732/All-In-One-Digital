from django.urls import path
from .views import CustomLoginView, SignOutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path( 'login/', CustomLoginView.as_view(), name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('auth/password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path(
        "auth/password-reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
