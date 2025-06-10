from django.apps import AppConfig


class SellersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sellers'

    def ready(self):
        import sellers.models # This will import models.py where the signal receiver is defined
