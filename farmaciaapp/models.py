from django.db import models


class Medicamento(models.Model):

    nombre = models.CharField("nombre", max_length=120)
    laboratorio = models.CharField("laboratorio", max_length=100)
    precio = models.IntegerField("precio", help_text="Precio en pesos chilenos (CLP).")
    stock = models.IntegerField("stock", default=0)
    descripcion = models.TextField("descripción")
    requiere_receta = models.BooleanField("requiere receta", default=False)
    fecha_vencimiento = models.DateField("fecha de vencimiento")

    class Meta:
        verbose_name = "medicamento"
        verbose_name_plural = "medicamentos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.laboratorio})"
