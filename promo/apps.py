# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.apps import AppConfig
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class PromoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'promo'

    def ready(self) -> None:
        import promo.signals
        return super().ready()
