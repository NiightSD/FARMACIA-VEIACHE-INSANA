from django.apps import AppConfig


class FarmaciaappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "farmaciaapp"
    verbose_name = "Farmacia"

    def ready(self):
        # Registra la creación automática de tokens para usuarios nuevos.
        from . import signals  # noqa: F401
