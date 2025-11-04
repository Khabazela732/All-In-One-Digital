import pandas as pd
from django.core.management.base import BaseCommand
from .models import Application

class Command(BaseCommand):
    help = 'Export all applications to an Excel file'

    def handle(self, *args, **kwargs):
        applications = Application.objects.all()
        data = []
        for application in applications:
            data.append({
                'Name': application.name,
                'Surname': application.surname,
                'National ID': application.national_id,
                'Email': application.email,
                'Phone Number': application.phone_number,
                'Age': application.age,
                'Gender': application.get_gender_display(),
                'Qualification': application.qualification,
                'Qualification Description': application.qualification_description,
                'College Name': application.college_name,
                'Residential Address': application.residental_address,
                'Post Address': application.post_address,
                'Status': application.get_status_display(),
                #'Created At': application.created_at,
            })

        df = pd.DataFrame(data)
        df.to_excel('applications.xlsx', index=False)
        self.stdout.write(self.style.SUCCESS('Successfully exported applications to applications.xlsx'))
