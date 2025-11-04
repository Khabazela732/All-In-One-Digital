from django.apps import AppConfig
from django.utils.timezone import now


class AdministrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administration'

    def ready(self):
        from .models import InductionPost
        InductionPost.objects.filter(closing_date__lt=now().date(), closed=False).update(closed=True) 
    