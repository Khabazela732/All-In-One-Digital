def hr_required(user):
    return user.userprofile.role == "HR"