def get_role(user):
    try:
        return user.userprofile.role
    except:
        return None


def is_hr(user):
    return get_role(user) == "HR"


def is_admin(user):
    return get_role(user) == "ADMIN"


def is_employee(user):
    return get_role(user) == "EMPLOYEE"