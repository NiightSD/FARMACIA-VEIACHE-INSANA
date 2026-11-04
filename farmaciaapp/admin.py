from django.contrib import admin

from .models import Medicamento


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "laboratorio",
        "precio",
        "stock",
        "requiere_receta",
        "fecha_vencimiento",
    )
    list_filter = ("requiere_receta", "laboratorio")
    search_fields = ("nombre", "laboratorio", "descripcion")
    ordering = ("nombre",)
