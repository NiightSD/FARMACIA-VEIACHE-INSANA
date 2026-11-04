from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Genera los tokens de API faltantes para los usuarios existentes."

    def handle(self, *args, **options):
        usuarios = get_user_model().objects.all()
        creados = 0
        existentes = 0

        for usuario in usuarios.iterator():
            _, creado = Token.objects.get_or_create(user=usuario)
            if creado:
                creados += 1
            else:
                existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Tokens generados: {creados}. "
                f"Tokens ya existentes: {existentes}."
            )
        )
