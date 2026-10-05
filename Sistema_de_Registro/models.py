from django.db import models

class Visita(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    motivo = models.CharField(max_length=250)

    hora_entrada = models.DateTimeField(auto_now_add=True)

    hora_salida = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.rut}"