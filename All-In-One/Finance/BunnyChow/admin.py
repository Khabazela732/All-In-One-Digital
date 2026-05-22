from django.contrib import admin

from .models import (
    Department,
    Employee
)

# =========================================================
# DEPARTMENT ADMIN
# =========================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# EMPLOYEE ADMIN
# =========================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "department",
        "position",
        "hire_date",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
    )

    list_filter = (
        "department",
        "gender",
        "hire_date",
    )