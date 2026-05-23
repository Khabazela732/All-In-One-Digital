from django.apps import AppConfig

class AuthenticationConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'

    name = 'authentication'

    def ready(self):
        import authentication.signals


class HrPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_portal'

    def ready(self):
        import hr_portal.signals

