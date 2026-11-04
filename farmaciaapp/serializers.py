from django.utils import timezone
from rest_framework import serializers

from .models import Medicamento


def _limites_fecha_vencimiento():
    """Entrega la fecha de hoy y el límite de diez años en el futuro."""
    hoy = timezone.localdate()
    try:
        limite = hoy.replace(year=hoy.year + 10)
    except ValueError:
        limite = hoy.replace(year=hoy.year + 10, day=28)
    return hoy, limite


class MedicamentoSerializer(serializers.ModelSerializer):
    """Representación JSON de un medicamento y sus reglas de negocio."""

    class Meta:
        model = Medicamento
        fields = [
            "id",
            "nombre",
            "laboratorio",
            "precio",
            "stock",
            "descripcion",
            "requiere_receta",
            "fecha_vencimiento",
        ]
        read_only_fields = ["id"]

    def validate_nombre(self, value):
        nombre = value.strip()
        if len(nombre) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )
        return nombre

    def validate_laboratorio(self, value):
        return value.strip()

    def validate_precio(self, value):
        if not 1 <= value <= 500000:
            raise serializers.ValidationError(
                "El precio debe estar entre 1 y 500.000 pesos."
            )
        return value

    def validate_stock(self, value):
        if not 0 <= value <= 10000:
            raise serializers.ValidationError(
                "El stock debe estar entre 0 y 10.000 unidades."
            )
        return value

    def validate_fecha_vencimiento(self, value):
        hoy, limite = _limites_fecha_vencimiento()
        if value < hoy:
            raise serializers.ValidationError(
                "La fecha de vencimiento no puede ser anterior a hoy."
            )
        if value > limite:
            raise serializers.ValidationError(
                "La fecha de vencimiento no puede superar los 10 años desde hoy."
            )
        return value
