from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="farmaciaapp.crear_token_usuario",
)
def crear_token_usuario(sender, instance, created, raw=False, **kwargs):
    """Crea un token de API automáticamente al registrar un usuario nuevo."""
    if created and not raw:
        Token.objects.get_or_create(user=instance)
