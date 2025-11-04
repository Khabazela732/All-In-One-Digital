from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Intern, InternProfile, HostEmployer, Coordinator

admin.site.index_title = "Internship Success"
admin.site.site_title = "Administration"
admin.site.site_header = "<p>Internship Success</p>"


# Custom admin for the User model
class UserAdmin(UserAdmin):
    list_display = ("username", "email", "role")
    list_filter = ("role",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Additional info", {"fields": ("role",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )
    search_fields = ("username", "email")
    ordering = ("username",)


# Register the User model with the custom admin
admin.site.register(User, UserAdmin)
admin.site.register(Intern)
admin.site.register(HostEmployer)
admin.site.register(Coordinator)
