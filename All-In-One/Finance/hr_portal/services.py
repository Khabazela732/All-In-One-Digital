from authentication.models import UserProfile
from hr_portal.models import Employee  # adjust if your model name differs


def convert_applicant_to_employee(application):
    user = application.applicant.user  # from recruitment app

    # 1. Update role
    profile = user.userprofile
    profile.role = "EMPLOYEE"
    profile.save()

    # 2. Create employee record
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            # map fields if needed
        }
    )

    return employee

def hire_applicant(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    application.status = "HIRED"
    application.save()

    convert_applicant_to_employee(application)

    return redirect("application_list")