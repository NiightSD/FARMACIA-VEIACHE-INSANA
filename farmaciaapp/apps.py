from django.apps import AppConfig


class FarmaciaappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "farmaciaapp"
    verbose_name = "Farmacia"

    def ready(self):
        from . import signals  # noqa: F401
